import json
import pandas as pd
import os
from datetime import datetime

LOG_DIR = "/home/miriam/cowrie-logs"

eventos_sesion = {}

def procesar_archivo(ruta):
    with open(ruta, "r") as f:
        for linea in f:
            try:
                evento = json.loads(linea)
            except:
                continue

            sid = evento.get("session")
            if not sid:
                continue

            if sid not in eventos_sesion:
                eventos_sesion[sid] = {
                    "session_id": sid,
                    "src_ip": None,
                    "start": None,
                    "end": None,
                    "commands": [],
                    "attempted_download": 0,
                }

            # origen
            if evento["eventid"] == "cowrie.session.connect":
                eventos_sesion[sid]["src_ip"] = evento.get("src_ip")
                eventos_sesion[sid]["start"] = evento.get("timestamp")

            # comandos ejecutados
            if evento["eventid"] == "cowrie.command.input":
                cmd = evento.get("input", "")
                eventos_sesion[sid]["commands"].append(cmd)

            # descargas
            if evento["eventid"] in ("cowrie.session.file_download", "cowrie.session.file_upload"):
                eventos_sesion[sid]["attempted_download"] += 1

            # cierre de sesión
            if evento["eventid"] == "cowrie.session.closed":
                eventos_sesion[sid]["end"] = evento.get("timestamp")


# Procesar todos los JSON
for archivo in sorted(os.listdir(LOG_DIR)):
    if archivo.startswith("cowrie.json"):
        print("Procesando:", archivo)
        procesar_archivo(os.path.join(LOG_DIR, archivo))

# Construir DataFrame
filas = []
for sid, data in eventos_sesion.items():
    start = pd.to_datetime(data["start"], errors="coerce")
    end = pd.to_datetime(data["end"], errors="coerce")

    dur = None
    if pd.notnull(start) and pd.notnull(end):
        dur = (end - start).total_seconds()

    filas.append({
        "session_id": sid,
        "src_ip": data["src_ip"],
        "start": start,
        "end": end,
        "duration_s": dur if dur else 0,
        "n_commands_total": len(data["commands"]),
        "n_unique_commands": len(set(data["commands"])),
        "attempted_download": 1 if data["attempted_download"] > 0 else 0,
    })

df = pd.DataFrame(filas)
df = df.sort_values("start")

df.to_csv("metrics_sessions_completo.csv", index=False)

print("=== Archivo generado: metrics_sessions_completo.csv ===")
print("Sesiones totales:", len(df))
