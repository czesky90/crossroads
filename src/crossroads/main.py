import os
import json
import jsonschema
from datetime import datetime
from flask import Flask, render_template, request
from flask_material import Material
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, DataRequired, FileRequired, FileAllowed
from wtforms import SubmitField, StringField, IntegerField
from wtforms.validators import Length
from jsonschema import validate
from geopy import distance

app = Flask(__name__)
Material(app)
app.config.from_object(__name__)
app.config.update(SECRET_KEY=os.getenv("FLASK_SECRET_KEY"))
app.config['GOOGLEMAPS_KEY'] = os.getenv("GOOGLEMAPS_KEY")

GoogleMaps(app)


class HomeForm(FlaskForm):
    first_name_field = StringField('Enter your name:',
                                   validators=[DataRequired(), Length(min=2, max=30)])
    first_raw_coordinates = FileField('Upload your JSON file  ',
                                      validators=[FileRequired(), FileAllowed(['json'], 'Just Google\'s json!')])

    second_name_field = StringField('Enter your friend\'s name:',
                                    validators=[DataRequired(), Length(min=2, max=30)])
    second_raw_coordinates = FileField('Upload your friend\'s JSON file ',
                                       validators=[FileRequired(), FileAllowed(['json'], 'Just Google\'s json!')])

    distance_limit_in_m = IntegerField('Distance limit (in meters):', default=1000)
    time_limit_in_h = IntegerField('Time limit (in hours):', default=24)

    submit_button = SubmitField('Find crossed roads!')


@app.route('/', methods=['GET', 'POST'])
def main_page():
    form = HomeForm()

    if form.validate_on_submit():
        if request.method == 'POST':
            user1 = request.files['first_raw_coordinates']
            first_user_raw_data = user1.read()
            first_user_name = request.form['first_name_field']

            user2 = request.files['second_raw_coordinates']
            second_user_raw_data = user2.read()
            second_user_name = request.form['second_name_field']

            distance_limit = int(request.form['distance_limit_in_m'])
            time_limit = int(request.form['time_limit_in_h'])

            return main_crossroads(first_user_raw_data, second_user_raw_data,
                                   first_user_name, second_user_name, distance_limit, time_limit)

    return render_template('index.html', form=form)


@app.route('/')
def problems(information):
    return render_template('problems.html', information=information, content=':(')


@app.route('/')
def locations_page(final_coordinates, first_user_name, second_user_name):
    google_map = generate_map(final_coordinates)

    return render_template('locations.html', crmap=google_map,
                           user_name_one=first_user_name, user_name_two=second_user_name)


def main():
    app.run(host='0.0.0.0', port=8080)


def generate_map(coordinates):
    google_map = Map(
        identifier="crmap",
        lat=coordinates[0].latitude,
        lng=coordinates[0].longitude,
        markers=[(loc.latitude, loc.longitude, loc.infobox, loc.icon) for loc in coordinates],
        style="height:600px;width:600px;margin:0;",
        scale_control=True,
        streetview_control=True,
        rotate_control=True,
        fullscreen_control=True,
        fit_markers_to_bounds=True
    )
    return google_map


class JsonProcessing:
    def __init__(self, json_content):
        self.json_content = json_content

    def validate(self):
        """
        Checks if the json file matches the pattern in the "schema.json" file.

        :param: JSON file
        :return: (bool) True or False
        """
        json_data = json.loads(self.json_content)

        with open('schema.json', 'r') as scheme:
            google_schema = json.load(scheme)

        try:
            validate(instance=json_data, schema=google_schema)
        except jsonschema.exceptions.ValidationError as err:
            return False
        return True

    def parse(self):
        """
        Parse .json content with Location History from Google Maps timeline.

        :param: JSON content
        :return parsed_locations: a list of chronologically arranged dictionaries, from the oldest ones
        """

        locations = json.loads(self.json_content)['locations']
        parsed_locations = []

        for location in locations:
            parsed_locations.append(dict(timestamp=int(location['timestampMs']) // 1000,
                                         latitude=location['latitudeE7'] / 10. ** 7,
                                         longitude=location['longitudeE7'] / 10. ** 7))

        return parsed_locations


