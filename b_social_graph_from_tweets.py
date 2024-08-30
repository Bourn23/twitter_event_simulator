import networkx as nx
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_social_graph_v6(num_basic_users, num_core_users, num_org_users):
    total_users = num_basic_users + num_core_users + num_org_users
    G = nx.DiGraph()  # Use a directed graph

    # Step 1: Connect the graph (ensure connectivity)
    nodes = list(range(total_users))
    random.shuffle(nodes)
    for i in range(total_users - 1):
        G.add_edge(nodes[i], nodes[i + 1])

    # Initialize users
    basic_users = list(range(num_basic_users))
    core_users = list(range(num_basic_users, num_basic_users + num_core_users))
    org_users = list(range(num_basic_users + num_core_users, total_users))

    # Step 2: Connect organization users to a smaller subset of others (reduce connections further)
    for org in org_users:
        connected_users = random.sample(basic_users + core_users, k=int(0.15 * total_users))  # Connect to 15% of users
        for user in connected_users:
            G.add_edge(org, user)

    # Step 3: Core (Influential) Users based on following/followers ratio
    for core in core_users:
        # Following/Follower Ratio ~ 0.01 to 0.1 (low ratio)
        followers_count = int(np.random.pareto(a=2.) * 8) + 1  # Slightly reduce followers count
        following_count = int(followers_count * random.uniform(0.02, 0.04))  # Slightly adjust following count

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
    for basic in basic_users:
        # Following/Follower Ratio ~ 0.1 to 10 (balanced ratio)
        followers_count = int(np.random.exponential(scale=0.8)) + 1  # Reduce followers count
        following_count = int(followers_count * random.uniform(0.1, 1.2))  # Adjust following count

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
        for i in range(len(components) - 1):
            u = random.choice(list(components[i]))
            v = random.choice(list(components[i + 1]))
            G.add_edge(u, v)

    # Step 6: Add a small number of triangles
    for node in basic_users:
        neighbors = list(G.neighbors(node))
        if len(neighbors) > 1:
            u, v = random.sample(neighbors, 2)
            if not G.has_edge(u, v):
                if random.random() < 0.1:  # Small probability of creating a triangle
                    G.add_edge(u, v)

    return G

# Parameters for the network
num_basic_users = 425
num_core_users = 50
num_org_users = 25

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

# Generate the social graph with adjusted parameters
social_graph = generate_social_graph_v6(num_basic_users, num_core_users, num_org_users)

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

# Visualize degree distribution excluding organization nodes
degrees = [d for n, d in social_graph.degree() if n not in range(num_basic_users + num_core_users, num_basic_users + num_core_users + num_org_users)]
plt.figure(figsize=(10, 6))
plt.hist(degrees, bins=30, edgecolor='black')
plt.title('Degree Distribution of Generated Network (Excluding Organization Nodes)')
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.show()

# Visualize the graph excluding organization nodes
# H = social_graph.subgraph([n for n in social_graph.nodes() if n not in range(num_basic_users + num_core_users, num_basic_users + num_core_users + num_org_users)])
# plt.figure(figsize=(12, 8))
# pos = nx.spring_layout(H)
# nx.draw(H, pos, node_size=20, node_color='lightblue', with_labels=False, arrows=True)
# plt.title('Visualization of Generated Social Graph (Excluding Organization Nodes)')
# plt.show()

## Interactive Network Visualization
from pyvis.network import Network

def create_interactive_network_graph(G, output_file='network.html'):
    """
    Creates an interactive network graph from a NetworkX graph object.

    Args:
        G: A NetworkX graph object.
        output_file: The path to the output HTML file for the interactive network.

    Returns:
        None. The function creates and saves an interactive network visualization.
    """

    # Create a PyVis network
    net = Network(notebook=True, directed=True)
    net.from_nx(G)  # Load the NetworkX graph into PyVis

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
        "enabled": false,
        "barnesHut": {
          "gravitationalConstant": -20000,
          "centralGravity": 0.3,
          "springLength": 95,
          "springConstant": 0.04,
          "damping": 0.09,
          "avoidOverlap": 0.1
        },
        "stabilization": {
          "enabled": true,
          "iterations": 300
        }
      }
    }
    """)

    # Save the network visualization to an HTML file
    net.show(output_file)
    print(f"Interactive network graph saved to {output_file}")


# Example usage with the generated social graph
# Assuming `social_graph` is the graph created from the generate_social_graph_v8 function
create_interactive_network_graph(social_graph, output_file='social_network.html')

## Save the network
nx.write_gml(social_graph, "social_network.gml")
print("Network saved as social_network.gml")