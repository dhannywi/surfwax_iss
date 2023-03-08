#!/usr/bin/env python3

from geopy.geocoders import Nominatim
from flask import Flask, request
import time
import math
import requests
import xmltodict
import yaml

app = Flask(__name__)
data = {}
MEAN_EARTH_RADIUS = 6371.0

def get_data() -> dict:
    '''
    Function fetches XML data from a URL and returns XML data as nested dictionaries. 
    Args:
        None
    Returns:
        data (dict): Nested dictionaries of the OEM data.
    '''
    global data
    data.clear()
    response = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.text) # xmltodict.parse(response.content) works too
    return data

def get_config() -> dict:
    '''
    Function reads a configuration file and return the associated values, or return a default.
    Args:
        None
    Returns:
        result (dict): A dictionary containing configuration (default or custom).
    '''
    default_config = {"debug": True}
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        # print(f"Couldn't load the config file; details: {e}")
        return default_config

def correct_longtitude(num: float) -> float:
    '''
    Given a number, function returns corrected longtitude value.
    Args:
        num (float): A longtitude value.
    Returns:
        result (float): Corrected longtitude value.
    '''
    if num > 180:
        return num - 360
    elif num < -180:
        return num + 360
    else:
        return num


@app.route('/', methods=['GET'])
def get_oem_data() -> dict:
    '''
    Function reads data stored in the `data` global variable. Returns nested dictionaries. 
    Args:
        None
    Returns:
        data (dict): Nested dictionaries of the OEM data.
    '''
    get_data()
    return data


@app.route('/epochs', methods=['GET'])
def get_epochs() -> list:
    '''
    Function fetches data stored in `data` global variable and iterates through the nested dictionary using a set of keys.
    Returns a list of Epochs from the dataset.
    Args:
        none
    Returns:
        epochs (list): A list of all Epochs in the data set (or modified list if limit and/or offset is specified).
                       Returns an error message (str) in cases of invalid input or no data.
    '''
    if len(data) == 0:
        return 'No data found. Please reload data.\n', 400
    
    epochs = []
    for i in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        epochs.append(i['EPOCH'])

    # implementing /epochs?limit=int&offset=int
    try:
        limit = int(request.args.get('limit', len(epochs)))
    except ValueError:
        return 'Bad Request. Invalid limit parameter.\n', 400
    try:
        offset = int(request.args.get('offset', 0))
    except ValueError:
        return 'Bad Request. Invalid offset parameter.\n', 400
    
    epochs = epochs[offset:]
    epochs = epochs[:limit]
    if len(epochs) == 0:
        return 'Bad Request. `offset` or `limit` parameter is either too large or too small.\n', 400
    else:
        return epochs


@app.route('/epochs/<epoch>', methods=['GET'])
def get_state_vectors(epoch: str) -> dict:
    '''
    Given a string, this function retrieve data, iterates through the nested dictionaries
    with a set of keys to retreive data for the requested epoch.  
    Returns a dictionary containing information for a given epoch.
    Args:
        epoch (str): A specific Epoch in the data set, requested by user.
    Returns:
        result (dict): State vectors for a specific Epoch from the data set.
                       Returns an error message (str) in cases of invalid input or no data.
    '''
    if len(data) == 0:
        return 'No data found. Please reload data.\n', 400
    elif epoch not in get_epochs():
        return 'The epoch you requested is not in the data.\n', 400
    else:
        for i in data['ndm']['oem']['body']['segment']['data']['stateVector']:
            if i['EPOCH'] == epoch:
                return i
            else:
                continue


@app.route('/epochs/<epoch>/speed', methods=['GET'])
def calculate_speed(epoch: str) -> dict:
    '''
    Given a string, this function calls the `get_state_vectors()` function to retrieve the state vector (dict) for a given epoch.
    Iterates through the dictionary, pulling out values associated with a given key.
    Returns instantaneous speed for a specific epoch in the data set.
    Args:
        epoch (str): A specific Epoch in the data set, requested by user.
    Returns:
        result (dict): A dictionary containing instantaneous speed (float) for a specific Epoch in the data set, and unit measure.
                       Returns an error message (str) in cases of invalid input or no data.
    '''
    if len(data) == 0:
        return 'No data found. Please reload data.\n', 400
    state_vec = get_state_vectors(epoch)

    try:
        x_dot = float(state_vec['X_DOT']['#text'])
        y_dot = float(state_vec['Y_DOT']['#text'])
        z_dot = float(state_vec['Z_DOT']['#text'])
    except TypeError:
        return 'We are unable to calculate speed. Invalid Epoch.\n', 400

    speed = math.sqrt( (x_dot**2) + (y_dot**2) + (z_dot**2) )
    return {"value": speed, "units": "km/s"}


