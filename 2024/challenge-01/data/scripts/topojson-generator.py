("""
import requests

def list_files_folders_github_repo(url):
    # Sending GET request to the GitHub API
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Extracting names of files and directories
        files_folders = [item['name'] for item in data]

        return files_folders
    else:
        print(f"Failed to retrieve data from GitHub API. Status code: {response.status_code}")
        return []

# Example usage:
github_repo_url = "https://api.github.com/repos/ajstarks/dubois-data-portraits/contents/plate06"
files_folders = list_files_folders_github_repo(github_repo_url)
if files_folders:
    print("Files and folders in the directory:")
    for item in files_folders:
        print(item)
else:
    print("No files or folders found.")

""")

import requests
import csv
import json

def get_csv_file_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return None

def extract_coordinates_from_csv(csv_data):
    coordinates = []
    reader = csv.reader(csv_data.splitlines())
    for row in reader:
        # Assuming lat is in the first column and long is in the second column
        lat, lon = float(row[0]), float(row[1])
        coordinates.append([lon, lat])  # GeoJSON format: [longitude, latitude]
    return coordinates

def rotate_coordinates(coordinates):
    # Rotate each coordinate counterclockwise by 90 degrees from its current orientation
    rotated_coordinates = [[-lat, lon] for lon, lat in coordinates]
    return rotated_coordinates

def create_geojson_from_github_repo(directory_url):
    geojson_features = []

    # Fetching contents of the directory from GitHub API
    response = requests.get(directory_url)
    if response.status_code == 200:
        data = response.json()

        for item in data:
            if item['name'].endswith('-coord.csv'):
                county_name = item['name'].split('-')[0]
                csv_content = get_csv_file_content(item['download_url'])
                if csv_content:
                    coordinates = extract_coordinates_from_csv(csv_content)
                    # Rotate the coordinates counterclockwise by 90 degrees
                    rotated_coordinates = rotate_coordinates(coordinates)
                    # Ensure the polygon is closed by repeating the first coordinate at the end
                    rotated_coordinates.append(rotated_coordinates[0])
                    # Add county polygon feature to GeoJSON features list
                    geojson_features.append({
                        "type": "Feature",
                        "properties": {
                            "county": county_name
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [rotated_coordinates]
                        }
                    })

    # Create GeoJSON object
    geojson_data = {
        "type": "FeatureCollection",
        "features": geojson_features
    }

    # Write GeoJSON to file
    with open("counties.geojson", "w") as geojson_file:
        json.dump(geojson_data, geojson_file)

# Example usage:
github_repo_directory_url = "https://api.github.com/repos/ajstarks/dubois-data-portraits/contents/plate06"
create_geojson_from_github_repo(github_repo_directory_url)
