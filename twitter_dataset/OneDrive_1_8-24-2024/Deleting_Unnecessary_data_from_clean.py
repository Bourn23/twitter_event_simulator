import json
from collections import OrderedDict

def clean_twitter_data(input_file, output_file):
    try:
        # Try reading the file with UTF-8 encoding
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        # If UTF-8 fails, try with 'utf-8-sig' (in case there's a BOM)
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

    cleaned_data = {}

    for user_id, user_data in data.items():
        cleaned_user = {
            "user_info": {
                "id_str": user_data["user_info"]["id_str"],
                "name": user_data["user_info"]["name"],
                "screen_name": user_data["user_info"]["screen_name"],
                "verified": user_data["user_info"]["verified"]
            },
            "tweets": []
        }

        # Use OrderedDict to maintain the order of tweets while removing duplicates
        unique_tweets = OrderedDict()

        for tweet in user_data["tweets"]:
            cleaned_tweet = {
                "id_str": tweet["id_str"],
                "created_at": tweet["created_at"],
                "text": tweet["text"],
                "favorite_count": tweet["favorite_count"],
                "lang": tweet["lang"],
                "is_reply": bool(tweet.get("in_reply_to_status_id_str")),
                "is_retweet": "retweeted_status" in tweet,
                "is_quote": bool(tweet.get("quoted_status_id_str"))
            }

            # Include reply details if it's a reply
            if cleaned_tweet["is_reply"]:
                cleaned_tweet["in_reply_to"] = {
                    "status_id_str": tweet["in_reply_to_status_id_str"],
                    "user_id_str": tweet["in_reply_to_user_id_str"],
                    "screen_name": tweet["in_reply_to_screen_name"]
                }

            # Include retweet details if it's a retweet
            if cleaned_tweet["is_retweet"] and "retweeted_status" in tweet:
                cleaned_tweet["retweet_info"] = {
                    "original_id_str": tweet["retweeted_status"]["id_str"],
                    "original_user_screen_name": tweet["retweeted_status"]["user"]["screen_name"]
                }

            # Include quote tweet details if it's a quote tweet
            if cleaned_tweet["is_quote"]:
                cleaned_tweet["quoted_status_id_str"] = tweet["quoted_status_id_str"]

            # Only include entities if they exist and are not empty
            if "entities" in tweet and tweet["entities"]:
                cleaned_tweet["entities"] = {
                    "hashtags": tweet["entities"].get("hashtags", []),
                    "user_mentions": tweet["entities"].get("user_mentions", []),
                    "urls": tweet["entities"].get("urls", [])
                }

            # Add to unique_tweets, overwriting if id_str already exists
            unique_tweets[cleaned_tweet["id_str"]] = cleaned_tweet

        # Convert the OrderedDict values back to a list
        cleaned_user["tweets"] = list(unique_tweets.values())

        cleaned_data[user_id] = cleaned_user

    # Write the output file with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"Cleaned data has been written to {output_file}")
    print(f"Number of users processed: {len(cleaned_data)}")
    total_tweets = sum(len(user_data['tweets']) for user_data in cleaned_data.values())
    print(f"Total number of tweets after removing duplicates: {total_tweets}")

# Example usage
input_file = 'tweets_2019_Clean_User_tweets.json'
output_file = 'cleaned_twitter_data.json'
clean_twitter_data(input_file, output_file)