# backend/app/services/data_service.py
"""
Data ingestion service.

Handles uploading and processing of loss events and throughput data.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.services.storage import storage, generate_id


class DataService:
    """Service for data ingestion and processing."""
    
    def upload_data(
        self,
        data_type: str,
        data: Optional[List[Dict[str, Any]]] = None,
        file_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Upload and process telemetry data.
        
        Args:
            data_type: Type of data (loss_events or throughput)
            data: Inline data records
            file_url: URL to data file (not implemented - placeholder)
            metadata: Optional metadata
            
        Returns:
            Upload response with upload_id and status
        """
        upload_id = generate_id("upl")
        
        # Process inline data
        if data:
            records = data
            records_count = len(records)
        elif file_url:
            # Placeholder for file download
            # In production, this would download from S3/GCS/etc
            records = self._generate_sample_data(data_type)
            records_count = len(records)
        else:
            # Generate sample data for demo
            records = self._generate_sample_data(data_type)
            records_count = len(records)
        
        # Validate data
        self._validate_data(data_type, records)
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(records)
        
        # Extract cell IDs
        cell_ids = sorted(df["cell_id"].unique().tolist())
        
        # Store the upload
        storage.store_upload(upload_id, {
            "upload_id": upload_id,
            "data_type": data_type,
            "records_count": records_count,
            "cell_ids": [str(c) for c in cell_ids],
            "status": "completed",
            "data": records,
            "metadata": metadata or {},
        })
        
        return {
            "upload_id": upload_id,
            "status": "completed",
            "records_count": records_count,
            "estimated_processing_time_sec": 1,
        }
    
    def get_upload(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve upload data."""
        return storage.get_upload(upload_id)
    
    def _generate_sample_data(self, data_type: str) -> List[Dict[str, Any]]:
        """Generate sample data for demo purposes."""
        np.random.seed(42)
        
        num_slots = 1000
        num_cells = 24
        
        records = []
        
        if data_type == "loss_events":
            # Generate correlated loss events to simulate shared links
            # Groups: [1,2,8,14], [3,6,9,15], [4,10,12,18], others independent
            group1 = [1, 2, 8, 14]
            group2 = [3, 6, 9, 15]
            group3 = [4, 10, 12, 18]
            
            for slot in range(num_slots):
                # Simulate congestion events at certain times
                congestion1 = np.random.random() < 0.2  # 20% congestion rate
                congestion2 = np.random.random() < 0.15
                congestion3 = np.random.random() < 0.1
                
                for cell in range(1, num_cells + 1):
                    if cell in group1:
                        loss = 1 if congestion1 and np.random.random() < 0.8 else 0
                    elif cell in group2:
                        loss = 1 if congestion2 and np.random.random() < 0.75 else 0
                    elif cell in group3:
                        loss = 1 if congestion3 and np.random.random() < 0.7 else 0
                    else:
                        loss = 1 if np.random.random() < 0.05 else 0
                    
                    records.append({
                        "slot_id": slot,
                        "cell_id": cell,
                        "loss_event": loss,
                    })
        else:  # throughput
            for slot in range(num_slots):
                for cell in range(1, num_cells + 1):
                    throughput = 30 + np.random.normal(0, 5)
                    records.append({
                        "slot_id": slot,
                        "cell_id": cell,
                        "throughput_slot": round(throughput, 3),
                    })
        
        return records
    
    def _validate_data(self, data_type: str, records: List[Dict[str, Any]]) -> None:
        """Validate data format."""
        if not records:
            raise ValueError("No records provided")
        
        required_fields = ["slot_id", "cell_id"]
        if data_type == "loss_events":
            required_fields.append("loss_event")
        else:
            required_fields.append("throughput_slot")
        
        for record in records[:10]:  # Check first 10 records
            for field in required_fields:
                if field not in record:
                    raise ValueError(f"Missing required field: {field}")


# Global service instance
data_service = DataService()
