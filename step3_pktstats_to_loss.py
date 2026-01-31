import pandas as pd

pkt_file = r"C:\Users\SANJAYRAM\OneDrive\Desktop\toposense\datasense\pkt-stats-cell-1.dat"

df_pkt = pd.read_csv(
    pkt_file,
    sep=r"\s+",
    header=None
)

df_pkt.columns = [
    "slot",
    "slotStart",
    "txPackets",
    "rxPackets",
    "tooLateRxPackets"
]

# Remove internal header row
df_pkt = df_pkt.iloc[1:].reset_index(drop=True)

# Force numeric conversion
df_pkt["txPackets"] = pd.to_numeric(df_pkt["txPackets"], errors="coerce")
df_pkt["rxPackets"] = pd.to_numeric(df_pkt["rxPackets"], errors="coerce")

# ✅ LOSS EVENT DEFINITION (CORRECT)
threshold = df_pkt["txPackets"].quantile(0.9)
df_pkt["loss_event"] = (
    (df_pkt["txPackets"] > df_pkt["rxPackets"]) &
    (df_pkt["txPackets"] > threshold)
).astype(int)



# Create slot_id for packet stats (row order = slot order)
df_pkt["slot_id"] = df_pkt.index

loss_df = df_pkt[["slot_id", "loss_event"]]


print(df_pkt[["slot", "txPackets", "rxPackets", "loss_event"]].head(20))
print("Total rows:", len(df_pkt))

loss_df = df_pkt[["slot_id", "loss_event"]]
loss_df.to_csv("cell1_lossdata.csv", index=False)
