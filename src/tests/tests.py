import unittest
import os
import datetime
from unittest.mock import patch, MagicMock
from src.crossroads import main

class TestCrossRoads(unittest.TestCase):
    tests_dir = os.path.dirname(__file__)
    correct_test_data1 = open(os.path.join(tests_dir, "sample1.json"), "rb").read()
    correct_test_data2 = open(os.path.join(tests_dir, "sample2.json"), "rb").read()

    def test_generate_coordinates(self):
        """ Test generated coordinates """

        correct_coordinates = [{'latitude': 51.207902, 'longitude': 16.16104, 'timestamp': datetime.datetime(2012, 11, 3, 17, 19, 26, 356000), 'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'},
            {'latitude': 51.2078704, 'longitude': 16.1610474, 'timestamp': datetime.datetime(2012, 11, 3, 17, 20, 26, 438000), 'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'},
            {'latitude': 51.2079648, 'longitude': 16.160865, 'timestamp': datetime.datetime(2013, 9, 28, 11, 28, 25, 688000), 'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'},
            {'latitude': 51.2079121, 'longitude': 16.1610401, 'timestamp': datetime.datetime(2012, 11, 3, 17, 19, 26, 356000), 'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'},
            {'latitude': 51.2078805, 'longitude': 16.1610475, 'timestamp': datetime.datetime(2012, 11, 3, 17, 20, 26, 438000), 'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'},
            {'latitude': 51.2079749, 'longitude': 16.1608651, 'timestamp': datetime.datetime(2013, 9, 28, 11, 28, 25, 688000), 'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'}]

        coordinates = main.generate_coordinates(self.correct_test_data1, self.correct_test_data2)

        count = 0
        for coordinate in coordinates:
            self.assertTrue(isinstance(coordinate, main.Coordinates))

            self.assertEqual(coordinate.__repr__(), str(correct_coordinates[count]))
            count += 1

class Test(unittest.TestCase):
    def data_which_overlap(self):
        """ Test json parser """



if __name__ == '__main__':
    unittest.main()