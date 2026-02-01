# visualization/plot_topology_graph.py
"""
Topology Graph Visualization Module

Generates network topology graphs from clustering data.
Supports both PNG file output and JSON data return for API usage.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any, List

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server usage
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default paths
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_GROUPS_PATH = PROJECT_ROOT / "Clustering" / "outputs" / "relative_fronthaul_groups.csv"
DEFAULT_SIMILARITY_PATH = PROJECT_ROOT / "Clustering" / "outputs" / "similarity_matrix.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Extended color palette for many groups
COLOR_PALETTE = [
    "#d4a574",  # tan/brown
    "#7aa874",  # sage green
    "#7488a8",  # steel blue
    "#a87488",  # mauve
    "#8b74a8",  # purple
    "#a89674",  # olive
    "#74a8a8",  # teal
    "#a87474",  # dusty rose
    "#88a874",  # lime green
    "#7498a8",  # sky blue
    "#a88874",  # terracotta
    "#9474a8",  # violet
    "#74a888",  # mint
    "#a87498",  # pink
    "#a8a874",  # yellow-green
    "#7474a8",  # periwinkle
]

# CSS-friendly color names for fallback
CSS_COLORS = {
    "red": "#e74c3c",
    "blue": "#3498db",
    "green": "#2ecc71",
    "orange": "#e67e22",
    "purple": "#9b59b6",
    "brown": "#795548",
    "pink": "#e91e63",
    "gray": "#95a5a6",
    "olive": "#8bc34a",
    "cyan": "#00bcd4",
}


def load_clustering_data(
    groups_path: Optional[str] = None
) -> tuple[pd.DataFrame, Dict[int, List[str]], Dict[int, str]]:
    """
    Load clustering/topology data from CSV.
    
    Args:
        groups_path: Path to groups CSV file.
                     Defaults to Clustering/outputs/relative_fronthaul_groups.csv
                     
    Returns:
        Tuple of:
        - DataFrame with cell_id, relative_group, group_color columns
        - Dict mapping group_id -> list of cell_ids
        - Dict mapping group_id -> hex color
        
    Raises:
        FileNotFoundError: If specified file doesn't exist
    """
    csv_path = Path(groups_path) if groups_path else DEFAULT_GROUPS_PATH
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Groups file not found at: {csv_path}")
    
    logger.info(f"Loading clustering data from: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Normalize cell_id format
    if df["cell_id"].dtype in [int, np.int64]:
        df["cell_id"] = df["cell_id"].apply(lambda x: f"cell_{int(x):02d}")
    else:
        df["cell_id"] = df["cell_id"].astype(str).str.strip()
    
    # Build group -> cells mapping
    grouped_cells = {}
    for _, row in df.iterrows():
        grp = int(row["relative_group"])
        cell = row["cell_id"]
        grouped_cells.setdefault(grp, []).append(cell)
    
    # Build group -> color mapping
    group_colors = {}
    for i, grp in enumerate(sorted(grouped_cells.keys())):
        if "group_color" in df.columns:
            # Use color from CSV if available
            color_name = df[df["relative_group"] == grp]["group_color"].iloc[0]
            group_colors[grp] = CSS_COLORS.get(color_name, COLOR_PALETTE[i % len(COLOR_PALETTE)])
        else:
            group_colors[grp] = COLOR_PALETTE[i % len(COLOR_PALETTE)]
    
    logger.info(f"Loaded {len(df)} cells in {len(grouped_cells)} groups")
    
    return df, grouped_cells, group_colors


def build_topology_graph(
    grouped_cells: Dict[int, List[str]],
    group_colors: Dict[int, str],
    similarity_matrix: Optional[pd.DataFrame] = None
) -> nx.Graph:
    """
    Build NetworkX graph from clustering data.
    
    Args:
        grouped_cells: Dict mapping group_id -> list of cell_ids
        group_colors: Dict mapping group_id -> hex color
        similarity_matrix: Optional similarity matrix for edge weights
        
    Returns:
        NetworkX Graph with node attributes (group, color) and edges
    """
    G = nx.Graph()
    
    # Add nodes with attributes
    for grp, cells in grouped_cells.items():
        for cell in cells:
            G.add_node(cell, group=grp, color=group_colors[grp])
    
    # Add edges within same group
    for grp, cells in grouped_cells.items():
        for i in range(len(cells)):
            for j in range(i + 1, len(cells)):
                weight = 1.0
                if similarity_matrix is not None:
                    try:
                        # Extract numeric ID for lookup
                        c1 = cells[i].replace("cell_", "").lstrip("0") or "0"
                        c2 = cells[j].replace("cell_", "").lstrip("0") or "0"
                        weight = similarity_matrix.loc[c1, c2]
                    except (KeyError, IndexError):
                        pass
                G.add_edge(cells[i], cells[j], weight=weight, group=grp)
    
    return G


def generate_topology_graph(
    groups_path: Optional[str] = None,
    similarity_path: Optional[str] = None,
    output_path: Optional[str] = None,
    return_json: bool = False,
    title: str = "Inferred Fronthaul Topology",
    figsize: tuple = (14, 10),
    dpi: int = 300,
    layout: str = "spring",
    seed: int = 42
) -> Union[str, Dict[str, Any]]:
    """
    Generate network topology graph visualization.
    
    Args:
        groups_path: Path to clustering output CSV
        similarity_path: Path to similarity matrix (for edge weights)
        output_path: Path to save PNG image
        return_json: If True, return JSON-serializable graph data
        title: Chart title
        figsize: Figure dimensions
        dpi: Output resolution
        layout: Graph layout algorithm ('spring', 'kamada_kawai', 'circular')
        seed: Random seed for reproducible layouts
        
    Returns:
        If return_json=False: Path to saved image
        If return_json=True: Dict with graph data (nodes, edges, positions)
    """
    # Load data
    df, grouped_cells, group_colors = load_clustering_data(groups_path)
    
    # Optionally load similarity matrix
    similarity_matrix = None
    sim_path = Path(similarity_path) if similarity_path else DEFAULT_SIMILARITY_PATH
    if sim_path.exists():
        similarity_matrix = pd.read_csv(sim_path, index_col=0)
        similarity_matrix.index = similarity_matrix.index.astype(str).str.strip()
        similarity_matrix.columns = similarity_matrix.columns.astype(str).str.strip()
    
    # Build graph
    G = build_topology_graph(grouped_cells, group_colors, similarity_matrix)
    
    # Calculate layout
    if layout == "spring":
        pos = nx.spring_layout(G, seed=seed, k=2, iterations=50)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    else:
        pos = nx.spring_layout(G, seed=seed)
    
    # Return JSON data if requested
    if return_json:
        nodes = []
        for node in G.nodes():
            nodes.append({
                "id": node,
                "group": G.nodes[node]["group"],
                "color": G.nodes[node]["color"],
                "x": float(pos[node][0]),
                "y": float(pos[node][1])
            })
        
        edges = []
        for u, v, data in G.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "weight": float(data.get("weight", 1.0)),
                "group": data.get("group")
            })
        
        groups = []
        for grp in sorted(grouped_cells.keys()):
            groups.append({
                "id": f"link_{grp}",
                "name": f"Link {grp}",
                "color": group_colors[grp],
                "cells": grouped_cells[grp]
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
            "totalNodes": len(nodes),
            "totalGroups": len(groups)
        }
    
    # Generate PNG visualization
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get node colors
    node_colors = [G.nodes[n]["color"] for n in G.nodes()]
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        ax=ax,
        alpha=0.4,
        width=1.5,
        edge_color="#cccccc"
    )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        ax=ax,
        node_color=node_colors,
        node_size=800,
        alpha=0.9,
        edgecolors='white',
        linewidths=2
    )
    
    # Draw labels
    nx.draw_networkx_labels(
        G, pos,
        ax=ax,
        font_size=8,
        font_weight='bold',
        font_color='white'
    )
    
    # Create legend
    legend_handles = []
    for grp in sorted(grouped_cells.keys()):
        patch = mpatches.Patch(
            color=group_colors[grp],
            label=f"Link {grp} ({len(grouped_cells[grp])} cells)"
        )
        legend_handles.append(patch)
    
    ax.legend(
        handles=legend_handles,
        loc='upper left',
        title="Inferred Links",
        fontsize=9
    )
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    # Determine output path
    if output_path is None:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = str(DEFAULT_OUTPUT_DIR / "topology_graph.png")
    else:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    
    logger.info(f"✅ Topology graph saved to: {output_path}")
    
    return output_path


def generate_topology_for_api(
    groups_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate topology data in frontend-compatible format.
    
    This is a convenience wrapper that formats output for the 
    /api/topology-groups endpoint.
    
    Args:
        groups_path: Path to clustering output CSV
        
    Returns:
        Dict matching frontend TopologyGroup[] interface:
        {
            "groups": [
                {"id": "link_1", "name": "Link 1", "color": "#hex", "cells": [...]}
            ]
        }
    """
    data = generate_topology_graph(groups_path=groups_path, return_json=True)
    
    return {
        "groups": data["groups"]
    }


