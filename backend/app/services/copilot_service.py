# backend/app/services/copilot_service.py
"""
LLM Copilot service.

Handles insight generation and interactive queries using Ollama.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import time

from app.services.storage import storage, generate_id
from app.providers.ollama import OllamaProvider
from app.providers.base import ChatMessage


class CopilotService:
    """Service for LLM-powered insights and queries."""
    
    def __init__(self):
        self.provider = OllamaProvider()
    
    async def generate_insights(
        self,
        topology_id: str,
        anomaly_id: Optional[str] = None,
        propagation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights using LLM.
        
        Args:
            topology_id: ID of topology result
            anomaly_id: Optional anomaly analysis ID
            propagation_id: Optional propagation analysis ID
            context: Additional context
            
        Returns:
            Response with report_id
        """
        start_time = time.time()
        
        # Get data
        topology = storage.get_topology(topology_id)
        if not topology:
            raise ValueError(f"Topology not found: {topology_id}")
        
        anomaly = storage.get_anomaly(anomaly_id) if anomaly_id else None
        propagation = storage.get_propagation(propagation_id) if propagation_id else None
        
        # Build prompt
        prompt = self._build_analysis_prompt(topology, anomaly, propagation, context)
        
        # Generate insights using LLM
        try:
            messages = [
                ChatMessage(role="system", content="You are a network intelligence analyst. Provide clear, actionable insights about network topology and congestion patterns."),
                ChatMessage(role="user", content=prompt),
            ]
            
            result = await self.provider.chat(messages)
            llm_response = result.content
        except Exception as e:
            # Fallback to template-based insights if LLM unavailable
            llm_response = self._generate_fallback_insights(topology, anomaly, propagation)
        
        # Build structured report
        report = self._build_report(topology, anomaly, propagation, llm_response, context)
        
        # Store
        report_id = generate_id("rpt")
        generation_time = time.time() - start_time
        
        report["report_id"] = report_id
        report["generation_time_sec"] = round(generation_time, 2)
        
        storage.store_report(report_id, report)
        
        return {
            "report_id": report_id,
            "status": "completed",
            "generation_time_sec": round(generation_time, 2),
            "result_url": f"/copilot/report/{report_id}",
        }
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve generated report."""
        return storage.get_report(report_id)
    
    async def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Handle interactive query about network state.
        
        Args:
            query: Natural language question
            context: Context including system_context, report_id, topology_id
            
        Returns:
            Query response with answer
        """
        query_id = generate_id("qry")
        
        # Check for rich system context (from chat endpoint)
        system_prompt = "You are a network intelligence assistant. Answer questions about network topology, congestion, and anomalies based on the provided context."
        context_data = ""
        supporting_data = {}
        
        if context:
            # Use rich system context if provided
            if context.get("system_context"):
                system_prompt = context["system_context"]
            
            if context.get("report_id"):
                report = storage.get_report(context["report_id"])
                if report:
                    context_data += f"Report summary: {report.get('summary', '')}\n"
            
            if context.get("topology_id"):
                topology = storage.get_topology(context["topology_id"])
                if topology:
                    context_data += f"Topology contains {topology['detected_groups']} groups with {topology['total_cells']} cells.\n"
                    for group in topology.get("groups", [])[:3]:
                        context_data += f"- {group['group_name']}: {group['cell_count']} cells, avg similarity {group['avg_similarity']}\n"
        
        # Query LLM
        try:
            messages = [
                ChatMessage(role="system", content=system_prompt),
            ]
            
            # Add context if we have additional data beyond system prompt
            if context_data:
                messages.append(ChatMessage(role="user", content=f"Additional context:\n{context_data}\n\nQuestion: {query}"))
            else:
                messages.append(ChatMessage(role="user", content=query))
            
            result = await self.provider.chat(messages)
            answer = result.content
        except Exception:
            # Fallback answer
            answer = self._generate_fallback_answer(query, context_data)
        
        return {
            "query_id": query_id,
            "question": query,
            "answer": answer,
            "supporting_data": supporting_data if supporting_data else None,
            "related_insights": [],
        }
    
    def _build_analysis_prompt(
        self,
        topology: Dict[str, Any],
        anomaly: Optional[Dict[str, Any]],
        propagation: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Build analysis prompt for LLM."""
        prompt = f"""Analyze the following network topology data and provide insights:

## Topology Summary
- Total cells: {topology['total_cells']}
- Detected groups: {topology['detected_groups']}
- Unassigned cells: {len(topology.get('unassigned_cells', []))}

## Groups
"""
        for group in topology.get("groups", []):
            prompt += f"- {group['group_name']} ({group['group_id']}): {group['cell_count']} cells, avg similarity: {group['avg_similarity']}\n"
        
        if anomaly:
            prompt += f"""
## Anomaly Analysis
- Anomalies detected: {anomaly['anomalies_detected']}
- Average confidence: {anomaly['statistics']['avg_confidence']}
"""
            for anom in anomaly.get("anomalies", [])[:3]:
                prompt += f"- Cell {anom['cell_id']}: confidence {anom['confidence_score']}, severity {anom['severity']}\n"
        
        if propagation:
            prompt += f"""
## Propagation Analysis
- Events detected: {len(propagation.get('events', []))}
- Paths identified: {len(propagation.get('propagation_paths', []))}
"""
        
        prompt += "\nProvide 3 key insights and 2-3 recommendations."
        
        return prompt
    
    def _generate_fallback_insights(
        self,
        topology: Dict[str, Any],
        anomaly: Optional[Dict[str, Any]],
        propagation: Optional[Dict[str, Any]],
    ) -> str:
        """Generate template-based insights when LLM is unavailable."""
        insights = []
        
        # Topology insight
        groups = topology.get("groups", [])
        if groups:
            largest = max(groups, key=lambda g: g["cell_count"])
            insights.append(f"The network topology reveals {len(groups)} distinct link groups. The largest group ({largest['group_name']}) contains {largest['cell_count']} cells with average similarity of {largest['avg_similarity']:.2f}.")
        
        # Anomaly insight
        if anomaly and anomaly.get("anomalies"):
            high_severity = [a for a in anomaly["anomalies"] if a.get("severity") == "high"]
            if high_severity:
                insights.append(f"Critical attention required: {len(high_severity)} high-severity anomalies detected. Cell {high_severity[0]['cell_id']} shows significant deviation from its assigned group.")
        
        # Propagation insight
        if propagation and propagation.get("events"):
            insights.append(f"Congestion propagation analysis identified {len(propagation['events'])} inter-group events, suggesting potential cascading effects that should be monitored.")
        
        return " ".join(insights)
    
    def _generate_fallback_answer(self, query: str, context: str) -> str:
        """Generate simple fallback answer."""
        query_lower = query.lower()
        
        if "congested" in query_lower or "congestion" in query_lower:
            return "Based on the analysis, congestion patterns vary across link groups. Check the topology report for detailed group-level congestion metrics."
        elif "anomal" in query_lower:
            return "Anomalies are detected based on cell-to-group correlation. Cells with low confidence scores indicate potential hardware issues or misconfiguration."
        elif "group" in query_lower:
            return "Groups represent cells sharing common fronthaul links. Higher average similarity within a group indicates stronger correlation in congestion patterns."
        else:
            return "I can help analyze network topology, anomalies, and congestion patterns. Please ask specific questions about link groups, anomalies, or propagation."
    
    def _build_report(
        self,
        topology: Dict[str, Any],
        anomaly: Optional[Dict[str, Any]],
        propagation: Optional[Dict[str, Any]],
        llm_response: str,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build structured report."""
        # Determine health status
        if anomaly and anomaly.get("anomalies_detected", 0) > 2:
            health_status = "critical" if any(a.get("severity") == "high" for a in anomaly.get("anomalies", [])) else "degraded"
        elif anomaly and anomaly.get("anomalies_detected", 0) > 0:
            health_status = "degraded"
        else:
            health_status = "healthy"
        
        # Build insights
        insights = self._extract_insights(topology, anomaly, propagation)
        
        # Build recommendations
        recommendations = self._build_recommendations(insights, anomaly)
        
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": llm_response[:500] if len(llm_response) > 500 else llm_response,
            "topology_summary": {
                "total_cells": topology["total_cells"],
                "detected_groups": topology["detected_groups"],
                "unassigned_cells": len(topology.get("unassigned_cells", [])),
                "avg_group_confidence": anomaly["statistics"]["avg_confidence"] if anomaly else 0.85,
            },
            "health_status": health_status,
            "insights": insights,
            "recommendations": recommendations,
            "metadata": {
                "analysis_duration_sec": 45,
                "data_points_analyzed": topology["total_cells"] * 1000,
                "confidence_level": "high" if health_status == "healthy" else "medium",
            },
        }
    
    def _extract_insights(
        self,
        topology: Dict[str, Any],
        anomaly: Optional[Dict[str, Any]],
        propagation: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extract structured insights."""
        insights = []
        insight_counter = 1
        
        # Group-based insight
        groups = topology.get("groups", [])
        if groups:
            sorted_groups = sorted(groups, key=lambda g: g["avg_similarity"])
            weakest = sorted_groups[0]
            insights.append({
                "insight_id": f"ins_{insight_counter:03d}",
                "type": "congestion_alert",
                "severity": "medium",
                "title": f"Congestion Pattern in {weakest['group_name']}",
                "description": f"{weakest['group_name']} ({weakest['group_id']}) shows correlation of {weakest['avg_similarity']:.2f} affecting {weakest['cell_count']} cells.",
                "affected_entities": [weakest["group_id"]],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            insight_counter += 1
        
        # Anomaly-based insight
        if anomaly and anomaly.get("anomalies"):
            for anom in anomaly["anomalies"][:2]:
                insights.append({
                    "insight_id": f"ins_{insight_counter:03d}",
                    "type": "anomaly_detected",
                    "severity": anom.get("severity", "medium"),
                    "title": f"Cell {anom['cell_id']} Behaving Abnormally",
                    "description": anom.get("explanation", "Cell shows deviation from group behavior"),
                    "affected_entities": [anom["cell_id"]],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                insight_counter += 1
        
        # Propagation-based insight
        if propagation and propagation.get("propagation_paths"):
            path = propagation["propagation_paths"][0]
            insights.append({
                "insight_id": f"ins_{insight_counter:03d}",
                "type": "propagation_detected",
                "severity": "medium",
                "title": "Cascading Congestion Pattern Identified",
                "description": f"Congestion propagates through {' → '.join(path['sequence'])} with {path['total_delay_ms']:.1f}ms total delay.",
                "affected_entities": path["sequence"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        
        return insights
    
    def _build_recommendations(
        self,
        insights: List[Dict[str, Any]],
        anomaly: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build action recommendations."""
        recommendations = []
        rec_counter = 1
        
        for insight in insights[:3]:
            action_type = "hardware_check" if insight["type"] == "anomaly_detected" else "capacity_upgrade"
            
            recommendations.append({
                "recommendation_id": f"rec_{rec_counter:03d}",
                "insight_id": insight["insight_id"],
                "action_type": action_type,
                "priority": insight["severity"],
                "title": f"Address {insight['title']}",
                "description": f"Recommended action based on: {insight['description'][:100]}",
                "expected_impact": "Improved network stability and reduced congestion",
                "estimated_effort": "medium",
                "implementation_steps": [
                    "Review current configuration",
                    "Identify root cause",
                    "Apply corrective measures",
                    "Monitor for improvement",
                ],
            })
            rec_counter += 1
        
        return recommendations


# Global service instance
copilot_service = CopilotService()
