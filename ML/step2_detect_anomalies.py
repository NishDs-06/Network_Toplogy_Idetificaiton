import pandas as pd
import numpy as np
from pathlib import Path

# -----------------------
# Paths
# -----------------------
BASE_DIR = Path(__file__).resolve().parents[1]
PRE_OUT = BASE_DIR / "Preprocessing" / "outputs"
ML_OUT = BASE_DIR / "ML" / "outputs"
ML_OUT.mkdir(exist_ok=True)

# -----------------------
# Load multicell throughput
# -----------------------
tp = pd.read_csv(PRE_OUT / "multicell_throughputdata.csv")

# Ensure correct ordering
tp = tp.sort_values(["cell_id", "slot_id"])

anomaly_rows = []

# -----------------------
# Parameters (strict + stable)
# -----------------------
WINDOW = 200
Z_THRESHOLD = -3.5

for cell_id, df in tp.groupby("cell_id"):
    df = df.copy()

    # Rolling baseline (robust, no labels)
    df["rolling_median"] = (
        df["throughput_slot"]
        .rolling(WINDOW, min_periods=50)
        .median()
    )

    # MAD (Median Absolute Deviation)
    df["mad"] = (
        (df["throughput_slot"] - df["rolling_median"])
        .abs()
        .rolling(WINDOW, min_periods=50)
        .median()
    )

    # Robust Z-score
    df["z_score"] = (
        df["throughput_slot"] - df["rolling_median"]
    ) / (df["mad"] + 1e-6)

    # Binary anomaly (strict → low FP)
    df["anomaly"] = (df["z_score"] < Z_THRESHOLD).astype(int)

    # -----------------------
    # CONFIDENCE SCORE (0–1)
    # -----------------------
    df["confidence"] = (
        np.abs(df["z_score"]) / abs(Z_THRESHOLD)
    ).clip(0.0, 1.0)

    # No anomaly → no confidence
    df.loc[df["anomaly"] == 0, "confidence"] = 0.0

    anomaly_rows.append(
        df[["slot_id", "cell_id", "anomaly", "confidence"]]
    )

# Combine all cells
anomaly_df = pd.concat(anomaly_rows, ignore_index=True)

# Save
anomaly_df.to_csv(
    ML_OUT / "cell_anomalies.csv", index=False
)

print("[DONE] Anomaly detection complete")
print("Cells:", anomaly_df["cell_id"].nunique())
print("Total anomaly slots:", anomaly_df["anomaly"].sum())
