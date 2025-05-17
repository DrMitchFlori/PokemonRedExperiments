import os
from pathlib import Path
import pytest

from v2.red_gym_env_v2 import RedGymEnv
from stable_baselines3 import PPO

ROOT = Path(__file__).resolve().parents[1]
ROM_PATH = ROOT / "PokemonRed.gb"
STATE_PATH = ROOT / "init.state"

skip_msg = "PokemonRed.gb not found; tests requiring the ROM are skipped"

@pytest.mark.skipif(not ROM_PATH.exists(), reason=skip_msg)
def test_env_reset_step(tmp_path):
    cwd = os.getcwd()
    os.chdir(ROOT / "v2")
    try:
        config = {
            "session_path": tmp_path,
            "save_final_state": False,
            "print_rewards": False,
            "headless": True,
            "init_state": str(STATE_PATH),
            "action_freq": 1,
            "max_steps": 16,
            "save_video": False,
            "fast_video": True,
            "gb_path": str(ROM_PATH),
        }
        env = RedGymEnv(config)
        obs, _ = env.reset()
        assert set(obs.keys()) == set(env.observation_space.spaces.keys())
        for key, space in env.observation_space.spaces.items():
            assert obs[key].shape == space.shape
        action = env.action_space.sample()
        obs, *_ = env.step(action)
        assert set(obs.keys()) == set(env.observation_space.spaces.keys())
    finally:
        env.pyboy.stop()
        os.chdir(cwd)


@pytest.mark.skipif(not ROM_PATH.exists(), reason=skip_msg)
def test_ppo_learn(tmp_path):
    cwd = os.getcwd()
    os.chdir(ROOT / "v2")
    try:
        config = {
            "session_path": tmp_path,
            "save_final_state": False,
            "print_rewards": False,
            "headless": True,
            "init_state": str(STATE_PATH),
            "action_freq": 1,
            "max_steps": 32,
            "save_video": False,
            "fast_video": True,
            "gb_path": str(ROM_PATH),
        }
        env = RedGymEnv(config)
        model = PPO(
            "MultiInputPolicy",
            env,
            n_steps=8,
            batch_size=4,
            n_epochs=1,
            learning_rate=1e-3,
            verbose=0,
        )
        model.learn(total_timesteps=128)
    finally:
        env.pyboy.stop()
        os.chdir(cwd)

