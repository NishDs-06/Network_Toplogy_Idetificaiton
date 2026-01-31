import numpy as np
import pandas as pd

# Fake similarity matrix
cells = ["cell_01", "cell_02", "cell_03", "cell_04", "cell_05", "cell_06"]
data = np.random.rand(6,6)
similarity_matrix = pd.DataFrame(data, index=cells, columns=cells)

# Make diagonal 1 and symmetric
for i in range(6):
    similarity_matrix.iloc[i,i] = 1
similarity_matrix = (similarity_matrix + similarity_matrix.T)/2

# Fake topology mapping
topology_result = {
    "cell_01": "Link_1",
    "cell_02": "Link_1",
    "cell_03": "Link_2",
    "cell_04": "Link_2",
    "cell_05": "Link_3",
    "cell_06": "Link_3"
}
