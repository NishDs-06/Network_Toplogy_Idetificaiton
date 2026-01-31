import pandas as pd
import numpy as np

# Load merged per-cell data
cell1 = pd.read_csv("merged_cell1.csv")
cell2 = pd.read_csv("merged_cell2.csv")
cell3 = pd.read_csv("merged_cell3.csv")

# Extract loss_event vectors (aligned by slot_id)
loss_vectors = {
    1: cell1["loss_event"].values,
    2: cell2["loss_event"].values,
    3: cell3["loss_event"].values
}

# Jaccard similarity for binary vectors
def jaccard_similarity(a, b):
    intersection = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return intersection / union if union != 0 else 0.0

# Compute similarity matrix
cell_ids = list(loss_vectors.keys())
similarity_matrix = pd.DataFrame(
    index=cell_ids,
    columns=cell_ids,
    dtype=float
)

for i in cell_ids:
    for j in cell_ids:
        similarity_matrix.loc[i, j] = jaccard_similarity(
            loss_vectors[i],
            loss_vectors[j]
        )

print("Loss-event similarity matrix (Jaccard):")
print(similarity_matrix)
