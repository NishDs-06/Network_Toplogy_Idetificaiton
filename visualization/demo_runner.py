from dummy_data import similarity_matrix, topology_result
from plot_heatmap import plot_similarity_heatmap
from plot_topology_graph import plot_topology

if __name__ == "__main__":
    plot_similarity_heatmap(similarity_matrix)
    plot_topology(topology_result)
