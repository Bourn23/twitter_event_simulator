# import networkx as nx
# import random
# from datetime import datetime

# def generate_social_graph(tweet_data, num_core_users, num_org_users, num_basic_users):
#     G = nx.DiGraph()  # Directed graph
    
#     # Add nodes for each user type
#     core_users = [f"core_{i}" for i in range(num_core_users)]
#     org_users = [f"org_{i}" for i in range(num_org_users)]
#     basic_users = [f"basic_{i}" for i in range(num_basic_users)]
#     all_users = core_users + org_users + basic_users
    
#     G.add_nodes_from(all_users)
    
#     # Connect all users to organization accounts
#     for user in all_users:
#         if user not in org_users:
#             for org in org_users:
#                 G.add_edge(user, org)
    
#     # Create connections based on retweets and replies
#     for date, data in tweet_data.items():
#         num_connections = data['retweets'] + data['replies']
#         for _ in range(num_connections):
#             source = random.choice(all_users)
#             target = random.choice(all_users)
#             if source != target:
#                 G.add_edge(source, target)
    
#     # Add some random connections to simulate organic relationships
#     num_random_connections = int(0.1 * G.number_of_edges())  # 10% of existing edges
#     for _ in range(num_random_connections):
#         source = random.choice(all_users)
#         target = random.choice(all_users)
#         if source != target and not G.has_edge(source, target):
#             G.add_edge(source, target)
    
#     return G

# # Example usage:
# tweet_data = {
#     datetime(2040, 5, 30).date(): {'total': 1840, 'with_url': 955, 'retweets': 165, 'replies': 608},
#     datetime(2040, 5, 31).date(): {'total': 2236, 'with_url': 1106, 'retweets': 196, 'replies': 706},
#     datetime(2040, 6, 1).date(): {'total': 3283, 'with_url': 1654, 'retweets': 297, 'replies': 1048},
#     datetime(2040, 6, 2).date(): {'total': 2120, 'with_url': 1042, 'retweets': 189, 'replies': 676},
#     datetime(2040, 6, 3).date(): {'total': 1849, 'with_url': 991, 'retweets': 159, 'replies': 610}
# }

# num_core_users = 50
# num_org_users = 25
# num_basic_users = 425

# social_graph = generate_social_graph(tweet_data, num_core_users, num_org_users, num_basic_users)

# print(f"Number of nodes: {social_graph.number_of_nodes()}")
# print(f"Number of edges: {social_graph.number_of_edges()}")


# ## Network analysis ##
# import networkx as nx
# import pandas as pd

# def calculate_network_statistics(G):
#     stats = {}
    
#     stats['N (number of nodes)'] = G.number_of_nodes()
#     stats['M (number of arcs)'] = G.number_of_edges()
#     stats['<k> (average degree)'] = sum(dict(G.degree()).values()) / G.number_of_nodes()
    
#     in_degrees = [d for n, d in G.in_degree()]
#     out_degrees = [d for n, d in G.out_degree()]
#     stats['max(kin) (maximum indegree)'] = max(in_degrees) if in_degrees else 'N/A'
#     stats['max(kout) (maximum outdegree)'] = max(out_degrees) if out_degrees else 'N/A'
    
#     stats['C (clustering)'] = nx.average_clustering(G)
    
#     # Note: average_shortest_path_length can be computationally expensive for large graphs
#     try:
#         stats['l (average path length)'] = nx.average_shortest_path_length(G)
#     except nx.NetworkXError:
#         stats['l (average path length)'] = 'N/A (Graph is not connected)'
    
#     return stats

# def create_comparison_table(generated_graph, mention_graph=None):
#     generated_stats = calculate_network_statistics(generated_graph)
    
#     if mention_graph:
#         mention_stats = calculate_network_statistics(mention_graph)
#     else:
#         mention_stats = {k: 'N/A' for k in generated_stats.keys()}
    
#     df = pd.DataFrame({
#         'Variable': generated_stats.keys(),
#         'Generated Network': generated_stats.values(),
#         'Mentions Network': mention_stats.values()
#     })
    
#     return df

# # Example usage:
# social_graph = generate_social_graph(tweet_data, num_core_users, num_org_users, num_basic_users)
# comparison_table = create_comparison_table(social_graph)
# print(comparison_table.to_string(index=False))

# ## Compare with the paper : DOI: 10.1177/0002764213479371 Table I##
# import pandas as pd

