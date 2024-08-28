## this script allows for analyzing user metrics such as total tweets, likes, replies, retweets, quotes, and interactions for individual users and the entire dataset.

import json

def analyze_user_metrics(file_path):
    """
    Analyzes user metrics from the dataset and prints a summary of key statistics
    for individual users as well as aggregate statistics for the entire dataset.
    
    Args:
        file_path: The path to the JSON file containing the dataset.
    """

    with open(file_path, 'r') as file:
        data = json.load(file)

    user_stats = {}
    total_users = len(data)
    total_tweets = 0
    total_likes = 0
    total_replies = 0
    total_retweets = 0
    total_quotes = 0
    total_interactions = 0

    for user_id, user_data in data.items():
        tweets = user_data['tweets']
        user_total_tweets = len(tweets)
        if user_total_tweets == 1: continue  # Skip users with only one tweet
        user_total_likes = sum(tweet['favorite_count'] for tweet in tweets)
        user_avg_likes = user_total_likes / user_total_tweets if user_total_tweets > 0 else 0

        user_reply_count = sum(1 for tweet in tweets if tweet['is_reply'])
        user_retweet_count = sum(1 for tweet in tweets if tweet['is_retweet'])
        user_quote_count = sum(1 for tweet in tweets if tweet['is_quote'])
        user_interaction_count = user_reply_count + user_retweet_count + user_quote_count

        user_stats[user_id] = {
            "total_tweets": user_total_tweets,
            "total_likes": user_total_likes,
            "avg_likes": user_avg_likes,
            "reply_count": user_reply_count,
            "retweet_count": user_retweet_count,
            "quote_count": user_quote_count,
            "interaction_count": user_interaction_count
        }

        # Update aggregate totals
        total_tweets += user_total_tweets
        total_likes += user_total_likes
        total_replies += user_reply_count
        total_retweets += user_retweet_count
        total_quotes += user_quote_count
        total_interactions += user_interaction_count

    # Calculate aggregate averages
    avg_tweets_per_user = total_tweets / total_users if total_users > 0 else 0
    avg_likes_per_user = total_likes / total_users if total_users > 0 else 0
    avg_replies_per_user = total_replies / total_users if total_users > 0 else 0
    avg_retweets_per_user = total_retweets / total_users if total_users > 0 else 0
    avg_quotes_per_user = total_quotes / total_users if total_users > 0 else 0
    avg_interactions_per_user = total_interactions / total_users if total_users > 0 else 0

    # Print individual user statistics
    print("User Metrics Summary:")
    for user_id, stats in user_stats.items():
        print(f"\nUser ID: {user_id}")
        print(f"Total Tweets: {stats['total_tweets']}")
        print(f"Total Likes: {stats['total_likes']}")
        print(f"Average Likes per Tweet: {stats['avg_likes']:.2f}")
        print(f"Reply Count: {stats['reply_count']}")
        print(f"Retweet Count: {stats['retweet_count']}")
        print(f"Quote Count: {stats['quote_count']}")
        print(f"Total Interactions (Replies, Retweets, Quotes): {stats['interaction_count']}")

    # Print aggregate statistics
    print("\nAggregate Metrics Summary:")
    print(f"Total Users: {total_users}")
    print(f"Total Tweets: {total_tweets}")
    print(f"Total Likes: {total_likes}")
    print(f"Total Replies: {total_replies}")
    print(f"Total Retweets: {total_retweets}")
    print(f"Total Quotes: {total_quotes}")
    print(f"Total Interactions (Replies, Retweets, Quotes): {total_interactions}")

    print(f"\nAverage Tweets per User: {avg_tweets_per_user:.2f}")
    print(f"Average Likes per User: {avg_likes_per_user:.2f}")
    print(f"Average Replies per User: {avg_replies_per_user:.2f}")
    print(f"Average Retweets per User: {avg_retweets_per_user:.2f}")
    print(f"Average Quotes per User: {avg_quotes_per_user:.2f}")
    print(f"Average Interactions per User: {avg_interactions_per_user:.2f}")

    import matplotlib.pyplot as plt

    # Extract the user_total_tweets values from user_stats dictionary
    user_total_tweets_values = [stats['total_tweets'] for stats in user_stats.values()]

    # Plot the histogram
    plt.hist(user_total_tweets_values, bins=10)
    plt.xlabel('Number of Tweets')
    plt.ylabel('Number of Users')
    plt.title('Histogram of User Total Tweets')
    plt.show()

    # print the count of users with more than 20 tweets
    users_with_more_than_10_tweets = sum(1 for value in user_total_tweets_values if value > 10)
    print(f"Number of users with more than 20 tweets: {users_with_more_than_10_tweets}")
    # print the count of users with less than 10 tweets
    users_with_more_than_10_tweets = sum(1 for value in user_total_tweets_values if value < 10)
    print(f"Number of users with less than 10 tweets: {users_with_more_than_10_tweets}")



if __name__ == "__main__":
    file_path = 'amir_recent_tweets.json'  # Replace with your dataset path
    analyze_user_metrics(file_path)