# import numpy as np
# from datetime import datetime, timedelta
# import random
# import matplotlib.pyplot as plt

# def tweet_probability(date, peak_prob):
#     protest_date = datetime(2024, 6, 1)
#     days_diff = (date - protest_date).days
    
#     base_prob = 0.01
#     protest_effect = peak_prob * np.exp(-0.5 * (days_diff / 1.0)**2)
    
#     total_prob = base_prob + protest_effect
#     return min(total_prob, 1.0)

# def simulate_tweets(num_users, peak_prob):
#     start_date = datetime(2024, 5, 30)
#     end_date = datetime(2024, 6, 3)
#     date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
#     results = {date.date(): 0 for date in date_range}
    
#     for date in date_range:
#         prob = tweet_probability(date, peak_prob)
#         for _ in range(num_users):
#             if random.random() < prob:
#                 results[date.date()] += 1
    
#     return results

# # Simulation parameters
# num_users = 500
# peak_prob = 0.254  # Based on Brazilian protest

# # Run simulation
# results = simulate_tweets(num_users, peak_prob)

# # Print results
# print("Tweet activity simulation results:")
# for date, count in results.items():
#     print(f"{date}: {count} tweets")

# # Visualize results
# dates = list(results.keys())
# tweet_counts = list(results.values())

# plt.figure(figsize=(10, 6))
# plt.bar(dates, tweet_counts, color='skyblue', edgecolor='navy')
# plt.title(f'Simulated Tweet Activity for {num_users} Users')
# plt.xlabel('Date')
# plt.ylabel('Number of Tweets')
# plt.xticks(rotation=45)
# plt.tight_layout()

# # Annotate peak
# peak_date = max(results, key=results.get)
# peak_count = results[peak_date]
# plt.annotate(f'Peak: {peak_count}', 
#              xy=(peak_date, peak_count), 
#              xytext=(10, 10),
#              textcoords='offset points',
#              ha='center',
#              va='bottom',
#              bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
#              arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# plt.show()

## Incorporating the user role ##
# import numpy as np
# from datetime import datetime, timedelta
# import random
# import matplotlib.pyplot as plt

# class User:
#     def __init__(self, user_type):
#         self.user_type = user_type
#         if user_type == 'core':
#             self.base_prob = 0.3
#             self.url_prob = 0.637
#             self.retweet_prob = 0.078
#             self.reply_prob = 0.511
#         elif user_type == 'org':
#             self.base_prob = 0.4
#             self.url_prob = 0.376
#             self.retweet_prob = 0.06
#             self.reply_prob = 0.505
#         else:  # basic user
#             self.base_prob = 0.05
#             self.url_prob = 0.522
#             self.retweet_prob = 0.1
#             self.reply_prob = 0.341

# def tweet_probability(date, peak_prob, user):
#     protest_date = datetime(2024, 6, 1)
#     days_diff = (date - protest_date).days
    
#     protest_effect = peak_prob * np.exp(-0.5 * (days_diff / 1.0)**2)
    
#     total_prob = user.base_prob + protest_effect
#     return min(total_prob, 1.0)

# def simulate_tweets(users, peak_prob):
#     start_date = datetime(2024, 5, 30)
#     end_date = datetime(2024, 6, 3)
#     date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
#     results = {date.date(): {'total': 0, 'with_url': 0, 'retweets': 0, 'replies': 0} for date in date_range}
    
#     for date in date_range:
#         for user in users:
#             prob = tweet_probability(date, peak_prob, user)
#             if random.random() < prob:
#                 results[date.date()]['total'] += 1
#                 if random.random() < user.url_prob:
#                     results[date.date()]['with_url'] += 1
#                 if random.random() < user.retweet_prob:
#                     results[date.date()]['retweets'] += 1
#                 elif random.random() < user.reply_prob:
#                     results[date.date()]['replies'] += 1
    
#     return results

# # Create users
# users = ([User('core') for _ in range(50)] +
#          [User('org') for _ in range(25)] +
#          [User('basic') for _ in range(425)])

# # Simulation parameters
# peak_prob = 0.254  # Based on Brazilian protest

