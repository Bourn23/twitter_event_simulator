import pandas as pd

# Load the dataset from disasters.csv
df = pd.read_csv('climate_change_disaster_tweets.csv')

# Preview the first few rows
# print(df.head())

# # Print all column names
# print(df.columns)

# # Shape of dataset
# print(df.shape)

# # Randomly choose 1 mil rows from dataset and save it to a new csv.
# df.sample(n=1000000).to_csv('sample_1mil_tweets.csv', index=False)

# # Extract the first 1000 tweets and save it to a raw text file. [use id column]
# df['id'][:1000].to_csv('first_1000_tweets.txt', index=False)

# load the sample_1mil_tweets.csv
# df = pd.read_csv('sample_1mil_tweets.csv')

# filter based on date: March 19th, 2014 to March 25th, 2014
df['created_at'] = pd.to_datetime(df['created_at'])

# create a new column 'year', 'month', 'day' from 'created_at' column
df['year'] = df['created_at'].dt.year
df['month'] = df['created_at'].dt.month
df['day'] = df['created_at'].dt.day

df.to_csv('climate_change_disaster_tweets_time_info_added.csv', index=False)

# print unique years
print(df['year'].unique())

# print histogram of years
print(df['year'].value_counts())

# filter the data based on year, month, day
df = df[(df['year'] == 2014) & (df['month'] == 3) & (df['day'] >= 19) & (df['day'] <= 25)]
print(df.shape)

df.to_csv('2014_protest.csv', index=False)



# Save the filtered dataset to a new csv file
# df.to_csv('2014_march_tweets.csv', index=False)
