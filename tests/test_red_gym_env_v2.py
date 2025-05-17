import os
import sys
import types
import importlib
import tempfile
from pathlib import Path
import numpy as np

# ---- stub dependencies ----

class DummyScreen:
    def __init__(self):
        self.ndarray = np.zeros((144, 160, 1), dtype=np.uint8)

class DummyPyBoy:
    def __init__(self, *args, **kwargs):
        self.memory = np.zeros(0x10000, dtype=np.uint8)
        self.screen = DummyScreen()
    def load_state(self, f):
        pass
    def set_emulation_speed(self, speed):
        pass
    def send_input(self, *args, **kwargs):
        pass
    def tick(self, *args, **kwargs):
        pass

class DummyWindowEvent:
    PRESS_ARROW_DOWN = 0
    PRESS_ARROW_LEFT = 1
    PRESS_ARROW_RIGHT = 2
    PRESS_ARROW_UP = 3
    PRESS_BUTTON_A = 4
    PRESS_BUTTON_B = 5
    PRESS_BUTTON_START = 6
    RELEASE_ARROW_DOWN = 7
    RELEASE_ARROW_LEFT = 8
    RELEASE_ARROW_RIGHT = 9
    RELEASE_ARROW_UP = 10
    RELEASE_BUTTON_A = 11
    RELEASE_BUTTON_B = 12
    RELEASE_BUTTON_START = 13

class DummyVideoWriter:
    def __init__(self, *a, **k):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
    def add_image(self, *a, **k):
        pass
    def close(self):
        pass

# simple stubs used by the environment
sys.modules.setdefault('mediapy', types.SimpleNamespace(VideoWriter=DummyVideoWriter))

def downscale_stub(arr, factors):
    return arr[::factors[0], ::factors[1], :]

sys.modules.setdefault('skimage', types.SimpleNamespace(transform=types.SimpleNamespace(downscale_local_mean=downscale_stub)))
sys.modules.setdefault('skimage.transform', types.SimpleNamespace(downscale_local_mean=downscale_stub))
sys.modules.setdefault('einops', types.SimpleNamespace(repeat=lambda arr, pattern, h2=1, w2=1: np.repeat(np.repeat(arr, h2, axis=0), w2, axis=1)))
spaces_stub = types.SimpleNamespace(Box=lambda *a, **k: None,
                                   MultiBinary=lambda *a, **k: None,
                                   MultiDiscrete=lambda *a, **k: None,
                                   Discrete=lambda *a, **k: None,
                                   Dict=lambda x: None)
sys.modules.setdefault('gymnasium', types.SimpleNamespace(Env=object, spaces=spaces_stub))
sys.modules.setdefault('gymnasium.spaces', spaces_stub)
pyboy_utils_stub = types.SimpleNamespace(WindowEvent=DummyWindowEvent)
sys.modules.setdefault('pyboy.utils', pyboy_utils_stub)
sys.modules.setdefault('pyboy', types.SimpleNamespace(PyBoy=DummyPyBoy, utils=pyboy_utils_stub))

# ---- helper to create environment ----

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / 'v2'
sys.path.insert(0, str(ENV_PATH))
red_gym_env_v2 = importlib.import_module('red_gym_env_v2')
sys.path.pop(0)
red_gym_env_v2.PyBoy = DummyPyBoy  # ensure stub is used


def make_env(max_steps=2):
    config = {
        'session_path': Path(tempfile.mkdtemp()),
        'save_final_state': False,
        'print_rewards': False,
        'headless': True,
        'init_state': ROOT / 'init.state',
        'action_freq': 1,
        'max_steps': max_steps,
        'save_video': False,
        'fast_video': False,
        'gb_path': ROOT / 'PokemonRed.gb',
    }
    cwd = os.getcwd()
    os.chdir(ENV_PATH)
    env = red_gym_env_v2.RedGymEnv(config)
    os.chdir(cwd)
    return env


def test_reset_observation_structure():
    env = make_env()
    obs, info = env.reset()
    expected_keys = {'screens', 'health', 'level', 'badges', 'events', 'map', 'recent_actions'}
    assert set(obs.keys()) == expected_keys
    assert obs['screens'].shape == env.output_shape
    assert obs['health'].shape == (1,)
    assert obs['level'].shape == (env.enc_freqs,)
    events_size = (red_gym_env_v2.event_flags_end - red_gym_env_v2.event_flags_start) * 8
    assert obs['events'].shape == (events_size,)
    assert obs['map'].shape == (env.coords_pad*4, env.coords_pad*4, 1)
    assert obs['recent_actions'].shape == (env.frame_stacks,)


def test_step_counter_and_max_steps():
    env = make_env(max_steps=2)
    env.reset()
    assert env.step_count == 0
    env.step(0)
    assert env.step_count == 1
    _, _, _, done, _ = env.step(0)
    assert env.step_count == 2
    assert done is True
