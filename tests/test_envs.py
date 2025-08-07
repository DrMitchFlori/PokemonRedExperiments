import pytest
import numpy as np
from pathlib import Path

from gymnasium.utils.env_checker import check_env

# Import environments
from baselines.red_gym_env import RedGymEnv as RedGymEnvV1
from v2.red_gym_env_v2 import RedGymEnv as RedGymEnvV2

REPO_ROOT = Path(__file__).resolve().parents[1]
ROM_PATH = REPO_ROOT / "PokemonRed.gb"
STATE_PATH = REPO_ROOT / "init.state"


def require_rom():
    if not ROM_PATH.exists():
        pytest.skip("PokemonRed.gb not found; skipping environment tests")


def make_config_v1(tmp_path):
    return {
        "debug": False,
        "session_path": tmp_path,
        "save_final_state": False,
        "print_rewards": False,
        "headless": True,
        "init_state": str(STATE_PATH),
        "action_freq": 1,
        "max_steps": 5,
        "early_stop": False,
        "save_video": False,
        "fast_video": True,
        "gb_path": str(ROM_PATH),
        "sim_frame_dist": 1.0,
        "explore_weight": 1.0,
        "use_screen_explore": False,
        "reward_scale": 1.0,
        "extra_buttons": False,
    }


def make_config_v2(tmp_path):
    return {
        "session_path": tmp_path,
        "save_final_state": False,
        "print_rewards": False,
        "headless": True,
        "init_state": str(STATE_PATH),
        "action_freq": 1,
        "max_steps": 5,
        "save_video": False,
        "fast_video": True,
        "gb_path": str(ROM_PATH),
        "explore_weight": 1.0,
        "reward_scale": 1.0,
    }


@pytest.mark.usefixtures("tmp_path")
def test_red_gym_env_api(tmp_path):
    require_rom()
    cfg = make_config_v1(tmp_path)
    env = RedGymEnvV1(cfg)
    check_env(env, skip_render_check=True)

    obs, info = env.reset()
    assert isinstance(obs, np.ndarray)
    assert obs.shape == env.observation_space.shape

    for _ in range(3):
        action = env.action_space.sample()
        obs, _, terminated, truncated, _ = env.step(action)
        assert obs.shape == env.observation_space.shape
        if terminated or truncated:
            break

    env.close()


@pytest.mark.usefixtures("tmp_path")
def test_red_gym_env_v2_api(tmp_path):
    require_rom()
    cfg = make_config_v2(tmp_path)
    env = RedGymEnvV2(cfg)
    check_env(env, skip_render_check=True)

    obs, info = env.reset()
    assert set(obs) == set(env.observation_space.spaces)
    for key, space in env.observation_space.spaces.items():
        assert obs[key].shape == space.shape

    for _ in range(3):
        action = env.action_space.sample()
        obs, _, terminated, truncated, _ = env.step(action)
        assert set(obs) == set(env.observation_space.spaces)
        if terminated or truncated:
            break

    env.close()
