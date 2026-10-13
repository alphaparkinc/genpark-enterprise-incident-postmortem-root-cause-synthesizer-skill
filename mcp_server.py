#!/usr/bin/env python3
import json
import sys
from client import EnterpriseIncidentPostmortemRootCauseSynthesizer

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        synth = EnterpriseIncidentPostmortemRootCauseSynthesizer()
        sample = {
            "incident_id": "INC-2026-10",
            "title": "Checkout Payment Gateway 502 Outage",
            "severity": "P0",
            "alarms": [
                {"timestamp_epoch": 1728734000, "service": "payment-auth", "metric": "cpu_98pct"},
                {"timestamp_epoch": 1728733980, "service": "db-billing-shard-1", "metric": "lock_wait_timeout"}
            ],
            "service_dependencies": {
                "db-billing-shard-1": ["payment-auth", "ledger-sync"],
                "payment-auth": ["checkout-ui"]
            },
            "suspected_trigger": "Hotfix v2.4.9 Rollout"
        }
        res = synth.synthesize_postmortem(sample)
        assert res["root_service"] == "db-billing-shard-1"
        assert len(res["cascading_blast_radius"]) >= 2
        print(f"[TEST PASS] Incident Postmortem Synthesized: {res['incident_id']} (Blast: {res['blast_radius_service_count']} svcs)")
        sys.exit(0)

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            if method == "initialize":
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"serverInfo": {"name": "genpark-postmortem-synthesizer", "version": "1.0.0"}}}))
            elif method == "tools/list":
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": [{"name": "synthesize_postmortem", "description": "Synthesize SRE incident root cause postmortem"}]}}))
            elif method == "tools/call":
                args = req.get("params", {}).get("arguments", {})
                synth = EnterpriseIncidentPostmortemRootCauseSynthesizer()
                out = synth.synthesize_postmortem(args.get("incident_data", {}))
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(out)}]}}))
            else:
                print(json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
