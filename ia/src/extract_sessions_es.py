#!/usr/bin/env python3
# ===========================================================
# Extrae features de sesiones Cowrie desde Elasticsearch
# ===========================================================

from elasticsearch import Elasticsearch, helpers
import pandas as pd
from datetime import datetime
import json

# ⚙️ Configuración
ES_HOST = "http://localhost:9200"
ES_USER = "elastic"
ES_PASS = "dhUY8pgapvWm1_I4Gb4g"
INDEX = "logstash-cowrie-*"

# 🧠 Conexión al servidor Elasticsearch
es = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_USER, ES_PASS)
)

# 🧮 Diccionario acumulador
sessions = {}

# 📡 Consulta: obtenemos todos los eventos que contengan 'session' y 'message'
query = {
    "query": {
        "bool": {
            "must": [
                {"exists": {"field": "session"}},
                {"exists": {"field": "message"}}
            ]
        }
    }
}

# 🔄 Escaneo incremental (puede tardar según tamaño de índice)
for doc in helpers.scan(es, index=INDEX, query=query, _source=True):
    src = doc["_source"]

    # --- Manejo robusto del campo 'session' ---
    session_field = src.get("session")
    if isinstance(session_field, dict):
        sid = session_field.get("session") or session_field.get("id")
    else:
        sid = session_field or src.get("sessionid")

    if not sid:
        continue

    # Creamos la estructura base si no existe
    s = sessions.setdefault(sid, {
        "session_id": sid,
        "src_ip": None,
        "start": None,
        "end": None,
        "commands": [],
        "usernames": set(),
        "attempted_download": False
    })

    # Timestamps
    ts = src.get("@timestamp") or src.get("timestamp")
    if ts:
        try:
            t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if s["start"] is None or t < s["start"]:
                s["start"] = t
            if s["end"] is None or t > s["end"]:
                s["end"] = t
        except Exception:
            pass

    # IP origen
    s["src_ip"] = s["src_ip"] or src.get("src_ip") or (src.get("source", {}) or {}).get("ip")

    # Usuario
    if src.get("username"):
        s["usernames"].add(src["username"])

    # Comando
    msg = src.get("message", "")
    if "CMD:" in msg:
        cmd = msg.split("CMD:")[-1].strip()
        s["commands"].append(cmd)
        low = cmd.lower()
        if any(k in low for k in ["wget ", "curl ", "tftp ", "scp ", "nc ", "python -c", "perl -e"]):
            s["attempted_download"] = True

# 🧾 Convertimos a DataFrame
rows = []
for sid, s in sessions.items():
    if not s["start"] or not s["end"]:
        continue
    duration = (s["end"] - s["start"]).total_seconds()
    rows.append({
        "session_id": sid,
        "src_ip": s["src_ip"],
        "start": s["start"].isoformat(),
        "end": s["end"].isoformat(),
        "duration_s": int(duration),
        "n_commands_total": len(s["commands"]),
        "n_unique_commands": len(set(s["commands"])),
        "username_tried_count": len(s["usernames"]),
        "attempted_download": int(s["attempted_download"]),
    })

# 📊 Exportar resultados
df = pd.DataFrame(rows)
df.to_csv("cowrie_sessions.csv", index=False)
print(f"[+] Dataset creado: {len(df)} sesiones exportadas a cowrie_sessions.csv")
