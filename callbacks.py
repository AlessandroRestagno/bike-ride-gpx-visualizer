import io
import base64
import gpxpy
import pandas as pd
import numpy as np
import geopy.distance
from dash import html, Input, Output, State, dash_table

# Define helper functions
def calculate_gradient(elevation_diff, distance):
    if distance == 0:
        return 0
    return np.round((elevation_diff / distance) * 100, 1)

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

def calculate_final_data(points):
    latitudes = []
    longitudes = []
    elevations = []
    gradients = []
    distances = []

    for i in range(1, len(points)):
        coords_1 = (points[i-1]['latitude'], points[i-1]['longitude'])
        coords_2 = (points[i]['latitude'], points[i]['longitude'])

        distance = geopy.distance.distance(coords_1, coords_2).m
        elevation_diff = points[i]['elevation'] - points[i-1]['elevation']
        altitude = points[i]['elevation']
        gradient = calculate_gradient(elevation_diff, distance)

        latitudes.append(points[i]['latitude'])
        longitudes.append(points[i]['longitude'])
        gradients.append(gradient)
        distances.append(distance)
        elevations.append(altitude)

    return latitudes, longitudes, gradients, distances, elevations

# Callback to handle file upload and display data
def register_callbacks(app):
    @app.callback(
        Output('output-data-upload', 'children'),
        [Input('upload-gpx', 'contents')],
        [State('upload-gpx', 'filename')]
    )
    def parse_and_display_gpx(contents, filename):
        if contents is not None:
            content_type, content_string = contents.split(',')
            decoded = io.StringIO(io.BytesIO(base64.b64decode(content_string)).read().decode('utf-8'))

            try:
                points = extract_gpx_data(decoded)
                latitudes, longitudes, gradients, distances, elevations = calculate_final_data(points)

                data = pd.DataFrame({
                    'Latitude': latitudes,
                    'Longitude': longitudes,
                    'Gradient (%)': gradients,
                    'Distance (m)': distances,
                    'Elevation (m)': elevations
                })
                data['Cumulative Distance (m)'] = data['Distance (m)'].cumsum()

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
                return f"An error occurred while parsing the GPX file: {str(e)}"
        return html.Div(   
                "Upload a GPX file to see its data.",
                className="text-center mt-4"
            )
