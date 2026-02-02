# backend/app/services/visualization_service.py
"""
Visualization generation service.

Handles creation of heatmaps, topology graphs, and flow diagrams.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import numpy as np

from app.services.storage import storage, generate_id


class VisualizationService:
    """Service for generating visualizations."""
    
    def __init__(self):
        # Create output directory
        self.output_dir = "/tmp/visualizations"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_heatmap(
        self,
        similarity_id: str,
        format: str = "png",
        dpi: int = 300,
        color_scheme: str = "viridis",
    ) -> Dict[str, Any]:
        """
        Generate similarity heatmap.
        
        Args:
            similarity_id: ID of similarity matrix
            format: Output format (png, svg, pdf)
            dpi: Resolution
            color_scheme: Color scheme
            
        Returns:
            Response with visualization_id and download URL
        """
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Get similarity matrix
        similarity = storage.get_similarity(similarity_id)
        if not similarity:
            raise ValueError(f"Similarity matrix not found: {similarity_id}")
        
        matrix = np.array(similarity["matrix"])
        cell_ids = similarity["cell_ids"]
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        
        sns.heatmap(
            matrix,
            xticklabels=cell_ids,
            yticklabels=cell_ids,
            cmap=color_scheme,
            annot=False,
            ax=ax,
            vmin=0,
            vmax=1,
            square=True,
        )
        
        ax.set_title(f"Cell Similarity Matrix\nMethod: {similarity.get('method', 'correlation')}")
        ax.set_xlabel("Cell ID")
        ax.set_ylabel("Cell ID")
        
        plt.tight_layout()
        
        # Save
        viz_id = generate_id("viz_heat")
        filename = f"{viz_id}.{format}"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.savefig(filepath, dpi=dpi, format=format)
        plt.close()
        
        # Store metadata
        storage.store_visualization(viz_id, {
            "visualization_id": viz_id,
            "type": "heatmap",
            "similarity_id": similarity_id,
            "format": format,
            "filepath": filepath,
        })
        
        return {
            "visualization_id": viz_id,
            "type": "heatmap",
            "download_url": f"/visualizations/download/{viz_id}.{format}",
            "thumbnail_url": None,
            "animation_url": None,
        }
    
    def generate_topology_graph(
        self,
        topology_id: str,
        format: str = "png",
        layout: str = "spring",
        show_labels: bool = True,
        dpi: int = 300,
    ) -> Dict[str, Any]:
        """
        Generate topology graph visualization.
        
        Args:
            topology_id: ID of topology result
            format: Output format
            layout: Graph layout algorithm
            show_labels: Whether to show labels
            dpi: Resolution
            
        Returns:
            Response with visualization_id and download URL
        """
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import networkx as nx
        
        # Get topology
        topology = storage.get_topology(topology_id)
        if not topology:
            raise ValueError(f"Topology not found: {topology_id}")
        
        groups = topology.get("groups", [])
        
        # Build graph
        G = nx.Graph()
        
        # Add group nodes (hub nodes)
        colors = plt.cm.Set3(np.linspace(0, 1, len(groups) + 1))
        node_colors = []
        
        for i, group in enumerate(groups):
            G.add_node(group["group_id"], node_type="group")
            node_colors.append(colors[i])
            
            # Add cell nodes connected to group
            for cell in group["cells"][:5]:  # Limit cells shown
                G.add_node(f"Cell_{cell}", node_type="cell")
                G.add_edge(group["group_id"], f"Cell_{cell}")
                node_colors.append(colors[i])
        
        # Layout
        if layout == "spring":
            pos = nx.spring_layout(G, k=2, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        # Draw
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Separate group and cell nodes
        group_nodes = [n for n in G.nodes() if G.nodes[n].get("node_type") == "group"]
        cell_nodes = [n for n in G.nodes() if G.nodes[n].get("node_type") == "cell"]
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.5, ax=ax)
        
        # Draw group nodes (larger)
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=group_nodes,
            node_size=2000,
            node_color=[colors[i] for i in range(len(group_nodes))],
            ax=ax,
        )
        
        # Draw cell nodes (smaller)
        cell_colors = []
        for cell in cell_nodes:
            for i, group in enumerate(groups):
                if any(f"Cell_{c}" == cell for c in group["cells"]):
                    cell_colors.append(colors[i])
                    break
            else:
                cell_colors.append("gray")
        
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=cell_nodes,
            node_size=500,
            node_color=cell_colors[:len(cell_nodes)] if cell_colors else "lightblue",
            ax=ax,
        )
        
        if show_labels:
            # Labels for groups
            group_labels = {n: n for n in group_nodes}
            nx.draw_networkx_labels(G, pos, group_labels, font_size=10, font_weight="bold", ax=ax)
            
            # Labels for cells
            cell_labels = {n: n.replace("Cell_", "") for n in cell_nodes}
            nx.draw_networkx_labels(G, pos, cell_labels, font_size=7, ax=ax)
        
        ax.set_title(f"Network Topology\n{len(groups)} Groups, {topology['total_cells']} Cells")
        ax.axis("off")
        
        plt.tight_layout()
        
        # Save
        viz_id = generate_id("viz_topo")
        filename = f"{viz_id}.{format}"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.savefig(filepath, dpi=dpi, format=format)
        plt.close()
        
        # Store metadata
        storage.store_visualization(viz_id, {
            "visualization_id": viz_id,
            "type": "topology_graph",
            "topology_id": topology_id,
            "format": format,
            "filepath": filepath,
        })
        
        return {
            "visualization_id": viz_id,
            "type": "topology_graph",
            "download_url": f"/visualizations/download/{viz_id}.{format}",
            "thumbnail_url": None,
            "animation_url": None,
        }
    
    def generate_propagation_flow(
        self,
        propagation_id: str,
        format: str = "svg",
        animation: bool = True,
        timeline: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate propagation flow diagram.
        
        Args:
            propagation_id: ID of propagation analysis
            format: Output format
            animation: Include animation (SVG only)
            timeline: Show timeline
            
        Returns:
            Response with visualization_id and download URL
        """
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import networkx as nx
        
        # Get propagation data
        propagation = storage.get_propagation(propagation_id)
        if not propagation:
            raise ValueError(f"Propagation not found: {propagation_id}")
        
        graph = propagation.get("network_graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        # Build directed graph
        G = nx.DiGraph()
        
        for node in nodes:
            G.add_node(node["id"], **node)
        
        for edge in edges:
            G.add_edge(edge["source"], edge["target"], **edge)
        
        # Layout
        pos = nx.spring_layout(G, k=3)
        
        # Draw
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Node colors based on congestion level
        node_colors = [n.get("congestion_level", 0.5) for n in nodes]
        
        nx.draw_networkx_nodes(
            G, pos,
            node_size=2000,
            node_color=node_colors,
            cmap=plt.cm.RdYlGn_r,
            vmin=0, vmax=1,
            ax=ax,
        )
        
        # Draw edges with arrows
        edge_weights = [e.get("strength", 1) * 3 for e in edges]
        nx.draw_networkx_edges(
            G, pos,
            width=edge_weights if edge_weights else 1,
            edge_color="gray",
            arrows=True,
            arrowsize=20,
            ax=ax,
        )
        
        # Labels
        labels = {n["id"]: n["id"] for n in nodes}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight="bold", ax=ax)
        
        # Edge labels (delay)
        edge_labels = {(e["source"], e["target"]): f"{e.get('delay_ms', 0):.1f}ms" for e in edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax)
        
        ax.set_title("Congestion Propagation Flow")
        ax.axis("off")
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn_r, norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
        cbar.set_label("Congestion Level")
        
        plt.tight_layout()
        
        # Save
        viz_id = generate_id("viz_flow")
        filename = f"{viz_id}.{format}"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.savefig(filepath, format=format)
        plt.close()
        
        # Store metadata
        storage.store_visualization(viz_id, {
            "visualization_id": viz_id,
            "type": "propagation_flow",
            "propagation_id": propagation_id,
            "format": format,
            "filepath": filepath,
        })
        
        return {
            "visualization_id": viz_id,
            "type": "propagation_flow",
            "download_url": f"/visualizations/download/{viz_id}.{format}",
            "thumbnail_url": None,
            "animation_url": f"/visualizations/animation/{viz_id}" if animation and format == "svg" else None,
        }
    
    def get_visualization(self, viz_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve visualization metadata."""
        return storage.get_visualization(viz_id)


# Global service instance
visualization_service = VisualizationService()
