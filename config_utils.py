import argparse
import json
from pathlib import Path
from typing import Tuple


def load_paths(default_gb_path: str = '../PokemonRed.gb',
               default_init_state: str = '../init.state') -> Tuple[str, str]:
    """Load paths to ROM and initial state.

    Parameters
    ----------
    default_gb_path : str
        Default path to the Game Boy ROM.
    default_init_state : str
        Default path to the emulator initial state.

    Returns
    -------
    Tuple[str, str]
        ``(gb_path, init_state)`` from command line or optional JSON config.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config', type=str,
                        help='JSON file containing "gb_path" and "init_state".')
    parser.add_argument('--gb_path', type=str, help='Path to PokemonRed.gb')
    parser.add_argument('--init_state', type=str, help='Path to emulator state')
    args, _ = parser.parse_known_args()

    config_data = {}
    if args.config:
        with open(Path(args.config), 'r') as f:
            config_data = json.load(f)

    gb_path = args.gb_path or config_data.get('gb_path', default_gb_path)
    init_state = args.init_state or config_data.get('init_state', default_init_state)
    return gb_path, init_state
