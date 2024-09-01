import json

def analyze_results(filepath):
    # Load the simulation results from the JSON file
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    # Exclude posts that have no content (i.e., content is null)
    data['tweets'] = [tweet for tweet in data['tweets'] if tweet['content'] is not None]

    # Count the total number of tweets
    total_tweets = len(data.get('tweets', []))
    
    # Count the total number of interactions
    total_interactions = len(data.get('interactions', []))
    
    # Print the results
    print(f"Total number of tweets: {total_tweets}")
    print(f"Total number of interactions: {total_interactions}")

if __name__ == "__main__":
    # Path to the simulation results file
    filepath = 'simulation_results.json'
    
    # Analyze the results
    analyze_results(filepath)