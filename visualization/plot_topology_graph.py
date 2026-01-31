import networkx as nx
import matplotlib.pyplot as plt
import os

def plot_topology(topology_result):
    os.makedirs("outputs", exist_ok=True)

    G = nx.Graph()

    for cell in topology_result:
        G.add_node(cell)

    for c1 in topology_result:
        for c2 in topology_result:
            if c1 != c2 and topology_result[c1] == topology_result[c2]:
                G.add_edge(c1, c2)

    link_colors = {
        "Link_1": "blue",
        "Link_2": "green",
        "Link_3": "orange"
    }

    node_colors = [link_colors[topology_result[cell]] for cell in G.nodes()]

    plt.figure(figsize=(8,6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1200)

    # Legend
    for link, color in link_colors.items():
        plt.scatter([], [], c=color, label=link)
    plt.legend(title="Inferred Links")

    plt.title("Inferred Fronthaul Topology")
    plt.tight_layout()

    plt.savefig("outputs/topology_graph.png", dpi=300)
    print("✅ Topology graph saved")
    plt.close()
