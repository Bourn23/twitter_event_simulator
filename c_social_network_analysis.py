import networkx as nx

# Load the network from the file
social_graph = nx.read_gml("social_network_small.gml")
print("Network loaded from social_network.gml")

# Calculate degree centrality
degree_centrality = nx.degree_centrality(social_graph)

# Calculate betweenness centrality
betweenness_centrality = nx.betweenness_centrality(social_graph)

# Calculate eigenvector centrality
eigenvector_centrality = nx.eigenvector_centrality(social_graph)

# Identify the top 10 superspreaders based on eigenvector centrality
top_superspreaders = sorted(eigenvector_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 Superspreaders:")
for node, centrality in top_superspreaders:
    print(f"Node: {node}, Eigenvector Centrality: {centrality}")

from networkx.algorithms.community import greedy_modularity_communities

# Detect communities using the Greedy Modularity algorithm
communities = greedy_modularity_communities(social_graph)

# Identify the largest community (Super Friends)
largest_community = max(communities, key=len)
print(f"Number of nodes in the largest community (Super Friends): {len(largest_community)}")