import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw_data"
OUT_DIR = BASE_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)

# Loop over all 24 cells
for cell_id in range(1, 25):
    tp_file = RAW_DIR / f"throughput-cell-{cell_id}.dat"

    if not tp_file.exists():
        print(f"[SKIP] Missing {tp_file}")
        continue

    df = pd.read_csv(tp_file, sep=r"\s+", header=None)
    df.columns = ["time", "throughput"]

    df["symbol_id"] = df.index
    df["slot_id"] = df["symbol_id"] // 14

    slot_df = (
        df.groupby("slot_id", as_index=False)
          .agg({"throughput": "sum"})
          .rename(columns={"throughput": "throughput_slot"})
    )

    out_file = OUT_DIR / f"cell{cell_id}_slot_throughput.csv"
    slot_df.to_csv(out_file, index=False)

    print(f"[OK] Cell {cell_id}: {len(slot_df)} slots written")
