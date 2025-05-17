import json
from pathlib import Path


EVENT_FLAGS_START = 0xD747
EVENT_FLAGS_END = 0xD7F6

class DummyEnv:
    def __init__(self, memory, event_names):
        self.memory = memory
        self.event_names = event_names
        self.current_event_flags_set = {}

    def read_m(self, addr):
        return self.memory[addr]

    def update_flags(self):
        for address in range(EVENT_FLAGS_START, EVENT_FLAGS_END):
            val = self.read_m(address)
            for bit_idx in range(8):
                if val & (1 << bit_idx):
                    key = f"0x{address:04X}-{bit_idx}"
                    if key in self.event_names:
                        self.current_event_flags_set[key] = self.event_names[key]

def test_event_flag_lookup():
    events_path = Path("v2/events.json")
    with events_path.open() as f:
        event_names = json.load(f)

    memory = bytearray(0x10000)
    memory[EVENT_FLAGS_START] = 0b00000001  # set bit 0

    env = DummyEnv(memory, event_names)
    env.update_flags()

    assert env.current_event_flags_set.get("0xD747-0") == event_names["0xD747-0"]
