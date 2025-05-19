import json
import unittest
from pathlib import Path

from v3.event_utils import scan_event_flags

class EventFlagTest(unittest.TestCase):
    def test_pallet_flag_after_reset(self):
        events_path = Path(__file__).resolve().parents[1] / 'v3' / 'events.json'
        with open(events_path) as f:
            event_names = json.load(f)

        memory = {0xD747: 1 << 6}
        flags = scan_event_flags(memory.get, event_names, 0xD747, 0xD748)
        self.assertIn('0xD747-6', flags)

if __name__ == '__main__':
    unittest.main()