# # Run simulation
# results = simulate_tweets(users, peak_prob)

# # Print results
# print("Tweet activity simulation results:")
# for date, counts in results.items():
#     print(f"{date}: {counts['total']} tweets (URLs: {counts['with_url']}, Retweets: {counts['retweets']}, Replies: {counts['replies']})")

# # Visualize results
# dates = list(results.keys())
# tweet_counts = [counts['total'] for counts in results.values()]

# plt.figure(figsize=(12, 6))
# plt.bar(dates, tweet_counts, color='skyblue', edgecolor='navy')
# plt.title(f'Simulated Tweet Activity for 500 Users (50 Core, 25 Org, 425 Basic)')
# plt.xlabel('Date')
# plt.ylabel('Number of Tweets')
# plt.xticks(rotation=45)
# plt.tight_layout()

# # Annotate peak
# peak_date = max(results, key=lambda x: results[x]['total'])
# peak_count = results[peak_date]['total']
# plt.annotate(f'Peak: {peak_count}', 
#              xy=(peak_date, peak_count), 
#              xytext=(10, 10),
#              textcoords='offset points',
#              ha='center',
#              va='bottom',
#              bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
#              arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# plt.show()

# # Stacked bar chart for tweet types
# urls = [counts['with_url'] for counts in results.values()]
# retweets = [counts['retweets'] for counts in results.values()]
# replies = [counts['replies'] for counts in results.values()]
# originals = [counts['total'] - counts['with_url'] - counts['retweets'] - counts['replies'] for counts in results.values()]

# plt.figure(figsize=(12, 6))
# plt.bar(dates, originals, label='Original Tweets', color='skyblue')
# plt.bar(dates, urls, bottom=originals, label='Tweets with URLs', color='lightgreen')
# plt.bar(dates, retweets, bottom=[i+j for i,j in zip(originals, urls)], label='Retweets', color='salmon')
# plt.bar(dates, replies, bottom=[i+j+k for i,j,k in zip(originals, urls, retweets)], label='Replies', color='plum')

# plt.title('Breakdown of Tweet Types')
# plt.xlabel('Date')
# plt.ylabel('Number of Tweets')
# plt.legend()
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

### Adjusted probabilities ###
# import numpy as np
# from datetime import datetime, timedelta
# import random
# import matplotlib.pyplot as plt

# class User:
#     def __init__(self, user_type):
#         self.user_type = user_type
#         if user_type == 'core':
#             self.base_prob = 0.8
#             self.url_prob = 0.637
#             self.retweet_prob = 0.078
#             self.reply_prob = 0.511
#         elif user_type == 'org':
#             self.base_prob = 0.9
#             self.url_prob = 0.376
#             self.retweet_prob = 0.06
#             self.reply_prob = 0.505
#         else:  # basic user
#             self.base_prob = 0.2
#             self.url_prob = 0.522
#             self.retweet_prob = 0.1
#             self.reply_prob = 0.341

# def tweet_probability(date, peak_prob, user):
#     protest_date = datetime(2024, 6, 1)
#     days_diff = (date - protest_date).days
    
#     protest_effect = peak_prob * np.exp(-0.5 * (days_diff / 0.5)**2)
    
#     total_prob = user.base_prob + protest_effect
#     return min(total_prob, 1.0)

# def simulate_tweets(users, peak_prob):
#     start_date = datetime(2024, 5, 30)
#     end_date = datetime(2024, 6, 3)
#     date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
#     results = {date.date(): {'total': 0, 'with_url': 0, 'retweets': 0, 'replies': 0} for date in date_range}
    
#     for date in date_range:
#         for user in users:
#             daily_tweets = 0
#             for _ in range(10):  # Allow up to 10 tweets per user per day
#                 if random.random() < tweet_probability(date, peak_prob, user):
#                     daily_tweets += 1
#                     results[date.date()]['total'] += 1
#                     if random.random() < user.url_prob:
#                         results[date.date()]['with_url'] += 1
#                     if random.random() < user.retweet_prob:
#                         results[date.date()]['retweets'] += 1
#                     elif random.random() < user.reply_prob:
#                         results[date.date()]['replies'] += 1
#                 else:
#                     break  # Stop if user doesn't tweet
    
