import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



def plot_active_users(users):
    # Create a date-time range from May 30 to June 3 with hourly intervals
    date_range = pd.date_range(start='2024-05-30', end='2024-06-03 23:59', freq='H')

    # Initialize a dictionary to count active users per hour
    active_users_per_hour = {str(date): 0 for date in date_range}

    # Count active users for each hour
    for user in users:
        join_time = user['join_time']
        leave_time = user['leave_time']
        for date in date_range:
            if join_time <= date <= leave_time:
                active_users_per_hour[str(date)] += 1

    # Plot the number of active users per hour
    plt.figure(figsize=(12, 6))
    plt.plot(list(active_users_per_hour.keys()), list(active_users_per_hour.values()), marker='o')
    plt.title('Number of Active Users per Hour (May 30 - June 3)')
    plt.xlabel('Date and Time')
    plt.ylabel('Number of Active Users')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


import json
import random

def generate_user_activity(num_users):
    # Define the possible join and leave dates
    join_dates = np.array(['2024-05-30', '2024-05-31', '2024-06-01'], dtype='datetime64[D]')
    leave_dates = np.array(['2024-06-01', '2024-06-02', '2024-06-03'], dtype='datetime64[D]')
    
    # Skewed distribution for joining and leaving
    join_prob = [0.55, 0.40, 0.05]  # Example probabilities: more users join on May 31
    leave_prob = [0.1, 0.35, 0.55]  # Example probabilities: more users leave on June 2

    # Randomly assign join and leave times to users
    users = []
    for _ in range(num_users):
        join_date = np.random.choice(join_dates, p=join_prob)
        leave_date = np.random.choice(leave_dates, p=leave_prob)
        
        # Add random hours and minutes to join and leave times
        join_time = join_date + np.timedelta64(np.random.randint(0, 24), 'h') + np.timedelta64(np.random.randint(0, 60), 'm')
        leave_time = leave_date + np.timedelta64(np.random.randint(0, 24), 'h') + np.timedelta64(np.random.randint(0, 60), 'm')
        
        users.append({'join_time': join_time, 'leave_time': leave_time})
    
    return users

# Function to randomly assign an start_date_time to each entry (more activation towards the protest day - july 1st 2040); it must be skewed towards the protest day
def assign_start_date_time(data, activity_times):
    for idx, entry in enumerate(data):
        # choose based on the user index
        start_end_time = activity_times[idx]
        start_time = start_end_time['join_time']
        end_time = start_end_time['leave_time']
        entry["join_time"] = str(start_time)
        entry["leave_time"] = str(end_time)
        print(f"Updated start_date_time: {start_time}, {end_time}")
    return data

activity_times = generate_user_activity(404)
# Load your JSON data
with open('data_characters_basic_borna.json', 'r', encoding='utf-8-sig') as file:
    data = json.load(file)

# Process each entry in the JSON data
new_data = assign_start_date_time(data, activity_times)

# Save the updated JSON data
with open('data_characters_basic_borna_activation_time.json', 'w' ,encoding='utf-8-sig') as file:
    json.dump(new_data, file, indent=4)

plot_active_users(activity_times)

print("Names have been updated and saved to data_updated.json")
