## V2 Adjusted probabilities ##
# probabilities are adopted from the following paper (with some modification to match the number of required tweets): doi:10.1371/journal.pone.0165387
# TODO: obtain correct probabilities for url_ retweet_ and reply_ probabilities. how?
import numpy as np
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt

class User:
    def __init__(self, user_type):
        self.user_type = user_type
        if user_type == 'core':
            self.base_prob = 0.8 # was 95
            self.url_prob = 0.637
            self.retweet_prob = 0.078
            self.reply_prob = 0.511
            self.max_daily_tweets = 20
        elif user_type == 'org':
            self.base_prob = 0.9 # was 98
            self.url_prob = 0.376
            self.retweet_prob = 0.06
            self.reply_prob = 0.505
            self.max_daily_tweets = 25
        else:  # basic user
            self.base_prob = 0.2 # was 0.6
            self.url_prob = 0.522
            self.retweet_prob = 0.1
            self.reply_prob = 0.341
            self.max_daily_tweets = 10

def tweet_probability(date, peak_prob, user):
    protest_date = datetime(2040, 6, 1)
    days_diff = (date - protest_date).days
    
    protest_effect = peak_prob * np.exp(-0.5 * (days_diff / 0.5)**2)
    
    total_prob = min(user.base_prob + protest_effect, 1.0)
    return total_prob

def simulate_tweets(users, peak_prob):
    start_date = datetime(2040, 5, 30)
    end_date = datetime(2040, 6, 3)
    date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
    results = {date.date(): {'total': 0, 'with_url': 0, 'retweets': 0, 'replies': 0} for date in date_range}
    
    for date in date_range:
        for user in users:
            daily_prob = tweet_probability(date, peak_prob, user)
            daily_tweets = np.random.binomial(user.max_daily_tweets, daily_prob)
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
# TODO: percentage of users are estimated. we can adjust this later based on other works.
# this ratio can be inferred from Figure 2c in the paper.
users = ([User('core') for _ in range(30)] + # was 50
         [User('org') for _ in range(25)] + # was 25
         [User('basic') for _ in range(445)]) # was 425

# Simulation parameters
peak_prob = 0.254  # Based on Brazillian protests

# Run simulation
results = simulate_tweets(users, peak_prob)

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