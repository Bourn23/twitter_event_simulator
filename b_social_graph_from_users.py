import networkx as nx
import random
import numpy as np
import json

def load_users(json_file, num_users):
    """
    Load a subset of users from a JSON file.

    Args:
        json_file: The path to the JSON file.
        num_users: The number of users to load from the file.

    Returns:
        A list of user data dictionaries.
    """
    with open(json_file, 'r') as f:
        users_data = json.load(f)
    
    # Randomly sample the required number of users
    sampled_users = random.sample(users_data, num_users)
    return sampled_users

def generate_social_graph_with_users(num_basic_users, num_core_users, num_org_users):
    total_users = num_basic_users + num_core_users + num_org_users
    G = nx.DiGraph()  # Use a directed graph

    # Step 1: Load only the required number of users
    basic_users_data = load_users('basic_characters_fixed_ids.json', num_basic_users)
    core_users_data = load_users('core_characters_fixed_ids.json', num_core_users)
    org_users_data = load_users('total_organizations_fixed_ids.json', num_org_users)

    # Assign user IDs to nodes
    basic_users_ids = [user['aesop_id'] for user in basic_users_data]
    core_users_ids = [user['aesop_id'] for user in core_users_data]
    org_users_ids = [user['aesop_id'] for user in org_users_data]

    # Initialize users
    basic_users = list(range(num_basic_users))
    core_users = list(range(num_basic_users, num_basic_users + num_core_users))
    org_users = list(range(num_basic_users + num_core_users, total_users))

    # Map nodes to user IDs
    user_id_mapping = {}
    for i, user_id in enumerate(basic_users_ids + core_users_ids + org_users_ids):
        user_id_mapping[i] = user_id

    # Add nodes with user IDs
    G.add_nodes_from([user_id_mapping[i] for i in range(total_users)])

    all_nodes = list(G.nodes())
    # Step 2: Connect organization users to a smaller subset of others (reduce connections further)
    for org in org_users_ids:
        connected_users = random.sample(basic_users + core_users, k=int(0.15 * total_users))  # Connect to 15% of users
        for user in connected_users:
            G.add_edge(org, all_nodes[user])

    # Step 3: Core (Influential) Users based on following/followers ratio
    
    for core in core_users_ids:
        # followers_count = int(np.random.pareto(a=2.8) * (num_basic_users + num_org_users) * 0.65) + 1  # Slightly reduce followers count
        # change followers_count distribution to normal
        # followers_count = int(np.random.normal(loc=200, scale=46)) + 1
        # change followers_count distribution to beta
        followers_count = int(np.random.beta(a=3, b=5) * (num_basic_users + num_org_users) * 0.75) + 1
        following_count = int(followers_count * random.uniform(1.5, 0.2))  # Slightly adjust following count

        print("core:", core, "followers_count:", followers_count, "following_count:", following_count)

        # Create incoming edges (followers)
        for _ in range(followers_count):
            follower = random.choice(list(G.nodes()))
            if follower != core and not G.has_edge(follower, core):
                G.add_edge(follower, core)
        
        # Create outgoing edges (following)
        for _ in range(following_count):
            following = random.choice(list(G.nodes()))
            if following != core and not G.has_edge(core, following):
                G.add_edge(core, following)

    # Step 4: Basic Users based on following/followers ratio
    for basic in basic_users_ids:
        # followers_count = int(np.random.exponential(scale=6.8)) + 1  # Reduce followers count
        # we will want to have users that are connected up to around 250 users and down to 25 users, so we'll use another distribution than exponential
        followers_count = int(np.random.beta(a=3, b=2) * (num_core_users + num_org_users) * 0.65) + 1
        following_count = int(followers_count * random.uniform(0.1, 1.2))  # Adjust following count

        print("basic:", basic, "followers_count:", followers_count, "following_count:", following_count)

        # Create incoming edges (followers)
        for _ in range(followers_count):
            follower = random.choice(list(G.nodes()))
            if follower != basic and not G.has_edge(follower, basic):
                G.add_edge(follower, basic)
        
        # Create outgoing edges (following)
        for _ in range(following_count):
            following = random.choice(list(G.nodes()))
            if following != basic and not G.has_edge(basic, following):
                G.add_edge(basic, following)

    # Step 5: Ensure Connectivity
    if not nx.is_connected(G.to_undirected()):
        components = list(nx.connected_components(G.to_undirected()))
        print("Components:", components)
        for i in range(len(components) - 1):
            u = random.choice(list(components[i]))
            v = random.choice(list(components[i + 1]))
            G.add_edge(u, v)

    # Step 6: Add a small number of triangles
    for node in basic_users_ids:
        neighbors = list(G.neighbors(node))
        if len(neighbors) > 1:
            u, v = random.sample(neighbors, 2)
            if not G.has_edge(u, v):
                if random.random() < 0.1:  # Small probability of creating a triangle
                    G.add_edge(u, v)

    return G