def generate_cells_for_api(
    groups_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate cell data in frontend-compatible format.
    
    This is a convenience wrapper for the /api/cells endpoint.
    Integrates anomaly detection results with confidence scores.
    
    Args:
        groups_path: Path to clustering output CSV
        
    Returns:
        Dict matching frontend CellData[] interface:
        {
            "cells": [
                {"id": "cell_01", "name": "CELL 01", "group": "link_1", 
                 "isAnomaly": false, "anomalyScore": null, "confidence": 0.0}
            ]
        }
    """
    df, grouped_cells, _ = load_clustering_data(groups_path)
    
    # Load anomaly data with confidence
    anomaly_path = PROJECT_ROOT / "ML" / "outputs" / "cell_anomalies.csv"
    anomaly_data = {}
    
    if anomaly_path.exists():
        try:
            anomaly_df = pd.read_csv(anomaly_path)
            # FIX: Use mean() to get anomaly RATE instead of max()
            # This gives the proportion of slots that are anomalous
            cell_anomalies = anomaly_df.groupby("cell_id").agg({
                "anomaly": "mean",     # Rate of anomalous slots (0.0 to 1.0)
                "confidence": "mean"   # Average confidence across slots
            }).reset_index()
            
            ANOMALY_RATE_THRESHOLD = 0.25  # Only flag if >25% of slots are anomalous
            
            for _, row in cell_anomalies.iterrows():
                cell_id = int(row["cell_id"])
                anomaly_rate = float(row["anomaly"])
                avg_confidence = float(row["confidence"])
                
                anomaly_data[cell_id] = {
                    "is_anomaly": anomaly_rate > ANOMALY_RATE_THRESHOLD,
                    "confidence": round(anomaly_rate, 3)  # Use rate as confidence
                }
            logger.info(f"Loaded anomaly data for {len(anomaly_data)} cells, " 
                       f"{sum(1 for v in anomaly_data.values() if v['is_anomaly'])} flagged as anomalies")
        except Exception as e:
            logger.warning(f"Failed to load anomaly data: {e}")
    
    cells = []
    for _, row in df.iterrows():
        cell_id = row["cell_id"]  # Format: "cell_XX"
        group_id = int(row["relative_group"])
        
        # Extract cell number for display name and anomaly lookup
        cell_num_str = cell_id.replace("cell_", "")
        cell_num = int(cell_num_str) if cell_num_str.isdigit() else 0
        
        # Get anomaly info
        anomaly_info = anomaly_data.get(cell_num, {"is_anomaly": False, "confidence": 0.0})
        
        cells.append({
            "id": cell_id,
            "name": f"CELL {cell_num_str}",
            "group": f"link_{group_id}",
            "isAnomaly": anomaly_info["is_anomaly"],
            "anomalyScore": anomaly_info["confidence"] if anomaly_info["is_anomaly"] else None,
            "confidence": round(anomaly_info["confidence"], 3)
        })
    
    return {"cells": cells}


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate topology graph")
    parser.add_argument(
        "--groups", "-g",
        type=str,
        default=None,
        help="Path to groups CSV"
    )
    parser.add_argument(
        "--similarity", "-s",
        type=str,
        default=None,
        help="Path to similarity matrix CSV"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output PNG path"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON data instead of PNG"
    )
    parser.add_argument(
        "--layout",
        type=str,
        default="spring",
        choices=["spring", "kamada_kawai", "circular"],
        help="Graph layout algorithm"
    )
    
    args = parser.parse_args()
    
    if args.json:
        data = generate_topology_graph(
            groups_path=args.groups,
            similarity_path=args.similarity,
            return_json=True
        )
        print(json.dumps(data, indent=2))
    else:
        path = generate_topology_graph(
            groups_path=args.groups,
            similarity_path=args.similarity,
            output_path=args.output,
            layout=args.layout
        )
        print(f"Saved to: {path}")
