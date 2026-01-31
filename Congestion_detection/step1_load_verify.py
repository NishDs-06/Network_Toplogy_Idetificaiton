import pandas as pd

# Load merged per-cell data (FILES ARE IN SAME FOLDER)
cell1 = pd.read_csv("merged_cell1.csv")
cell2 = pd.read_csv("merged_cell2.csv")
cell3 = pd.read_csv("merged_cell3.csv")

print("Cell 1 preview:")
print(cell1.head())

print("\nCell 2 preview:")
print(cell2.head())

print("\nCell 3 preview:")
print(cell3.head())

print("\nCell 1 columns:", cell1.columns.tolist())
print("Cell 2 columns:", cell2.columns.tolist())
print("Cell 3 columns:", cell3.columns.tolist())

print("\nCell 1 rows:", len(cell1))
print("Cell 2 rows:", len(cell2))
print("Cell 3 rows:", len(cell3))
