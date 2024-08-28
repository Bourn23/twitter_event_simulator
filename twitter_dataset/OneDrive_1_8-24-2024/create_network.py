# import json

# def get_user_interactions(file_path):
#   """
#   Reads a JSON file containing Twitter user data and returns a dictionary 
#   representing the network of user interactions.

#   Args:
#     file_path: The path to the JSON file.

#   Returns:
#     A dictionary where keys are user screen names and values are lists of screen 
#     names they interacted with. Interactions include replies, mentions, and quotes.
#   """

#   interactions = {}

#   with open(file_path, 'r') as file:
#     data = json.load(file)

#   for user_id, user_data in data.items():
#     screen_name = user_data['user_info']['screen_name']
#     interactions[screen_name] = set() # Still use a set to avoid duplicates
#     for tweet in user_data['tweets']:
#       if tweet.get('in_reply_to_screen_name'):
#         interactions[screen_name].add(tweet['in_reply_to_screen_name'])
#       for mention in tweet.get('entities', {}).get('user_mentions', []):
#         interactions[screen_name].add(mention['screen_name'])
#       if tweet.get('quoted_tweet'):
#         quoted_screen_name = tweet['quoted_tweet']['user']['screen_name']
#         interactions[screen_name].add(quoted_screen_name)

#   # Convert sets to lists before returning
#   interactions = {user: list(interactions_set) for user, interactions_set in interactions.items()}

#   return interactions

# # Example usage:

# file_path = 'tweets_2019_Clean_User_tweets.json'
# interactions = get_user_interactions(file_path)
# print(json.dumps(interactions, indent=2))


### with visualization ###
# import json
# import networkx as nx

# def get_user_interactions(file_path):
#     """
#     Reads a JSON file containing Twitter user data and returns a dictionary 
#     representing the network of user interactions.

#     Args:
#         file_path: The path to the JSON file.

#     Returns:
#         A dictionary where keys are user screen names and values are lists of screen 
#         names they interacted with. Interactions include replies, mentions, and quotes.
#     """

#     interactions = {}

#     with open(file_path, 'r') as file:
#         data = json.load(file)

#     for user_id, user_data in data.items():
#         screen_name = user_data['user_info']['screen_name']
#         interactions[screen_name] = set()
#         for tweet in user_data['tweets']:
#             if tweet.get('in_reply_to_screen_name'):
#                 interactions[screen_name].add(tweet['in_reply_to_screen_name'])
#             for mention in tweet.get('entities', {}).get('user_mentions', []):
#                 interactions[screen_name].add(mention['screen_name'])
#             if tweet.get('quoted_tweet'):
#                 quoted_screen_name = tweet['quoted_tweet']['user']['screen_name']
#                 interactions[screen_name].add(quoted_screen_name)

#     interactions = {user: list(interactions_set) for user, interactions_set in interactions.items()}
#     return interactions

# def create_network_graph(interactions):
#     """
#     Creates a NetworkX graph from a dictionary of user interactions.

#     Args:
#         interactions: A dictionary where keys are user screen names and values are 
#                       lists of screen names they interacted with.

#     Returns:
#         A NetworkX DiGraph object representing the user interaction network.
#     """

#     graph = nx.DiGraph()  # Create a directed graph

#     for user, interactions_list in interactions.items():
#         graph.add_node(user)  # Add the user as a node
#         for interacted_user in interactions_list:
#             graph.add_edge(user, interacted_user)  # Add an edge representing the interaction

#     return graph

# # Example usage:
# file_path = 'amir_recent_tweets.json'
# interactions = get_user_interactions(file_path)
# graph = create_network_graph(interactions)

# # You can now analyze and visualize the graph using NetworkX functions
# print(f'Number of nodes: {graph.number_of_nodes()}')
# print(f'Number of edges: {graph.number_of_edges()}')
# print(f'Some edges: {list(graph.edges())[:5]}') # Print the first 5 edges

# # For visualization (requires matplotlib):
# import matplotlib.pyplot as plt
# nx.draw(graph, with_labels=True)
# plt.show() 

#### with visualization and interactive graph ####
import json
import networkx as nx
from pyvis.network import Network

def get_user_interactions(file_path):
    """
    Reads a JSON file containing Twitter user data and returns a dictionary 
    representing the network of user interactions.

    Args:
        file_path: The path to the JSON file.

    Returns:
        A dictionary where keys are user screen names and values are lists of screen 
        names they interacted with. Interactions include replies, mentions, and quotes.
    """

    interactions = {}

    with open(file_path, 'r') as file:
        data = json.load(file)

    for user_id, user_data in data.items():
        screen_name = user_data['user_info']['screen_name']
        interactions[screen_name] = set()
        for tweet in user_data['tweets']:
            if tweet.get('in_reply_to_screen_name'):
                interactions[screen_name].add(tweet['in_reply_to_screen_name'])
            for mention in tweet.get('entities', {}).get('user_mentions', []):
                interactions[screen_name].add(mention['screen_name'])
            if tweet.get('quoted_tweet'):
                quoted_screen_name = tweet['quoted_tweet']['user']['screen_name']
                interactions[screen_name].add(quoted_screen_name)

    interactions = {user: list(interactions_set) for user, interactions_set in interactions.items()}
    return interactions

def create_interactive_network_graph(interactions, output_file='network.html'):
    """
    Creates an interactive network graph from a dictionary of user interactions.

    Args:
        interactions: A dictionary where keys are user screen names and values are 
                      lists of screen names they interacted with.
        output_file: The path to the output HTML file for the interactive network.

    Returns:
        None. The function creates and saves an interactive network visualization.
    """

    graph = nx.DiGraph()  # Create a directed graph

    for user, interactions_list in interactions.items():
        graph.add_node(user)  # Add the user as a node
        for interacted_user in interactions_list:
            graph.add_edge(user, interacted_user)  # Add an edge representing the interaction

    # Create a PyVis network
    net = Network(notebook=True, directed=True)
    net.from_nx(graph)  # Load the NetworkX graph into PyVis

    # Customize options (optional)
    net.set_options("""
    var options = {
      "nodes": {
        "color": {
          "border": "rgba(0,0,0,1)",
          "background": "rgba(97,195,238,1)",
          "highlight": {
            "border": "rgba(0,0,0,1)",
            "background": "rgba(97,195,238,1)"
          },
          "hover": {
            "border": "rgba(0,0,0,1)",
            "background": "rgba(97,195,238,1)"
          }
        },
        "font": {
          "color": "rgba(0,0,0,1)",
          "size": 12,
          "face": "arial"
        }
      },
      "edges": {
        "color": {
          "color": "rgba(0,0,0,0.4)",
          "highlight": "rgba(97,195,238,1)",
          "hover": "rgba(97,195,238,1)",
          "inherit": true,
          "opacity": 0.4
        },
        "smooth": false
      },
      "physics": {
        "enabled": true
      }
    }
    """)

    # Save the network visualization to an HTML file
    net.show(output_file)
    print(f"Interactive network graph saved to {output_file}")

# Example usage:
file_path = 'amir_recent_tweets.json'
interactions = get_user_interactions(file_path)
create_interactive_network_graph(interactions)