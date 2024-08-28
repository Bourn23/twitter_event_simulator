import json
from collections import defaultdict

def reorganize_json(input_file, output_file):
    # Read the input JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        # If UTF-8 fails, try with 'utf-8-sig' (to handle BOM)
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

    # Create a defaultdict to store tweets by user
    users_tweets = defaultdict(list)

    # Reorganize tweets by user
    for tweet in data:
        if isinstance(tweet, dict) and 'user' in tweet and 'id_str' in tweet['user']:
            user_id = tweet['user']['id_str']
            # Remove the 'user' field from the tweet to avoid redundancy
            tweet_copy = tweet.copy()
            del tweet_copy['user']
            users_tweets[user_id].append(tweet_copy)

    # Convert defaultdict to regular dict for JSON serialization
    result = {
        user_id: {
            "user_info": next((t['user'] for t in data if t.get('user', {}).get('id_str') == user_id), None),
            "tweets": tweets
        }
        for user_id, tweets in users_tweets.items()
    }

    # Write the reorganized data to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Reorganized JSON has been written to {output_file}")

# Usage
input_file = "tweets_2019_Clean.json"
output_file = "tweets_2019_Clean_User_tweets.json"
reorganize_json(input_file, output_file)