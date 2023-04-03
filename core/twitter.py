from datetime import datetime, timedelta
import pandas as pd
import snscrape.modules.twitter as sntwitter

def str_to_datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')

def datetime_to_str(date_time):
    return date_time.strftime('%Y-%m-%d')

def get_tweets(query, lang_code, start_date, end_date, max_tweets, exclude_retweets=True):
    try:
        tweets_list = []
        search_query = f"{query} lang:{lang_code} since:{start_date} until:{end_date} "
        if exclude_retweets:
            search_query += "-filter:nativeretweets -filter:retweets"

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
            if i >= max_tweets:
                break
            
            tweet_dict = {f"tweet_{k}": v for k, v in tweet.__dict__.items() if k != 'user'}
            tweet_dict.update({f"user_{k}": v for k, v in tweet.user.__dict__.items()})
            
            tweets_list.append(tweet_dict)

        df = pd.DataFrame(tweets_list)
        df['tweet_date'] = df['tweet_date'].dt.tz_convert(None)
        df['user_created'] = df['user_created'].dt.tz_convert(None)
        df['df_tag'] = query
        return df
    except Exception as e:
        print(f'❌ ERROR: {e}\n {search_query}')
        return None

def get_tweets_for_tag(tag, start_date, end_date, max_retries=3, limit=3000):
    tag_df = pd.DataFrame()
    date_list = pd.date_range(start_date, end_date)
    date_list_2 = pd.date_range(start_date + timedelta(days=1), end_date + timedelta(days=1))

    for start, end in zip(date_list, date_list_2):
        start_str = datetime_to_str(start)
        end_str = datetime_to_str(end)

        retries = 0
        success = False

        while not success and retries < max_retries:
            try:
                print(f'🔎 Searching for {tag} from {start_str} to {end_str} (Attempt {retries + 1}). Length: {len(tag_df)}')
                tag_df = pd.concat([tag_df, get_tweets(tag, 'ja', start_str, end_str, limit, exclude_retweets=False)])
                success = True

            except Exception as e:
                print(f'Error: {e}')
                retries += 1

                if retries == max_retries:
                    print(f'⚠️ Max retries reached for {tag} from {start_str} to {end_str}')
                else:
                    print(f'🔄 Retrying for {tag} from {start_str} to {end_str}')

    return tag_df

def get_tweets_between_dates(tags, start_date, end_date, limit=3000):
    start_date = str_to_datetime(start_date)
    end_date = str_to_datetime(end_date)
    overall_df = pd.DataFrame()

    for tag in tags:
        tag_df = get_tweets_for_tag(tag, start_date, end_date, limit=limit)
        overall_df = pd.concat([overall_df, tag_df])

    try:
        overall_df.to_excel(f'./data/{datetime_to_str(start_date)}_{datetime_to_str(end_date)}.xlsx', index=False, encoding='utf-8', engine='xlsxwriter')
    except Exception as e:
        print(f'❌ ERROR: {e}')
    print(f'📝 Everything is done!')
    print(f'📝 Overall shape: {overall_df.shape}')
    print(f"📝 Overall stats per df_tag: {overall_df['df_tag'].value_counts()}")
    return overall_df
