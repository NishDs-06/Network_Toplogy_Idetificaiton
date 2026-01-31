# backend/app/services/batch_service.py
"""
Batch processing service.

Handles orchestration of complete analysis pipelines.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.storage import storage, generate_id
from app.services.data_service import data_service
from app.services.similarity_service import similarity_service
from app.services.topology_service import topology_service
from app.services.anomaly_service import anomaly_service
from app.services.propagation_service import propagation_service
from app.services.copilot_service import copilot_service
from app.services.visualization_service import visualization_service


class BatchService:
    """Service for batch processing pipelines."""
    
    async def run_full_analysis(
        self,
        upload_id: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run complete analysis pipeline.
        
        Args:
            upload_id: ID of uploaded data
            config: Pipeline configuration
            
        Returns:
            Initial batch response with status URL
        """
        config = config or {}
        batch_id = generate_id("batch")
        
        # Initialize batch status
        steps = [
            {"step": "data_validation", "status": "pending", "result_id": None, "error": None},
            {"step": "similarity_computation", "status": "pending", "result_id": None, "error": None},
            {"step": "topology_inference", "status": "pending", "result_id": None, "error": None},
            {"step": "anomaly_detection", "status": "pending", "result_id": None, "error": None},
            {"step": "propagation_analysis", "status": "pending", "result_id": None, "error": None},
            {"step": "insight_generation", "status": "pending", "result_id": None, "error": None},
            {"step": "visualization_generation", "status": "pending", "result_id": None, "error": None},
        ]
        
        # Remove optional steps based on config
        if not config.get("propagation_analysis", True):
            steps = [s for s in steps if s["step"] != "propagation_analysis"]
        if not config.get("generate_report", True):
            steps = [s for s in steps if s["step"] != "insight_generation"]
        if not config.get("generate_visualizations", True):
            steps = [s for s in steps if s["step"] != "visualization_generation"]
        
        storage.store_batch(batch_id, {
            "batch_id": batch_id,
            "upload_id": upload_id,
            "config": config,
            "status": "processing",
            "steps": steps,
            "results": {},
        })
        
        # Start async processing
        asyncio.create_task(self._run_pipeline(batch_id, upload_id, config))
        
        # Calculate estimated time
        estimated_time = datetime.now(timezone.utc)
        
        return {
            "batch_id": batch_id,
            "status": "processing",
            "estimated_completion_time": estimated_time.isoformat(),
            "steps": steps,
            "status_url": f"/batch/status/{batch_id}",
        }
    
    async def _run_pipeline(
        self,
        batch_id: str,
        upload_id: str,
        config: Dict[str, Any],
    ) -> None:
        """Run the full pipeline asynchronously."""
        results = {}
        batch = storage.get_batch(batch_id)
        steps = batch["steps"]
        
        try:
            # Step 1: Data validation
            self._update_step(batch_id, "data_validation", "processing")
            upload = data_service.get_upload(upload_id)
            if not upload:
                raise ValueError(f"Upload not found: {upload_id}")
            self._update_step(batch_id, "data_validation", "completed", upload_id)
            
            # Step 2: Similarity computation
            self._update_step(batch_id, "similarity_computation", "processing")
            sim_result = similarity_service.compute_similarity(
                upload_id=upload_id,
                method=config.get("similarity_method", "correlation"),
            )
            similarity_id = sim_result["similarity_matrix_id"]
            results["similarity_id"] = similarity_id
            self._update_step(batch_id, "similarity_computation", "completed", similarity_id)
            
            # Step 3: Topology inference
            self._update_step(batch_id, "topology_inference", "processing")
            topo_result = topology_service.infer_topology(
                similarity_id=similarity_id,
                clustering_method=config.get("clustering_method", "hierarchical"),
                num_clusters=None if config.get("num_clusters") == "auto" else config.get("num_clusters"),
            )
            topology_id = topo_result["topology_id"]
            results["topology_id"] = topology_id
            self._update_step(batch_id, "topology_inference", "completed", topology_id)
            
            # Step 4: Anomaly detection
            self._update_step(batch_id, "anomaly_detection", "processing")
            anom_result = anomaly_service.detect_anomalies(
                topology_id=topology_id,
                similarity_id=similarity_id,
                threshold=config.get("anomaly_threshold", 0.5),
            )
            anomaly_id = anom_result["analysis_id"]
            results["anomaly_id"] = anomaly_id
            self._update_step(batch_id, "anomaly_detection", "completed", anomaly_id)
            
            # Step 5: Propagation analysis (optional)
            propagation_id = None
            if config.get("propagation_analysis", True):
                self._update_step(batch_id, "propagation_analysis", "processing")
                prop_result = propagation_service.analyze_propagation(
                    topology_id=topology_id,
                    upload_id=upload_id,
                )
                propagation_id = prop_result["propagation_id"]
                results["propagation_id"] = propagation_id
                self._update_step(batch_id, "propagation_analysis", "completed", propagation_id)
            
            # Step 6: Insight generation (optional)
            if config.get("generate_report", True):
                self._update_step(batch_id, "insight_generation", "processing")
                insight_result = await copilot_service.generate_insights(
                    topology_id=topology_id,
                    anomaly_id=anomaly_id,
                    propagation_id=propagation_id,
                )
                report_id = insight_result["report_id"]
                results["report_id"] = report_id
                self._update_step(batch_id, "insight_generation", "completed", report_id)
            
            # Step 7: Visualization generation (optional)
            visualizations = []
            if config.get("generate_visualizations", True):
                self._update_step(batch_id, "visualization_generation", "processing")
                
                # Generate heatmap
                heat_result = visualization_service.generate_heatmap(similarity_id)
                visualizations.append(heat_result["visualization_id"])
                
                # Generate topology graph
                topo_viz = visualization_service.generate_topology_graph(topology_id)
                visualizations.append(topo_viz["visualization_id"])
                
                # Generate propagation flow if available
                if propagation_id:
                    flow_viz = visualization_service.generate_propagation_flow(propagation_id)
                    visualizations.append(flow_viz["visualization_id"])
                
                results["visualizations"] = visualizations
                self._update_step(batch_id, "visualization_generation", "completed", ",".join(visualizations))
            
            # Update final status
            storage.update_batch(batch_id, {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "results": results,
            })
            
        except Exception as e:
            # Find current step and mark as failed
            batch = storage.get_batch(batch_id)
            for step in batch["steps"]:
                if step["status"] == "processing":
                    step["status"] = "failed"
                    step["error"] = str(e)
                    break
            
            storage.update_batch(batch_id, {
                "status": "failed",
                "steps": batch["steps"],
                "error": str(e),
            })
    
    def _update_step(
        self,
        batch_id: str,
        step_name: str,
        status: str,
        result_id: Optional[str] = None,
    ) -> None:
        """Update a specific step in the batch."""
        batch = storage.get_batch(batch_id)
        if not batch:
            return
        
        for step in batch["steps"]:
            if step["step"] == step_name:
                step["status"] = status
                if result_id:
                    step["result_id"] = result_id
                break
        
        storage.update_batch(batch_id, {"steps": batch["steps"]})
    
    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch job status."""
        batch = storage.get_batch(batch_id)
        if not batch:
            return None
        
        # Calculate duration if completed
        duration_sec = None
        if batch.get("completed_at") and batch.get("started_at"):
            try:
                start = datetime.fromisoformat(batch["started_at"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(batch["completed_at"].replace("Z", "+00:00"))
                duration_sec = int((end - start).total_seconds())
            except:
                pass
        
        return {
            "batch_id": batch["batch_id"],
            "status": batch["status"],
            "started_at": batch.get("started_at", ""),
            "completed_at": batch.get("completed_at"),
            "duration_sec": duration_sec,
            "steps": batch["steps"],
            "results": batch.get("results") if batch["status"] == "completed" else None,
        }


# Global service instance
batch_service = BatchService()
