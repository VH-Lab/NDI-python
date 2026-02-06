import unittest
import numpy as np
from ndi.cache import Cache
import time

class TestCache(unittest.TestCase):

    def test_cache_creation(self):
        c = Cache()
        self.assertIsInstance(c, Cache)
        self.assertEqual(c.maxMemory, 10e9)
        self.assertEqual(c.replacement_rule, 'fifo')

        c2 = Cache(maxMemory=5e6, replacement_rule='lifo')
        self.assertEqual(c2.maxMemory, 5e6)
        self.assertEqual(c2.replacement_rule, 'lifo')

    def test_add_and_lookup(self):
        c = Cache(maxMemory=1e6)
        test_data = np.random.rand(100, 100)
        c.add('mykey', 'mytype', test_data)
        retrieved = c.lookup('mykey', 'mytype')
        self.assertTrue(np.array_equal(retrieved['data'], test_data))

    def test_remove(self):
        c = Cache(maxMemory=1e6)
        test_data = np.random.rand(100, 100)
        c.add('mykey', 'mytype', test_data)
        c.remove('mykey', 'mytype')
        retrieved = c.lookup('mykey', 'mytype')
        self.assertIsNone(retrieved)

    def test_clear(self):
        c = Cache(maxMemory=1e6)
        c.add('mykey1', 'mytype', np.random.rand(10, 10))
        c.add('mykey2', 'mytype', np.random.rand(10, 10))
        c.clear()
        self.assertEqual(c.bytes(), 0)

    def test_fifo_replacement(self):
        c = Cache(maxMemory=900000, replacement_rule='fifo')
        c.add('key1', 'type1', np.random.rand(1, 100000))
        c.add('key2', 'type2', np.random.rand(1, 100000))
        retrieved1 = c.lookup('key1', 'type1')
        retrieved2 = c.lookup('key2', 'type2')
        self.assertIsNone(retrieved1)
        self.assertIsNotNone(retrieved2)

    def test_lifo_replacement(self):
        c = Cache(maxMemory=900000, replacement_rule='lifo')
        c.add('key1', 'type1', np.random.rand(1, 100000))
        time.sleep(0.1)
        c.add('key2', 'type2', np.random.rand(1, 100000))
        retrieved1 = c.lookup('key1', 'type1')
        retrieved2 = c.lookup('key2', 'type2')
        self.assertIsNotNone(retrieved1)
        self.assertIsNone(retrieved2)

    def test_error_replacement(self):
        c = Cache(maxMemory=800000, replacement_rule='error')
        c.add('key1', 'type1', np.random.rand(1, 100000))
        with self.assertRaises(Exception):
            c.add('key2', 'type2', np.random.rand(1, 1))

    def test_priority_eviction(self):
        # Test that high priority items are preserved
        c = Cache(maxMemory=800000, replacement_rule='fifo')
        c.add('low_priority_old', 'type', np.random.rand(1, 50000), 0) # 400KB
        time.sleep(0.01)
        c.add('high_priority', 'type', np.random.rand(1, 50000), 10) # 400KB
        time.sleep(0.01)
        c.add('low_priority_new', 'type', np.random.rand(1, 50000), 0) # 400KB

        # low_priority_old should be gone, high_priority should be preserved
        self.assertIsNone(c.lookup('low_priority_old','type'))
        self.assertIsNotNone(c.lookup('high_priority','type'))
        self.assertIsNotNone(c.lookup('low_priority_new','type'))

    def test_adding_large_item(self):
        # Test adding an item that is larger than the cache
        c = Cache(maxMemory=1e6)
        c.add('small_item', 'type', np.random.rand(1,100))

        # This should fail with an error
        with self.assertRaises(Exception):
            c.add('large_item', 'type', np.random.rand(1, 200000))

        # And the cache should be unchanged
        self.assertIsNotNone(c.lookup('small_item','type'))

    def test_complex_lifo_eviction(self):
        # Test LIFO eviction with multiple small items
        c = Cache(maxMemory=1e6, replacement_rule='lifo')
        for i in range(1, 11):
            c.add(f'small{i}', 'type', np.random.rand(1, 10000), i) # 80KB each
            time.sleep(0.01)
        # Cache is now at 800KB

        # Add a large item that will be rejected because it has the lowest priority
        c.add('large_item', 'type', np.random.rand(1, 50000), 0) # 400KB

        # The cache should be unchanged because the new item was not safe to add
        for i in range(1, 11):
            self.assertIsNotNone(c.lookup(f'small{i}','type'))
        self.assertIsNone(c.lookup('large_item','type'))

if __name__ == '__main__':
    unittest.main()
