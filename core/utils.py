import pandas as pd
import json

def convert_to_datetime(df):
    df['tweet_date'] = pd.to_datetime(df['tweet_date'], format='%d.%m.%Y %H:%M:%S')
    print(f'📅 Converted tweet_date to datetime')
    return df

def get_prefecture(location_data):
    for component in location_data['address_components']:
        if 'administrative_area_level_1' in component['types']:
            return component['long_name']
    return None

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        output = json.load(f)
        print(f'📄 Loaded {path} as JSON | Length: {len(output)}')
        return output