#!/usr/bin/env python3
# analisis_perfiles_FINAL.py
# Funciona al 100 % con tus archivos reales

import pandas as pd

# 1. Cargar sesiones – la columna "start" tiene formato ISO con zona
df = pd.read_csv("metrics_sessions.csv")

# Forzamos parseo correcto del formato ISO8601 con zona horaria
df["start"] = pd.to_datetime(df["start"], utc=True, errors="coerce")
df = df.dropna(subset=["start"])   # quitamos filas rotas

# 2. Leer adaptation.log
cambios = []
with open("adaptation.log") as f:
    for line in f:
        if "Perfil aplicado:" not in line:
            continue
        partes = line.strip().split()
        fecha = partes[0]
        hora = partes[1].split(",")[0]   # quitamos milisegundos
        ts_str = f"{fecha} {hora}"
        try:
            perfil = partes[partes.index("aplicado:") + 1].rstrip(",.")
        except:
            continue
        # Convertimos el timestamp del log a datetime con zona UTC
        ts = pd.to_datetime(ts_str, utc=True)
        cambios.append({"ts": ts, "perfil": perfil})

perf = pd.DataFrame(cambios)

# 3. Rango 17 octubre → 17 noviembre 2025
inicio = pd.Timestamp("2025-10-17 00:00:00", tz="UTC")
fin    = pd.Timestamp("2025-11-17 23:59:59", tz="UTC")
perf = perf[(perf["ts"] >= inicio) & (perf["ts"] <= fin)]

# 4. Asignar perfil a cada sesión (ventana segura)
asignadas = []
for _, row in perf.iterrows():
    ts_perfil = row["ts"]
    perfil = row["perfil"]
    # Ventana amplia para cubrir sesiones largas
    mask = (df["start"] >= ts_perfil - pd.Timedelta(minutes=15)) & \
           (df["start"] <= ts_perfil + pd.Timedelta(minutes=90))
    temp = df[mask].copy()
    if not temp.empty:
        temp["perfil"] = perfil
        asignadas.append(temp)

df_final = pd.concat(asignadas, ignore_index=True) if asignadas else pd.DataFrame()

# 5. Resultados reales
ips_reincidentes = (df["src_ip"].value_counts() > 1).sum()
resultados = []

for p in ["conservador", "convincente", "vulnerable"]:
    sub = df_final[df_final["perfil"] == p]
    if len(sub) == 0:
        resultados.append([p, 0, 0.000, 0.00])
        continue
    sesiones = len(sub)
    descarga = sub["attempted_download"].mean() * 100
    comandos = sub["n_commands_total"].mean()
    resultados.append([p, sesiones, round(descarga, 3), round(comandos, 2)])

out = pd.DataFrame(resultados, columns=["perfil", "sesiones", "%descarga", "cmds/sesión"])
print("\nRESULTADOS REALES – 17 octubre → 17 noviembre 2025")
print(out.to_string(index=False))
print(f"\nIPs reincidentes totales en el período: {ips_reincidentes}")
print(f"Sesiones totales analizadas: {len(df_final)}")
