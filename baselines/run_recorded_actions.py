from pathlib import Path
import pandas as pd
import numpy as np
import argparse
from red_gym_env import RedGymEnv


def find_project_root() -> Path:
    path = Path(__file__).resolve()
    while not (path / "README.md").exists() and path.parent != path:
        path = path.parent
    return path

def run_recorded_actions_on_emulator_and_save_video(sess_id, instance_id, run_index, rom_path: Path, state_path: Path):
    sess_path = Path(f'session_{sess_id}')
    tdf = pd.read_csv(f"session_{sess_id}/agent_stats_{instance_id}.csv.gz", compression='gzip')
    tdf = tdf[tdf['map'] != 'map'] # remove unused 
    action_arrays = np.array_split(tdf, np.array((tdf["step"].astype(int) == 0).sum()))
    action_list = [int(x) for x in list(action_arrays[run_index]["last_action"])]
    max_steps = len(action_list) - 1

    env_config = {
            'headless': True, 'save_final_state': True, 'early_stop': False,
            'action_freq': 24, 'init_state': str(state_path), 'max_steps': max_steps, #ep_length,
            'print_rewards': False, 'save_video': True, 'fast_video': False, 'session_path': sess_path,
            'gb_path': str(rom_path), 'debug': False, 'sim_frame_dist': 2_000_000.0, 'instance_id': f'{instance_id}_recorded'
    }
    env = RedGymEnv(env_config)
    env.reset_count = run_index

    obs = env.reset()
    for action in action_list:
        obs, rewards, term, trunc, info = env.step(action)
        env.render()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay recorded actions and save video")
    parser.add_argument("session_id", help="Session identifier")
    parser.add_argument("instance_id", help="Instance identifier")
    parser.add_argument("run_index", type=int, help="Run index to replay")
    project_root = find_project_root()
    parser.add_argument("--rom", type=Path, default=project_root / "PokemonRed.gb",
                        help="Path to Pokemon Red ROM")
    parser.add_argument("--init-state", type=Path,
                        default=project_root / "has_pokedex_nballs.state",
                        help="Path to initial state file")
    args = parser.parse_args()

    run_recorded_actions_on_emulator_and_save_video(
        args.session_id,
        args.instance_id,
        args.run_index,
        args.rom,
        args.init_state,
    )
