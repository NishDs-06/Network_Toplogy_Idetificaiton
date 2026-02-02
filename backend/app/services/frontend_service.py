# backend/app/services/frontend_service.py
"""
Frontend Integration Service.

Provides data in the exact format expected by the React frontend,
loading from actual ML pipeline outputs.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Add visualization to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "visualization"))

from plot_heatmap import load_similarity_matrix, generate_heatmap_for_api
from plot_topology_graph import (
    load_clustering_data,
    generate_topology_for_api,
    generate_cells_for_api,
)


class FrontendService:
    """Service for frontend data integration."""
    
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self._cache_time:
            return False
        elapsed = (datetime.now(timezone.utc) - self._cache_time[key]).total_seconds()
        return elapsed < self._cache_ttl
    
    def get_similarity_matrix(self) -> Dict[str, Any]:
        """
        Get similarity matrix in frontend format.
        
        Returns:
            {
                "matrix": [[float, ...], ...],
                "cellIds": ["cell_01", ...],
                "timestamp": "ISO8601"
            }
        """
        cache_key = "similarity_matrix"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        data = generate_heatmap_for_api()
        
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now(timezone.utc)
        
        return data
    
    def get_cells(self, include_anomalies: bool = True) -> Dict[str, Any]:
        """
        Get cell data with anomaly information.
        
        Returns:
            {
                "cells": [
                    {"id": "cell_01", "name": "CELL 01", "group": "link_1", 
                     "isAnomaly": false, "anomalyScore": null}
                ]
            }
        """
        cache_key = "cells"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        data = generate_cells_for_api()
        
        # Optionally integrate with anomaly service
        if include_anomalies:
            try:
                from app.services.anomaly_service import anomaly_service
                from app.services.storage import storage
                
                # Get latest anomaly results if available
                anomalies = storage.list_all("anomalies")
                if anomalies:
                    latest = list(anomalies.values())[-1]
                    for anomaly in latest.get("anomalies", []):
                        cell_id = anomaly.get("cell_id", "")
                        if isinstance(cell_id, int):
                            cell_id = f"cell_{cell_id:02d}"
                        
                        for cell in data["cells"]:
                            if cell["id"] == cell_id:
                                cell["isAnomaly"] = True
                                cell["anomalyScore"] = anomaly.get("confidence", 0.5)
            except Exception:
                pass  # Anomaly data optional
        
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now(timezone.utc)
        
        return data
    
    def get_topology_groups(self) -> Dict[str, Any]:
        """
        Get topology groups.
        
        Returns:
            {
                "groups": [
                    {"id": "link_1", "name": "Link 1", "color": "#hex", "cells": [...]}
                ]
            }
        """
        cache_key = "topology_groups"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        data = generate_topology_for_api()
        
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now(timezone.utc)
        
        return data
    
    def get_propagation_events(self) -> Dict[str, Any]:
        """
        Get propagation events in frontend format.
        
        Returns:
            {
                "events": [...],
                "timeRange": [0, 15]
            }
        """
        cache_key = "propagation_events"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        # Try to get from storage
        try:
            from app.services.storage import storage
            propagations = storage.list_all("propagations")
            
            if propagations:
                latest = list(propagations.values())[-1]
                events = []
                
                for i, path in enumerate(latest.get("propagation_paths", [])):
                    events.append({
                        "id": f"p{i+1}",
                        "sourceGroup": f"link_{path.get('source_group', 1)}",
                        "targetGroup": f"link_{path.get('target_group', 2)}",
                        "timestamp": path.get("delay_ms", i * 5) / 1000,
                        "severity": path.get("severity", "degraded"),
                        "correlation": path.get("correlation", 0.5)
                    })
                
                data = {
                    "events": events,
                    "timeRange": [0, 15]
                }
            else:
                data = self._generate_sample_propagation()
        except Exception:
            data = self._generate_sample_propagation()
        
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now(timezone.utc)
        
        return data
    
    def _generate_sample_propagation(self) -> Dict[str, Any]:
        """Generate sample propagation data for demo."""
        groups = self.get_topology_groups()["groups"]
        
        if len(groups) < 2:
            return {"events": [], "timeRange": [0, 15]}
        
        events = []
        for i in range(min(4, len(groups) - 1)):
            events.append({
                "id": f"p{i+1}",
                "sourceGroup": groups[i]["id"],
                "targetGroup": groups[i+1]["id"],
                "timestamp": i * 3,
                "severity": ["degraded", "critical", "degraded", "healthy"][i % 4],
                "correlation": round(0.4 + (i % 3) * 0.15, 2)
            })
        
        return {
            "events": events,
            "timeRange": [0, 15]
        }
    
    async def get_insights_llm(self) -> Dict[str, Any]:
        """
        Get LLM-generated insights with long-term caching.
        Uses LLM once, then caches for 1 hour to reduce GPU load.
        
        Returns:
            {
                "insights": [
                    {"id": "i1", "type": "critical|warning|info", "message": "...", "timestamp": "..."}
                ]
            }
        """
        cache_key = "insights_llm"
        # Use 1 hour cache for LLM-generated content
        cache_ttl = 3600  # 1 hour
        
        if cache_key in self._cache:
            elapsed = (datetime.now(timezone.utc) - self._cache_time.get(cache_key, datetime.min.replace(tzinfo=timezone.utc))).total_seconds()
            if elapsed < cache_ttl:
                return self._cache[cache_key]
        
        # Get data for LLM context
        groups = self.get_topology_groups()["groups"]
        cells = self.get_cells()["cells"]
        matrix_data = self.get_similarity_matrix()
        
        anomaly_cells = [c for c in cells if c.get("isAnomaly")]
        
        # Build compact context for LLM
        context = f"""Network topology analysis results:
