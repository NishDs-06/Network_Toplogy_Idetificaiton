import pandas as pd

cell1 = pd.read_csv("merged_cell1.csv")
cell2 = pd.read_csv("merged_cell2.csv")
cell3 = pd.read_csv("merged_cell3.csv")

cell1 = cell1[["slot_id", "cell_id", "congestion_event"]]
cell2 = cell2[["slot_id", "cell_id", "congestion_event"]]
cell3 = cell3[["slot_id", "cell_id", "congestion_event"]]

multi_df = pd.concat([cell1, cell2, cell3], ignore_index=True)

# Keep only informative slots
informative_slots = (
    multi_df.groupby("slot_id")["congestion_event"].sum() > 0
)

multi_df = multi_df[
    multi_df["slot_id"].isin(informative_slots[informative_slots].index)
]

multi_df.to_csv("multicell_congestiondata.csv", index=False)

print(multi_df.head())
print("Unique cells:", multi_df["cell_id"].nunique())
print("Per-cell congestion mean:")
print(multi_df.groupby("cell_id")["congestion_event"].mean())