# # Create the provided data table
# provided_data = pd.DataFrame({
#     'Variable': [
#         'N (number of nodes)',
#         'M (number of arcs)',
#         '<k> (average degree)',
#         'max(kin) (maximum indegree)',
#         'max(kout) (maximum outdegree)',
#         'C (clustering)',
#         'l (average path length)'
#     ],
#     'Following-Follower Network': [87569, 6030459, 69, 5773, 31798, 0.22, 3.24],
#     'Mentions Network': [87569, 206592, 2.36, 29155, 289, 0.034, 1.7]
# })

# # Generate our social graph
# social_graph = generate_social_graph(tweet_data, num_core_users, num_org_users, num_basic_users)

# # Calculate statistics for our generated graph
# our_stats = calculate_network_statistics(social_graph)

# # Create a comparison table
# comparison = pd.DataFrame({
#     'Variable': provided_data['Variable'],
#     'Our Generated Network': [our_stats.get(var, 'N/A') for var in provided_data['Variable']],
#     'Provided Following-Follower Network': provided_data['Following-Follower Network'],
#     'Provided Mentions Network': provided_data['Mentions Network']
# })

# print(comparison.to_string(index=False))

# ## Normalized stats ##
# import math

# def normalize_network_statistics(stats, num_nodes):
#     normalized_stats = stats.copy()
    
#     # Normalize number of arcs (edges)
#     max_possible_edges = num_nodes * (num_nodes - 1) / 2
#     normalized_stats['M (number of arcs)'] = stats['M (number of arcs)'] / max_possible_edges
    
#     # Average degree is already normalized
    
#     # Normalize maximum indegree and outdegree
#     normalized_stats['max(kin) (maximum indegree)'] = stats['max(kin) (maximum indegree)'] / (num_nodes - 1)
#     normalized_stats['max(kout) (maximum outdegree)'] = stats['max(kout) (maximum outdegree)'] / (num_nodes - 1)
    
#     # Clustering coefficient is already normalized
    
#     # Normalize average path length
#     # We'll use the theoretical minimum (1) and maximum (diameter of a linear graph) as bounds
#     max_path_length = num_nodes - 1
#     if isinstance(stats['l (average path length)'], (int, float)):
#         normalized_stats['l (average path length)'] = (stats['l (average path length)'] - 1) / (max_path_length - 1)
    
#     return normalized_stats

# def create_normalized_comparison_table(generated_graph, provided_data, num_users=500):
#     generated_stats = calculate_network_statistics(generated_graph)
#     normalized_generated_stats = normalize_network_statistics(generated_stats, num_users)
    
#     # Normalize the provided data for the Mentions Network
#     mentions_stats = {
#         'N (number of nodes)': provided_data.loc[0, 'Mentions Network'],
#         'M (number of arcs)': provided_data.loc[1, 'Mentions Network'],
#         '<k> (average degree)': provided_data.loc[2, 'Mentions Network'],
#         'max(kin) (maximum indegree)': provided_data.loc[3, 'Mentions Network'],
#         'max(kout) (maximum outdegree)': provided_data.loc[4, 'Mentions Network'],
#         'C (clustering)': provided_data.loc[5, 'Mentions Network'],
#         'l (average path length)': provided_data.loc[6, 'Mentions Network']
#     }
#     normalized_mentions_stats = normalize_network_statistics(mentions_stats, mentions_stats['N (number of nodes)'])
    
#     comparison = pd.DataFrame({
#         'Variable': generated_stats.keys(),
#         'Our Generated Network (Raw)': generated_stats.values(),
#         'Our Generated Network (Normalized)': normalized_generated_stats.values(),
#         'Provided Mentions Network (Raw)': [mentions_stats[var] for var in generated_stats.keys()],
#         'Provided Mentions Network (Normalized)': [normalized_mentions_stats[var] for var in generated_stats.keys()]
#     })
    
#     return comparison

# # Generate our social graph
# social_graph = generate_social_graph(tweet_data, num_core_users, num_org_users, num_basic_users)

# # Create the provided data table
# provided_data = pd.DataFrame({
#     'Variable': [
#         'N (number of nodes)',
#         'M (number of arcs)',
#         '<k> (average degree)',
#         'max(kin) (maximum indegree)',
#         'max(kout) (maximum outdegree)',
#         'C (clustering)',
#         'l (average path length)'
#     ],
#     'Following-Follower Network': [87569, 6030459, 69, 5773, 31798, 0.22, 3.24],
#     'Mentions Network': [87569, 206592, 2.36, 29155, 289, 0.034, 1.7]
# })

