import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "Preprocessing" / "outputs"
ML_OUT = BASE_DIR / "ML" / "outputs"
ML_OUT.mkdir(exist_ok=True)

# Load multicell throughput
tp = pd.read_csv(OUT_DIR / "multicell_throughputdata.csv")

# Ensure ordering
tp = tp.sort_values(["cell_id", "slot_id"])

anomaly_rows = []

for cell_id, df in tp.groupby("cell_id"):
    df = df.copy()

    # Rolling baseline (robust, no labels)
    window = 200
    df["rolling_median"] = df["throughput_slot"].rolling(
        window, min_periods=50
    ).median()

    df["mad"] = (
        (df["throughput_slot"] - df["rolling_median"])
        .abs()
        .rolling(window, min_periods=50)
        .median()
    )

    # Robust z-score (MAD-based)
    df["z_score"] = (
        df["throughput_slot"] - df["rolling_median"]
    ) / (df["mad"] + 1e-6)

    # Anomaly condition (strict, low false positives)
    df["anomaly"] = (df["z_score"] < -3.5).astype(int)

    anomaly_rows.append(
        df[["slot_id", "cell_id", "anomaly"]]
    )

anomaly_df = pd.concat(anomaly_rows, ignore_index=True)

anomaly_df.to_csv(
    ML_OUT / "cell_anomalies.csv", index=False
)

print("[DONE] Anomaly detection complete")
print("Cells:", anomaly_df["cell_id"].nunique())
print("Total anomaly slots:", anomaly_df["anomaly"].sum())
