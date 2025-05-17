import numpy as np
from unittest.mock import patch
from pathlib import Path

import v3.red_gym_env_v3 as env_v3

class DummyScreen:
    def __init__(self):
        self.ndarray = np.zeros((144, 160, 3), dtype=np.uint8)

class DummyPyBoy:
    def __init__(self, *args, **kwargs):
        self.memory = bytearray(0x10000)
        self.screen = DummyScreen()
    def load_state(self, f):
        pass
    def send_input(self, *args, **kwargs):
        pass
    def tick(self, *args, **kwargs):
        pass
    def set_emulation_speed(self, *args, **kwargs):
        pass


def test_event_logged_after_reset(tmp_path):
    config = {
        "session_path": tmp_path,
        "save_final_state": False,
        "print_rewards": False,
        "headless": True,
        "init_state": str(Path("init.state")),
        "action_freq": 8,
        "max_steps": 2,
        "save_video": False,
        "fast_video": False,
    }

    with patch.object(env_v3, "PyBoy", DummyPyBoy):
        env = env_v3.RedGymEnv(config)
        env.pyboy.memory[env_v3.event_flags_start] = 0b10000000
        env.reset()
        env.step(0)
        assert "0xD747-0" in env.current_event_flags_set
