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

    # lets do deeper analysis of the data
    # 1. make a follower/following ratio for each user (we can load the user bio from: core_characters.json, basic_characters.json, total_organizations.json) ## but let's wait on this since this has nothing to do with the tweets graph
    # 2. identify the group of users (core, basic, organization) and plot the count of their posts and interactions
    core_users_ids = [user["aesop_id"] for user in json.load(open('Core_characters_fixed_ids.json', 'r'))]
    basic_users_ids = [user["aesop_id"] for user in json.load(open('basic_characters_fixed_ids.json', 'r'))]
    organization_users_ids = [user["aesop_id"] for user in json.load(open('total_organizations_fixed_ids.json', 'r'))]

    core_tweets = 0
    basic_tweets = 0
    organization_tweets = 0

    core_interactions = 0
    basic_interactions = 0
    organization_interactions = 0

    print('core user ids ', core_users_ids)
    print('basic user ids ', basic_users_ids)
    print('organization user ids ', organization_users_ids)

    for tweet in data['tweets']:
        if tweet['owner'] in core_users_ids:
            core_tweets += 1
        elif tweet['owner'] in basic_users_ids:
            basic_tweets += 1
        elif tweet['owner'] in organization_users_ids:
            organization_tweets += 1

    for interaction in data['interactions']:
        if interaction['source_post_id'] in core_users_ids:
            core_interactions += 1
        elif interaction['source_post_id'] in basic_users_ids:
            basic_interactions += 1
        elif interaction['source_post_id'] in organization_users_ids:
            organization_interactions += 1

    print(f"Core users: {len(core_users_ids)}")
    print(f"Basic users: {len(basic_users_ids)}")
    print(f"Organization users: {len(organization_users_ids)}")

    print(f"Core users' tweets: {core_tweets}")
    print(f"Basic users' tweets: {basic_tweets}")
    print(f"Organization users' tweets: {organization_tweets}")

    print(f"Core users' interactions: {core_interactions}")
    print(f"Basic users' interactions: {basic_interactions}")
    print(f"Organization users' interactions: {organization_interactions}")

    # 3. plot the number of tweets and interactions for each user
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.bar(['Core', 'Basic', 'Organization'], [core_tweets, basic_tweets, organization_tweets], color='skyblue', edgecolor='navy')
    plt.title('Number of Tweets by User Group')
    plt.xlabel('User Group')
    plt.ylabel('Number of Tweets')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Path to the simulation results file
    filepath = 'simulation_results.json'
    
    # Analyze the results
    analyze_results(filepath)