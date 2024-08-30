## verifies if we parsed all characters and their tweets correctly.
import json

def check_tweet_counts(json_file_path):
    # Load the parsed JSON data
    with open(json_file_path, 'r', encoding='utf-8') as file:
        characters = json.load(file)

    # List to store characters with less than 10 tweets
    characters_with_fewer_tweets = []

    # Iterate through the characters to count tweets
    for character in characters:
        tweet_count = len(character.get("tweets", []))
        if tweet_count != 10:
            characters_with_fewer_tweets.append({
                "aesop_id": character.get("aesop_id"),
                "name": character.get("name"),
                "tweets": character.get("tweets")
            })

    # Report characters with fewer than 10 tweets
    if characters_with_fewer_tweets:
        print("Characters with less than 10 tweets:")
        for char in characters_with_fewer_tweets:
            print(f"\nID: {char['aesop_id']}, Name: {char['name']}")
            print("Tweets:")
            for tweet in char['tweets']:
                print(f"- {tweet}")
    else:
        print("All characters have exactly 10 tweets.")

# File path to the JSON file containing parsed character data
json_file_path = 'characters.json'

# Run the check
check_tweet_counts(json_file_path)