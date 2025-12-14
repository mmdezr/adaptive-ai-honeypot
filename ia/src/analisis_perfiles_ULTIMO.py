#!/usr/bin/env python3
# analisis_perfiles_CORRECTO_Y_FINAL.py
# Funciona con tus datos reales (17 oct – 17 nov 2025)

import pandas as pd

# 1. Cargar sesiones (columna "start" está en UTC)
df = pd.read_csv("metrics_sessions.csv")
df["start"] = pd.to_datetime(df["start"], utc=True)
print(f"Sesiones totales: {len(df)}")

# 2. Leer adaptation.log (tus logs están en hora local Canarias → UTC+0 o +1)
cambios = []
with open("adaptation.log") as f:
    for line in f:
        if "Perfil aplicado:" not in line:
            continue
        partes = line.strip().split()
        fecha = partes[0]
        hora_completa = partes[1]
        hora = hora_completa.split(",")[0] if "," in hora_completa else hora_completa
        ts_local_str = f"{fecha} {hora}"
        
        # Convertimos asumiendo que el log está en hora local de Canarias
        # Forzamos zona horaria local y luego convertimos a UTC
        ts_local = pd.to_datetime(ts_local_str, utc=False)  # interpreta como local
        ts_utc = ts_local.tz_localize("Atlantic/Canary").tz_convert("UTC")
        
        try:
            perfil = partes[partes.index("aplicado:") + 1].rstrip(",.")
        except:
            perfil = "desconocido"
            
        cambios.append({"ts_utc": ts_utc, "perfil": perfil.lower()})

perf = pd.DataFrame(cambios)
print(f"Cambios de perfil detectados: {len(perf)}")

# 3. Rango 17 oct – 17 nov 2025
inicio = pd.Timestamp("2025-10-17 00:00:00", tz="UTC")
fin    = pd.Timestamp("2025-11-17 23:59:59", tz="UTC")
perf = perf[(perf["ts_utc"] >= inicio) & (perf["ts_utc"] <= fin)]

# 4. Asignar perfil a cada sesión (ventana muy amplia por si hay desfase residual)
asignadas = []
for _, cambio in perf.iterrows():
    ts = cambio["ts_utc"]
    perfil = cambio["perfil"]
    # Ventana ±3 horas para cubrir cualquier desfase residual
    mask = (df["start"] >= ts - pd.Timedelta(hours=3)) & \
           (df["start"] <= ts + pd.Timedelta(hours=3))
    temp = df[mask].copy()
    if not temp.empty:
        temp["perfil"] = perfil
        asignadas.append(temp)

df_final = pd.concat(asignadas, ignore_index=True) if asignadas else pd.DataFrame()
print(f"Sesiones asignadas a algún perfil: {len(df_final)}")

# 5. Tabla final
resultados = []
for p in ["conservador", "convincente", "vulnerable"]:
    sub = df_final[df_final["perfil"] == p]
    n = len(sub)
    descarga = sub["attempted_download"].mean() * 100 if n > 0 else 0
    comandos = sub["n_commands_total"].mean() if n > 0 else 0
    resultados.append([p, n, round(descarga, 3), round(comandos, 2)])

out = pd.DataFrame(resultados, columns=["perfil", "sesiones", "%descarga", "cmds/sesión"])
print("\n" + "="*65)
print("RESULTADOS REALES (17 oct – 17 nov 2025) – CORREGIDOS ZONA HORARIA")
print("="*65)
print(out.to_string(index=False))
print("="*65)
