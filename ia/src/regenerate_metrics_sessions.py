import json
import pandas as pd
from datetime import datetime
from glob import glob

# Ruta real donde tienes cowrie.json
LOG_PATH = "/home/miriam/cowrie-logs/cowrie.json"

sessions = {}  # Diccionario: session_id -> info sesión

# ========================================
# 1. LEER cowrie.json LÍNEA A LÍNEA
# ========================================
with open(LOG_PATH, "r") as f:
    for line in f:
        try:
            event = json.loads(line.strip())
        except json.JSONDecodeError:
            continue

        sid = event.get("session")
        if not sid:
            continue

        eventid = event.get("eventid")
        timestamp = event.get("timestamp")

        if not timestamp:
            continue

        # Convertir timestamp ISO8601 Z a datetime
        ts = pd.to_datetime(timestamp, format="mixed", utc=True).tz_convert(None)

        # Si es una nueva sesión, inicializarla
        if sid not in sessions:
            sessions[sid] = {
                "session_id": sid,
                "src_ip": event.get("src_ip", ""),
                "start": ts,
                "end": ts,
                "n_commands_total": 0,
                "cmd_set": set(),
                "username_tried": set(),
                "attempted_download": 0
            }

        # Actualizar tiempo final
        if ts > sessions[sid]["end"]:
            sessions[sid]["end"] = ts

        # ==========================
        # 2. EVENTOS QUE IMPORTAN
        # ==========================

        # a) Comandos ejecutados
        if eventid == "cowrie.command.input":
            cmd = event.get("input", "")
            sessions[sid]["n_commands_total"] += 1
            if cmd:
                sessions[sid]["cmd_set"].add(cmd)

            # detección de descargas
            if any(x in cmd.lower() for x in ["wget", "curl", "fetch", "http"]):
                sessions[sid]["attempted_download"] = 1

        # b) Intentos de login -> usuarios usados
        if eventid in ("cowrie.login.failed", "cowrie.login.success"):
            user = event.get("username")
            if user:
                sessions[sid]["username_tried"].add(user)

# ========================================
# 3. CONVERTIR A DATAFRAME LIMPIO
# ========================================

rows = []
for sid, s in sessions.items():
    duration = (s["end"] - s["start"]).total_seconds()

    rows.append({
        "session_id": s["session_id"],
        "src_ip": s["src_ip"],
        "start": s["start"].isoformat(),
        "end": s["end"].isoformat(),
        "duration_s": int(duration),
        "n_commands_total": s["n_commands_total"],
        "n_unique_commands": len(s["cmd_set"]),
        "username_tried_count": len(s["username_tried"]),
        "attempted_download": s["attempted_download"]
    })

df = pd.DataFrame(rows)
df = df.sort_values("start")

# ========================================
# 4. GUARDAR CSV FINAL
# ========================================
df.to_csv("metrics_sessions.csv", index=False)

print("\n[OK] metrics_sessions.csv regenerado correctamente.")
print(f"Sesiones reconstruidas: {len(df)}")
print("Primeras filas:\n")
print(df.head())
