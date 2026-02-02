import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

# ==================================================
# Load similarity matrix
# ==================================================
SIMILARITY_PATH = "outputs/similarity_matrix.csv"
similarity = pd.read_csv(SIMILARITY_PATH, index_col=0)

# Normalize labels
similarity.index = similarity.index.astype(str).str.strip()
similarity.columns = similarity.columns.astype(str).str.strip()
similarity = similarity.loc[similarity.index, similarity.index]

assert similarity.shape[0] == similarity.shape[1], "Similarity matrix must be square"

# ==================================================
# Hierarchical clustering
# ==================================================
distance_matrix = 1 - similarity
condensed_distance = squareform(distance_matrix.values, checks=False)
linkage_matrix = linkage(condensed_distance, method="average")

DISTANCE_THRESHOLD = 0.6
cluster_labels = fcluster(linkage_matrix, t=DISTANCE_THRESHOLD, criterion="distance")

# ==================================================
# Build outputs
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
    for i, grp in enumerate(sorted(grouped_cells))
}

topology_table["group_color"] = topology_table["relative_group"].map(group_colors)

# ==================================================
# OUTPUT — CLEAN TABLE
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
OUTPUT_FILE = OUT_DIR / "relative_fronthaul_groups.csv"
topology_table.to_csv(OUTPUT_FILE, index=False)

print("[DONE] Relative fronthaul topology inferred")
print("Cells:", topology_table["cell_id"].nunique())
print("Groups:", topology_table["relative_group"].nunique())
print(f"Saved to: {OUTPUT_FILE}")
