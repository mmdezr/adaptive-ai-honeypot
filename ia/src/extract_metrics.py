#!/usr/bin/env python3
import json
import pandas as pd
import glob

# Ruta de logs de Cowrie
LOG_PATH = "/home/miriam/cowrie-logs/cowrie.json"

rows = []
with open(LOG_PATH) as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("eventid") == "cowrie.session.closed":
                rows.append({
                    "session": data["session"],
                    "start": data.get("starttime"),
                    "end": data.get("endtime"),
                    "duration": data.get("duration"),
                    "commands": len(data.get("commands", [])),
                    "unique_cmds": len(set(cmd["input"] for cmd in data.get("commands", []))) if "commands" in data else 0,
                    "login_success": 1 if data.get("loggedin", False) else 0,
                    "src_ip": data.get("src_ip")
                })
        except Exception:
            continue

df = pd.DataFrame(rows)
df.to_csv("/home/miriam/honeypot-ai/metrics_sessions.csv", index=False)
print(f"✅ Guardado metrics_sessions.csv con {len(df)} sesiones.")
