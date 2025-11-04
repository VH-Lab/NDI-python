import unittest
from unittest.mock import Mock
from ndi.file.navigator_class import Navigator
from ndi.file.navigator.epochdir import EpochDir

# Concrete classes for testing
class ConcreteNavigator(Navigator):
    def search_query(self, a,b,c):
        return {}
    def buildepochtable(self):
        return []

class ConcreteEpochDir(EpochDir):
    def search_query(self, a,b,c):
        return {}
    def buildepochtable(self):
        return []


class TestNavigator(unittest.TestCase):
    def test_navigator_instantiation(self):
        session = Mock()
        nav = ConcreteNavigator(session)
        self.assertIsNotNone(nav)

    def test_epochdir_instantiation(self):
        session = Mock()
        nav = ConcreteEpochDir(session)
        self.assertIsNotNone(nav)

if __name__ == '__main__':
    unittest.main()
