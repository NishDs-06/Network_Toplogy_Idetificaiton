import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw_data"
OUT_DIR = BASE_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)

# Loop over all 24 cells
for cell_id in range(1, 25):
    pkt_file = RAW_DIR / f"pkt-stats-cell-{cell_id}.dat"

    if not pkt_file.exists():
        print(f"[SKIP] Missing {pkt_file}")
        continue

    df = pd.read_csv(pkt_file, sep=r"\s+", header=None)
    df.columns = ["slot", "slotStart", "txPackets", "rxPackets", "tooLateRxPackets"]

    # Drop header row if present
    df = df.iloc[1:].reset_index(drop=True)

    df["txPackets"] = pd.to_numeric(df["txPackets"], errors="coerce").fillna(0)
    df["rxPackets"] = pd.to_numeric(df["rxPackets"], errors="coerce").fillna(0)

    # Loss event: transmitted > received
    df["loss_event"] = (df["txPackets"] > df["rxPackets"]).astype(int)

    loss_df = df[["slot", "loss_event"]].rename(columns={"slot": "slot_id"})

    out_file = OUT_DIR / f"cell{cell_id}_loss.csv"
    loss_df.to_csv(out_file, index=False)

    print(f"[OK] Cell {cell_id}: {loss_df['loss_event'].sum()} loss slots")
