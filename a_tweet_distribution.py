# ## V2 Adjusted probabilities ##
# # probabilities are adopted from the following paper (with some modification to match the number of required tweets): doi:10.1371/journal.pone.0165387
import numpy as np
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt

## Calculations for user probabilities:
"""
For the Brazilian protest (May 1 to Aug 1, 2013):
Total days: 92 days

For Individuals:
Mean Tweets: 182.611
Mean Prop. of Tweets with URL: 0.522
Mean Prop. Retweet: 0.1
Mean Prop. Replies: 0.341
Daily averages:
Tweets per day: 182.611 / 92 = 1.985 tweets/day
Tweets with URL per day: 1.985 * 0.522 = 1.036 tweets with URL/day
Retweets per day: 1.985 * 0.1 = 0.199 retweets/day
Replies per day: 1.985 * 0.341 = 0.677 replies/day
For Organizations:
Mean Tweets: 372.87
Mean Prop. of Tweets with URL: 0.376
Mean Prop. Retweet: 0.06
Mean Prop. Replies: 0.505
Daily averages:
Tweets per day: 372.87 / 92 = 4.053 tweets/day
Tweets with URL per day: 4.053 * 0.376 = 1.524 tweets with URL/day
Retweets per day: 4.053 * 0.06 = 0.243 retweets/day
Replies per day: 4.053 * 0.505 = 2.047 replies/day
"""
class User:
    def __init__(self, user_type):
        self.user_type = user_type
        #TODO; the original paper only distinguishes between individuals and organizations. so we are still estimating the core user statistics based on basic user. need to adjust these numbers.
        if user_type == 'core': 
            self.tweets_per_day = 3  # Slightly higher than average individual
            self.url_prob = 0.522
            self.retweet_prob = 0.1
            self.reply_prob = 0.341
        elif user_type == 'org':
            self.tweets_per_day = 4.053
            self.url_prob = 0.376
            self.retweet_prob = 0.06
            self.reply_prob = 0.505
        else:  # basic user
            self.tweets_per_day = 1.985
            self.url_prob = 0.522
            self.retweet_prob = 0.1
            self.reply_prob = 0.341

def simulate_tweets(users, peak_factor, num_days):
    start_date = datetime(2040, 5, 30)
    date_range = [start_date + timedelta(days=i) for i in range(num_days)]
    
    results = {date.date(): {'total': 0, 'with_url': 0, 'retweets': 0, 'replies': 0} for date in date_range}
    
    for date in date_range:
        days_to_protest = abs((date - datetime(2040, 6, 1)).days)
        day_factor = peak_factor * (1 / (1 + days_to_protest))  # Higher activity closer to protest day
        
        for user in users:
            daily_tweets = np.random.poisson(user.tweets_per_day * (1 + day_factor))
            results[date.date()]['total'] += daily_tweets
            
            for _ in range(daily_tweets):
                if random.random() < user.url_prob:
                    results[date.date()]['with_url'] += 1
                if random.random() < user.retweet_prob:
                    results[date.date()]['retweets'] += 1
                elif random.random() < user.reply_prob:
                    results[date.date()]['replies'] += 1
    
    return results

# Create users
users = ([User('core') for _ in range(5)] +
         [User('org') for _ in range(5)] +
         [User('basic') for _ in range(25)])

# Simulation parameters
peak_factor = 2  # Increase activity on protest day
num_days = 5  # Simulate for 5 days

# Run simulation
results = simulate_tweets(users, peak_factor, num_days)

# Print results
total_tweets = sum(counts['total'] for counts in results.values())
print(f"Total tweets generated: {total_tweets}")
print("\nTweet activity simulation results:")
for date, counts in results.items():
    print(f"{date}: {counts['total']} tweets (URLs: {counts['with_url']}, Retweets: {counts['retweets']}, Replies: {counts['replies']})")

# Visualize results
dates = list(results.keys())
tweet_counts = [counts['total'] for counts in results.values()]

plt.figure(figsize=(12, 6))
plt.bar(dates, tweet_counts, color='skyblue', edgecolor='navy')
plt.title(f'Simulated Tweet Activity for 500 Users (50 Core, 25 Org, 425 Basic)\nTotal Tweets: {total_tweets}')
plt.xlabel('Date')
plt.ylabel('Number of Tweets')
plt.xticks(rotation=45)
plt.tight_layout()

# Annotate peak
peak_date = max(results, key=lambda x: results[x]['total'])
peak_count = results[peak_date]['total']
plt.annotate(f'Peak: {peak_count}', 
             xy=(peak_date, peak_count), 
             xytext=(10, 10),
             textcoords='offset points',
             ha='center',
             va='bottom',
             bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

plt.show()

# Stacked bar chart for tweet types
urls = [counts['with_url'] for counts in results.values()]
retweets = [counts['retweets'] for counts in results.values()]
replies = [counts['replies'] for counts in results.values()]
originals = [counts['total'] - counts['with_url'] - counts['retweets'] - counts['replies'] for counts in results.values()]

plt.figure(figsize=(12, 6))
plt.bar(dates, originals, label='Original Tweets', color='skyblue')
plt.bar(dates, urls, bottom=originals, label='Tweets with URLs', color='lightgreen')
plt.bar(dates, retweets, bottom=[i+j for i,j in zip(originals, urls)], label='Retweets', color='salmon')
plt.bar(dates, replies, bottom=[i+j+k for i,j,k in zip(originals, urls, retweets)], label='Replies', color='plum')

plt.title(f'Breakdown of Tweet Types\nTotal Tweets: {total_tweets}')
plt.xlabel('Date')
plt.ylabel('Number of Tweets')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()