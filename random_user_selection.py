import json
import random

# Step 1: Read the input file containing the JSON data
input_file = './twitter_dataset/aug27_tweets_test.txt'
output_file = './twitter_dataset/first_100_selected_users.txt'

# Convert the string to a dictionary
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Step 2: Randomly select users
num_users_to_select = 100  # You can adjust this number
selected_users = random.sample(list(data.keys()), num_users_to_select)

# Step 3: Create a new dictionary with only the selected users
selected_data = {user: data[user] for user in selected_users}

# Step 4: Save the selected users and their tweets to a new text file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(selected_data, f, indent=2)

print(f"{num_users_to_select} users have been randomly selected and saved to {output_file}")
