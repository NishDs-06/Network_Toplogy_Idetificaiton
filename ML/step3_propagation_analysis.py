import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
ML_OUT = BASE_DIR / "ML" / "outputs"
PRE_OUT = BASE_DIR / "Preprocessing" / "outputs"
CLUSTER_DIR = BASE_DIR / "Clustering"

# Load inputs
anomalies = pd.read_csv(ML_OUT / "cell_anomalies.csv")
groups = pd.read_csv(CLUSTER_DIR / "groups.csv")  # cell_id, group_id

# Merge group info
df = anomalies.merge(groups, on="cell_id", how="inner")

results = []

# Analyze propagation per group
for group_id, gdf in df.groupby("group_id"):
    pivot = gdf.pivot_table(
        index="slot_id",
        columns="cell_id",
        values="anomaly",
        fill_value=0
    )

    # Count simultaneous anomalies
    simultaneous = (pivot.sum(axis=1) >= 2).sum()

    # Directionality (who fires first)
    lead_counts = {cell: 0 for cell in pivot.columns}

    for _, row in pivot.iterrows():
        active = row[row == 1].index.tolist()
        if len(active) >= 2:
            lead_counts[active[0]] += 1

    leader = max(lead_counts, key=lead_counts.get)

    results.append({
        "group_id": group_id,
        "cells_in_group": list(pivot.columns),
        "simultaneous_events": int(simultaneous),
        "likely_leader_cell": int(leader)
    })

propagation_df = pd.DataFrame(results)

propagation_df.to_csv(
    ML_OUT / "congestion_propagation.csv",
    index=False
)

print("[DONE] Congestion propagation analysis complete")
print(propagation_df)
