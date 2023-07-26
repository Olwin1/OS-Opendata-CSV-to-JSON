# Import necessary libraries
import csv
import json
import os
from multiprocessing import Process
import math

# Import the pyproj library for coordinate transformation
from pyproj import Transformer

# Function to convert Easting and Northing coordinates to Latitude and Longitude
def en_to_lat_lon(easting, northing):
    # Create a coordinate transformer from EPSG:27700 (British National Grid) to EPSG:4326 (WGS 84)
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326")

    # Perform the transformation
    lat, lon = transformer.transform(easting, northing)

    return lat, lon

# Function to check if the word "road" is present in a string and remove it
def removeRoads(road: str):
    target = road.lower()
    replaced = target.replace("road", "")
    if target == replaced:
        return True
    else:
        return False

# Function to convert a CSV file to JSON format
def csvToJSON(file):
    locations = []
    try:
        # Open the CSV file for reading
        with open(f'./Data/{file}', newline='') as csvfile:
            # Create a CSV reader
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                # Check if the row contains valid data and if the word "road" is not present in the location name
                if row[7].lower() != "postcode" and removeRoads(row[7]):
                    # Convert Easting and Northing coordinates to Latitude and Longitude
                    lat, long = en_to_lat_lon(row[8], row[9])

                    # Calculate distance based on coordinates (distance formula for 2D points)
                    x = int(row[14]) - int(row[12])
                    y = int(row[15]) - int(row[13])
                    distance = math.sqrt(x^2 + y^2) / 2

                    # Append the location details to the list
                    locations.append({"name": row[2], "lat": lat, "long": long, "region": row[24], "country": row[27], "distance": distance})
                    #print(row[2], row[7], lat, long, row[24], row[27])

        # Write the locations list to a JSON file with the same name as the CSV file
        with open(f'./JSON/{file[:-4]}.json', 'w') as fp:
            json.dump(locations, fp)

        # Print a message indicating successful processing of the file
        print("Finished File:", file)
    except Exception as e:
        # Print an error message if the file processing fails
        print(f"File failed: {file}")
        print(e)

# Function to process a single file using multiprocessing
def process_file(file):
    csvToJSON(file)

if __name__ == "__main__":
    # Get a list of CSV files in the "./Data/" directory
    files = os.listdir("./Data/")

    # Get a list of JSON files that have already been created in the "./JSON/" directory
    createdFilesTmp = os.listdir("./JSON/")
    createdFiles = [createdFile[:-5] for createdFile in createdFilesTmp]

    processes = []
    for i, file in enumerate(files):
        # Check if the JSON file for this CSV file has not been created yet
        if file[:-4] not in createdFiles:
            # Create a new process to handle the conversion for this file
            p = Process(target=process_file, args=[file])
            processes.append(p)
            p.start()

            # Limit the number of concurrent processes to 20
            if len(processes) > 20:
                # Wait for all processes to finish
                for p in processes:
                    p.join()
                processes.clear()
