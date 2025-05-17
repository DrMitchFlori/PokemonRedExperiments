import asyncio
import unittest
from unittest import mock

try:
    import websockets
except ModuleNotFoundError:  # Provide minimal stub if websockets not installed
    import types, sys
    async def _dummy_connect(*args, **kwargs):
        return None
    websockets = types.SimpleNamespace(
        exceptions=types.SimpleNamespace(WebSocketException=Exception, ConnectionClosed=Exception),
        connect=_dummy_connect
    )
    sys.modules['websockets'] = websockets

try:
    import gymnasium as gym
except ModuleNotFoundError:
    import types, sys
    class DummyWrapper:
        def __init__(self, env):
            self.env = env
    gym = types.SimpleNamespace(Wrapper=DummyWrapper)
    sys.modules['gymnasium'] = gym

import v2.stream_agent_wrapper as v2_wrapper
import baselines.stream_agent_wrapper as base_wrapper

class DummyEmulator:
    def __init__(self):
        self.memory = {v2_wrapper.X_POS_ADDRESS: 0,
                       v2_wrapper.Y_POS_ADDRESS: 0,
                       v2_wrapper.MAP_N_ADDRESS: 0}
    def get_memory_value(self, addr):
        return self.memory.get(addr, 0)

class DummyEnv:
    def __init__(self):
        self.pyboy = DummyEmulator()
        self.seen_coords = []
    def step(self, action):
        return "obs", 0, False, False, {}

def make_wrapper(module):
    env = DummyEnv()
    wrapper = module.StreamWrapper(env)
    wrapper.upload_interval = 1
    return wrapper

class FakeWebSocket:
    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail
    async def send(self, message):
        if self.fail:
            self.fail = False
            raise websockets.exceptions.ConnectionClosed(1000, "closed")
        self.sent.append(message)

def run_step(wrapper, times=1):
    result = None
    for _ in range(times):
        result = wrapper.step(0)
    return result

class StreamWrapperTests(unittest.TestCase):
    def test_counter_increment(self):
        for module in (v2_wrapper, base_wrapper):
            ws = FakeWebSocket()
            async def connect_mock(*args, **kwargs):
                return ws
            with mock.patch.object(module.websockets, 'connect', side_effect=connect_mock):
                wrapper = make_wrapper(module)
                self.assertEqual(wrapper.stream_step_counter, 0)
                run_step(wrapper)
                self.assertEqual(wrapper.stream_step_counter, 1)

    def test_reconnect_on_failure(self):
        for module in (v2_wrapper, base_wrapper):
            ws1 = FakeWebSocket(fail=True)
            ws2 = FakeWebSocket()
            connect_results = [ws1, ws2]
            async def connect_mock(*args, **kwargs):
                return connect_results.pop(0)
            with mock.patch.object(module.websockets, 'connect', side_effect=connect_mock) as connect_mock:
                wrapper = make_wrapper(module)
                run_step(wrapper, times=2)  # second step triggers send and reconnect
                self.assertEqual(connect_mock.call_count, 2)
                self.assertEqual(len(ws2.sent), 1)

if __name__ == '__main__':
    unittest.main()
