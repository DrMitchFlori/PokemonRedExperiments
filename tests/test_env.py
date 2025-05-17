import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from v2.red_gym_env_v2 import RedGymEnv, event_flags_start

class DummyScreen:
    def __init__(self):
        self.ndarray = np.zeros((144, 160, 3), dtype=np.uint8)

class DummyPyBoy:
    def __init__(self, *_, **__):
        self.screen = DummyScreen()

    def load_state(self, f):
        pass

    def send_input(self, action):
        pass

    def tick(self, ticks, render):
        pass

    def botsupport_manager(self):
        return SimpleNamespace(screen=lambda: self.screen)

@pytest.fixture
def dummy_env(monkeypatch, tmp_path):
    monkeypatch.setattr('v2.red_gym_env_v2.PyBoy', DummyPyBoy)
    conf = {
        'session_path': tmp_path,
        'save_final_state': False,
        'print_rewards': False,
        'headless': True,
        'init_state': str(Path('init.state')),
        'action_freq': 1,
        'max_steps': 10,
        'save_video': False,
        'fast_video': False,
        'gb_path': 'PokemonRed.gb',
    }
    env = RedGymEnv(conf)
    memory = {event_flags_start: 1}
    env.read_m = lambda addr: memory.get(addr, 0)
    return env

def test_reset_step(dummy_env):
    dummy_env.reset()
    obs, _, _, _, _ = dummy_env.step(0)
    assert dummy_env.step_count == 1
    assert 'events' in obs


def test_event_names_load():
    events_path = Path('common/events.json')
    data = json.loads(events_path.read_text())
    assert '0xD747-7' in data
