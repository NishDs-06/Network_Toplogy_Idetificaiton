import pandas as pd
import numpy as np
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
OUTPUT_FILE = OUT_DIR / "relative_fronthaul_groups.csv"

# ==================================================
# Load similarity matrix
# ==================================================
similarity = pd.read_csv(SIMILARITY_PATH, index_col=0)

# Normalize labels
similarity.index = similarity.index.astype(int)
similarity.columns = similarity.columns.astype(int)
similarity = similarity.loc[similarity.index, similarity.index]

# Sanity check
assert similarity.shape[0] == similarity.shape[1], "Similarity matrix must be square"

# ==================================================
# Similarity → Distance
# ==================================================
distance_matrix = 1.0 - similarity
condensed_distance = squareform(distance_matrix.values, checks=False)

# ==================================================
# Hierarchical clustering (RELATIVE topology only)
# ==================================================
linkage_matrix = linkage(condensed_distance, method="average")

# Adaptive cut (robust, no hallucination)
upper_triangle = distance_matrix.values[
    np.triu_indices_from(distance_matrix, k=1)
]

DISTANCE_THRESHOLD = np.median(upper_triangle) + 0.5 * np.std(upper_triangle)

cluster_labels = fcluster(
    linkage_matrix,
    t=DISTANCE_THRESHOLD,
    criterion="distance"
)

# ==================================================
# Build topology table
# ==================================================
topology_table = pd.DataFrame({
    "cell_id": similarity.index,
    "relative_group": cluster_labels
}).sort_values("relative_group")

# ==================================================
# Color assignment (frontend only)
# ==================================================
COLOR_MAP = [
    "red", "blue", "green", "orange", "purple",
    "brown", "pink", "gray", "olive", "cyan"
]

unique_groups = sorted(topology_table["relative_group"].unique())

group_colors = {
    grp: COLOR_MAP[i % len(COLOR_MAP)]
    for i, grp in enumerate(unique_groups)
}

topology_table["group_color"] = topology_table["relative_group"].map(group_colors)

# ==================================================
# Save output (CRITICAL CONTRACT)
# ==================================================
topology_table.to_csv(OUTPUT_FILE, index=False)

# ==================================================
# Logs
# ==================================================
print("[DONE] Relative fronthaul topology inferred")
print("Cells :", topology_table['cell_id'].nunique())
print("Groups:", topology_table['relative_group'].nunique())
print(f"Saved to: {OUTPUT_FILE}")
