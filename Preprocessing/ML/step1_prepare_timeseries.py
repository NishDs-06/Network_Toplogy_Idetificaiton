import pandas as pd
from pathlib import Path

# --------------------
# Paths
# --------------------
BASE_DIR = Path(__file__).resolve().parents[2]

PRE_OUT = BASE_DIR / "Preprocessing" / "outputs"
CLUSTER_DIR = BASE_DIR / "Clustering"
ML_OUT = BASE_DIR / "ML" / "ml_inputs"

ML_OUT.mkdir(parents=True, exist_ok=True)

# --------------------
# Load data
# --------------------
loss_df = pd.read_csv(PRE_OUT / "multicell_lossdata.csv")
tp_df = pd.read_csv(PRE_OUT / "multicell_throughputdata.csv")

groups_df = pd.read_csv(CLUSTER_DIR / "groups.csv")  # cell_id, group_id

# --------------------
# Build congestion_event
# --------------------
tp_threshold = tp_df["throughput_slot"].quantile(0.1)
tp_df["congestion_event"] = (tp_df["throughput_slot"] < tp_threshold).astype(int)

# --------------------
# Merge loss + congestion
# --------------------
cell_ts = pd.merge(
    loss_df,
    tp_df[["slot_id", "cell_id", "congestion_event"]],
    on=["slot_id", "cell_id"],
    how="inner"
)

cell_ts = cell_ts.merge(groups_df, on="cell_id", how="left")

# --------------------
# Save cell-level time series
# --------------------
cell_ts_out = cell_ts[[
    "slot_id",
    "cell_id",
    "loss_event",
    "congestion_event"
]]

cell_ts_out.to_csv(ML_OUT / "cell_timeseries.csv", index=False)

# --------------------
# Build group-level time series
# --------------------
group_ts = (
    cell_ts
    .groupby(["slot_id", "group_id"], as_index=False)
    .agg(
        loss_rate=("loss_event", "mean"),
        congestion_rate=("congestion_event", "mean")
    )
)

group_ts.to_csv(ML_OUT / "group_timeseries.csv", index=False)

# --------------------
# Sanity prints
# --------------------
print("[DONE] ML time-series prepared")
print("Cells:", cell_ts_out["cell_id"].nunique())
print("Groups:", group_ts["group_id"].nunique())
print("Slots:", cell_ts_out["slot_id"].nunique())
