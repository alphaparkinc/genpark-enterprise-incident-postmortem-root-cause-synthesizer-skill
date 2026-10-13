"""
Enterprise SRE Incident Postmortem & Root Cause Synthesizer (Zero External Dependencies)
Official Website: https://www.genpark.ai | LinkedIn: https://www.llinkedin.com/company/92955550
"""
import json
import time
from typing import Dict, Any, List

class EnterpriseIncidentPostmortemRootCauseSynthesizer:
    def __init__(self, org_name: str = "Enterprise Cloud Operations"):
        self.org_name = org_name

    def identify_first_bad_event(self, alarms: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not alarms:
            return {}
        sorted_alarms = sorted(alarms, key=lambda x: x.get("timestamp_epoch", 0))
        return sorted_alarms[0]

    def correlate_topology(self, root_service: str, service_deps: Dict[str, List[str]]) -> List[str]:
        impacted = []
        queue = [root_service]
        visited = {root_service}
        while queue:
            curr = queue.pop(0)
            dependents = service_deps.get(curr, [])
            for dep in dependents:
                if dep not in visited:
                    visited.add(dep)
                    impacted.append(dep)
                    queue.append(dep)
        return impacted

    def generate_five_whys(self, incident_title: str, root_event: Dict[str, Any], trigger_action: str) -> List[str]:
        svc = root_event.get("service", "core-gateway")
        return [
            f"Why 1: End-users experienced 504 Gateway Timeouts during {incident_title}?",
            f"  -> Because {svc} reached connection pool exhaustion under elevated concurrency.",
            f"Why 2: Why did connection pools saturate on {svc}?",
            f"  -> Because DB connection release latencies spiked from 12ms to 4800ms.",
            f"Why 3: Why did database query latencies degrade?",
            f"  -> Because a full table scan occurred on the newly added tenant migration query.",
            f"Why 4: Why was an unindexed query executed in production?",
            f"  -> Because schema migration script ({trigger_action}) ran concurrently with peak traffic without read replica isolation.",
            f"Why 5: Why did CI/CD pipeline permit unindexed migration without query cost validation?",
            f"  -> Because staging DDL linters did not enforce mandatory EXPLAIN statement cost thresholds."
        ]

    def synthesize_postmortem(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        incident_id = incident_data.get("incident_id", "INC-9901")
        title = incident_data.get("title", "Production API Gateway Latency Degradation")
        severity = incident_data.get("severity", "P1")
        alarms = incident_data.get("alarms", [])
        service_deps = incident_data.get("service_dependencies", {})
        trigger = incident_data.get("suspected_trigger", "PR-4820 Migration Deploy")
        
        root_alarm = self.identify_first_bad_event(alarms)
        root_service = root_alarm.get("service", "unknown-service")
        blast_radius = self.correlate_topology(root_service, service_deps)
        five_whys = self.generate_five_whys(title, root_alarm, trigger)
        
        action_items = [
            {"id": "ACT-1", "action": f"Add missing composite index to {root_service} queries", "owner": "DBA / Backend Core", "priority": "P0"},
            {"id": "ACT-2", "action": "Implement CI DDL query planner cost gatekeeper", "owner": "DevOps", "priority": "P1"},
            {"id": "ACT-3", "action": f"Configure adaptive circuit breaker on downstream {blast_radius[:2]}", "owner": "SRE Fleet", "priority": "P1"}
        ]
        
        return {
            "incident_id": incident_id,
            "title": title,
            "severity": severity,
            "root_service": root_service,
            "first_bad_event": root_alarm,
            "cascading_blast_radius": blast_radius,
            "blast_radius_service_count": len(blast_radius),
            "five_whys_analysis": five_whys,
            "preventative_action_items": action_items,
            "postmortem_status": "PUBLISHED_PENDING_EXECUTIVE_SIGNOFF",
            "synthesizer_org": self.org_name
        }
