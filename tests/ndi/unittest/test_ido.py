import unittest
from ndi.ido import Ido

class TestIdo(unittest.TestCase):

    def test_ido_creation(self):
        ido = Ido()
        self.assertIsInstance(ido, Ido)
        self.assertIsNotNone(ido.id())

    def test_ido_uniqueness(self):
        ido1 = Ido()
        ido2 = Ido()
        self.assertNotEqual(ido1.id(), ido2.id())

if __name__ == '__main__':
    unittest.main()
