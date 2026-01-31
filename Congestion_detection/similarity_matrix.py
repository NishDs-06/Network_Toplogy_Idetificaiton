import pandas as pd
import numpy as np

# Load congestion data
df = pd.read_csv("outputs/multicell_congestiondata.csv")

# Ensure congestion_event is binary
df["congestion_event"] = (df["congestion_event"] > 0).astype(int)

# Pivot with aggregation (FIX)
pivot = df.pivot_table(
    index="slot_id",
    columns="cell_id",
    values="congestion_event",
    aggfunc="max"
).fillna(0)

# Convert to matrix (cells x slots)
X = pivot.T.values

# Cosine similarity
norms = np.linalg.norm(X, axis=1)
similarity = (X @ X.T) / (norms[:, None] * norms[None, :])
similarity = np.nan_to_num(similarity)

# Create DataFrame
similarity_matrix = pd.DataFrame(
    similarity,
    index=pivot.columns,
    columns=pivot.columns
)

# Output
print("\nSimilarity Matrix:\n")
print(similarity_matrix)

similarity_matrix.to_csv("outputs/similarity_matrix.csv")
