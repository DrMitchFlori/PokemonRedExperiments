import unittest
import poke_memory as pm

class TestPokeMemory(unittest.TestCase):
    def test_required_addresses_present(self):
        required = [
            'X_POS_ADDRESS',
            'Y_POS_ADDRESS',
            'MAP_N_ADDRESS',
            'HP_ADDRESSES',
            'MAX_HP_ADDRESSES',
            'EVENT_FLAGS_START_ADDRESS',
            'EVENT_FLAGS_END_ADDRESS',
        ]
        for name in required:
            self.assertTrue(hasattr(pm, name), f"{name} missing")

    def test_coordinate_addresses_unique(self):
        vals = [pm.X_POS_ADDRESS, pm.Y_POS_ADDRESS, pm.MAP_N_ADDRESS]
        self.assertEqual(len(vals), len(set(vals)))

    def test_hp_addresses_unique(self):
        self.assertTrue(pm.ensure_unique(pm.HP_ADDRESSES))
        self.assertTrue(pm.ensure_unique(pm.MAX_HP_ADDRESSES))
        self.assertTrue(set(pm.HP_ADDRESSES).isdisjoint(pm.MAX_HP_ADDRESSES))

    def test_event_flag_range_valid(self):
        self.assertGreater(pm.EVENT_FLAGS_END_ADDRESS, pm.EVENT_FLAGS_START_ADDRESS)

if __name__ == '__main__':
    unittest.main()
