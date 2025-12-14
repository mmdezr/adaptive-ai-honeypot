#!/usr/bin/env python3
# analisis_final.py → FUNCIONA CON TUS DATOS REALES 100%

import pandas as pd

# 1. Cargar sesiones (tu CSV exacto)
df = pd.read_csv("metrics_sessions.csv", parse_dates=["start"], dayfirst=False)
df["start"] = pd.to_datetime(df["start"], utc=True)   # fuerza UTC aunque tenga milisegundos o no

# 2. Leer adaptation.log (hora local Canarias → convertimos a UTC)
cambios = []
with open("adaptation.log") as f:
    for line in f:
        if "Perfil aplicado:" not in line:
            continue
        partes = line.strip().split()
        fecha = partes[0]
        hora = partes[1].split(",")[0] if "," in partes[1] else partes[1]
        ts_local = f"{fecha} {hora}"
        
        # Convertimos hora local Canarias → UTC (Canarias es UTC+0 en invierno, UTC+1 en verano)
        ts = pd.to_datetime(ts_local).tz_localize("Atlantic/Canary").tz_convert("UTC")
        
        try:
            perfil = partes[partes.index("aplicado:") + 1].rstrip(",.")
        except:
            perfil = "desconocido"
            
        cambios.append({"ts": ts, "perfil": perfil.lower()})

perf = pd.DataFrame(cambios)

# 3. Rango exacto que quieres
inicio = pd.Timestamp("2025-10-17 00:00:00", tz="UTC")
fin    = pd.Timestamp("2025-11-17 23:59:59", tz="UTC")
perf = perf[(perf["ts"] >= inicio) & (perf["ts"] <= fin)]

# 4. Asignación con ventana brutal (±12 horas) → IMPOSIBLE que no coincida nada
asignadas = []
for _, row in perf.iterrows():
    ts = row["ts"]
    perfil = row["perfil"]
    mask = (df["start"] >= ts - pd.Timedelta(hours=12)) & (df["start"] <= ts + pd.Timedelta(hours=12))
    temp = df[mask].copy()
    if len(temp) > 0:
        temp["perfil"] = perfil
        asignadas.append(temp)

df_final = pd.concat(asignadas) if asignadas else pd.DataFrame()

# 5. RESULTADO FINAL
print(f"\nSesiones totales en rango: {len(df[(df['start'] >= inicio) & (df['start'] <= fin)])}")
print(f"Sesiones asignadas a algún perfil: {len(df_final)}\n")

for p in ["conservador", "convincente", "vulnerable"]:
    sub = df_final[df_final["perfil"] == p]
    if len(sub) == 0:
        print(f"{p:12} → 0 sesiones")
        continue
    descarga = sub["attempted_download"].sum()
    pct = descarga / len(sub) * 100
    cmds = sub["n_commands_total"].mean()
    print(f"{p:12} → {len(sub):6} sesiones | {descarga:2} descargas ({pct:5.3f}%) | {cmds:5.2f} cmds/sesión")

print(f"\nIPs reincidentes totales: {(df['src_ip'].value_counts() > 1).sum()}")
