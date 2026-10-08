import subprocess
import re
import json
from collections import Counter
from datetime import datetime

# Read real SSH logs from Kali
result = subprocess.run(
    ["sudo", "journalctl", "-u", "ssh", "--no-pager", "-n", "200"],
    capture_output=True,
    text=True
)

logs = result.stdout.splitlines()

failed_ips = []
events = []

for line in logs:

    # Failed SSH authentication
    if "Failed password" in line:
        match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line)

        if match:
            ip = match.group(1)
            failed_ips.append(ip)

            events.append({
                "type": "Failed SSH Login",
                "ip": ip,
                "log": line
            })

# Count failures per IP
counts = Counter(failed_ips)

threats = []

for ip, count in counts.items():
    if count >= 3:
        threats.append({
            "severity": "HIGH",
            "type": "Possible SSH Brute Force",
            "ip": ip,
            "attempts": count
        })

# Dashboard data
dashboard_data = {
    "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "events_analyzed": len(logs),
    "failed_logins": len(failed_ips),
    "threats": len(threats),
    "threat_details": threats,
    "recent_events": events[-10:]
}

with open("reports/dashboard_data.json", "w") as f:
    json.dump(dashboard_data, f, indent=4)

print("=" * 60)
print("SentinelLog - Security Log Analyzer")
print("=" * 60)

print(f"\nEvents analyzed : {len(logs)}")
print(f"Failed logins   : {len(failed_ips)}")
print(f"Threats detected: {len(threats)}")

for threat in threats:
    print("\n[HIGH] Possible SSH Brute Force")
    print(f"Source IP       : {threat['ip']}")
    print(f"Failed attempts : {threat['attempts']}")

print("\nAnalysis completed.")
