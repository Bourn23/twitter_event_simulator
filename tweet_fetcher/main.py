import requests
import time

def fetch_tweet(tweet_id):
    url = f"https://twitter.com/anyusr/status/{tweet_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def fetch_tweets(tweet_ids):
    results = {}
    for tweet_id in tweet_ids:
        print(f"Fetching tweet {tweet_id}...")
        content = fetch_tweet(tweet_id)
        if content:
            results[tweet_id] = content
        else:
            print(f"Failed to fetch tweet {tweet_id}")
        time.sleep(1)  # Be polite to the server
    return results

def main():
    tweet_ids_input = input("Enter tweet IDs separated by commas: ")
    tweet_ids = [id.strip() for id in tweet_ids_input.split(',')]
    
    results = fetch_tweets(tweet_ids)
    
    print("\nResults:")
    for tweet_id, content in results.items():
        print(f"Tweet {tweet_id}: {len(content)} characters fetched, content: {content}...")

if __name__ == "__main__":
    main()