# Parameters for the network
num_basic_users = 10
num_core_users = 3
num_org_users = 2

# Generate the network with user IDs
social_graph = generate_social_graph_with_users(num_basic_users, num_core_users, num_org_users)

import pandas as pd
# Calculate statistics for analysis
def calculate_network_statistics(G):
    stats = {}
    stats['N (number of nodes)'] = G.number_of_nodes()
    stats['M (number of arcs)'] = G.number_of_edges()
    stats['<k> (average degree)'] = 2 * G.number_of_edges() / G.number_of_nodes()
    
    in_degrees = [G.in_degree(n) for n in G.nodes()]
    out_degrees = [G.out_degree(n) for n in G.nodes()]
    stats['max(kin) (maximum indegree)'] = max(in_degrees)
    stats['max(kout) (maximum outdegree)'] = max(out_degrees)
    
    stats['C (clustering)'] = nx.average_clustering(G.to_undirected())
    
    try:
        stats['l (average path length)'] = nx.average_shortest_path_length(G)
    except nx.NetworkXError:
        stats['l (average path length)'] = 'N/A (Graph is not connected)'
    
    return stats

def calculate_network_statistics_excluding_orgs(G, org_users):
    # Exclude organization nodes from the network statistics calculation
    non_org_nodes = [n for n in G.nodes() if n not in org_users]
    H = G.subgraph(non_org_nodes)
    
    stats = {}
    stats['N (number of nodes)'] = H.number_of_nodes()
    stats['M (number of arcs)'] = H.number_of_edges()
    stats['<k> (average degree)'] = 2 * H.number_of_edges() / H.number_of_nodes()
    
    in_degrees = [H.in_degree(n) for n in H.nodes()]
    out_degrees = [H.out_degree(n) for n in H.nodes()]
    stats['max(kin) (maximum indegree)'] = max(in_degrees)
    stats['max(kout) (maximum outdegree)'] = max(out_degrees)
    
    stats['C (clustering)'] = nx.average_clustering(H.to_undirected())
    
    try:
        stats['l (average path length)'] = nx.average_shortest_path_length(H)
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


# Calculate statistics excluding organization users
generated_stats = calculate_network_statistics_excluding_orgs(social_graph, range(num_basic_users + num_core_users, num_basic_users + num_core_users + num_org_users))
generated_normalized_stats = normalize_network_statistics(generated_stats, generated_stats['N (number of nodes)'])

# Provided (baseline) network data
baseline_data = {
    'N (number of nodes)': 87569,
    'M (number of arcs)': 206592,
    '<k> (average degree)': 2.36,
    'max(kin) (maximum indegree)': 29155,
    'max(kout) (maximum outdegree)': 289,
    'C (clustering)': 0.034,
    'l (average path length)': 1.7
}
baseline_normalized = normalize_network_statistics(baseline_data, baseline_data['N (number of nodes)'])

# Create comparison table
comparison = pd.DataFrame({
    'Variable': generated_stats.keys(),
    'Generated Network (Raw)': generated_stats.values(),
    'Generated Network (Normalized)': generated_normalized_stats.values(),
    'Baseline Network (Raw)': [baseline_data[var] for var in generated_stats.keys()],
    'Baseline Network (Normalized)': [baseline_normalized[var] for var in generated_stats.keys()]
})

# Print the comparison table
print(comparison.to_string(index=False))


## Save the network
nx.write_gml(social_graph, "social_network_small_15.gml")
print("Network saved as social_network.gml", "with n_nodes:", len(social_graph.nodes()), "and n_edges:", len(social_graph.edges()))