#     return results

# # Create users
# users = ([User('core') for _ in range(50)] +
#          [User('org') for _ in range(25)] +
#          [User('basic') for _ in range(425)])

# # Simulation parameters
# peak_prob = 0.5  # Increased peak probability

# # Run simulation
# results = simulate_tweets(users, peak_prob)

# # Print results
# total_tweets = sum(counts['total'] for counts in results.values())
# print(f"Total tweets generated: {total_tweets}")
# print("\nTweet activity simulation results:")
# for date, counts in results.items():
#     print(f"{date}: {counts['total']} tweets (URLs: {counts['with_url']}, Retweets: {counts['retweets']}, Replies: {counts['replies']})")

# # Visualize results
# dates = list(results.keys())
# tweet_counts = [counts['total'] for counts in results.values()]

# plt.figure(figsize=(12, 6))
# plt.bar(dates, tweet_counts, color='skyblue', edgecolor='navy')
# plt.title(f'Simulated Tweet Activity for 500 Users (50 Core, 25 Org, 425 Basic)\nTotal Tweets: {total_tweets}')
# plt.xlabel('Date')
# plt.ylabel('Number of Tweets')
# plt.xticks(rotation=45)
# plt.tight_layout()

# # Annotate peak
# peak_date = max(results, key=lambda x: results[x]['total'])
# peak_count = results[peak_date]['total']
# plt.annotate(f'Peak: {peak_count}', 
#              xy=(peak_date, peak_count), 
#              xytext=(10, 10),
#              textcoords='offset points',
#              ha='center',
#              va='bottom',
#              bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
#              arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# plt.show()

# # Stacked bar chart for tweet types
# urls = [counts['with_url'] for counts in results.values()]
# retweets = [counts['retweets'] for counts in results.values()]
# replies = [counts['replies'] for counts in results.values()]
# originals = [counts['total'] - counts['with_url'] - counts['retweets'] - counts['replies'] for counts in results.values()]

# plt.figure(figsize=(12, 6))
# plt.bar(dates, originals, label='Original Tweets', color='skyblue')
# plt.bar(dates, urls, bottom=originals, label='Tweets with URLs', color='lightgreen')
# plt.bar(dates, retweets, bottom=[i+j for i,j in zip(originals, urls)], label='Retweets', color='salmon')
# plt.bar(dates, replies, bottom=[i+j+k for i,j,k in zip(originals, urls, retweets)], label='Replies', color='plum')

# plt.title(f'Breakdown of Tweet Types\nTotal Tweets: {total_tweets}')
# plt.xlabel('Date')
# plt.ylabel('Number of Tweets')
# plt.legend()
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

## V2 Adjusted probabilities ##
import numpy as np
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt

class User:
    def __init__(self, user_type):
        self.user_type = user_type
        if user_type == 'core':
            self.base_prob = 0.95
            self.url_prob = 0.637
            self.retweet_prob = 0.078
            self.reply_prob = 0.511
            self.max_daily_tweets = 20
        elif user_type == 'org':
            self.base_prob = 0.98
            self.url_prob = 0.376
            self.retweet_prob = 0.06
            self.reply_prob = 0.505
            self.max_daily_tweets = 25
        else:  # basic user
            self.base_prob = 0.6
            self.url_prob = 0.522
            self.retweet_prob = 0.1
            self.reply_prob = 0.341
            self.max_daily_tweets = 10

def tweet_probability(date, peak_prob, user):
    protest_date = datetime(2024, 6, 1)
    days_diff = (date - protest_date).days
    
    protest_effect = peak_prob * np.exp(-0.5 * (days_diff / 0.5)**2)
    
    total_prob = min(user.base_prob + protest_effect, 1.0)
    return total_prob

def simulate_tweets(users, peak_prob):
    start_date = datetime(2024, 5, 30)
    end_date = datetime(2024, 6, 3)
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
users = ([User('core') for _ in range(50)] +
         [User('org') for _ in range(25)] +
         [User('basic') for _ in range(425)])

# Simulation parameters
peak_prob = 0.6  # Increased peak probability

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