import pandas as pd
import numpy as np

# Load congestion data
df = pd.read_csv("multicell_congestiondata.csv")

# Ensure congestion_event is binary
df["congestion_event"] = (df["congestion_event"] > 0).astype(int)

# Pivot to slot x cell matrix
pivot = df.pivot(index="slot_id", columns="cell_id", values="congestion_event")
pivot = pivot.fillna(0)

# Convert to matrix (cells x slots)
X = pivot.T.values

# Cosine similarity (no sklearn)
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

similarity_matrix.to_csv("similarity_matrix.csv")