@app.route('/help', methods=['GET'])
def help_info() -> str:
    '''
    Function returns help text (as a string) that briefly describes each route.
    Args:
        None
    Returns:
        help_str (str):  Help text that briefly describes each route
    '''
    help_str = '''
    Usage: curl localhost:5000[ROUTE]

    A Flask application for querying and returning interesting information from the ISS data set.

    Route                           Method  What it returns
    /                               GET     Return entire data set
    /epochs                         GET     Return list of all Epochs in the data set
    /epochs?limit=int&offset=int    GET     Return modified list of Epochs given query parameters
    /epochs/<epoch>                 GET     Return state vectors for a specific Epoch from the data set
    /epochs/<epoch>/speed           GET     Return instantaneous speed for a specific Epoch in the data set
    /help                           GET     Return help text that briefly describes each route
    /delete-data                    DELETE  Delete all data from the dictionary object
    /post-data                      POST    Reload the dictionary object with data from the web
    /comment 	                    GET     Return 'comment' list object from ISS data
    /header 	                    GET     Return 'header' dict object from ISS data
    /metadata 	                    GET     Return 'metadata' dict object from ISS data
    /epochs/<epoch>/location 	    GET     Return latitude, longitude, altitude, and geoposition for given Epoch
    /now 	                    GET     Return latitude, longitude, altidue, and geoposition for Epoch that is nearest in time
    \n'''
    return help_str


@app.route('/delete-data', methods=['DELETE'])
def delete_data() -> str:
    '''
    Function to clear data stored in the `data` global variable.
    Args:
        None
    Returns:
        result (str): String confirming deletion of data.
    '''
    global data
    if len(data) == 0:
        return 'No data to delete.\n', 400
    
    data.clear()
    return 'All the data has been removed.\n'


@app.route('/post-data', methods=['POST'])
def post_data() -> dict:
    '''
    Function to populate (or re-populate) `data` global variable with the OEM data set.
    Args:
        None
    Returns:
        data (dict): Nested dictionaries of the OEM data.
    '''
    global data
    get_data()
    return data


@app.route('/comment', methods=['GET'])
def get_comment() -> list:
    '''
    Function fetches `comment` from data.
    Args:
        None
    Returns:
        result (list): A list containing `comment` information.
    '''
    try:
        return data['ndm']['oem']['body']['segment']['data']['COMMENT']
    except KeyError:
        return 'No data found. Please reload data.\n', 400


@app.route('/header', methods=['GET'])
def get_header() -> dict:
    '''
    Function fetches `header` from data.
    Args:
        None
    Returns:
        result (dict): A list containing `header` information.
    '''
    try:
        return data['ndm']['oem']['header']
    except KeyError:
        return 'No data found. Please reload data.\n', 400


@app.route('/metadata', methods=['GET'])
def get_metadata() -> dict:
    '''
    Function fetches `metadata` from data.
    Args:
        None
    Returns:
        result (dict): A dictionary containing `metadata` information.
    '''
    try:
        return data['ndm']['oem']['body']['segment']['metadata']
    except KeyError:
        return 'No data found. Please reload data.\n', 400


@app.route('/epochs/<epoch>/location', methods=['GET'])
def get_location(epoch: str) -> dict:
    '''
    Given a string, this function calls the `get_state_vectors()` function to retrieve the state vector (dict) for a given epoch.
    Iterates through the dictionary, pulling out values associated with a given key.
    Returns a dictionary containing latitude, longitude, altitude, and geoposition for given Epoch in the data set.
    Args:
        epoch (str): A specific Epoch in the data set, requested by user.
    Returns:
        location (dict): A dictionary containing latitude, longitude, altitude, and geoposition.
    '''
    if len(data) == 0:
        return 'No data found. Please reload data.\n', 400
    
    state_vec = get_state_vectors(epoch)
    try:
        epoch = state_vec['EPOCH']
        x = float(state_vec['X']['#text'])
        y = float(state_vec['Y']['#text'])
        z = float(state_vec['Z']['#text'])
    except Exception:
        return 'Bad request. Invalid Epoch.\n', 400

    time_epoch = time.mktime(time.strptime(epoch[:-5], '%Y-%jT%H:%M:%S'))
    utc_time = time.gmtime(time_epoch)
    hrs = utc_time.tm_hour
    mins = utc_time.tm_min

    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 14
    alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS

    lon = correct_longtitude(lon)

    geocoder = Nominatim(user_agent='iss_tracker')
    geoloc = geocoder.reverse((lat, lon), zoom=18, language='en')
    try:
        loc = [i for i in geoloc.raw.values()][7] # index 6 for only location or 7 for more info
    except AttributeError:
        loc = 'Unknown location, possibly somewhere over the ocean.'
    
    location = {"latitude": lat, "longtitude": lon, "altitude": {"value": alt, "units": "km"}, "geo": loc}
    return location

@app.route('/now', methods=['GET'])
def location_now() -> dict:
    if len(data) == 0:
        return 'No data found. Please reload data.\n', 400
    
    epochs = get_epochs()
    if type(epochs) != list:
        return 'No data.\n', 400    
    
    time_now = time.time()
    time_diff = []
    for e in epochs:
        time_epoch = time.mktime(time.strptime(e[:-5], '%Y-%jT%H:%M:%S'))
        difference = time_now - time_epoch
        time_diff.append(difference)

    abs_diff = min(time_diff, key=abs)
    position = time_diff.index(abs_diff)
    closest_epoch = epochs[position]

    time_format = time.mktime(time.strptime(closest_epoch[:-5], '%Y-%jT%H:%M:%S'))
    epoch_time = time.gmtime(time_format)

    location_now = {"closest_epoch": closest_epoch,\
                    "seconds_from_now": abs_diff,\
                    "location": get_location(closest_epoch),\
                    "speed": calculate_speed(closest_epoch)}
    return location_now
    

if __name__ == '__main__':
    get_data()

    config = get_config()
    if config.get('debug', True):
        app.run(debug=True, host='0.0.0.0')
    else:
        app.run(host='0.0.0.0')
