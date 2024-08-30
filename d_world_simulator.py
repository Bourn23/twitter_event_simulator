import networkx as nx
import json
import random
from datetime import timedelta

class WorldModel:
    def __init__(self, dataset_path, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.current_time = start_date
        self.graph = self.load_network(network_path)
        self.actors = []
        self.biographies = self.load_bigraphies(biography_path)
        self.load_dataset_and_initialize_graph()


    def load_network(self, network_path):
        """
        Load the existing social network from a .gml file.
        """
        return nx.read_gml(network_path)
    
    def load_bigraphies(self, biography_path):
        """
        Load the biographies of the actors from a JSON file.
        """
        with open(biography_path, 'r') as file:
            return json.load(file)

    def add_actor(self, actor):
        self.actors.append(actor)
        for account in actor.accounts:
            self.add_twitter_account_to_graph(account)

    def add_twitter_account_to_graph(self, account):
        self.graph.add_node(account.handle, account=account)
        #TODO: Add edges based on followers

    def simulate_social_media_activity(self):
        # Simulate social media activities based on tweet data
        for node in self.graph.nodes():
            user = self.graph.nodes[node]['user']
            user_world_state = self.get_world_state(user)
            action = user.take_action(user_world_state, self.get_tweets_for_user(user))
            self.process_action(node, action)

        self.propagate_information()
        self.current_time += timedelta(minutes=15)

    def get_tweets_for_user(self, user):
        # Fetch tweets relevant to the user
        # This could be based on historical data or newly generated data
        tweets = []
        # Logic to fetch relevant tweets for the user
        return tweets

    def process_action(self, node, action):
        # Implement logic for processing user actions (post, retweet, reply, like)
        pass

    def propagate_information(self):
        # Simulate the information flow between connected users
        for edge in self.graph.edges():
            source, target = edge
            source_user = self.graph.nodes[source]['user']
            target_user = self.graph.nodes[target]['user']
            shared_info = source_user.knowledge & target_user.knowledge # TODO: we need more advanced knowledge sharing/represnetation mechanism than just aggregating all the information; perhaps something like a summary
            target_user.knowledge.update(shared_info)

    def load_dataset_and_initialize_graph(self):
        with open(self.dataset_path, 'r') as file:
            data = json.load(file)

        for user_id, user_data in data.items():
            user = self.create_user(user_id, user_data)
            self.graph.add_node(user_id, user=user)
            self.add_edges_from_social_network(user_data)

    def create_user(self, user_id, user_data):
        if self.is_core_user(user_data):
            return CoreUser(user_id)
        else:
            return OrdinaryUser(user_id)

    def is_core_user(self, user_data):
        return user_data.get('retweets', 0) > 500

    def add_edges_from_social_network(self, user_data):
        user_id = user_data['user_info']['id']
        for follower_id in user_data.get('followers', []):
            self.graph.add_edge(user_id, follower_id)

    def get_world_state(self, user):
        return {
            'current_time': self.current_time,
            'graph': self.graph,
            # Include more state information as needed
        }

# Simulation Runner
def run_simulation(dataset_path, start_date, end_date):
    world = WorldModel(dataset_path, start_date, end_date)
    
    while world.current_time <= world.end_date:
        world.simulate_social_media_activity()
        
        if world.current_time.minute == 0:  # Log every hour
            print(f"Simulation time: {world.current_time}")
    
    return world.get_world_state()