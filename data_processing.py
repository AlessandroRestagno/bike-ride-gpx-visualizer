import gpxpy
import geopy.distance
import numpy as np

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