# backend/app/services/storage.py
"""
In-memory storage for development and demo purposes.

This module provides thread-safe storage for all data entities.
For production, replace with database integration.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


def generate_id(prefix: str) -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@dataclass
class StoredData:
    """Base class for stored data."""
    id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)


class InMemoryStorage:
    """Thread-safe in-memory storage."""
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Data uploads
        self._uploads: Dict[str, Dict[str, Any]] = {}
        
        # Similarity matrices
        self._similarities: Dict[str, Dict[str, Any]] = {}
        
        # Topology results
        self._topologies: Dict[str, Dict[str, Any]] = {}
        
        # Anomaly analyses
        self._anomalies: Dict[str, Dict[str, Any]] = {}
        
        # Propagation analyses
        self._propagations: Dict[str, Dict[str, Any]] = {}
        
        # Copilot reports
        self._reports: Dict[str, Dict[str, Any]] = {}
        
        # Visualizations
        self._visualizations: Dict[str, Dict[str, Any]] = {}
        
        # Batch jobs
        self._batches: Dict[str, Dict[str, Any]] = {}
        
        # Metrics
        self._metrics: Dict[str, Any] = {
            "requests_total": 0,
            "active_jobs": 0,
            "storage_items": 0,
        }
    
    # =====================
    # Upload operations
    # =====================
    def store_upload(self, upload_id: str, data: Dict[str, Any]) -> None:
        """Store uploaded data."""
        with self._lock:
            self._uploads[upload_id] = {
                **data,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._metrics["storage_items"] += 1
    
    def get_upload(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve uploaded data."""
        with self._lock:
            return self._uploads.get(upload_id)
    
    # =====================
    # Similarity operations
    # =====================
    def store_similarity(self, similarity_id: str, data: Dict[str, Any]) -> None:
        """Store similarity matrix."""
        with self._lock:
            self._similarities[similarity_id] = {
                **data,
                "computed_at": datetime.now(timezone.utc).isoformat(),
            }
            self._metrics["storage_items"] += 1
    
    def get_similarity(self, similarity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve similarity matrix."""
        with self._lock:
            return self._similarities.get(similarity_id)
    
    # =====================
    # Topology operations
    # =====================
    def store_topology(self, topology_id: str, data: Dict[str, Any]) -> None:
        """Store topology result."""
        with self._lock:
            self._topologies[topology_id] = {
                **data,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._metrics["storage_items"] += 1
    
    def get_topology(self, topology_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve topology result."""
        with self._lock:
            return self._topologies.get(topology_id)
    
    # =====================
    # Anomaly operations
    # =====================
    def store_anomaly(self, analysis_id: str, data: Dict[str, Any]) -> None:
        """Store anomaly analysis."""
        with self._lock:
            self._anomalies[analysis_id] = {
                **data,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }
            self._metrics["storage_items"] += 1
    
    def get_anomaly(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve anomaly analysis."""
        with self._lock:
            return self._anomalies.get(analysis_id)
    
    # =====================
    # Propagation operations
    # =====================
    def store_propagation(self, propagation_id: str, data: Dict[str, Any]) -> None:
        """Store propagation analysis."""
        with self._lock:
            self._propagations[propagation_id] = {
                **data,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }
            self._metrics["storage_items"] += 1
    
    def get_propagation(self, propagation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve propagation analysis."""
        with self._lock:
            return self._propagations.get(propagation_id)
    
    # =====================
    # Report operations
    # =====================
    def store_report(self, report_id: str, data: Dict[str, Any]) -> None:
        """Store copilot report."""
        with self._lock:
            self._reports[report_id] = {
                **data,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            self._metrics["storage_items"] += 1
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve copilot report."""
        with self._lock:
            return self._reports.get(report_id)
    
    # =====================
    # Visualization operations
    # =====================
    def store_visualization(self, viz_id: str, data: Dict[str, Any]) -> None:
        """Store visualization metadata."""
        with self._lock:
            self._visualizations[viz_id] = {
                **data,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._metrics["storage_items"] += 1
    
    def get_visualization(self, viz_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve visualization metadata."""
        with self._lock:
            return self._visualizations.get(viz_id)
    
    # =====================
    # Batch operations
    # =====================
    def store_batch(self, batch_id: str, data: Dict[str, Any]) -> None:
        """Store batch job."""
        with self._lock:
            self._batches[batch_id] = {
                **data,
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
            self._metrics["active_jobs"] += 1
    
    def update_batch(self, batch_id: str, data: Dict[str, Any]) -> None:
        """Update batch job."""
        with self._lock:
            if batch_id in self._batches:
                self._batches[batch_id].update(data)
                if data.get("status") in ("completed", "failed"):
                    self._metrics["active_jobs"] = max(0, self._metrics["active_jobs"] - 1)
    
    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve batch job."""
        with self._lock:
            return self._batches.get(batch_id)
    
    # =====================
    # Metrics operations
    # =====================
    def increment_requests(self) -> None:
        """Increment request counter."""
        with self._lock:
            self._metrics["requests_total"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        with self._lock:
            return {
                **self._metrics,
                "uploads_count": len(self._uploads),
                "similarities_count": len(self._similarities),
                "topologies_count": len(self._topologies),
                "anomalies_count": len(self._anomalies),
                "propagations_count": len(self._propagations),
                "reports_count": len(self._reports),
                "visualizations_count": len(self._visualizations),
                "batches_count": len(self._batches),
            }


# Global storage instance
storage = InMemoryStorage()
