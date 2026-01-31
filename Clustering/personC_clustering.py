import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from pathlib import Path

# ==================================================
# Paths
# ==================================================
BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "Clustering" / "outputs"
OUT_DIR.mkdir(exist_ok=True)

SIMILARITY_PATH = OUT_DIR / "similarity_matrix.csv"

# ==================================================
# Load similarity matrix
# ==================================================
similarity = pd.read_csv(SIMILARITY_PATH, index_col=0)

# Normalize labels
similarity.index = similarity.index.astype(int)
similarity.columns = similarity.columns.astype(int)
similarity = similarity.loc[similarity.index, similarity.index]

assert similarity.shape[0] == similarity.shape[1], "Similarity matrix must be square"

# ==================================================
# Hierarchical clustering (relative topology)
# ==================================================
distance_matrix = 1.0 - similarity
condensed_distance = squareform(distance_matrix.values, checks=False)

linkage_matrix = linkage(condensed_distance, method="average")

DISTANCE_THRESHOLD = 0.6
cluster_labels = fcluster(
    linkage_matrix,
    t=DISTANCE_THRESHOLD,
    criterion="distance"
)

# ==================================================
# Build output table
# ==================================================
topology_table = pd.DataFrame({
    "cell_id": similarity.index,
    "relative_group": cluster_labels
}).sort_values("relative_group")

# Group cells
grouped_cells = {}
for cell, grp in zip(similarity.index, cluster_labels):
    grouped_cells.setdefault(grp, []).append(cell)

# ==================================================
# 1️⃣ COLOR ASSIGNMENT
# ==================================================
COLOR_MAP = [
    "red", "blue", "green", "orange", "purple",
    "brown", "pink", "gray", "olive", "cyan"
]

group_colors = {
    grp: COLOR_MAP[i % len(COLOR_MAP)]
    for i, grp in enumerate(sorted(topology_table.relative_group.unique()))
}

topology_table["group_color"] = topology_table["relative_group"].map(group_colors)

# ==================================================
# Save output
# ==================================================
print("\n==========================================")
print(" Relative Fronthaul Topology")
print("==========================================\n")
print(topology_table.to_string(index=False))

# ==================================================
# OUTPUT — FLOWCHART STYLE
# ==================================================
print("\n==========================================")
print(" Relative Fronthaul Grouping")
print("==========================================\n")

for grp in sorted(grouped_cells):
    print(f"Group {grp} ({group_colors[grp]})")
    print("  ↓")
    for cell in grouped_cells[grp]:
        print(f"  {cell}")
    print()

# ==================================================
# SAVE TABLE FOR PERSON D
# ==================================================
topology_table.to_csv("outputs/relative_fronthaul_groups.csv", index=False)

# ==================================================
# 2️⃣ SIMPLE NETWORK GRAPH
# ==================================================
G = nx.Graph()

# Add nodes
for cell in similarity.index:
    grp = topology_table.loc[topology_table.cell_id == cell, "relative_group"].values[0]
    G.add_node(cell, group=grp)

# Connect nodes within same group
for grp, cells in grouped_cells.items():
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            G.add_edge(cells[i], cells[j])

# Draw graph
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G, seed=42)

node_colors = [
    group_colors[G.nodes[n]["group"]] for n in G.nodes
]

nx.draw(
    G,
    pos,
    with_labels=True,
    node_color=node_colors,
    node_size=800,
    font_size=9
)

plt.title("Relative Fronthaul Topology (Graph View)")
plt.show()
