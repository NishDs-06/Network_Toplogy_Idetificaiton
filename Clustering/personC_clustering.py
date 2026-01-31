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

# Color assignment (frontend only)
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
OUTPUT_FILE = OUT_DIR / "relative_fronthaul_groups.csv"
topology_table.to_csv(OUTPUT_FILE, index=False)

print("[DONE] Relative fronthaul topology inferred")
print("Cells:", topology_table["cell_id"].nunique())
print("Groups:", topology_table["relative_group"].nunique())
print(f"Saved to: {OUTPUT_FILE}")
