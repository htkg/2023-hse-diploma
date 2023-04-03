from tqdm import tqdm
from IPython.display import clear_output
from geopy.geocoders import Nominatim
from concurrent.futures import ThreadPoolExecutor

geolocator = Nominatim(user_agent="python")

def get_address(location):
    try:
        loc = geolocator.geocode(location, language='en', timeout=15)
        return loc.address
    except Exception as e:
        return None

def get_address_wrapper(location):
    return (location, get_address(location))

def process_locations(df, num_threads=3):
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
