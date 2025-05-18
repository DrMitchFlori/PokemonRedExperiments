import json
import unittest
from baselines import memory_addresses

EVENTS_FILE = 'v2/events.json'

class EventFlagTests(unittest.TestCase):
    def setUp(self):
        with open(EVENTS_FILE) as f:
            self.events = json.load(f)

    def test_events_json_complete(self):
        start = memory_addresses.EVENT_FLAGS_START_ADDRESS
        end = memory_addresses.EVENT_FLAGS_END_ADDRESS
        missing = [
            f"0x{addr:X}-{bit}"
            for addr in range(start, end + 1)
            for bit in range(8)
            if f"0x{addr:X}-{bit}" not in self.events
        ]
        self.assertEqual(missing, [])

    def test_lookup_names(self):
        memory = {
            0xD754: 0b00000001,  # Bought Museum Ticket
            0xD755: 0b10000000,  # Beat Brock
        }
        found = []
        for addr, val in memory.items():
            for bit in range(8):
                if val & (1 << bit):
                    key = f"0x{addr:X}-{bit}"
                    found.append(self.events.get(key))
        self.assertIn("Bought Museum Ticket", found)
        self.assertIn("Beat Brock", found)

if __name__ == '__main__':
    unittest.main()
