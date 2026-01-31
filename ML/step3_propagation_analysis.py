import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
ML_OUT = BASE_DIR / "ML" / "outputs"

# ✅ CORRECT clustering output path
CLUSTER_FILE = (
    BASE_DIR
    / "Clustering"
    / "outputs"
    / "relative_fronthaul_groups.csv"
)


# ---------------- LOAD DATA ----------------
anomalies = pd.read_csv(ML_OUT / "cell_anomalies.csv")
groups = pd.read_csv(CLUSTER_FILE)

# Normalize column name
groups = groups.rename(columns={"relative_group": "group_id"})

# Merge anomaly + topology
df = anomalies.merge(groups[["cell_id", "group_id"]], on="cell_id", how="inner")

results = []

# ---------------- PROPAGATION LOGIC ----------------
for group_id, gdf in df.groupby("group_id"):
    pivot = gdf.pivot_table(
        index="slot_id",
        columns="cell_id",
        values="anomaly",
        fill_value=0
    )

    # Simultaneous anomalies = congestion propagation signal
    simultaneous_slots = pivot[pivot.sum(axis=1) >= 2]
    simultaneous_count = len(simultaneous_slots)

    # Confidence: normalized propagation strength
    confidence = simultaneous_count / max(len(pivot), 1)

    # Leader inference: earliest anomaly per slot
    leader_counts = {cell: 0 for cell in pivot.columns}

    for _, row in simultaneous_slots.iterrows():
        active_cells = row[row == 1].index.tolist()
        if active_cells:
            leader_counts[active_cells[0]] += 1

    leader_cell = max(leader_counts, key=leader_counts.get)

    results.append({
        "group_id": int(group_id),
        "cells_in_group": list(map(int, pivot.columns)),
        "simultaneous_events": int(simultaneous_count),
        "leader_cell": int(leader_cell),
        "group_confidence": round(confidence, 4)
    })

# ---------------- SAVE ----------------
propagation_df = pd.DataFrame(results)
propagation_df.to_csv(
    ML_OUT / "congestion_propagation.csv",
    index=False
)

print("[DONE] Congestion propagation analysis complete")
print(propagation_df)
