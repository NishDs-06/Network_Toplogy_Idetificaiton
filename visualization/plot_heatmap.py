# visualization/plot_heatmap.py
"""
Heatmap Visualization Module

Generates similarity heatmaps from network cell data.
Supports both PNG file output and JSON data return for API usage.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any, List

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server usage
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default paths
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_SIMILARITY_PATH = PROJECT_ROOT / "Clustering" / "outputs" / "similarity_matrix.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"


def load_similarity_matrix(
    path: Optional[str] = None
) -> tuple[pd.DataFrame, List[str]]:
    """
    Load similarity matrix from CSV file.
    
    Args:
        path: Path to similarity matrix CSV. 
              Defaults to Clustering/outputs/similarity_matrix.csv
              
    Returns:
        Tuple of (similarity_matrix DataFrame, list of cell_ids)
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If the matrix is not valid (not square, etc.)
    """
    csv_path = Path(path) if path else DEFAULT_SIMILARITY_PATH
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Similarity matrix not found at: {csv_path}")
    
    logger.info(f"Loading similarity matrix from: {csv_path}")
    
    # Load with first column as index
    df = pd.read_csv(csv_path, index_col=0)
    
    # Normalize index and columns
    df.index = df.index.astype(str).str.strip()
    df.columns = df.columns.astype(str).str.strip()
    
    # Validate square matrix
    if df.shape[0] != df.shape[1]:
        raise ValueError(f"Matrix must be square, got shape {df.shape}")
    
    # Ensure symmetric alignment
    df = df.loc[df.index, df.index]
    
    cell_ids = [f"cell_{int(c):02d}" for c in df.index]
    
    logger.info(f"Loaded {len(cell_ids)}x{len(cell_ids)} similarity matrix")
    
    return df, cell_ids


def generate_heatmap(
    data_path: Optional[str] = None,
    similarity_matrix: Optional[pd.DataFrame] = None,
    output_path: Optional[str] = None,
    return_data: bool = False,
    title: str = "Cell Congestion Similarity Matrix",
    cmap: str = "viridis",
    figsize: tuple = (12, 10),
    dpi: int = 300,
    annotate: bool = True
) -> Union[str, Dict[str, Any]]:
    """
    Generate congestion heatmap visualization.
    
    Args:
        data_path: Path to CSV file with similarity matrix
        similarity_matrix: Pre-loaded DataFrame (alternative to data_path)
        output_path: Path to save PNG image. If None, saves to outputs/
        return_data: If True, return JSON-serializable dict instead of image path
        title: Chart title
        cmap: Matplotlib colormap name
        figsize: Figure dimensions (width, height)
        dpi: Output resolution
        annotate: Show values in cells (only for small matrices)
        
    Returns:
        If return_data=False: Path to saved image
        If return_data=True: Dict with matrix data and metadata
        
    Example:
        >>> path = generate_heatmap()  # Save PNG
        >>> data = generate_heatmap(return_data=True)  # Get JSON
    """
    # Load data
    if similarity_matrix is not None:
        df = similarity_matrix
        cell_ids = [f"cell_{int(c):02d}" for c in df.index]
    else:
        df, cell_ids = load_similarity_matrix(data_path)
    
    # Return JSON data if requested
    if return_data:
        matrix = df.values.tolist()
        
        # Round for readability
        matrix = [[round(v, 4) for v in row] for row in matrix]
        
        return {
            "matrix": matrix,
            "cellIds": cell_ids,
            "size": len(cell_ids),
            "metadata": {
                "min_value": float(df.values.min()),
                "max_value": float(df.values.max()),
                "mean_value": float(df.values.mean()),
            }
        }
    
    # Generate PNG visualization
    fig, ax = plt.subplots(figsize=figsize)
    
    # Determine whether to annotate (only for smaller matrices)
    show_annot = annotate and len(cell_ids) <= 15
    
    sns.heatmap(
        df,
        ax=ax,
        cmap=cmap,
        annot=show_annot,
        fmt=".2f" if show_annot else None,
        linewidths=0.5,
        cbar_kws={"label": "Similarity Score"},
        vmin=0,
        vmax=1,
        square=True,
        xticklabels=cell_ids,
        yticklabels=cell_ids,
    )
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Cells", fontsize=11)
    ax.set_ylabel("Cells", fontsize=11)
    
    # Rotate labels for readability
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    
    plt.tight_layout()
    
    # Determine output path
    if output_path is None:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = str(DEFAULT_OUTPUT_DIR / "similarity_heatmap.png")
    else:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    
    logger.info(f"✅ Heatmap saved to: {output_path}")
    
    return output_path


def generate_heatmap_for_api(
    data_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate heatmap data in frontend-compatible format.
    
    This is a convenience wrapper that formats output for the 
    /api/similarity-matrix endpoint.
    
    Args:
        data_path: Path to similarity matrix CSV
        
    Returns:
        Dict matching frontend SimilarityMatrix interface:
        {
            "matrix": [[float, ...], ...],
            "cellIds": ["cell_01", ...],
            "timestamp": "ISO8601 string"
        }
    """
    from datetime import datetime, timezone
    
    data = generate_heatmap(data_path=data_path, return_data=True)
    
    return {
        "matrix": data["matrix"],
        "cellIds": data["cellIds"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate similarity heatmap")
    parser.add_argument(
        "--input", "-i",
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
    
    args = parser.parse_args()
    
    if args.json:
        data = generate_heatmap(data_path=args.input, return_data=True)
        print(json.dumps(data, indent=2))
    else:
        path = generate_heatmap(data_path=args.input, output_path=args.output)
        print(f"Saved to: {path}")