class CoordinatesFactory:
    def __init__(self, first, second):
        self.first_data_list = first
        self.second_data_list = second
        self.coordinates_for_google = self.CoordinatesForGoogleMaps

    def __repr__(self):
        return self.first_data_list, self.second_data_list

    class CoordinatesForGoogleMaps:
        def __init__(self, location):
            self.latitude = location["latitude"]
            self.longitude = location["longitude"]
            self.infobox = location["timestamp"]
            self.icon = location['icon']

        def __repr__(self):
            return str({
                "latitude": self.latitude,
                "longitude": self.longitude,
                "timestamp": self.infobox,
                "icon": self.icon
            })

    def lists_have_common_parts(self):
        """
        Checks that the dates in both dictionary lists have are common parts.

        :param: (list) first user dictionaries list with coordinates
        :param: (list) second user dictionaries list with coordinates
        :return: (bool) True or False
        """

        if int(self.first_data_list[-1]['timestamp']) < int(self.second_data_list[0]['timestamp']) or \
                int(self.second_data_list[-1]['timestamp']) < int(self.first_data_list[0]['timestamp']):
            return False
        else:
            return True

    def consolation_coordinates(self):
        """
        If the lists do not coincide but the closest dates are less than 7 days apart,
        returns two new lists that contain only those dates, otherwise, if the time ranges do not match,
        returns two empty lists.

        :param: (list) first user dictionaries list with coordinates
        :param: (list) second user dictionaries list with coordinates
        :return: (lists) two dictionary lists or two empty lists
        """

        if 0 <= int(self.first_data_list[0]['timestamp']) - int(self.second_data_list[-1]['timestamp']) <= 604800:
            return self.first_data_list[0:1], self.second_data_list[-1:]

        elif 0 <= int(self.second_data_list[0]['timestamp']) - int(self.first_data_list[-1]['timestamp']) <= 604800:
            return self.first_data_list[-1:], self.second_data_list[0:1]

        else:
            self.first_data_list = []
            self.second_data_list = []
            return self.first_data_list, self.second_data_list

    def establishing_common_part(self):
        """
        Checks which page and where exactly to trim the lists to get only common parts.

        :param: (list) first user dictionaries list with coordinates
        :param: (list) second user dictionaries list with coordinates
        :return: (lists) two dictionaries lists with overlapping coordinates
        """

        if int(self.first_data_list[0]['timestamp']) > int(self.second_data_list[0]['timestamp']):
            self.second_data_list = self.list_shortener(self.second_data_list,
                                                        int(self.first_data_list[0]['timestamp']), "up")
        elif int(self.first_data_list[0]['timestamp']) < int(self.second_data_list[0]['timestamp']):
            self.first_data_list = self.list_shortener(self.first_data_list,
                                                       int(self.second_data_list[0]['timestamp']), "up")

        if int(self.first_data_list[-1]['timestamp']) > int(self.second_data_list[-1]['timestamp']):
            self.first_data_list = self.list_shortener(self.first_data_list,
                                                       int(self.second_data_list[-1]['timestamp']), "down")
        elif int(self.first_data_list[-1]['timestamp']) < int(self.second_data_list[-1]['timestamp']):
            self.second_data_list = self.list_shortener(self.second_data_list,
                                                        int(self.first_data_list[-1]['timestamp']), "down")

        return self.first_data_list, self.second_data_list

    @staticmethod
    def list_shortener(list_to_trim, cut_point_date, side_to_cut):
        """
        Trims the list of dictionaries from the top or bottom, near the position specified in the arguments.

        :param list_to_trim: list of dictionaries to cut
        :param cut_point_date: (int) date on seconds
        :param side_to_cut: (str) 'up' or 'down'
        :return: short_list
        """
        epsilon = 10000
        wanted = cut_point_date
        low = 0
        high = len(list_to_trim) - 1
        ans = (high + low) // 2

        while abs(int(list_to_trim[ans]['timestamp']) - wanted) >= epsilon:
            if int(list_to_trim[ans]['timestamp']) <= wanted:
                low = ans
            else:
                high = ans
            ans = (high + low) // 2

        if side_to_cut == 'up':
            return list_to_trim[ans:]
        else:
            return list_to_trim[:ans + 1]

    def searches_for_close_coordinates(self, distance_limit, time_limit):
        """
        Finds coordinates that are distant from each other maximally by the values declared
        by the user (time and distance).

        :param: (list) first user dictionaries list with overlapping coordinates
        :param: (list) second user dictionaries list with overlapping coordinates
        :param distance_limit: (int) distance limit in m
        :param time_limit: (int) time limit in h
        :return: (lists) two lists of dictionaries with coordinates up to 1000m and 24h
        """
        time_limit_in_s = time_limit * 3600

        new_first_data_list = []
        new_second_data_list = []

        min_index = 0
        max_index = 0

        max_starting_timestamp = self.first_data_list[0]['timestamp'] + time_limit_in_s
        for coordinate in self.second_data_list:
            if coordinate['timestamp'] >= max_starting_timestamp:
                max_index = self.second_data_list.index(coordinate)
                break
            else:
                max_index = self.second_data_list.index(self.second_data_list[-1])

        for coordinate_from_first in self.first_data_list:
            try:
                while coordinate_from_first['timestamp'] - time_limit_in_s >= self.second_data_list[min_index]['timestamp']:
                    min_index += 1
                    break

                while coordinate_from_first['timestamp'] + time_limit_in_s >= self.second_data_list[max_index]['timestamp']:
                    max_index += 1
                    break
            except IndexError:
                break

            for coordinate_from_second in self.second_data_list[min_index:max_index]:
                dist = abs(float(distance.distance((coordinate_from_first['latitude'], coordinate_from_first['longitude']),
                                               (coordinate_from_second['latitude'], coordinate_from_second['longitude'])).m))
                if dist <= distance_limit:
                    if coordinate_from_first not in new_first_data_list:
                        new_first_data_list.append(coordinate_from_first)
                    if coordinate_from_second not in new_second_data_list:
                        new_second_data_list.append(coordinate_from_second)

        self.first_data_list = new_first_data_list
        self.second_data_list = new_second_data_list

        return self.first_data_list, self.second_data_list

    def add_icon(self):
        """
        Adds the "icon" key and value depending on the parameter "colour" to the parsed .json file
        with Location History.

        :param: list of dictionaries
        :param: (str) the color of the icon to be added
        :return parsed_locations_list: list of dictionaries with "icon" key
        """
        first_locations_list_with_icon = self.which_color_icon(self.first_data_list, 'blue')
        second_locations_list_with_icon = self.which_color_icon(self.second_data_list, 'red')

        return first_locations_list_with_icon, second_locations_list_with_icon

    @staticmethod
    def which_color_icon(locations_list, color):

        if color == 'blue':
            icon = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
        else:
            icon = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'

        for location in locations_list:
            locations_list[locations_list.index(location)]['icon'] = icon

        return locations_list

    def generate_coordinates(self):

        coordinates = []
        locations = self.first_data_list + self.second_data_list

        for loc in locations:
            locations[locations.index(loc)]['timestamp'] = datetime.fromtimestamp(
                int(locations[locations.index(loc)]['timestamp']))
            coordinates.append(self.coordinates_for_google(loc))

        return coordinates


