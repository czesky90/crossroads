import os
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from datetime import datetime as dt
from flask import Flask, render_template, flash, request
from flask_material import Material
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_wtf import Form, RecaptchaField
from flask_wtf.file import FileField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators
from wtforms.validators import Required

app = Flask(__name__)
Material(app)
app.config.from_object(__name__)
app.config.update(SECRET_KEY=os.getenv("FLASK_SECRET_KEY"))
app.config['GOOGLEMAPS_KEY'] = os.getenv("GOOGLEMAPS_KEY")

GoogleMaps(app)

class TelephoneForm(Form):
    country_code = IntegerField('Country Code', [validators.required()])
    area_code = IntegerField('Area Code/Exchange', [validators.required()])
    number = TextField('Number')

class MainForm(Form):
    first_name_field = TextField('Your name', description='Put here your name',
                        validators=[Required()])
    first_raw_coordinates = FileField('Upload')
    second_name_field = TextField('Your friend\'s name', description='Put here name of your friend',
                       validators=[Required()])
    second_raw_coordinates = FileField('Upload')
    submit_button = SubmitField('Find crossed roads!')

    def validate_hidden_field(form, field):
        raise ValidationError('Always wrong')

@app.route('/', methods=['GET', 'POST'])
def main_page():
    # Just for tests in order to create coordinates on map
    coordinates = generate_coordinates()
    form = MainForm()
    map = generate_map(coordinates)
    return render_template('index.html', form = form, crmap = map)

def main():
    app.run(host='0.0.0.0', port=8080)

def generate_map(coordinates):

    map = Map(
        identifier="crmap",
        lat = coordinates[0].latitude,
        lng = coordinates[0].longitude,
        markers=[(loc.latitude, loc.longitude, loc.infobox) for loc in coordinates],
        style = "height:600px;width:600px;margin:0;",
        scale_control = True,
        streetview_control = True,
        rotate_control = True,
        fullscreen_control = True,
        fit_markers_to_bounds = True
    )
    return map

def generate_coordinates():
    coordinates = []
    locations = [
                    {
                     'lat': 51.205278,
                     'lng': 16.156389,
                     'infobox': "<b>Z Legni...</b>"
                    },
                    {
                     'lat': 25.066667,
                     'lng': -77.333333,
                     'infobox': "<b>...na Bahamy człeniu!!!</b>"
                    }
                ]
    for loc in locations:
        coordinates.append(Coordinates(loc))

    return coordinates

class Coordinates():
    def __init__(self, location):
        self.latitude = location["lat"]
        self.longitude = location["lng"]
        self.infobox = location["infobox"]

def backend():
    df_gps = pd.read_json('sample.json')
    print('There are {:,} rows in the location history dataset'.format(len(df_gps)))

    # parse lat, lon, and timestamp from the dict inside the locations column
    df_gps['lat'] = df_gps['locations'].map(lambda x: x['latitudeE7'])
    df_gps['lon'] = df_gps['locations'].map(lambda x: x['longitudeE7'])
    df_gps['timestamp_ms'] = df_gps['locations'].map(lambda x: x['timestampMs'])

    # convert lat/lon to decimalized degrees and the timestamp to date-time
    df_gps['lat'] = df_gps['lat'] / 10.**7
    df_gps['lon'] = df_gps['lon'] / 10.**7
    df_gps['timestamp_ms'] = df_gps['timestamp_ms'].astype(float) / 1000
    df_gps['datetime'] = df_gps['timestamp_ms'].map(lambda x: dt.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    date_range = '{}-{}'.format(df_gps['datetime'].min()[:4], df_gps['datetime'].max()[:4])


    # drop columns we don't need, then show a slice of the dataframe
    df_gps = df_gps.drop(labels=['locations', 'timestamp_ms'], axis=1, inplace=False)
    print(df_gps)
    #df_gps[1000:1005]
