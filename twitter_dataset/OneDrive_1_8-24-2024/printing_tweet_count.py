import json

def print_tweet_counts(input_file):
    # Read the reorganized JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(data.items())
    except UnicodeDecodeError:
        # If UTF-8 fails, try with 'utf-8-sig' (to handle BOM)
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

    # Print header
    print("User ID\t\tTweet Count")
    print("-" * 30)

    # Sort users by tweet count (descending)
    sorted_users = sorted(data.items(), key=lambda x: len(x[1]['tweets']), reverse=True)

    # Print each user's ID and tweet count
    for user_id, user_data in sorted_users:
        tweet_count = len(user_data['tweets'])
        print(f"{user_id}\t{tweet_count}")

    # Print total statistics
    total_users = len(data)
    total_tweets = sum(len(user_data['tweets']) for user_data in data.values())
    print("\nTotal Statistics:")
    print(f"Total Users: {total_users}")
    print(f"Total Tweets: {total_tweets}")
    print(f"Average Tweets per User: {total_tweets / total_users:.2f}")

# Usage
input_file = "tweets_2019_Clean_User_tweets.json"
print_tweet_counts(input_file)