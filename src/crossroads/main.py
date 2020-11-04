import os
import json
import jsonschema
from datetime import datetime
from flask import Flask, render_template, request, flash
from flask_material import Material
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, DataRequired, FileRequired, FileAllowed
from wtforms import SubmitField, StringField
from wtforms.validators import Length
from jsonschema import validate

app = Flask(__name__)
Material(app)
app.config.from_object(__name__)
app.config.update(SECRET_KEY=os.getenv("FLASK_SECRET_KEY"))
app.config['GOOGLEMAPS_KEY'] = os.getenv("GOOGLEMAPS_KEY")

GoogleMaps(app)

class HomeForm(FlaskForm):
    first_name_field = StringField('Your name', description='Put here your name',
                                   validators=[DataRequired(), Length(min=2, max=30)])
    first_raw_coordinates = FileField('Upload',
                                      validators=[FileRequired(), FileAllowed(['json'], 'Just Google\'s json!')])
    second_name_field = StringField('Your friend\'s name', description='Put here name of your friend',
                                    validators=[DataRequired(), Length(min=2, max=30)])
    second_raw_coordinates = FileField('Upload',
                                       validators=[FileRequired(), FileAllowed(['json'], 'Just Google\'s json!')])
    submit_button = SubmitField('Find crossed roads!')

@app.route('/', methods=['GET', 'POST'])
def main_page():
    form = HomeForm()
    coordinates = sample_coordinates()
    google_map = generate_map(coordinates)

    if form.validate_on_submit():
        if request.method == 'POST':
            user1 = request.files['first_raw_coordinates']
            first_user_raw_data = user1.read()
            first_user_name = request.form['first_name_field']

            user2 = request.files['second_raw_coordinates']
            second_user_raw_data = user2.read()
            second_user_name = request.form['second_name_field']

            if validate_json(first_user_raw_data) and validate_json(second_user_raw_data):
                return locations_page(first_user_raw_data, second_user_raw_data, first_user_name, second_user_name)
            else:
                flash('Just Google\'s json!')

    return render_template('index.html', form=form, crmap=google_map, )

def locations_page(first_user_raw_loc, second_user_raw_loc, first_user_name, second_user_name):
    full_parsed_coordinate_lists = json_parser(first_user_raw_loc), json_parser(second_user_raw_loc)

    if lists_have_common_parts(full_parsed_coordinate_lists[0], full_parsed_coordinate_lists[1]) is False:
        final_lists = consolation_coordinates(full_parsed_coordinate_lists[0], full_parsed_coordinate_lists[1])

        if final_lists == ([], []):
            return render_template('problems.html', crmap=generate_map(sample_coordinates()),
                                   information="Your time ranges do not match.", content=':(')
    else:
        final_lists = establishing_common_part(full_parsed_coordinate_lists[0], full_parsed_coordinate_lists[1])

    coordinates = generate_coordinates(add_color_icon(final_lists[0], 'blue'), add_color_icon(final_lists[1], 'red'))
    google_map = generate_map(coordinates)

    return render_template('locations.html', crmap=google_map,
                           user_name_one=first_user_name, user_name_two=second_user_name)

def main():
    app.run(host='0.0.0.0', port=8080)

def generate_map(coordinates):

    google_map = Map(
        identifier="crmap",
        lat = coordinates[0].latitude,
        lng = coordinates[0].longitude,
        markers=[(loc.latitude, loc.longitude, loc.infobox, loc.icon) for loc in coordinates],
        style = "height:600px;width:600px;margin:0;",
        scale_control = True,
        streetview_control = True,
        rotate_control = True,
        fullscreen_control = True,
        fit_markers_to_bounds = True
    )
    return google_map

def generate_coordinates(first_user_raw_loc, second_user_raw_loc):
    coordinates = []
    locations = first_user_raw_loc + second_user_raw_loc

    for loc in locations:
        locations[locations.index(loc)]['timestamp'] = datetime.fromtimestamp(int(locations[locations.index(loc)]['timestamp']))
        coordinates.append(Coordinates(loc))
    return coordinates

def sample_coordinates():
    coordinates = []

    locations = [
                    {
                     'latitude': 51.205278,
                     'longitude': 16.156389,
                     'timestamp': "<b>Z Legni...</b>",
                     'icon': None
                    },
                    {
                     'latitude': 25.066667,
                     'longitude': -77.333333,
                     'timestamp': "<b>...na Bahamy człeniu!!!</b>",
                     'icon': None
                    }
                ]

    for loc in locations:
        coordinates.append(Coordinates(loc))

    return coordinates

class Coordinates():
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