def main_crossroads(first_user_raw_data, second_user_raw_data,
                    first_user_name, second_user_name, distance_limit, time_limit):
    first_user_json_file_object = JsonProcessing(first_user_raw_data)
    second_user_json_object = JsonProcessing(second_user_raw_data)

    if first_user_json_file_object.validate() and second_user_json_object.validate():

        coordinates_in_time = CoordinatesFactory(first_user_json_file_object.parse(), second_user_json_object.parse())
        overlaps = coordinates_in_time.lists_have_common_parts()

        if not overlaps:
            if coordinates_in_time.consolation_coordinates() == ([], []):

                return problems("Your time ranges do not match.")
            else:
                coordinates_in_time.add_icon()
                final_coordinates = coordinates_in_time.generate_coordinates()

                return locations_page(final_coordinates, first_user_name, second_user_name)

        else:
            coordinates_in_time.establishing_common_part()
            if coordinates_in_time.searches_for_close_coordinates(distance_limit, time_limit) == ([], []):

                return problems("Your coordinates are more than %dm apart." % distance_limit)
            else:
                coordinates_in_time.add_icon()
                final_coordinates = coordinates_in_time.generate_coordinates()

                return locations_page(final_coordinates, first_user_name, second_user_name)

    else:

        return problems("Just Google's json!")
