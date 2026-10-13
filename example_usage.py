from client import EnterpriseIncidentPostmortemRootCauseSynthesizer

def main():
    synth = EnterpriseIncidentPostmortemRootCauseSynthesizer()
    payload = {
        "incident_id": "INC-7741",
        "title": "WeChat Work Integration Webhook Cascade Drop",
        "severity": "P1",
        "alarms": [
            {"timestamp_epoch": 1760000000, "service": "token-verifier", "metric": "memory_leak_oom"},
            {"timestamp_epoch": 1760000020, "service": "msg-router", "metric": "queue_overflow"}
        ],
        "service_dependencies": {
            "token-verifier": ["msg-router", "audit-logger"],
            "msg-router": ["bot-dispatcher"]
        },
        "suspected_trigger": "Cert Renewal Script"
    }
    report = synth.synthesize_postmortem(payload)
    print(f"=== Postmortem Report: {report['incident_id']} ({report['severity']}) ===")
    print(f"Root Cause Service: {report['root_service']}")
    print(f"Blast Radius ({report['blast_radius_service_count']} svcs): {', '.join(report['cascading_blast_radius'])}")
    print("\nFive Whys:")
    for why in report['five_whys_analysis']:
        print(f"  {why}")

if __name__ == "__main__":
    main()
