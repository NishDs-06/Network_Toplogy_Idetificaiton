import pandas as pd

# Paste similarity matrix from Step 2 (use YOUR actual values if different)
similarity_matrix = pd.DataFrame(
    [[1.0, 0.82, 0.10],
     [0.82, 1.0, 0.12],
     [0.10, 0.12, 1.0]],
    index=[1, 2, 3],
    columns=[1, 2, 3]
)

# Similarity threshold for same fronthaul link
THRESHOLD = 0.6

inferred_links = {}
current_link = 1
visited = set()

for cell in similarity_matrix.index:
    if cell in visited:
        continue
    
    # Start new link group
    inferred_links[cell] = current_link
    visited.add(cell)
    
    # Group similar cells
    for other_cell in similarity_matrix.columns:
        if other_cell not in visited:
            if similarity_matrix.loc[cell, other_cell] >= THRESHOLD:
                inferred_links[other_cell] = current_link
                visited.add(other_cell)
    
    current_link += 1

# Final topology
topology = pd.DataFrame(
    list(inferred_links.items()),
    columns=["cell_id", "inferred_fronthaul_link"]
)

print("Inferred fronthaul topology:")
print(topology.sort_values("cell_id"))