# # Calculate and display the normalized comparison table
# comparison_table = create_normalized_comparison_table(social_graph, provided_data, num_users=500)
# print(comparison_table.to_string(index=False))


### V2 graph ###
import networkx as nx
import random
import pandas as pd
import matplotlib.pyplot as plt

def generate_social_graph_v2(num_users, num_org_users, target_avg_degree, power_law_exp=2.5, small_world_prob=0.1):
    G = nx.Graph()
    
    # Add nodes
    G.add_nodes_from(range(num_users))
    
    # Implement preferential attachment with power-law distribution
    target_edges = (target_avg_degree * num_users) // 2
    while G.number_of_edges() < target_edges:
        source = random.choice(list(G.nodes()))
        # Choose target based on current degree (preferential attachment)
        target = random.choices(list(G.nodes()), weights=[G.degree(n) + 1 for n in G.nodes()])[0]
        if source != target and not G.has_edge(source, target):
            G.add_edge(source, target)
    
    # Add small-world effect
    for u, v in list(G.edges()):
        if random.random() < small_world_prob:
            w = random.choice(list(G.nodes()))
            if w != u and w != v and not G.has_edge(u, w):
                G.remove_edge(u, v)
                G.add_edge(u, w)
    
    return G

def calculate_network_statistics(G):
    stats = {}
    
    stats['N (number of nodes)'] = G.number_of_nodes()
    stats['M (number of arcs)'] = G.number_of_edges()
    stats['<k> (average degree)'] = 2 * G.number_of_edges() / G.number_of_nodes()
    
    degrees = [d for n, d in G.degree()]
    stats['max(kin) (maximum indegree)'] = max(degrees)
    stats['max(kout) (maximum outdegree)'] = max(degrees)
    
    stats['C (clustering)'] = nx.average_clustering(G)
    
    try:
        stats['l (average path length)'] = nx.average_shortest_path_length(G)
    except nx.NetworkXError:
        stats['l (average path length)'] = 'N/A (Graph is not connected)'
    
    return stats

def normalize_network_statistics(stats, num_nodes):
    normalized_stats = stats.copy()
    
    max_possible_edges = num_nodes * (num_nodes - 1) / 2
    normalized_stats['M (number of arcs)'] = stats['M (number of arcs)'] / max_possible_edges
    normalized_stats['max(kin) (maximum indegree)'] = stats['max(kin) (maximum indegree)'] / (num_nodes - 1)
    normalized_stats['max(kout) (maximum outdegree)'] = stats['max(kout) (maximum outdegree)'] / (num_nodes - 1)
    
    if isinstance(stats['l (average path length)'], (int, float)):
        max_path_length = num_nodes - 1
        normalized_stats['l (average path length)'] = (stats['l (average path length)'] - 1) / (max_path_length - 1)
    
    return normalized_stats

# Generate new social graph
num_users = 500
num_org_users = 25
target_avg_degree = 2.5  # Slightly higher than the provided network to account for the smaller size
new_social_graph = generate_social_graph_v2(num_users, num_org_users, target_avg_degree)

# Calculate statistics for the new graph
new_stats = calculate_network_statistics(new_social_graph)
new_normalized_stats = normalize_network_statistics(new_stats, num_users)

# Provided network data
provided_data = {
    'N (number of nodes)': 87569,
    'M (number of arcs)': 206592,
    '<k> (average degree)': 2.36,
    'max(kin) (maximum indegree)': 29155,
    'max(kout) (maximum outdegree)': 289,
    'C (clustering)': 0.034,
    'l (average path length)': 1.7
}
provided_normalized = normalize_network_statistics(provided_data, provided_data['N (number of nodes)'])

# Create comparison table
comparison = pd.DataFrame({
    'Variable': new_stats.keys(),
    'New Generated Network (Raw)': new_stats.values(),
    'New Generated Network (Normalized)': new_normalized_stats.values(),
    'Provided Mentions Network (Raw)': [provided_data[var] for var in new_stats.keys()],
    'Provided Mentions Network (Normalized)': [provided_normalized[var] for var in new_stats.keys()]
})

print(comparison.to_string(index=False))

