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
    # Add more dates as needed
}
# 2040-05-30: 143 tweets (URLs: 68, Retweets: 10, Replies: 49)
# 2040-05-31: 176 tweets (URLs: 85, Retweets: 15, Replies: 68)
# 2040-06-01: 255 tweets (URLs: 122, Retweets: 23, Replies: 85)
# 2040-06-02: 197 tweets (URLs: 90, Retweets: 18, Replies: 80)
# 2040-06-03: 146 tweets (URLs: 68, Retweets: 15, Replies: 43)



class Post:
    def __init__(self, post_id, content, owner):
        self.post_id = post_id
        self.content = content
        self.owner = owner
        self.likes = 0
        self.retweets = 0
        self.replies = []
    

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

    def initialize_users_db(self): 
        # generate a dictionary of user_ids and their corresponding user_type (core, basic, org) from the biography data
        user_types = {}
        for user in self.core_bios:
            user_types[user['aesop_id']] = 'core'
        for user in self.basic_bios:
            user_types[user['aesop_id']] = 'basic'
        for user in self.org_bios:
            user_types[user['aesop_id']] = 'org'
        return user_types

    def load_network(self, network_path):
        """
        Load the existing social network from a .gml file.
        """
        return nx.read_gml(network_path)
    
    def load_biographies(self, biography_path):
        """
        Load the biographies of the actors from a JSON file.
        """
        with open(biography_path, 'r') as file:
            return json.load(file)

    def simulate_social_media_activity(self):
        # Simulate social media activities based on tweet data
        for user_type in ['org', 'core', 'basic']:
            for node in self.graph.nodes():
                user = self.graph.nodes[node]['user_id']
                if self.users_role[user] == user_type:
                    if any(action_count > 0 for action_count in self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
                        action_info = self.take_action(user, self.get_world_state(user), self.get_tweets_for_user(user)) # fix this
                        if action_info[0]:  # Only process if there's an action
                            self.process_action(node, action_info)

        self.propagate_information()
        self.current_time += timedelta(minutes=15)

    def get_tweets_for_user(self, user):
        connected_nodes = list(self.graph.neighbors(user))
        tweets = []
        for node in connected_nodes:
            connected_user = self.graph.nodes[node]['user']
            tweets.extend(connected_user.posts[-5:])  # Get the last 5 posts
        return tweets[:15]  # Limit to 15 tweets max

    def process_action(self, node, action_info):
        action, target_post = action_info
        user = self.graph.nodes[node]['user']

        if action == 'post':
            new_post = Post(post_id=len(user.posts) + 1, content=f"User {user.name} posts something interesting.", owner=user)
            self.add_to_tweet_history(user, new_post)

        elif action == 'like' and target_post:
            target_post.likes += 1
            self.add_to_tweet_history(user, '<LIKE>'+target_post)

        elif action == 'retweet' and target_post:
            target_post.retweets += 1
            retweeted_post = Post(post_id=len(self.read_tweet_history(user)) + 1, content=f"RT: {target_post.content}", owner=user)
            self.add_to_tweet_history(user, '<RT>'+retweeted_post)

        elif action == 'reply' and target_post:
            reply_content = f"User {user} replies to {target_post.owner}: Interesting!"
            target_post.replies.append(reply_content)
            self.add_to_tweet_history(user, '<RE>'+reply_content)

    def take_action(self, user, world_state, tweets):
        current_date = world_state['current_time'].strftime('%Y-%m-%d')
        
        if current_date not in self.remaining_actions and current_date in predetermined_tweets:
            self.remaining_actions[current_date] = predetermined_tweets[current_date].copy()

        actions_today = self.remaining_actions.get(current_date, {})

        # Calculate action probability based on user role
        user_role = self.users_role[user]
        action_probability = priority_weights[user_role] / sum(priority_weights.values())

        # Determine if the user should take action
        if random.random() < action_probability:
            print(f"User {user} ({user_role}) is taking action today.")
            if actions_today.get('URLs', 0) > 0:
                action = 'post_url'
                actions_today['URLs'] -= 1
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

        # Select a tweet to interact with if retweeting or replying
        selected_tweet = random.choice(tweets) if tweets and action in ['retweet', 'reply'] else None
        
        return action, selected_tweet
    
    # def take_action(self, user, world_state):
    #     # Base probabilities
    #     base_probs = {
    #         'post': 0.1,
    #         'retweet': 0.2,
    #         'reply': 0.15,
    #         'like': 0.25,
    #         'do_nothing': 0.3
    #     }
        
    #     # Adjust probabilities based on opinion strength
    #     opinion_strength = abs(user.opinion)
    #     for action in ['post', 'retweet', 'reply', 'like']:
    #         base_probs[action] *= (1 + opinion_strength)
        
    #     # Normalize probabilities
    #     total = sum(base_probs.values())
    #     action = np.random.choice(['post', 'retweet', 'reply', 'like', 'do_nothing'], p=[base_probs[action] / total for action in ['post', 'retweet', 'reply', 'like', 'do_nothing']])
    #     target_post = None

    #     if action == 'retweet' or action == 'like' or action == 'reply':
    #         tweets = self.get_tweets_for_user(user)
    #         if tweets:
    #             target_post = random.choice(tweets)
        
    #     return action, target_post
    # def propagate_information(self):
    #     for edge in self.graph.edges():
    #         source, target = edge
    #         source_user = self.graph.nodes[source]['user']
    #         target_user = self.graph.nodes[target]['user']
            
    #         # Share a summarized version of the knowledge
    #         # TODO (later) implement a more sophisticated information sharing mechanism.
    #         shared_info = self.summarize_knowledge(source_user.knowledge)
    #         target_user.knowledge.update(shared_info)

    def summarize_knowledge(self, knowledge):
        # Simplified example of summarizing information
        return {k for k in knowledge if 'important' in k}  # Arbitrary filter

    def propagate_information(self):
        for edge in self.graph.edges():
            source, target = edge
            source_user = self.graph.nodes[source]['user_id']
            target_user = self.graph.nodes[target]['user_id']
            
            # Share post history
            for post in self.read_tweet_history(source_user):
                if post not in self.read_tweet_history(target_user):
                    self.add_to_tweet_history(target_user,post)

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
        
        if user_bio.get("tweet_history"):
            return user_bio["tweet_history"]
        else:
            user_bio["tweet_history"] = []
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
        
        if "tweet_history" not in user_bio:
            user_bio["tweet_history"] = []

        user_bio["tweet_history"].append(tweet)

    def save_tweets(self, filepath):
        all_tweets = []
        for node in self.graph.nodes():
            user = self.graph.nodes[node]['user_id']
            for post in self.read_tweet_history(user):
                all_tweets.append({
                    'post_id': post.post_id,
                    'content': post.content,
                    'owner': post.owner,
                    'likes': post.likes,
                    'retweets': post.retweets,
                    'replies': post.replies
                })

        with open(filepath, 'w') as file:
            json.dump(all_tweets, file, indent=4)

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
    end_date = datetime(2040, 6, 1)
    final_state = run_simulation(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets)
    print("Simulation completed.")