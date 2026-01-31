import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PRE_OUT = BASE_DIR / "Preprocessing" / "outputs"
OUT_DIR = BASE_DIR / "Clustering" / "outputs"
OUT_DIR.mkdir(exist_ok=True)

tp = pd.read_csv(PRE_OUT / "multicell_throughputdata.csv")

# Compute rolling z-score per cell
features = []

for cell_id, df in tp.groupby("cell_id"):
    df = df.sort_values("slot_id").copy()

    med = df["throughput_slot"].rolling(200, min_periods=50).median()
    mad = (df["throughput_slot"] - med).abs().rolling(200, min_periods=50).median()

    z = (df["throughput_slot"] - med) / (mad + 1e-6)
    z = z.fillna(0)

    features.append(
        z.rename(cell_id).reset_index(drop=True)
    )

Z = pd.concat(features, axis=1)

# Pearson correlation
similarity = Z.corr().fillna(0)

similarity.to_csv(OUT_DIR / "similarity_matrix.csv")

print("[DONE] Robust similarity matrix computed")
print(similarity)
