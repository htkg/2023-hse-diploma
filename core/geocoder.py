from tqdm import tqdm
from IPython.display import clear_output
from geopy.geocoders import Nominatim
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import googlemaps
import pandas as pd
import json
import os 

load_dotenv()  # take environment variables from .env.
gmaps = googlemaps.Client(key=os.getenv('GOOGLEMAPS_API_KEY'))

geolocator = Nominatim(user_agent="python")

def get_address(location):
    try:
        loc = geolocator.geocode(location, language='en', timeout=15)
        return loc.address
    except Exception as e:
        return None

def get_address_wrapper(location):
    return (location, get_address(location))

def process_locations_osm(df, num_threads=3):
    to_map = df['user_location'].unique().tolist()

    errors_count = 0
    errors_loc_list = []
    total_count = len(to_map)
    result_dict = {}
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i, result in enumerate(tqdm(executor.map(get_address_wrapper, to_map), total=total_count, desc="Processing locations")):
            if result[1] is None:
                errors_count += 1
                errors_loc_list.append(result[0])
            result_dict[result[0]] = result[1]

            # Print success rate every 10 processed steps
            if (i+1) % 10 == 0:
                clear_output(wait=True)
                current_success_rate = round(((i + 1 - errors_count) / (i + 1)) * 100, 2)
                print(f"Success Rate after {i + 1} steps: {current_success_rate}% | {errors_count} errors out of {i + 1} steps")

    final_success_rate = round(((total_count - errors_count) / total_count) * 100, 2)
    print(f"\nFinal Success Rate: {final_success_rate}%")
    
    return result_dict, errors_loc_list

def geocode_location(location, gmaps):
    try:
        geocode_result = gmaps.geocode(location)
        if geocode_result:
            return location, geocode_result[0]
        else:
            return location, None
    except Exception as e:
        print(f"An error occurred while geocoding '{location}': {e}")
        return location, 'Error'

def process_locations_gmaps(df, api_key=None, max_workers=10):
    if api_key is None:
        api_key = os.getenv('GOOGLEMAPS_API_KEY')
    
    gmaps = googlemaps.Client(key=api_key)
    locations_unique = df['user_location'].unique().tolist()

    geocoded_results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(geocode_location, locations_unique, [gmaps] * len(locations_unique)), total=len(locations_unique)))
    
    for location, formatted_address in results:
        geocoded_results[location] = formatted_address

    # Convert the geocoded_errors dictionary to a JSON object
    json_output = json.dumps(geocoded_results, ensure_ascii=False)

    return json_output

