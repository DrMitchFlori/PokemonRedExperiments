from typing import Callable, Dict


def scan_event_flags(read_memory: Callable[[int], int], event_names: Dict[str, str], start: int, end: int) -> Dict[str, str]:
    """Return a mapping of event flag keys to names for all set flags."""
    flags: Dict[str, str] = {}
    for address in range(start, end):
        val = read_memory(address)
        for idx in range(8):
            if (val >> idx) & 1:
                key = f"0x{address:X}-{idx}"
                name = event_names.get(key)
                if name:
                    flags[key] = name
    return flags
