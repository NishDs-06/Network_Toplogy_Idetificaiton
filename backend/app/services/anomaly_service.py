# backend/app/services/anomaly_service.py
"""
Anomaly detection service.

Handles detection of anomalous cells based on their fit within groups.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

from app.services.storage import storage, generate_id


class AnomalyService:
    """Service for anomaly detection."""
    
    def detect_anomalies(
        self,
        topology_id: str,
        similarity_id: str,
        threshold: float = 0.5,
        method: str = "isolation_forest",
    ) -> Dict[str, Any]:
        """
        Detect anomalous cells based on group membership confidence.
        
        Args:
            topology_id: ID of topology result
            similarity_id: ID of similarity matrix
            threshold: Confidence threshold (below = anomaly)
            method: Detection method
            
        Returns:
            Response with analysis_id and anomaly count
        """
        # Get data
        topology = storage.get_topology(topology_id)
        similarity = storage.get_similarity(similarity_id)
        
        if not topology:
            raise ValueError(f"Topology not found: {topology_id}")
        if not similarity:
            raise ValueError(f"Similarity matrix not found: {similarity_id}")
        
        matrix = np.array(similarity["matrix"])
        cell_ids = similarity["cell_ids"]
        groups = topology["groups"]
        
        # Compute confidence scores for each cell
        anomalies = []
        normal_cells = []
        all_scores = []
        
        for group in groups:
            group_cells = group["cells"]
            group_indices = [cell_ids.index(c) for c in group_cells if c in cell_ids]
            
            for cell in group_cells:
                if cell not in cell_ids:
                    continue
                    
                cell_idx = cell_ids.index(cell)
                
                # Compute confidence as average similarity to group members
                if len(group_indices) > 1:
                    other_indices = [i for i in group_indices if i != cell_idx]
                    similarities = [matrix[cell_idx][i] for i in other_indices]
                    confidence = float(np.mean(similarities))
                else:
                    confidence = 1.0
                
                all_scores.append(confidence)
                
                # Determine if anomaly
                is_anomaly = confidence < threshold
                
                cell_result = {
                    "cell_id": cell,
                    "group_id": group["group_id"],
                    "confidence_score": round(confidence, 3),
                    "is_anomaly": is_anomaly,
                    "anomaly_type": "low_correlation" if is_anomaly else None,
                    "severity": self._get_severity(confidence, threshold),
                    "deviation_percentage": round((1 - confidence) * 100, 1) if is_anomaly else None,
                    "explanation": self._get_explanation(confidence, is_anomaly),
                }
                
                if is_anomaly:
                    anomalies.append(cell_result)
                else:
                    normal_cells.append(cell_result)
        
        # Compute statistics
        statistics = {
            "avg_confidence": round(float(np.mean(all_scores)), 3) if all_scores else 0,
            "min_confidence": round(float(np.min(all_scores)), 3) if all_scores else 0,
            "max_confidence": round(float(np.max(all_scores)), 3) if all_scores else 0,
        }
        
        # Store result
        analysis_id = generate_id("anom")
        
        storage.store_anomaly(analysis_id, {
            "analysis_id": analysis_id,
            "topology_id": topology_id,
            "similarity_id": similarity_id,
            "method": method,
            "threshold": threshold,
            "total_cells_analyzed": len(all_scores),
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "normal_cells": normal_cells,
            "statistics": statistics,
        })
        
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "anomalies_detected": len(anomalies),
            "result_url": f"/intelligence/anomalies/{analysis_id}",
        }
    
    def get_anomaly(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve anomaly analysis result."""
        return storage.get_anomaly(analysis_id)
    
    def _get_severity(self, confidence: float, threshold: float) -> str:
        """Determine severity based on confidence score."""
        if confidence >= threshold:
            return "none"
        elif confidence >= threshold * 0.7:
            return "low"
        elif confidence >= threshold * 0.5:
            return "medium"
        else:
            return "high"
    
    def _get_explanation(self, confidence: float, is_anomaly: bool) -> str:
        """Generate explanation for the cell status."""
        if not is_anomaly:
            return "Cell behavior aligns well with its assigned group"
        elif confidence < 0.3:
            return "Cell shows significantly lower correlation with group peers"
        elif confidence < 0.5:
            return "Cell exhibits notable deviation from expected group behavior"
        else:
            return "Cell shows minor inconsistency with group pattern"


# Global service instance
anomaly_service = AnomalyService()
