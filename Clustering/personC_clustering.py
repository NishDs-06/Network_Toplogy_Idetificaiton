import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform


def infer_topology(similarity_matrix: pd.DataFrame):
    """
    Contract #3: Relative Topology Identification (Round 1)

    Input:
        similarity_matrix (pd.DataFrame)
    Output:
        topology_result (dict)
        link_groups (dict)
    """

    # Sanity checks
    assert similarity_matrix.shape[0] == similarity_matrix.shape[1]
    assert (similarity_matrix.index == similarity_matrix.columns).all()

    # Convert similarity → distance
    distance_matrix = 1 - similarity_matrix
    condensed_distance = squareform(distance_matrix.values, checks=False)

    # Hierarchical clustering
    linkage_matrix = linkage(condensed_distance, method="average")

    # For Round-1: do NOT overclaim exact number of links
    # We cut at 2 clusters to infer relative grouping
    cluster_labels = fcluster(linkage_matrix, t=2, criterion="maxclust")

    topology_result = {}
    link_groups = {}

    for cell_id, cluster_id in zip(similarity_matrix.index, cluster_labels):
        group_name = f"Group_{cluster_id}"
        topology_result[cell_id] = group_name
        link_groups.setdefault(group_name, []).append(cell_id)

    return topology_result, link_groups


if __name__ == "__main__":

    # Similarity matrix provided by Person B
    similarity_matrix = pd.DataFrame(
        [
            [1.0, 0.409153, 0.446456],
            [0.409153, 1.0, 0.436335],
            [0.446456, 0.436335, 1.0]
        ],
        index=["cell_01", "cell_02", "cell_03"],
        columns=["cell_01", "cell_02", "cell_03"]
    )

    topology_result, link_groups = infer_topology(similarity_matrix)

    # ----- FINAL ROUND-1 OUTPUT -----

    print("\nRelative Fronthaul Topology (Illustrative)\n")

    shared_groups = []
    independent_cells = []

    for group, cells in link_groups.items():
        if len(cells) > 1:
            shared_groups.append(cells)
        else:
            independent_cells.extend(cells)

    for group in shared_groups:
        print("        ┌──────────┐")
        print(f"        │ {group[0]} │")
        print("        └────┬─────┘")
        print("             │")
        print("     Shared Fronthaul Link")
        print("             │")
        print("        ┌────┴─────┐")
        print(f"        │ {group[1]} │")
        print("        └──────────┘\n")

    for cell in independent_cells:
        print("        ┌──────────┐")
        print(f"        │ {cell} │")
        print("        └──────────┘")
        print("   (Less correlated / independent)\n")

