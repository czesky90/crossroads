import unittest
import os
from src.crossroads.main import JsonProcessing, CoordinatesFactory
from src.tests.test_data import InputTestData, CorrectTestData


class TestJsonProcessing(unittest.TestCase):
    tests_dir = os.path.dirname(__file__)
    user_raw_data = open(os.path.join(tests_dir, "sample1.json"), "rb").read()

    def setUp(self):
        self.json_content = JsonProcessing(self.user_raw_data)

    def test_parser(self):
        """ Test parser """

        parsed_locations = self.json_content.parse()
        correct_parsed_locations = InputTestData.parsed_data1_with_common_part

        self.assertEqual(str(parsed_locations), str(correct_parsed_locations))


class TestCoordinatesFactory(unittest.TestCase):

    def setUp(self):

        # to_test_lists_have_common_parts
        self.data_lists_with_common_part \
            = CoordinatesFactory(InputTestData.parsed_data1_with_common_part,
                                 InputTestData.parsed_data2_with_common_part)
        self.data_lists_without_common_part \
            = CoordinatesFactory(InputTestData.parsed_data1_without_common_part,
                                 InputTestData.parsed_data2_without_common_part)

        # to_test_consolation_coordinates
        self.data_lists_without_common_part_break_less_than_7_days_first_data_greater_second_data \
            = CoordinatesFactory(InputTestData.parsed_data1_without_common_part_break_less_than_7_days,
                                 InputTestData.parsed_data2_without_common_part_break_less_than_7_days)
        self.data_lists_without_common_part_break_less_than_7_days_first_data_less_second_data \
            = CoordinatesFactory(InputTestData.parsed_data2_without_common_part_break_less_than_7_days,
                                 InputTestData.parsed_data1_without_common_part_break_less_than_7_days)
        self.data_lists_without_common_part_to_consolation_coordinates \
            = CoordinatesFactory(InputTestData.parsed_data1_without_common_part,
                                 InputTestData.parsed_data2_without_common_part)

        # to_test_establishing_common_part
        self.data_first_list_older_than_second \
            = CoordinatesFactory(InputTestData.parsed_data1_with_common_part, InputTestData.parsed_data2_with_common_part)
        self.data_first_list_younger_than_second \
            = CoordinatesFactory(InputTestData.parsed_data2_with_common_part, InputTestData.parsed_data1_with_common_part)
        self.data_first_list_bigger_than_second \
            = CoordinatesFactory(InputTestData.parsed_data_bigger_list, InputTestData.parsed_data_smaller_list)
        self.data_first_list_smaller_than_second \
            = CoordinatesFactory(InputTestData.parsed_data_smaller_list, InputTestData.parsed_data_bigger_list)
        self.data_lists_with_only_common_parts_correct_to_first_list_older_than_second \
            = CoordinatesFactory(CorrectTestData.correct_data_first_only_common_parts, CorrectTestData.correct_data_second_only_common_parts)
        self.data_lists_with_only_common_parts_correct_to_first_list_younger_than_second\
            = CoordinatesFactory(CorrectTestData.correct_data_second_only_common_parts, CorrectTestData.correct_data_first_only_common_parts)

        # to_test_add_icon and to_test_which_color_icon
        self.data_lists_without_icons \
            = CoordinatesFactory(InputTestData.parsed_data1_without_icons, InputTestData.parsed_data2_without_icons)
        self.data_lists_with_icons \
            = CoordinatesFactory(InputTestData.parsed_data1_with_blue_icons, InputTestData.parsed_data2_with_red_icons)

        # to_generate_coordinate
        self.data_lists_to_generate_coordinate \
            = CoordinatesFactory(InputTestData.parsed_data1_to_generate_coordinates, InputTestData.parsed_data2_to_generate_coordinates)

    def test_lists_have_common_parts(self):
        """ Test lists have common parts """

        test_with_common_parts = CoordinatesFactory.lists_have_common_parts(self.data_lists_with_common_part)
        test_without_common_parts = CoordinatesFactory.lists_have_common_parts(self.data_lists_without_common_part)

        self.assertTrue(test_with_common_parts)
        self.assertFalse(test_without_common_parts)

    def test_consolation_coordinates(self):
        """ Test consolation coordinates """

        test_distance_between_lists_is_less_than_7_days_first_data_greater_second_data \
            = CoordinatesFactory.consolation_coordinates(self.data_lists_without_common_part_break_less_than_7_days_first_data_greater_second_data)
        test_distance_between_lists_is_less_than_7_days_first_data_less_second_data \
            = CoordinatesFactory.consolation_coordinates(self.data_lists_without_common_part_break_less_than_7_days_first_data_less_second_data)
        test_distance_between_lists_is_greater_than_7_days \
            = CoordinatesFactory.consolation_coordinates(self.data_lists_without_common_part_to_consolation_coordinates)

        self.assertEqual(test_distance_between_lists_is_less_than_7_days_first_data_greater_second_data, CorrectTestData.correct_consolation_coordinates_first_data_greater_second_data)
        self.assertEqual(test_distance_between_lists_is_less_than_7_days_first_data_less_second_data, CorrectTestData.correct_consolation_coordinates_first_data_less_second_data)
        self.assertEqual(test_distance_between_lists_is_greater_than_7_days, ([], []))

    def test_establishing_common_part(self):
        """ Test establishing common part"""

        test_first_data_first_element_older_second_data_first_element_and_first_data_last_element_younger_second_data_last_element \
            = CoordinatesFactory.establishing_common_part(self.data_first_list_older_than_second)
        test_first_data_first_element_younger_second_data_first_element_and_first_data_last_element_older_second_data_last_element \
            = CoordinatesFactory.establishing_common_part(self.data_first_list_younger_than_second)
        test_first_data_first_element_older_second_data_first_element_and_first_data_last_element_older_second_data_last_element \
            = CoordinatesFactory.establishing_common_part(self.data_first_list_bigger_than_second)
        test_first_data_first_element_younger_second_data_first_element_and_first_data_last_element_younger_second_data_last_element \
            = CoordinatesFactory.establishing_common_part(self.data_first_list_smaller_than_second)

        self.assertEqual(
            test_first_data_first_element_older_second_data_first_element_and_first_data_last_element_younger_second_data_last_element,
            self.data_lists_with_only_common_parts_correct_to_first_list_older_than_second.__repr__())
        self.assertEqual(
            test_first_data_first_element_younger_second_data_first_element_and_first_data_last_element_older_second_data_last_element,
            self.data_lists_with_only_common_parts_correct_to_first_list_younger_than_second.__repr__())
        self.assertEqual(
            test_first_data_first_element_older_second_data_first_element_and_first_data_last_element_older_second_data_last_element,
            self.data_lists_with_only_common_parts_correct_to_first_list_older_than_second.__repr__())
        self.assertEqual(
            test_first_data_first_element_younger_second_data_first_element_and_first_data_last_element_younger_second_data_last_element,
            self.data_lists_with_only_common_parts_correct_to_first_list_younger_than_second.__repr__())

    def test_list_shortener(self):
        """ Test list shortener """

        shortened_list_from_the_top = CoordinatesFactory.list_shortener(InputTestData.parsed_data1_to_list_shortener, 1438631356, "up")
        shortened_list_from_the_bottom = CoordinatesFactory.list_shortener(InputTestData.parsed_data2_to_list_shortener, 1438631962, "down")

        self.assertEqual(shortened_list_from_the_top, CorrectTestData.correctly_shortened_list1)
        self.assertEqual(shortened_list_from_the_bottom, CorrectTestData.correctly_shortened_list2)


    def test_add_icon(self):
        """ Test add icon """

        test_icons_have_been_added_properly = CoordinatesFactory.add_icon(self.data_lists_without_icons)

        self.assertEqual(test_icons_have_been_added_properly, self.data_lists_with_icons.__repr__())

    def test_which_color_icon(self):
        """ Test which color icon """

        test_with_blue = CoordinatesFactory.which_color_icon(InputTestData.parsed_data1_without_icons, "blue")
        test_with_red = CoordinatesFactory.which_color_icon(InputTestData.parsed_data2_without_icons, "red")

        self.assertEqual(test_with_blue, InputTestData.parsed_data1_with_blue_icons)
        self.assertEqual(test_with_red, InputTestData.parsed_data2_with_red_icons)

    def test_generate_coordinates(self):
        """ Test generate coordinates """

        correct_coordinates = InputTestData.parsed_data_after_generate_coordinate

        coordinates = CoordinatesFactory.generate_coordinates(self.data_lists_to_generate_coordinate)

        count = 0
        for coordinate in coordinates:
            self.assertTrue(isinstance(coordinate, CoordinatesFactory.CoordinatesForGoogleMaps))
            self.assertEqual(coordinate.__repr__(), str(correct_coordinates[count]))
            count += 1


if __name__ == '__main__':
    unittest.main()
