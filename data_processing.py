import gpxpy
import geopy.distance
import numpy as np
import pandas as pd
import io
import base64
from dash import html
import re
import plotly.colors as colors
import plotly.graph_objects as go
import plotly.express as px

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

# Helper function to convert 'rgb(r,g,b)' string to tuple (r, g, b)
def rgb_to_tuple(rgb_string):
    return tuple(map(int, re.findall(r'\d+', rgb_string)))

# Helper function to convert (r, g, b) tuple to 'rgb(r,g,b)' string
def tuple_to_rgb(rgb_tuple):
    return f'rgb({rgb_tuple[0]},{rgb_tuple[1]},{rgb_tuple[2]})'

# Linear interpolation between two RGB values
def interpolate_colors(color1, color2, num_steps):
    return [(int(color1[0] + (color2[0] - color1[0]) * t),
             int(color1[1] + (color2[1] - color1[1]) * t),
             int(color1[2] + (color2[2] - color1[2]) * t))
            for t in np.linspace(0, 1, num_steps)]

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
        # Given colorscale
        original_colors = colors.sequential.Jet

        # Create the new expanded colorscale
        expanded_colors = []

        for i in range(len(original_colors) - 1):
            # Convert the current color and the next color to RGB tuples
            color_start = rgb_to_tuple(original_colors[i])
            color_end = rgb_to_tuple(original_colors[i + 1])

            # Interpolate 6 points (including both start and end colors)
            interpolated_colors = interpolate_colors(color_start, color_end, 3)

            # Convert back to 'rgb(r,g,b)' strings and add to the expanded list
            expanded_colors.extend([tuple_to_rgb(c) for c in interpolated_colors[:-1]])  # Skip last to avoid duplication

        # Add the last color manually
        expanded_colors.append(original_colors[-1])

        # Create a list of points that have the same distance in meters and assign a specific gradient and color
        gradient_series = pd.Series(['red'] * int(max(data['Cumulative Distance (m)']) / 10))
        gradient_range = 20 # minimum and maximum gradient visible on the plot
        for i in range(len(gradient_series)):
            closest_index = data['Cumulative Distance (m)'].sub(i*10).abs().idxmin()
            gradient_retrieved = max(min(data.loc[closest_index,'Gradient (%)'],gradient_range),-gradient_range)
            gradient_series[i] = expanded_colors[round((gradient_retrieved+gradient_range)/(gradient_range/int(len(expanded_colors)/2)))]

        fig_all = go.Figure()

        # Power Trace with Gradient Fill
        fig_all.add_trace(
            go.Scatter(
                x=np.round(data['Cumulative Distance (m)']),
                y=np.round(data['Elevation (m)']),
                customdata=data['Gradient (%)'],
                hovertemplate='Distance: %{x} m<br>Elevation: %{y} m<br>Gradient: %{customdata}%<extra></extra>',
                fill='tozeroy',
                fillgradient=dict(
                            type='horizontal',
                            colorscale=gradient_series,
                        ),
                mode='lines+markers',
                marker=dict(
                    size=1,
                    symbol='diamond',
                    showscale=True,
                    colorscale=expanded_colors,
                    cmin=-gradient_range,
                    cmax=gradient_range
                ),
                line={'color': 'black'},
                name='Gradient'),
                # Custom gradient fill not directly supported; using color per point is limited
            )

        fig_all.update_layout(
            title=dict(
                text='Route Profile',
                font_size=24,
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
            xaxis=dict(
                title='Distance (m)',
                title_font_size=18,
                title_standoff=10,
            ),
            yaxis=dict(
                title='Altitude (m)',
                title_font_size=18,
                title_standoff=10,
            ),
            showlegend=False
        )

        return fig_all
    
    except Exception as e:
        raise ValueError(f"Error visualizing data: {str(e)}")

