import pandas as pd
from pathlib import Path

# -------------------------------------------------
# Export cell → group mapping for ML & API
# Source: relative_fronthaul_groups.csv (Person C)
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
SRC = BASE_DIR / "Clustering" / "outputs" / "relative_fronthaul_groups.csv"
DST = BASE_DIR / "ML" / "ml_inputs" / "groups.csv"

if not SRC.exists():
    raise FileNotFoundError(f"Missing clustering output: {SRC}")

df = pd.read_csv(SRC)

# Normalize schema to API / ML contract
groups_df = (
    df.rename(columns={"relative_group": "group_id"})
      [["cell_id", "group_id"]]
      .sort_values("cell_id")
)

groups_df.to_csv(DST, index=False)

print("[OK] groups.csv exported for ML / API")
print("Cells:", groups_df["cell_id"].nunique())
print("Groups:", groups_df["group_id"].nunique())
print(groups_df.head())
