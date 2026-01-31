import pandas as pd
from pathlib import Path

# -------------------------------------------------
# This script exports cell → group mapping for ML
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
CLUSTER_DIR = BASE_DIR / "Clustering"

# ⚠️ Adjust this filename ONLY if your clustering output
# is saved under a different name
CLUSTER_RESULT_FILE = CLUSTER_DIR / "clustering_result.csv"

# Expected format of clustering_result.csv:
# cell_id, cluster_id

if not CLUSTER_RESULT_FILE.exists():
    raise FileNotFoundError(
        f"Clustering result not found: {CLUSTER_RESULT_FILE}"
    )

df = pd.read_csv(CLUSTER_RESULT_FILE)

# Normalize column names
df = df.rename(columns={"cluster_id": "group_id"})

groups_df = df[["cell_id", "group_id"]].sort_values("cell_id")

groups_df.to_csv(CLUSTER_DIR / "groups.csv", index=False)

print("[DONE] groups.csv created")
print("Groups:", groups_df["group_id"].nunique())
print("Cells:", groups_df["cell_id"].nunique())
