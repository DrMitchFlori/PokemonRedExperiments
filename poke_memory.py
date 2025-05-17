"""Shared constants and helpers for Pokemon Red emulator memory.

This module centralizes all Game Boy RAM addresses used across the project
and provides small helper utilities for reading values from a pyboy emulator
instance.  The addresses are taken from documentation at
https://datacrystal.romhacking.net and the pokered disassembly.
"""

from __future__ import annotations

from typing import Iterable, Sequence

# Core addresses
PARTY_SIZE_ADDRESS = 0xD163
X_POS_ADDRESS, Y_POS_ADDRESS = 0xD362, 0xD361
MAP_N_ADDRESS = 0xD35E
BADGE_COUNT_ADDRESS = 0xD356

# Party related
LEVELS_ADDRESSES = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]
PARTY_ADDRESSES = [0xD164, 0xD165, 0xD166, 0xD167, 0xD168, 0xD169]
OPPONENT_LEVELS_ADDRESSES = [0xD8C5, 0xD8F1, 0xD91D, 0xD949, 0xD975, 0xD9A1]

# Event flags
EVENT_FLAGS_START_ADDRESS = 0xD747
EVENT_FLAGS_END_ADDRESS = 0xD886
MUSEUM_TICKET_ADDRESS = 0xD754

# Health related
HP_ADDRESSES = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248]
MAX_HP_ADDRESSES = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269]

# Money
MONEY_ADDRESS_1 = 0xD347
MONEY_ADDRESS_2 = 0xD348
MONEY_ADDRESS_3 = 0xD349

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _memory_view(emulator) -> Sequence[int]:
    """Return a sequence-like view of emulator memory."""
    if hasattr(emulator, "memory"):
        return emulator.memory
    if hasattr(emulator, "get_memory_value"):
        class _Proxy(Sequence[int]):
            def __getitem__(self, idx):
                return emulator.get_memory_value(idx)
            def __len__(self):
                return 0x10000
        return _Proxy()
    raise TypeError("Unsupported emulator interface")


def read_memory(emulator, addr: int) -> int:
    """Read a single byte from ``addr``."""
    return _memory_view(emulator)[addr]


def read_bit(emulator, addr: int, bit: int) -> bool:
    """Return ``True`` if the bit at ``addr`` is set."""
    return bin(256 + read_memory(emulator, addr))[-bit - 1] == "1"


def read_hp(emulator, start: int) -> int:
    """Read a two-byte HP value starting at ``start``."""
    mem = _memory_view(emulator)
    return 256 * mem[start] + mem[start + 1]


def read_hp_fraction(emulator) -> float:
    """Return total party HP fraction."""
    hp_sum = sum(read_hp(emulator, a) for a in HP_ADDRESSES)
    max_hp_sum = sum(read_hp(emulator, a) for a in MAX_HP_ADDRESSES)
    max_hp_sum = max(max_hp_sum, 1)
    return hp_sum / max_hp_sum


def read_party(emulator) -> list[int]:
    """Return party species identifiers."""
    return [read_memory(emulator, addr) for addr in PARTY_ADDRESSES]


def read_event_bits(emulator) -> list[int]:
    """Return event flag bits as a list of 0/1 integers."""
    bits = []
    for addr in range(EVENT_FLAGS_START_ADDRESS, EVENT_FLAGS_END_ADDRESS):
        val = read_memory(emulator, addr)
        bits.extend(int(b) for b in f"{val:08b}")
    return bits


def ensure_unique(addresses: Iterable[int]) -> bool:
    """Utility used in tests to assert uniqueness of addresses."""
    lst = list(addresses)
    return len(lst) == len(set(lst))
