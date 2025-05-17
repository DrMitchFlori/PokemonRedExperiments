import os
from pathlib import Path
import numpy as np

class DummyScreen:
    def __init__(self):
        self.ndarray = np.zeros((144, 160, 3), dtype=np.uint8)
    def screen_ndarray(self):
        return self.ndarray

class DummyBotSupport:
    def __init__(self):
        self._screen = DummyScreen()
    def screen(self):
        return self._screen

class DummyPyBoy:
    def __init__(self, *args, **kwargs):
        self.memory = [0] * 0x10000
        self.screen = DummyScreen()
    def set_emulation_speed(self, speed):
        pass
    def send_input(self, event):
        pass
    def tick(self, *args, **kwargs):
        pass
    def load_state(self, f):
        pass
    def botsupport_manager(self):
        return DummyBotSupport()
    def _rendering(self, enabled):
        pass
    def get_memory_value(self, addr):
        return self.memory[addr]


def test_v2_reset_and_step(monkeypatch, tmp_path):
    from v2 import red_gym_env_v2 as env_mod
    monkeypatch.setattr(env_mod, "PyBoy", DummyPyBoy)

    cwd = os.getcwd()
    monkeypatch.chdir(Path(__file__).resolve().parents[1] / "v2")

    init_state = tmp_path / "init.state"
    init_state.write_bytes(b"\x00")

    config = {
        "session_path": tmp_path,
        "save_final_state": False,
        "print_rewards": False,
        "headless": True,
        "init_state": str(init_state),
        "action_freq": 2,
        "max_steps": 2,
        "save_video": False,
        "fast_video": False,
        "gb_path": "PokemonRed.gb",
    }

    env = env_mod.RedGymEnv(config)
    env.reset()
    assert env.step_count == 0
    env.step(0)
    assert env.step_count == 1

    monkeypatch.chdir(cwd)


def test_minimal_reset_and_step(monkeypatch, tmp_path):
    from baselines import red_gym_env_minimal as env_mod
    monkeypatch.setattr(env_mod, "PyBoy", DummyPyBoy)

    cwd = os.getcwd()
    monkeypatch.chdir(Path(__file__).resolve().parents[1] / "baselines")

    init_state = tmp_path / "init.state"
    init_state.write_bytes(b"\x00")

    env = env_mod.PokeRedEnv("PokemonRed.gb", str(init_state), max_steps=2, headless=True, action_frequency=2)
    env.reset()
    assert env.step_count == 0
    env.step(0)
    assert env.step_count == 1

    monkeypatch.chdir(cwd)
