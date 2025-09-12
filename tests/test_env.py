import numpy as np
from pathlib import Path
from v2.red_gym_env_v2 import RedGymEnv, event_flags_start, event_flags_end


def make_env(tmp_path):
    config = {
        'session_path': tmp_path,
        'save_final_state': False,
        'print_rewards': False,
        'headless': True,
        'init_state': str(Path('init.state')),
        'action_freq': 1,
        'max_steps': 10,
        'save_video': False,
        'fast_video': False,
        'gb_path': 'PokemonRed.gb'
    }
    return RedGymEnv(config)


def test_reset_observation_shapes(tmp_path):
    env = make_env(tmp_path)
    obs, info = env.reset()

    assert obs['screens'].shape == (72, 80, env.frame_stacks)
    assert obs['health'].shape == (1,)
    assert obs['level'].shape == (env.enc_freqs,)
    assert obs['badges'].shape == (8,)
    assert obs['events'].shape == ((event_flags_end - event_flags_start) * 8,)
    assert obs['map'].shape == (env.coords_pad*4, env.coords_pad*4, 1)
    assert obs['recent_actions'].shape == (env.frame_stacks,)


def test_step_increments_step_count(tmp_path):
    env = make_env(tmp_path)
    env.reset()
    initial = env.step_count
    env.step(0)
    assert env.step_count == initial + 1


def test_event_reward_and_explore_map(tmp_path):
    env = make_env(tmp_path)
    obs, _ = env.reset()
    # set an event flag in memory
    env.pyboy.memory[event_flags_start] = 0b00000001
    reward_before = env.update_reward()
    env.update_explore_map()
    # event reward should now be positive
    assert env.progress_reward['event'] >= 0
    c = env.get_global_coords()
    assert env.explore_map[c[0], c[1]] == 255
