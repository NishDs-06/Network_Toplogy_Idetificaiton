import pandas as pd

# Load merged per-cell datasets (YOU ALREADY HAVE THESE)
cell1 = pd.read_csv("merged_cell1.csv")
cell2 = pd.read_csv("merged_cell2.csv")
cell3 = pd.read_csv("merged_cell3.csv")   # optional but recommended

# Keep ONLY what Person B needs
cell1 = cell1[["slot_id", "cell_id", "loss_event"]]
cell2 = cell2[["slot_id", "cell_id", "loss_event"]]
cell3 = cell3[["slot_id", "cell_id", "loss_event"]]

# Find common slot range
max_common_slot = min(
    cell1["slot_id"].max(),
    cell2["slot_id"].max(),
    cell3["slot_id"].max()
)

# Truncate to common slot range
cell1 = cell1[cell1["slot_id"] <= max_common_slot]
cell2 = cell2[cell2["slot_id"] <= max_common_slot]
cell3 = cell3[cell3["slot_id"] <= max_common_slot]

# STACK (this is the key step)
multicell_loss_df = pd.concat([cell1, cell2, cell3], ignore_index=True)

# Final sanity: enforce column order
multicell_loss_df = multicell_loss_df[["slot_id", "cell_id", "loss_event"]]

# Keep only slots where at least one cell has loss
informative_slots = (
    multicell_loss_df
    .groupby("slot_id")["loss_event"]
    .sum()
    .reset_index()
)

informative_slots = informative_slots[informative_slots["loss_event"] > 0]

# Filter multicell data to informative slots
multicell_loss_df = multicell_loss_df[
    multicell_loss_df["slot_id"].isin(informative_slots["slot_id"])
]


# Save final file
multicell_loss_df.to_csv("multicell_lossdata_informative.csv", index=False)


print(multicell_loss_df.head())
print("Total rows:", len(multicell_loss_df))
print("Unique cells:", multicell_loss_df["cell_id"].nunique())

print(
    multicell_loss_df
    .groupby("cell_id")["loss_event"]
    .mean()
)

