# backend/app/services/similarity_service.py
"""
Similarity computation service.

Handles computation of similarity matrices using various methods.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.services.storage import storage, generate_id


class SimilarityService:
    """Service for computing similarity matrices."""
    
    def compute_similarity(
        self,
        upload_id: str,
        method: str = "correlation",
        window_size: int = 100,
        cell_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compute similarity matrix from uploaded data.
        
        Args:
            upload_id: ID of the uploaded data
            method: Similarity method (correlation, dtw, mutual_info)
            window_size: Window size for analysis
            cell_ids: Specific cells to analyze (defaults to all)
            
        Returns:
            Response with similarity_matrix_id and status
        """
        import time
        start_time = time.time()
        
        # Get upload data
        upload = storage.get_upload(upload_id)
        if not upload:
            raise ValueError(f"Upload not found: {upload_id}")
        
        # Convert to DataFrame
        df = pd.DataFrame(upload["data"])
        
        # Filter cells if specified
        if cell_ids:
            df = df[df["cell_id"].isin([int(c) for c in cell_ids])]
        
        # Get unique cells
        unique_cells = sorted(df["cell_id"].unique().tolist())
        cell_id_strs = [str(c) for c in unique_cells]
        
        # Create congestion vectors (pivot table)
        if upload["data_type"] == "loss_events":
            pivot = df.pivot_table(
                index="slot_id",
                columns="cell_id",
                values="loss_event",
                fill_value=0,
            )
        else:
            pivot = df.pivot_table(
                index="slot_id",
                columns="cell_id",
                values="throughput_slot",
                fill_value=0,
            )
        
        # Compute similarity matrix based on method
        if method == "correlation":
            similarity_matrix = self._compute_correlation(pivot)
        elif method == "dtw":
            similarity_matrix = self._compute_dtw(pivot)
        elif method == "mutual_info":
            similarity_matrix = self._compute_mutual_info(pivot)
        else:
            similarity_matrix = self._compute_correlation(pivot)
        
        # Generate ID and store
        similarity_id = generate_id("sim")
        computation_time = time.time() - start_time
        
        storage.store_similarity(similarity_id, {
            "similarity_id": similarity_id,
            "upload_id": upload_id,
            "matrix": similarity_matrix.tolist(),
            "cell_ids": cell_id_strs,
            "method": method,
            "window_size": window_size,
            "computation_time_sec": round(computation_time, 2),
        })
        
        return {
            "job_id": f"job_{similarity_id}",
            "status": "completed",
            "similarity_matrix_id": similarity_id,
            "computation_time_sec": round(computation_time, 2),
            "result_url": f"/topology/similarity/{similarity_id}",
        }
    
    def get_similarity(self, similarity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve similarity matrix."""
        result = storage.get_similarity(similarity_id)
        if result:
            result["download_url"] = f"/topology/similarity/{similarity_id}/download"
        return result
    
    def _compute_correlation(self, pivot: pd.DataFrame) -> np.ndarray:
        """Compute Pearson correlation matrix."""
        # Fill NaN with 0 for correlation computation
        corr_matrix = pivot.corr().fillna(0).values.copy()  # Copy to make writable
        # Ensure diagonal is 1 and values are in [0, 1] range for similarity
        np.fill_diagonal(corr_matrix, 1.0)
        # Convert to similarity (handle negative correlations)
        similarity = (corr_matrix + 1) / 2  # Scale from [-1,1] to [0,1]
        return np.round(similarity, 4)
    
    def _compute_dtw(self, pivot: pd.DataFrame) -> np.ndarray:
        """
        Compute DTW-based similarity matrix.
        Simplified implementation using correlation as fallback.
        """
        # For simplicity, use correlation-based approach
        # Full DTW would require scipy or dtw-python
        return self._compute_correlation(pivot)
    
    def _compute_mutual_info(self, pivot: pd.DataFrame) -> np.ndarray:
        """
        Compute mutual information-based similarity.
        Simplified implementation.
        """
        # Use correlation as base, could be enhanced with sklearn
        return self._compute_correlation(pivot)


# Global service instance
similarity_service = SimilarityService()
