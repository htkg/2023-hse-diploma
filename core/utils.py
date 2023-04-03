import pandas as pd

def convert_to_datetime(df):
    df['tweet_date'] = pd.to_datetime(df['tweet_date'], format='%d.%m.%Y %H:%M:%S')
    print(f'📅 Converted tweet_date to datetime')
    return df