- {len(cells)} cells in {len(groups)} link groups
- {len(anomaly_cells)} anomalies detected
- Groups: {', '.join([f"{g['name']} ({len(g['cells'])} cells)" for g in groups[:5]])}"""
        
        try:
            from app.providers.ollama import OllamaProvider
            from app.providers.base import ChatMessage
            
            provider = OllamaProvider()
            
            messages = [
                ChatMessage(
                    role="system", 
                    content="You are a network analyst. Generate exactly 3 insights about network health. Be concise - each insight must be under 80 characters. Format: one insight per line, prefix with [INFO], [WARNING], or [CRITICAL]."
                ),
                ChatMessage(role="user", content=context),
            ]
            
            result = await provider.chat(messages)
            llm_text = result.content
            
            # Parse LLM response
            insights = self._parse_llm_insights(llm_text)
            
        except Exception as e:
            print(f"LLM insight generation failed: {e}, using fallback")
            insights = self._generate_default_insights()["insights"]
        
        data = {"insights": insights}
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now(timezone.utc)
        
        return data
    
    def _parse_llm_insights(self, llm_text: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured insights."""
        insights = []
        lines = llm_text.strip().split('\n')
        
        for i, line in enumerate(lines[:5]):  # Max 5 insights
            line = line.strip()
            if not line:
                continue
            
            # Determine type from prefix
            insight_type = "info"
            if "[CRITICAL]" in line.upper():
                insight_type = "critical"
                line = line.replace("[CRITICAL]", "").replace("[critical]", "").strip()
            elif "[WARNING]" in line.upper():
                insight_type = "warning"
                line = line.replace("[WARNING]", "").replace("[warning]", "").strip()
            elif "[INFO]" in line.upper():
                line = line.replace("[INFO]", "").replace("[info]", "").strip()
            
            # Truncate if too long
            message = line[:100] if len(line) > 100 else line
            
            if message:
                insights.append({
                    "id": f"i{i+1}",
                    "type": insight_type,
                    "message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        # Ensure at least one insight
        if not insights:
            insights = self._generate_default_insights()["insights"]
        
        return insights
    
    async def get_recommendations_llm(self) -> Dict[str, Any]:
        """
        Get LLM-generated recommendations with long-term caching.
        
        Returns:
            {
                "recommendations": [
                    {"id": "r1", "type": "ACTION|MONITOR|INFO", "title": "...", "description": "..."}
                ]
            }
        """
        cache_key = "recommendations_llm"
        cache_ttl = 3600  # 1 hour
        
        if cache_key in self._cache:
            elapsed = (datetime.now(timezone.utc) - self._cache_time.get(cache_key, datetime.min.replace(tzinfo=timezone.utc))).total_seconds()
            if elapsed < cache_ttl:
                return self._cache[cache_key]
        
        # Get data for context
        groups = self.get_topology_groups()["groups"]
        cells = self.get_cells()["cells"]
        anomaly_cells = [c for c in cells if c.get("isAnomaly")]
        
        context = f"""Based on topology with {len(cells)} cells in {len(groups)} groups, {len(anomaly_cells)} anomalies detected.
Generate 3 actionable recommendations. Be concise - title under 30 chars, description under 60 chars.
Format each as: [TYPE] Title | Description
Types: ACTION, MONITOR, INFO"""
        
        try:
            from app.providers.ollama import OllamaProvider
            from app.providers.base import ChatMessage
            
            provider = OllamaProvider()
            
            messages = [
                ChatMessage(
                    role="system",
                    content="You are a network operations advisor. Give exactly 3 brief recommendations."
                ),
                ChatMessage(role="user", content=context),
            ]
            
            result = await provider.chat(messages)
            recommendations = self._parse_llm_recommendations(result.content)
            
        except Exception as e:
            print(f"LLM recommendation generation failed: {e}, using fallback")
            recommendations = self._generate_default_recommendations()
        
        data = {"recommendations": recommendations}
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now(timezone.utc)
        
        return data
    
    def _parse_llm_recommendations(self, llm_text: str) -> List[Dict[str, Any]]:
        """Parse LLM response into recommendations."""
        recs = []
        lines = llm_text.strip().split('\n')
        
        for i, line in enumerate(lines[:3]):
            line = line.strip()
            if not line:
                continue
            
            rec_type = "INFO"
            if "[ACTION]" in line.upper():
                rec_type = "ACTION"
                line = line.replace("[ACTION]", "").strip()
            elif "[MONITOR]" in line.upper():
                rec_type = "MONITOR"
                line = line.replace("[MONITOR]", "").strip()
            elif "[INFO]" in line.upper():
                line = line.replace("[INFO]", "").strip()
            
            # Split title and description
            if "|" in line:
                parts = line.split("|", 1)
                title = parts[0].strip()[:40]
                desc = parts[1].strip()[:80] if len(parts) > 1 else ""
            else:
                title = line[:40]
                desc = ""
            
            if title:
                recs.append({
                    "id": f"r{i+1}",
                    "type": rec_type.lower(),
                    "title": title,
                    "description": desc
                })
        
        if not recs:
            recs = self._generate_default_recommendations()
        
        return recs
    
    def _generate_default_recommendations(self) -> List[Dict[str, Any]]:
        """Generate default recommendations."""
        return [
            {"id": "r1", "type": "action", "title": "Review shared fronthaul", "description": "Check Link groups with high correlation"},
            {"id": "r2", "type": "monitor", "title": "Watch anomaly cells", "description": "Monitor flagged cells for 15 min"},
            {"id": "r3", "type": "info", "title": "Topology stable", "description": "No major structural changes detected"}
        ]
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get LLM-generated insights (sync wrapper).
        Returns cached if available, otherwise generates defaults.
        """
        cache_key = "insights"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        # Check if LLM insights are cached
        if "insights_llm" in self._cache:
            return self._cache["insights_llm"]
        
        # Return default insights (LLM will be called async separately)
        return self._generate_default_insights()
    
    def get_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations (sync wrapper).
        """
        cache_key = "recommendations_llm"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        return {"recommendations": self._generate_default_recommendations()}
    
    def _generate_default_insights(self) -> Dict[str, Any]:
        """Generate default insights based on topology."""
        groups = self.get_topology_groups()["groups"]
        cells = self.get_cells()["cells"]
        
        anomaly_count = sum(1 for c in cells if c.get("isAnomaly"))
        
        insights = [
            {
                "id": "i1",
                "type": "info",
                "message": f"Topology clustering complete: {len(groups)} distinct groups identified",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "i2", 
                "type": "info",
                "message": f"Monitoring {len(cells)} cells across {len(groups)} links",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        if anomaly_count > 0:
            insights.insert(0, {
                "id": "i0",
                "type": "warning",
                "message": f"Detected {anomaly_count} cells with anomalous behavior",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return {"insights": insights}
    
    def get_complete_state(self) -> Dict[str, Any]:
        """
        Get complete application state in one call.
        Matches the example response format in InstructionsToIntegrate.md.
        """
        matrix_data = self.get_similarity_matrix()
        cells_data = self.get_cells()
        groups_data = self.get_topology_groups()
        events_data = self.get_propagation_events()
        insights_data = self.get_insights()
        
        return {
            "matrix": matrix_data["matrix"],
            "cellIds": matrix_data["cellIds"],
            "cells": cells_data["cells"],
            "topologyGroups": groups_data["groups"],
            "propagationEvents": events_data["events"],
            "insights": insights_data["insights"]
        }
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._cache_time.clear()


# Global instance
frontend_service = FrontendService()
