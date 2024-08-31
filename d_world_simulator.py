import networkx as nx
import json
import random
from datetime import datetime, timedelta

priority_weights = {
    'org': 3,
    'core': 2,
    'basic': 1
}

predetermined_tweets = {
    '2040-05-30': {
        'Tweets': 75,
        'URLs': 68,
        'Retweets': 10,
        'Replies': 49
    },
    '2040-05-31': {
        'Tweets': 176,
        'URLs': 85,
        'Retweets': 15,
        'Replies': 68
    },
    '2040-06-01': {
        'Tweets': 255,
        'URLs': 122,
        'Retweets': 23,
        'Replies': 85
    },
    '2040-06-02': {
        'Tweets': 197,
        'URLs': 90,
        'Retweets': 18,
        'Replies': 80
    },
    '2040-06-03': {
        'Tweets': 146,
        'URLs': 68,
        'Retweets': 15,
        'Replies': 43
    }
}


class WorldModel:
    def __init__(self, network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets):
        self.start_date = start_date
        self.end_date = end_date
        self.current_time = start_date
        self.graph = self.load_network(network_path)
        self.actors = []
        self.core_bios = self.load_biographies(core_biography_path)
        self.basic_bios = self.load_biographies(basic_biography_path)
        self.org_bios = self.load_biographies(org_biography_path)
        self.users_role = self.initialize_users_db()
        self.remaining_actions = predetermined_tweets
        self.posts_graph = nx.MultiDiGraph()  # Initialize the posts graph from the start

    def initialize_users_db(self): 
        user_types = {}
        for user in self.core_bios:
            user_types[user['aesop_id']] = 'core'
        for user in self.basic_bios:
            user_types[user['aesop_id']] = 'basic'
        for user in self.org_bios:
            user_types[user['aesop_id']] = 'org'
        return user_types

    def load_network(self, network_path):
        return nx.read_gml(network_path)
    
    def load_biographies(self, biography_path):
        with open(biography_path, 'r') as file:
            return json.load(file)

    def simulate_social_media_activity(self):
        for user_type in ['org', 'core', 'basic']:
            for user in self.graph.nodes():
                if self.users_role[user] == user_type:
                    if any(action_count > 0 for action_count in self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
                        action_info = self.take_action(user, self.get_tweets_for_user(user))
                        if action_info[0]:  # Only process if there's an action
                            self.process_action(user, action_info)

        self.propagate_information()
        self.current_time += timedelta(minutes=15)

    def get_tweets_for_user(self, user):
        connected_nodes = list(self.graph.neighbors(user))
        tweets = []

        for connected_user_id in connected_nodes:
            tweets.extend(self.read_tweet_history(connected_user_id)[-5:])  # Get the last 5 posts

        return random.sample(tweets, min(15, len(tweets)))

    def get_user_property(self, user, property):
        def get_user_bio(bios, user):
            for bio in bios:
                if bio.get('aesop_id') == user:
                    return bio
            return None
        
        if user == {}:
            return []
        if self.users_role[user] == 'org':
            user_bio = get_user_bio(self.org_bios, user)
        elif self.users_role[user] == 'core':
            user_bio = get_user_bio(self.core_bios, user)
        elif self.users_role[user] == 'basic':
            user_bio = get_user_bio(self.basic_bios, user)
        else:
            raise ValueError("User not found in any biography data.")
        
        if user_bio is None:
            raise ValueError(f"User with ID {user} not found in the biography data.")
        
        return user_bio.get(property)

    def process_action(self, user, action_info):
        action, target_post_id = action_info
        new_post_id = len(self.posts_graph.nodes) + 1  # Generate a unique post ID
        
        if action == 'post':
            new_post = f"User {self.get_user_property(user, 'name')} posts something interesting."
            self.posts_graph.add_node(new_post_id, content=new_post, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.add_to_tweet_history(user, new_post_id)
        
        elif action == 'post_url':
            new_post = f"User {self.get_user_property(user, 'name')} posts an interesting URL."
            self.posts_graph.add_node(new_post_id, content=new_post, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.add_to_tweet_history(user, new_post_id)

        elif action == 'like' and target_post_id:
            self.posts_graph.nodes[target_post_id]['likes'] += 1

        elif action == 'retweet' and target_post_id:
            target_post_data = self.posts_graph.nodes[target_post_id]
            new_content = f"RT: {target_post_data['content']}"
            retweeted_post = f"User {self.get_user_property(user, 'name')} retweets: {new_content}"
            self.posts_graph.add_node(new_post_id, content=retweeted_post, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.add_to_tweet_history(user, new_post_id)
            self.posts_graph.add_edge(new_post_id, target_post_id, interaction='retweet', timestamp=self.current_time)

        elif action == 'reply' and target_post_id:
            target_post_data = self.posts_graph.nodes[target_post_id]
            reply_content = f"User {user} replies to {target_post_data['owner']}: Interesting!"
            reply_post = f"User {self.get_user_property(user, 'name')} replies to {self.get_user_property(target_post_data['owner'], 'name')}: {reply_content}"
            self.posts_graph.add_node(new_post_id, content=reply_post, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.posts_graph.add_edge(new_post_id, target_post_id, interaction='reply', timestamp=self.current_time)
            self.add_to_tweet_history(user, new_post_id)

    def take_action(self, user, tweets):
        current_date = self.current_time.strftime('%Y-%m-%d')
        
        if current_date not in self.remaining_actions and current_date in predetermined_tweets:
            self.remaining_actions[current_date] = predetermined_tweets[current_date].copy()

        actions_today = self.remaining_actions.get(current_date, {})

        user_role = self.users_role[user]
        action_probability = priority_weights[user_role] / sum(priority_weights.values())

        if random.random() < action_probability:
            if actions_today.get('URLs', 0) > 0:
                action = 'post_url'
                actions_today['URLs'] -= 1
            elif actions_today.get('Tweets', 0) > 0:
                action = 'post'
                actions_today['Tweets'] -= 1
                actions_today['URLs'] -= 1 # Assume that a tweet with a URL is also a tweet
            elif actions_today.get('Retweets', 0) > 0:
                action = 'retweet'
                actions_today['Retweets'] -= 1
            elif actions_today.get('Replies', 0) > 0:
                action = 'reply'
                actions_today['Replies'] -= 1
            else:
                action = None
        else:
            action = None

        selected_tweet = random.choice(tweets) if tweets and action in ['retweet', 'reply'] else None
        
        return action, selected_tweet

    def propagate_information(self):
        for edge in self.graph.edges():
            source, target = edge
            source_user = self.graph.nodes[source]
            target_user = self.graph.nodes[target]
            
            for post in self.read_tweet_history(source_user):
                if post not in self.read_tweet_history(target_user):
                    self.add_to_tweet_history(target_user, post)

    def get_world_state(self, user):
        return {
            'current_time': self.current_time,
            'read_tweet_history': self.read_tweet_history(user)[-15:],  # Limit to last 15 tweets
        }
    
    def read_tweet_history(self, user):
        def get_user_bio(bios, user):
            for bio in bios:
                if bio.get('aesop_id') == user:
                    return bio
            return None
        
        if user == {}:
            return []
        if self.users_role[user] == 'org':
            user_bio = get_user_bio(self.org_bios, user)
        elif self.users_role[user] == 'core':
            user_bio = get_user_bio(self.core_bios, user)
        elif self.users_role[user] == 'basic':
            user_bio = get_user_bio(self.basic_bios, user)
        else:
            raise ValueError("User not found in any biography data.")
        
        if user_bio is None:
            raise ValueError(f"User with ID {user} not found in the biography data.")
        
        if user_bio.get("tweets_simulation"):
            return user_bio["tweets_simulation"]
        else:
            user_bio["tweets_simulation"] = []
            return user_bio.get("tweets", [])

    def add_to_tweet_history(self, user, tweet):
        def get_user_bio(bios, user):
            for bio in bios:
                if bio.get('aesop_id') == user:
                    return bio
            return None

        if self.users_role[user] == 'org':
            user_bio = get_user_bio(self.org_bios, user)
        elif self.users_role[user] == 'core':
            user_bio = get_user_bio(self.core_bios, user)
        elif self.users_role[user] == 'basic':
            user_bio = get_user_bio(self.basic_bios, user)
        else:
            raise ValueError("User not found in any biography data.")
        
        if user_bio is None:
            raise ValueError(f"User with ID {user} not found in the biography data.")
        
        if "tweets_simulation" not in user_bio:
            user_bio["tweets_simulation"] = []

        user_bio["tweets_simulation"].append(tweet)

    def save_tweets(self, filepath):
        all_tweets = []
        
        # Extract information from nodes (tweets)
        for node, data in self.posts_graph.nodes(data=True):
            tweet_info = {
                'post_id': node,
                'content': data.get('content'),
                'owner': data.get('owner'),
                'timestamp': data.get('timestamp').isoformat() if data.get('timestamp') else None,
                'likes': data.get('likes', 0),
                'retweets': data.get('retweets', 0),
                'replies': data.get('replies', [])
            }
            all_tweets.append(tweet_info)

        # Extract information from edges (interactions)
        all_interactions = []
        for source, target, data in self.posts_graph.edges(data=True):
            interaction_info = {
                'source_post_id': source,
                'target_post_id': target,
                'interaction': data.get('interaction'),
                'timestamp': data.get('timestamp').isoformat() if data.get('timestamp') else None
            }
            all_interactions.append(interaction_info)

        # Save the tweets and interactions to a file
        save_data = {
            'tweets': all_tweets,
            'interactions': all_interactions
        }

        with open(filepath, 'w') as file:
            json.dump(save_data, file, indent=4)

# Simulation Runner
def run_simulation(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets):
    world = WorldModel(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets)
    
    while world.current_time <= world.end_date:
        world.simulate_social_media_activity()
        
        if world.current_time.minute == 0:  # Log every hour
            print(f"Simulation time: {world.current_time}")
    
    return world.save_tweets('simulation_results.json')


if __name__ == "__main__":
    # Run the simulation
    network_path = 'social_network_small.gml'
    core_biography_path = 'core_users.json'
    basic_biography_path = 'basic_users.json'
    org_biography_path = 'organization_users.json'

    start_date = datetime(2040, 5, 30)
    end_date = datetime(2040, 6, 4)
    final_state = run_simulation(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets)
    print("Simulation completed.")