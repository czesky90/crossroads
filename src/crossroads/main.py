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
                return render_template('index.html', form=form, crmap=google_map,)

    return render_template('index.html', form=form, crmap=google_map, )

def locations_page(first_user_raw_loc, second_user_raw_loc, first_user_name, second_user_name):
    coordinates = generate_coordinates(first_user_raw_loc, second_user_raw_loc)
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
    locations = add_color_icon(json_parser(first_user_raw_loc), 'blue') \
                + add_color_icon(json_parser(second_user_raw_loc), 'red')

    for loc in locations:
        coordinates.append(Coordinates(loc))

    return coordinates

def sample_coordinates():
    coordinates = []

    locations = [
                    {
                     'latitude': 51.205278,
                     'longitude': 16.156389,
                     'datetime': "<b>Z Legni...</b>",
                     'icon': None
                    },
                    {
                     'latitude': 25.066667,
                     'longitude': -77.333333,
                     'datetime': "<b>...na Bahamy człeniu!!!</b>",
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
        self.infobox = location["datetime"]
        self.icon = location['icon']

def json_parser(json_file):
    """
    Parse .json file with Location History from Google Maps timeline.

    :param json_file: JSON file
    :return parsed_locations: a list of chronologically arranged dictionaries, from the oldest ones
    """

    locations = json.loads(json_file)['locations']
    parsed_locations = []

    for location in locations:
        parsed_locations.append(dict(datetime=datetime.fromtimestamp(int(location['timestampMs']) / 1000),
                                     latitude=(location['latitudeE7'] / 10. ** 7),
                                     longitude=(location['longitudeE7'] / 10. ** 7)))

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


def data_which_overlap():
    pass

def similar_coordinates():
    pass