import gpxpy
import geopy.distance
import numpy as np
import pandas as pd
import io
import base64
import re
import plotly.colors as colors
import plotly.graph_objects as go
import folium
import math
import time

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

def visualize_map(data):

    # prompt: find the index of the closest  value of data Cumulative Distance (m) that is equal to 10000
    indexes_10km = []
    for i in range(int(data['Cumulative Distance (m)'].max()/10000)):
        index_10 = data['Cumulative Distance (m)'].sub(10000*(i+1)).abs().idxmin()
        indexes_10km.append(index_10)

    images = ['assets/images/number-10.png','assets/images/number-20.png',
              'assets/images/number-30.png','assets/images/40.png',
              'assets/images/50.png','assets/images/60.png','assets/images/70.png','assets/images/80.png']

    map_center = [data.Latitude[0], data.Longitude[0]]
    m = folium.Map(location=map_center, zoom_start=13)

    # Extract points
    points = np.column_stack((data.Latitude, data.Longitude))

    # Add path with arrows
    folium.PolyLine(points, color="red", weight=5.0, opacity=0.8).add_to(m)
    # 10Km markers
    # Attribution https://www.flaticon.com/free-icon/number-10_9494570?term=ten&page=1&position=6&origin=search&related_id=9494570
    # # 80 blue https://www.flaticon.com/free-icon/80_6913959?related_id=6913959
    for i in range(len(indexes_10km)):
        try:
            pushpin = folium.features.CustomIcon(images[i], icon_size=(45,45))
            folium.Marker(points[indexes_10km[i]+1], icon=pushpin, popup=str((i+1)*10)).add_to(m)
        except IndexError:
            break

    # # Mark start and end points
    pushpin = folium.features.CustomIcon('assets/images/startline.png', icon_size=(60,60))
    folium.Marker(points[0], icon=pushpin, popup="Start").add_to(m)
    pushpin = folium.features.CustomIcon('assets/images/finish.png', icon_size=(60,60))
    folium.Marker(points[-1], icon=pushpin, popup="Finish").add_to(m)

    return m.get_root().render()

def create_pacing(pacing_factor):
  pacing_power_table = pd.DataFrame({'Gradient (%)': range(15, -16, -1)})
  pacing_power_table['pacing_factor'] = 0.0
  pacing_power_table.loc[pacing_power_table['Gradient (%)'] > -10, 'pacing_factor'] = (pacing_power_table.loc[pacing_power_table['Gradient (%)'] > -10, 'Gradient (%)'] + 10) / 10 * pacing_factor
  pacing_power_table.loc[pacing_power_table['Gradient (%)'] > 0, 'pacing_factor'] = ((pacing_power_table.loc[pacing_power_table['Gradient (%)'] > 0, 'Gradient (%)'] + 10) / 50 + 0.8) * pacing_factor
  pacing_power_table.loc[pacing_power_table['Gradient (%)'] >= 10, 'pacing_factor'] = 1.2 * pacing_factor
  pacing_power_table.index = pacing_power_table['Gradient (%)']
  pacing_power_table = pacing_power_table.drop(columns=['Gradient (%)'])
  return pacing_power_table

def update_speed_pacing(data,ftp,bike_mass,rider_mass,C_r,C_d,A,rho,strategy):
    """
    Args:
    data: data of the ride. distance, time, gradient, n-timestamps
    power: Functional Threshold Power (FTP)
    pacing: pacing strategy
    """
    # V_hw = 0.0  # Headwind Velocity in m/s
    W = bike_mass + rider_mass  # Weight in Kg (Rider + Bike)
    # Loss_dt = 2.0  # Percentage of losses
    # P_legs = power  # Power from legs in watts
    
    pacing_factors = {
        'zone1':0.5,
        'zone2':0.7,
        'zone3':0.85,
        'push_hard':1
    }
    pacing = create_pacing(pacing_factors[strategy])
    power = ftp

    for i in range(1,len(data)):
        if i == 1:
            actual_speed = 0
        else:
            actual_speed = data.iloc[i-1]['updated_speed']
        actual_power = power * pacing.loc[max(min(int(data.loc[i,'Gradient (%)']), 15), -15)].values[0]
        cum_segment_distance = 0
        cum_segment_time = 0
        if data.loc[i,'Gradient (%)'] > 20:
            delta_t = 0.025
        elif data.loc[i,'Gradient (%)'] > 10:
            delta_t = 0.05
        else:
            delta_t = 0.1
        last_step = False
        while not last_step:
            # Calulate forces and accelearation
            air_resistance = 0.5 * C_d * A * rho * actual_speed**3
            rolling_resistance = C_r * W * 9.8067 * math.cos(math.atan(data.iloc[i]['Gradient (%)']/100)) * actual_speed
            gravity_resistance = W * 9.8067 * math.sin(math.atan(data.iloc[i]['Gradient (%)']/100)) * actual_speed
            net_force = actual_power - (air_resistance + rolling_resistance + gravity_resistance)
            acceleration = net_force / W

            # Calculate delta_d
            delta_d = actual_speed * delta_t + 0.5 * acceleration * delta_t**2
            # print('Under the Root ',actual_speed**2 + 2 * acceleration * delta_d)
            actual_speed = math.sqrt(actual_speed**2 + 2 * acceleration * delta_d)
            cum_segment_distance += delta_d
            # delta_d is bigger than the actual segment
            if cum_segment_distance > data.iloc[i]['Distance (m)']:
                last_step = True
                cum_segment_distance -= delta_d
                delta_d = data.iloc[i]['Distance (m)'] - (cum_segment_distance)
                cum_segment_distance += delta_d
                actual_speed = math.sqrt(actual_speed**2 + 2 * acceleration * delta_d)
                delta_t = delta_d / actual_speed

            # Update segment time
            cum_segment_time += delta_t
            # print('Actual Speed',np.round(actual_speed,4),'Gradient ',data.iloc[i]['Gradient'],'Distance ',np.round(cum_segment_distance,2),'Cumulative Time ',np.round(cum_segment_time,2),'Net Power ',net_force)

        data.at[i,'updated_speed'] = actual_speed
        data.at[i,'updated_distance'] = cum_segment_distance
        data.at[i,'updated_pacing_time'] = cum_segment_time
        data.at[i,'updated_power'] = actual_power

    data['updated_power'] = data['updated_power'].bfill()
    data.at[0, 'updated_pacing_time'] = 3.1
    data['cum_pacing_time'] = data['updated_pacing_time'].cumsum()
    
    total_energy_consumption = round((data['updated_power'] * data['updated_pacing_time']).sum() / 1000)
    elevation_gain = int(((data['Gradient (%)'] > 0) * data['Distance (m)'] * data['Gradient (%)']/100).sum())
    sec = data['cum_pacing_time'].tail(1).values + 60 # Adding 1 minute to the ride
    ty_res = time.gmtime(int(sec))
    if sec < 3600:
        res = time.strftime("%-M minute(s)",ty_res)
    else:
        res = time.strftime("%-H hour(s) and %-M minute(s)",ty_res)        
    return res, total_energy_consumption, elevation_gain