import json
import unittest

event_flags_start = 0xD747
event_flags_end = 0xD87E

class DummyEventEnv:
    def __init__(self):
        with open("v2/events.json") as f:
            self.event_names = json.load(f)
        self.memory = {addr: 0 for addr in range(event_flags_start, event_flags_end)}
        self.current_event_flags_set = {}

    def read_m(self, addr):
        return self.memory.get(addr, 0)

    def generate_event_flag_key(self, address: int, bit: int) -> str:
        return f"0x{address:X}-{bit}"

    def scan_event_flags(self):
        self.current_event_flags_set = {}
        for address in range(event_flags_start, event_flags_end):
            val = self.read_m(address)
            for bit in range(8):
                if val & (1 << bit):
                    key = self.generate_event_flag_key(address, bit)
                    if key in self.event_names:
                        self.current_event_flags_set[key] = self.event_names[key]

    def set_flag(self, address: int, bit: int):
        self.memory[address] |= (1 << bit)

class TestEventScanning(unittest.TestCase):
    def test_scan_event_flags_recognizes_set_flag(self):
        env = DummyEventEnv()
        key = list(env.event_names.keys())[0]
        addr_str, bit_str = key.split("-")
        address = int(addr_str, 16)
        bit = int(bit_str)
        env.set_flag(address, bit)
        env.scan_event_flags()
        self.assertIn(key, env.current_event_flags_set)
        self.assertEqual(env.current_event_flags_set[key], env.event_names[key])

if __name__ == "__main__":
    unittest.main()