# Visualize degree distribution
degrees = [d for n, d in new_social_graph.degree()]
plt.figure(figsize=(10, 6))
plt.hist(degrees, bins=30, edgecolor='black')
plt.title('Degree Distribution of Generated Network')
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.show()

### V3 Graph ###
# import networkx as nx
# import random
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# def generate_social_graph_v3(num_users, target_avg_degree, power_law_exp=2.1, rewiring_prob=0.4):
#     # Start with a connected graph (e.g., a ring lattice)
#     k = int(target_avg_degree)
#     G = nx.connected_watts_strogatz_graph(num_users, k, rewiring_prob)
    
#     # Add more edges using preferential attachment
#     target_edges = int((target_avg_degree * num_users) / 4)
#     while G.number_of_edges() < target_edges:
#         source = random.choice(list(G.nodes()))
#         # Choose target based on degree (preferential attachment)
#         degrees = [G.degree(n) for n in G.nodes()]
#         degree_sum = sum(degrees)
#         probabilities = [d / degree_sum for d in degrees]
#         target = random.choices(list(G.nodes()), weights=probabilities)[0]
#         if source != target and not G.has_edge(source, target):
#             G.add_edge(source, target)
    
#     return G

# def calculate_network_statistics(G):
#     stats = {}
    
#     stats['N (number of nodes)'] = G.number_of_nodes()
#     stats['M (number of arcs)'] = G.number_of_edges()
#     stats['<k> (average degree)'] = 2 * G.number_of_edges() / G.number_of_nodes()
    
#     degrees = [d for n, d in G.degree()]
#     stats['max(kin) (maximum indegree)'] = max(degrees)
#     stats['max(kout) (maximum outdegree)'] = max(degrees)
    
#     stats['C (clustering)'] = nx.average_clustering(G)
    
#     stats['l (average path length)'] = nx.average_shortest_path_length(G)
    
#     return stats

# def normalize_network_statistics(stats, num_nodes):
#     normalized_stats = stats.copy()
    
#     max_possible_edges = num_nodes * (num_nodes - 1) / 2
#     normalized_stats['M (number of arcs)'] = stats['M (number of arcs)'] / max_possible_edges
#     normalized_stats['max(kin) (maximum indegree)'] = stats['max(kin) (maximum indegree)'] / (num_nodes - 1)
#     normalized_stats['max(kout) (maximum outdegree)'] = stats['max(kout) (maximum outdegree)'] / (num_nodes - 1)
    
#     max_path_length = num_nodes - 1
#     normalized_stats['l (average path length)'] = (stats['l (average path length)'] - 1) / (max_path_length - 1)
    
#     return normalized_stats

# # Generate new social graph
# num_users = 500
# target_avg_degree = 2.36  # Matching the provided network's average degree
# new_social_graph = generate_social_graph_v3(num_users, target_avg_degree)

# # Calculate statistics for the new graph
# new_stats = calculate_network_statistics(new_social_graph)
# new_normalized_stats = normalize_network_statistics(new_stats, num_users)

# # Provided network data
# provided_data = {
#     'N (number of nodes)': 87569,
#     'M (number of arcs)': 206592,
#     '<k> (average degree)': 2.36,
#     'max(kin) (maximum indegree)': 29155,
#     'max(kout) (maximum outdegree)': 289,
#     'C (clustering)': 0.034,
#     'l (average path length)': 1.7
# }
# provided_normalized = normalize_network_statistics(provided_data, provided_data['N (number of nodes)'])

# # Create comparison table
# comparison = pd.DataFrame({
#     'Variable': new_stats.keys(),
#     # 'New Generated Network (Raw)': new_stats.values(),
#     'New Generated Network (Normalized)': new_normalized_stats.values(),
#     # 'Provided Mentions Network (Raw)': [provided_data[var] for var in new_stats.keys()],
#     'Provided Mentions Network (Normalized)': [provided_normalized[var] for var in new_stats.keys()]
# })

# print(comparison.to_string(index=False))

# # Visualize degree distribution
# degrees = [d for n, d in new_social_graph.degree()]
# plt.figure(figsize=(10, 6))
# plt.hist(degrees, bins=30, edgecolor='black')
# plt.title('Degree Distribution of Generated Network')
# plt.xlabel('Degree')
# plt.ylabel('Frequency')
# plt.show()

# Visualize the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(new_social_graph)
nx.draw(new_social_graph, pos, node_size=20, node_color='lightblue', with_labels=False)
plt.title('Visualization of Generated Social Graph')
plt.show()