import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "outputs"

tp = pd.read_csv(OUT_DIR / "multicell_throughputdata.csv")

thresholds = (
    tp.groupby("cell_id")["throughput_slot"]
      .quantile(0.1)
      .to_dict()
)

tp["congestion_event"] = tp.apply(
    lambda row: 1 if row["throughput_slot"] < thresholds[row["cell_id"]] else 0,
    axis=1
)

congestion = tp[["slot_id", "cell_id", "congestion_event"]]

congestion.to_csv(
    OUT_DIR / "multicell_congestiondata.csv",
    index=False
)

print("[DONE] multicell_congestiondata.csv created")
print("Cells:", congestion["cell_id"].nunique())
print("Slots:", congestion["slot_id"].nunique())
