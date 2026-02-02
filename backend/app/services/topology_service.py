# backend/app/services/topology_service.py
"""
Topology inference service.

Handles clustering and topology inference from similarity matrices.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

from app.services.storage import storage, generate_id


class TopologyService:
    """Service for topology inference via clustering."""
    
    def infer_topology(
        self,
        similarity_id: str,
        clustering_method: str = "hierarchical",
        num_clusters: Optional[int] = None,
        distance_threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Infer topology groups from similarity matrix.
        
        Args:
            similarity_id: ID of the similarity matrix
            clustering_method: Method (hierarchical, kmeans, dbscan)
            num_clusters: Number of clusters (auto-detect if None)
            distance_threshold: Distance threshold for clustering
            
        Returns:
            Response with topology_id and detected groups
        """
        # Get similarity matrix
        similarity_data = storage.get_similarity(similarity_id)
        if not similarity_data:
            raise ValueError(f"Similarity matrix not found: {similarity_id}")
        
        matrix = np.array(similarity_data["matrix"])
        cell_ids = similarity_data["cell_ids"]
        
        # Convert similarity to distance
        distance_matrix = 1 - matrix
        np.fill_diagonal(distance_matrix, 0)
        
        # Perform clustering
        if clustering_method == "hierarchical":
            labels = self._hierarchical_clustering(
                distance_matrix, num_clusters, distance_threshold
            )
        elif clustering_method == "kmeans":
            labels = self._kmeans_clustering(distance_matrix, num_clusters or 3)
        elif clustering_method == "dbscan":
            labels = self._dbscan_clustering(distance_matrix, distance_threshold)
        else:
            labels = self._hierarchical_clustering(
                distance_matrix, num_clusters, distance_threshold
            )
        
        # Build groups
        groups = self._build_groups(cell_ids, labels, matrix)
        
        # Build cell assignments
        cell_assignments = self._build_assignments(cell_ids, labels, groups)
        
        # Find unassigned cells (noise in DBSCAN or low confidence)
        unassigned = [
            cell_ids[i] for i, label in enumerate(labels) 
            if label == -1
        ]
        
        # Generate topology ID and store
        topology_id = generate_id("topo")
        
        storage.store_topology(topology_id, {
            "topology_id": topology_id,
            "similarity_id": similarity_id,
            "clustering_method": clustering_method,
            "total_cells": len(cell_ids),
            "detected_groups": len([g for g in groups if g["cell_count"] > 0]),
            "groups": groups,
            "cell_assignments": cell_assignments,
            "unassigned_cells": unassigned,
        })
        
        return {
            "topology_id": topology_id,
            "status": "completed",
            "detected_groups": len([g for g in groups if g["cell_count"] > 0]),
            "result_url": f"/topology/result/{topology_id}",
        }
    
    def get_topology(self, topology_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve topology result."""
        return storage.get_topology(topology_id)
    
    def _hierarchical_clustering(
        self,
        distance_matrix: np.ndarray,
        num_clusters: Optional[int],
        threshold: float,
    ) -> np.ndarray:
        """Perform hierarchical clustering."""
        # Convert to condensed form
        condensed = squareform(distance_matrix, checks=False)
        
        # Linkage
        Z = linkage(condensed, method="average")
        
        # Cluster
        if num_clusters:
            labels = fcluster(Z, num_clusters, criterion="maxclust")
        else:
            labels = fcluster(Z, threshold, criterion="distance")
        
        return labels - 1  # Convert to 0-indexed
    
    def _kmeans_clustering(
        self,
        distance_matrix: np.ndarray,
        num_clusters: int,
    ) -> np.ndarray:
        """Perform K-means clustering."""
        from sklearn.cluster import KMeans
        
        # Use distance matrix as features
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(distance_matrix)
        return labels
    
    def _dbscan_clustering(
        self,
        distance_matrix: np.ndarray,
        eps: float,
    ) -> np.ndarray:
        """Perform DBSCAN clustering."""
        from sklearn.cluster import DBSCAN
        
        dbscan = DBSCAN(eps=eps, min_samples=2, metric="precomputed")
        labels = dbscan.fit_predict(distance_matrix)
        return labels
    
    def _build_groups(
        self,
        cell_ids: List[str],
        labels: np.ndarray,
        similarity_matrix: np.ndarray,
    ) -> List[Dict[str, Any]]:
        """Build group objects from clustering labels."""
        unique_labels = sorted(set(labels) - {-1})  # Exclude noise
        groups = []
        
        link_names = ["Link_A", "Link_B", "Link_C", "Link_D", "Link_E"]
        
        for i, label in enumerate(unique_labels):
            indices = np.where(labels == label)[0]
            cells = [cell_ids[idx] for idx in indices]
            
            # Compute average similarity within group
            if len(indices) > 1:
                group_sim = similarity_matrix[np.ix_(indices, indices)]
                avg_sim = (group_sim.sum() - len(indices)) / (len(indices) * (len(indices) - 1))
            else:
                avg_sim = 1.0
            
            groups.append({
                "group_id": f"Group_{i + 1}",
                "group_name": link_names[i % len(link_names)],
                "cells": cells,
                "avg_similarity": round(float(avg_sim), 3),
                "cell_count": len(cells),
            })
        
        return groups
    
    def _build_assignments(
        self,
        cell_ids: List[str],
        labels: np.ndarray,
        groups: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build cell assignment objects."""
        assignments = []
        
        for i, (cell_id, label) in enumerate(zip(cell_ids, labels)):
            if label == -1:
                continue
            
            group = groups[label] if label < len(groups) else None
            confidence = group["avg_similarity"] if group else 0.5
            
            assignments.append({
                "cell_id": cell_id,
                "group_id": f"Group_{label + 1}",
                "confidence": round(confidence + np.random.uniform(-0.05, 0.05), 2),
            })
        
        return assignments


# Global service instance
topology_service = TopologyService()
