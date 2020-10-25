import unittest
import os
from unittest.mock import patch, MagicMock
from crossroads import main

class TestCrossRoads(unittest.TestCase):
    tests_dir = os.path.dirname(__file__)
    correct_test_data1 = open(os.path.join(tests_dir, "sample.json"), "rb").read()
    correct_test_data2 = open(os.path.join(tests_dir, "sample2.json"), "rb").read()

    def test_generate_coordinates(self):
        """ Test generated cooridnates """
        #correct_coordinates = None
        coordinates = main.generate_coordinates(self.correct_test_data1, self.correct_test_data2)
        for coordinate in coordinates:
            self.assertTrue(isinstance(coordinate, main.Coordinates))
            print(coordinate.__repr__())
        #assertEqual(coordinates, correct_coordinates)

if __name__ == '__main__':
    unittest.main()