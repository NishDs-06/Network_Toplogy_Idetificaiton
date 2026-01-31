import pandas as pd

# ---------- LOAD SLOT-LEVEL THROUGHPUT ----------
tp_file = r"C:\Users\SANJAYRAM\OneDrive\Desktop\toposense\datasense\throughput-cell-2.dat"

df_tp = pd.read_csv(tp_file, sep=r"\s+", header=None)
df_tp.columns = ["time", "throughput"]

df_tp["symbol_id"] = df_tp.index
df_tp["slot_id"] = df_tp["symbol_id"] // 14

slot_tp = (
    df_tp.groupby("slot_id", as_index=False)
         .agg({"throughput": "sum"})
         .rename(columns={"throughput": "throughput_slot"})
)

# ---------- LOAD PACKET STATS ----------
pkt_file = r"C:\Users\SANJAYRAM\OneDrive\Desktop\toposense\datasense\pkt-stats-cell-2.dat"

df_pkt = pd.read_csv(pkt_file, sep=r"\s+", header=None)
df_pkt.columns = ["slot", "slotStart", "txPackets", "rxPackets", "tooLateRxPackets"]

df_pkt = df_pkt.iloc[1:].reset_index(drop=True)

df_pkt["txPackets"] = pd.to_numeric(df_pkt["txPackets"], errors="coerce")
df_pkt["rxPackets"] = pd.to_numeric(df_pkt["rxPackets"], errors="coerce")

# Burst-based loss definition to avoid always-on loss
threshold = df_pkt["txPackets"].quantile(0.9)

df_pkt["loss_event"] = (
    (df_pkt["txPackets"] > df_pkt["rxPackets"]) &
    (df_pkt["txPackets"] > threshold)
).astype(int)

df_pkt["slot_id"] = df_pkt.index

loss_df = df_pkt[["slot_id", "loss_event"]]

# ---------- ALIGN COMMON SLOT RANGE ----------
max_common_slot = min(slot_tp["slot_id"].max(), loss_df["slot_id"].max())

slot_tp = slot_tp[slot_tp["slot_id"] <= max_common_slot]
loss_df = loss_df[loss_df["slot_id"] <= max_common_slot]

# ---------- MERGE ----------
merged_df = pd.merge(slot_tp, loss_df, on="slot_id", how="inner")

# Add cell ID
merged_df["cell_id"] = 2

# Final column order
merged_df = merged_df[["cell_id", "slot_id", "throughput_slot", "loss_event"]]


# ---- Robust congestion detection using relative drop ----

# Rolling median as baseline
baseline = (
    merged_df["throughput_slot"]
    .rolling(window=20, min_periods=1)
    .median()
)

# Congestion if throughput drops significantly below baseline
merged_df["congestion_event"] = (
    merged_df["throughput_slot"] < 0.5 * baseline
).astype(int)

print("Congestion mean:", merged_df["congestion_event"].mean())




print(merged_df.head(10))
print(merged_df.tail(10))
print("Final rows:", len(merged_df))

merged_df.to_csv("merged_cell2_updated.csv", index=False)

# ---- congestion_event already computed above ----

print("Congestion mean:", merged_df["congestion_event"].mean())

# 🔴 THIS LINE MUST BE LAST
merged_df.to_csv("merged_cell2.csv", index=False)