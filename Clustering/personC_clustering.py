import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform


def infer_topology(similarity_matrix: pd.DataFrame):
    """
    Contract #3: Relative Topology Identification (Round 1)

    Input:
        similarity_matrix (pd.DataFrame): symmetric similarity matrix
    Output:
        topology_result (dict): cell_id -> group_name
        link_groups (dict): group_name -> list[cell_id]
    """

    # ---- Sanity checks ----
    assert similarity_matrix.shape[0] == similarity_matrix.shape[1], "Matrix must be square"
    assert (similarity_matrix.index == similarity_matrix.columns).all(), "Index/columns mismatch"

    # ---- Similarity → Distance ----
    distance_matrix = 1.0 - similarity_matrix
    condensed_distance = squareform(distance_matrix.values, checks=False)

    # ---- Hierarchical clustering ----
    linkage_matrix = linkage(condensed_distance, method="average")

    # Round-1 constraint: infer relative grouping only
    cluster_labels = fcluster(linkage_matrix, t=2, criterion="maxclust")

    topology_result = {}
    link_groups = {}

    for cell_id, cluster_id in zip(similarity_matrix.index, cluster_labels):
        group_name = f"Group_{cluster_id}"
        topology_result[cell_id] = group_name
        link_groups.setdefault(group_name, []).append(cell_id)

    return topology_result, link_groups


if __name__ == "__main__":

    # ------------------------------------------------------------------
    # INPUT: Similarity matrix from Person B
    # ------------------------------------------------------------------
    similarity_matrix = pd.DataFrame(
        [
            [1.000000, 0.409153, 0.446456],
            [0.409153, 1.000000, 0.436335],
            [0.446456, 0.436335, 1.000000],
        ],
        index=["cell_01", "cell_02", "cell_03"],
        columns=["cell_01", "cell_02", "cell_03"],
    )

    topology_result, link_groups = infer_topology(similarity_matrix)

    # ------------------------------------------------------------------
    # HUMAN-READABLE OUTPUT (Round-1 Visualization)
    # ------------------------------------------------------------------
    print("\nRelative Fronthaul Topology (Round-1)\n")

    for group, cells in link_groups.items():
        if len(cells) > 1:
            print("        ┌──────────┐")
            print(f"        │ {cells[0]} │")
            print("        └────┬─────┘")
            print("             │")
            print("     Shared Fronthaul Link")
            print("             │")
            print("        ┌────┴─────┐")
            print(f"        │ {cells[1]} │")
            print("        └──────────┘\n")
        else:
            print("        ┌──────────┐")
            print(f"        │ {cells[0]} │")
            print("        └──────────┘")
            print("   (Less correlated / independent)\n")

    # ------------------------------------------------------------------
    # EXPORT FOR ML + BACKEND (CRITICAL)
    # ------------------------------------------------------------------
    rows = []
    for cell, group in topology_result.items():
        cell_num = int(cell.split("_")[1])     # cell_01 → 1
        group_num = int(group.split("_")[1])   # Group_1 → 1
        rows.append({"cell_id": cell_num, "group_id": group_num})

    groups_df = pd.DataFrame(rows).sort_values("cell_id")
    groups_df.to_csv("groups.csv", index=False)

    print("[OK] groups.csv exported")
    print(groups_df)