def json_parser(json_content):
    """
    Parse .json content with Location History from Google Maps timeline.

    :param json_content: JSON content
    :return parsed_locations: a list of chronologically arranged dictionaries, from the oldest ones
    """

    locations = json.loads(json_content)['locations']
    parsed_locations = []

    for location in locations:
        parsed_locations.append(dict(timestamp=int(location['timestampMs']) // 1000,
                                     latitude=location['latitudeE7'] / 10. ** 7,
                                     longitude=location['longitudeE7'] / 10. ** 7))

    return parsed_locations

def add_color_icon(parsed_locations_list, colour):
    """
    Adds the "icon" key and value depending on the parameter "colour" to the parsed .json file with Location History.

    :param parsed_locations_list: list of dictionaries
    :param colour: (str) the color of the icon to be added
    :return parsed_locations_list: list of dictionaries with "icon" key
    """

    if colour == 'blue':
        icon = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
    else:
        icon = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'

    for location in parsed_locations_list:
        parsed_locations_list[parsed_locations_list.index(location)]['icon'] = icon

    return parsed_locations_list

def validate_json(json_content):
    """
    Checks if the json file matches the pattern in the "schema.json" file.

    :param json_content: JSON file
    :return: (bool) True or False
    """
    json_data = json.loads(json_content)

    with open('schema.json', 'r') as scheme:
        google_schema = json.load(scheme)

    try:
        validate(instance=json_data, schema=google_schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

def lists_have_common_parts(first_data_list, second_data_list):
    """
    Checks that the dates in both dictionary lists have are common parts.

    :param first_data_list: (list) first user dictionaries list with coordinates
    :param second_data_list: (list) second user dictionaries list with coordinates
    :return: (bool) True or False
    """

    if int(first_data_list[-1]['timestamp']) < int(second_data_list[0]['timestamp']) or\
            int(second_data_list[-1]['timestamp']) < int(first_data_list[0]['timestamp']):
        return False
    else:
        return True

def consolation_coordinates(first_data_list, second_data_list):
    """
    If the lists do not coincide but the closest dates are less than 7 days apart,
    returns two new lists that contain only those dates, otherwise, if the time ranges do not match,
    returns two empty lists.

    :param first_data_list: (list) first user dictionaries list with coordinates
    :param second_data_list: (list) second user dictionaries list with coordinates
    :return: (lists) two dictionary lists or two empty lists
    """
    first_new_list = first_data_list.copy()
    second_new_list = second_data_list.copy()

    if 0 <= int(first_new_list[0]['timestamp']) - int(second_new_list[-1]['timestamp']) <= 604800:
        return first_new_list[0:1], second_new_list[-1:]
    elif 0 <= int(second_new_list[0]['timestamp']) - int(first_new_list[-1]['timestamp']) <= 604800:
        return first_new_list[-1:], second_new_list[0:1]
    else:
        first_new_list = []
        second_new_list = []
        return first_new_list, second_new_list

def establishing_common_part(first_data_list, second_data_list):
    """
    Checks which page and where exactly to trim the lists to get only common parts.

    :param first_data_list: (list) first user dictionaries list with coordinates
    :param second_data_list: (list) second user dictionaries list with coordinates
    :return: (lists) two dictionaries lists with overlapping coordinates
    """
    first_list_common_parts = first_data_list.copy()
    second_list_common_parts = second_data_list.copy()

    if int(first_list_common_parts[0]['timestamp']) > int(second_list_common_parts[0]['timestamp']):
        second_list_common_parts = list_shortener(second_list_common_parts,
                                                  int(first_list_common_parts[0]['timestamp']), "up")
    elif int(first_list_common_parts[0]['timestamp']) < int(second_list_common_parts[0]['timestamp']):
        first_list_common_parts = list_shortener(first_list_common_parts,
                                                 int(second_list_common_parts[0]['timestamp']), "up")

    if int(first_list_common_parts[-1]['timestamp']) > int(second_list_common_parts[-1]['timestamp']):
        first_list_common_parts = list_shortener(first_list_common_parts,
                                                 int(second_list_common_parts[-1]['timestamp']), "down")
    elif int(first_list_common_parts[-1]['timestamp']) < int(second_list_common_parts[-1]['timestamp']):
        second_list_common_parts = list_shortener(second_list_common_parts,
                                                  int(first_list_common_parts[-1]['timestamp']), "down")

    return first_list_common_parts, second_list_common_parts

def list_shortener(list_to_trim, cut_point_date, side_to_cut):
    """
    Trims the list of dictionaries from the top or bottom, near the position specified in the arguments.

    :param list_to_trim: list of dictionaries to cut
    :param cut_point_date: (int) date on milliseconds
    :param side_to_cut: (str) 'up' or 'down'
    :return: short_list
    """
    epsilon = 1
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
        return list_to_trim[:ans+1]


def similar_coordinates():
    pass
