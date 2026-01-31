import pandas as pd
from pathlib import Path

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "outputs"

loss_frames = []
tp_frames = []

# =========================
# Load per-cell outputs
# =========================
for cell_id in range(1, 25):
    loss_file = OUT_DIR / f"cell{cell_id}_loss.csv"
    tp_file = OUT_DIR / f"cell{cell_id}_slot_throughput.csv"

    if not loss_file.exists() or not tp_file.exists():
        print(f"[SKIP] Cell {cell_id} missing files")
        continue

    loss_df = pd.read_csv(loss_file)
    tp_df = pd.read_csv(tp_file)

    # =========================
    # CRITICAL FIX:
    # Ensure slot_id types match BEFORE merge
    # =========================
    loss_df["slot_id"] = loss_df["slot_id"].astype(int)
    tp_df["slot_id"] = tp_df["slot_id"].astype(int)

    # =========================
    # Merge throughput + loss
    # =========================
    merged = pd.merge(tp_df, loss_df, on="slot_id", how="inner")
    merged["cell_id"] = cell_id

    loss_frames.append(
        merged[["slot_id", "cell_id", "loss_event"]]
    )
    tp_frames.append(
        merged[["slot_id", "cell_id", "throughput_slot"]]
    )

    print(f"[OK] Cell {cell_id}: merged {len(merged)} slots")

# =========================
# Build multicell tables
# =========================
multicell_loss = pd.concat(loss_frames, ignore_index=True)
multicell_tp = pd.concat(tp_frames, ignore_index=True)

multicell_loss.to_csv(OUT_DIR / "multicell_lossdata.csv", index=False)
multicell_tp.to_csv(OUT_DIR / "multicell_throughputdata.csv", index=False)

print("\n[DONE] Multicell tables created")
print("Cells:", multicell_loss["cell_id"].nunique())
print("Slots:", multicell_loss["slot_id"].nunique())
print("Loss rows:", len(multicell_loss))
print("Throughput rows:", len(multicell_tp))
