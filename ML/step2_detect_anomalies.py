import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PRE_OUT = BASE_DIR / "Preprocessing" / "outputs"
ML_OUT = BASE_DIR / "ML" / "outputs"
ML_OUT.mkdir(exist_ok=True)

tp = pd.read_csv(PRE_OUT / "multicell_throughputdata.csv")

# 🔧 FIX: collapse duplicates
tp = (
    tp.groupby(["cell_id", "slot_id"], as_index=False)
      .agg({"throughput_slot": "mean"})
)

tp = tp.sort_values(["cell_id", "slot_id"])

WINDOW = 100
DROP_RATIO = 0.30  # FIX: Increased from 0.15 - 30% drop is more significant

rows = []

for cell_id, df in tp.groupby("cell_id"):
    df = df.copy()

    df["baseline"] = (
        df["throughput_slot"]
        .rolling(WINDOW, min_periods=30)
        .median()
    )

    df["drop_ratio"] = (
        (df["baseline"] - df["throughput_slot"])
        / (df["baseline"] + 1e-6)
    )

    df["anomaly"] = (df["drop_ratio"] > DROP_RATIO).astype(int)

    # FIX: Better confidence calculation - scales from 0 at threshold to 1 at 2x threshold
    # This gives gradual confidence instead of immediate clip to 1.0
    df["confidence"] = (
        (df["drop_ratio"] - DROP_RATIO) / DROP_RATIO  # 0 at threshold, 1 at 2x threshold
    ).clip(0.0, 1.0)

    df.loc[df["anomaly"] == 0, "confidence"] = 0.0

    rows.append(
        df[["slot_id", "cell_id", "anomaly", "confidence"]]
    )

anomaly_df = pd.concat(rows, ignore_index=True)
anomaly_df.to_csv(ML_OUT / "cell_anomalies.csv", index=False)

print("[DONE] Anomaly detection complete")
print("Cells:", anomaly_df["cell_id"].nunique())
print("Total anomalies:", int(anomaly_df["anomaly"].sum()))
