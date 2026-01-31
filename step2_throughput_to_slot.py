import pandas as pd

# === CHANGE THIS PATH ===
throughput_file = r"C:\Users\SANJAYRAM\OneDrive\Desktop\toposense\datasense\throughput-cell-1.dat"
 # update filename

# Load throughput file
df = pd.read_csv(
    throughput_file,
    sep=r"\s+",        # whitespace separated
    header=None
)

# Name columns for clarity
df.columns = ["time", "throughput"]\

# Create symbol_id (each row = one symbol)
df["symbol_id"] = df.index

# Convert symbols to slots (14 symbols = 1 slot)
df["slot_id"] = df["symbol_id"] // 14

# Aggregate throughput per slot (SUM is recommended)
slot_df = (
    df.groupby("slot_id", as_index=False)
      .agg({"throughput": "sum"})
)

slot_df.rename(columns={"throughput": "throughput_slot"}, inplace=True)




print("Raw data:")
print(df.head())
print("Total rows:", len(df))
print("\nSymbol ID check:")
print(df[["symbol_id", "throughput"]].head(20))
print("\nSymbol to Slot mapping check:")
print(df[["symbol_id", "slot_id"]].head(30))
print("\nSlot-level throughput (first 5):")
print(slot_df.head())

print("\nSlot-level throughput (last 5):")
print(slot_df.tail())

print("\nTotal slots:", len(slot_df))



