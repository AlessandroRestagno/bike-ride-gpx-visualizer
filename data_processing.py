import gpxpy
import geopy.distance
import numpy as np
import pandas as pd
import io
import base64
from dash import dash_table

# Function to calculate the gradient
def calculate_gradient(elevation_diff, distance):
    if distance == 0:
        return 0
    return np.round((elevation_diff / distance) * 100, 1)

# Parse GPX file and extract data
def extract_gpx_data(gpx_file):
    gpx = gpxpy.parse(gpx_file)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation
                })
    return points

# Calculate gradients for each point
def calculate_final_data(points):
    latitudes = []
    longitudes = []
    elevations = []
    gradients = []
    distances = []

    for i in range(1, len(points)):
        # Get coordinates for consecutive points
        coords_1 = (points[i-1]['latitude'], points[i-1]['longitude'])
        coords_2 = (points[i]['latitude'], points[i]['longitude'])

        # Calculate the distance in meters between the points
        distance = geopy.distance.distance(coords_1, coords_2).m

        # Calculate the elevation difference
        elevation_diff = points[i]['elevation'] - points[i-1]['elevation']

        # Obtain altitude from point
        altitude = points[i]['elevation']

        # Calculate the gradient
        gradient = calculate_gradient(elevation_diff, distance)

        latitudes.append(points[i]['latitude'])
        longitudes.append(points[i]['longitude'])
        gradients.append(gradient)
        distances.append(distance)
        elevations.append(altitude)

    return latitudes, longitudes, gradients, distances, elevations

def parse_gpx(contents):
    try:
        # Extract the base64-encoded string
        content_string = contents.split(',')[1]

        # Decode and read as a file-like object
        decoded = io.StringIO(io.BytesIO(base64.b64decode(content_string)).read().decode('utf-8'))

        # Extract GPS points from the GPX file
        points = extract_gpx_data(decoded)

        return points
    except Exception as e:
        raise ValueError(f"Error parsing GPX file: {str(e)}")


def build_dataframe(points):
    try:
        # Calculate gradients, distances, and elevations
        latitudes, longitudes, gradients, distances, elevations = calculate_final_data(points)

        # Build the DataFrame
        data = pd.DataFrame({
            'Latitude': latitudes,
            'Longitude': longitudes,
            'Gradient (%)': gradients,
            'Distance (m)': distances,
            'Elevation (m)': elevations
        })

        # Add cumulative distance
        data['Cumulative Distance (m)'] = data['Distance (m)'].cumsum()

        return data
    except Exception as e:
        raise ValueError(f"Error building DataFrame: {str(e)}")


def visualize_data(data):
    try:
        return dash_table.DataTable(
            data=data.head(10).to_dict('records'),
            columns=[{"name": i, "id": i} for i in data.columns],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'center',
                'padding': '5px',
            },
            style_header={
                'backgroundColor': 'lightgrey',
                'fontWeight': 'bold'
            }
        )
    except Exception as e:
        raise ValueError(f"Error visualizing data: {str(e)}")
