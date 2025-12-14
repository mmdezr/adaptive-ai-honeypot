import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === Cargar datos ===
df = pd.read_csv("metrics_sessions_completo.csv")

# Convertir fechas y forzar zona horaria UTC
df["start"] = pd.to_datetime(df["start"], utc=True, errors="coerce")
df["end"] = pd.to_datetime(df["end"], utc=True, errors="coerce")

# Fecha de cambio convertida a UTC
fecha_cambio = pd.Timestamp("2025-10-30 12:05:00", tz="UTC")

# Clasificar sesiones
df["fase"] = np.where(df["start"] < fecha_cambio, "Estatico", "Dinamico")

# === Sesiones por día ===
df["dia"] = df["start"].dt.date
sesiones_por_dia = df.groupby(["dia", "fase"]).size().unstack(fill_value=0)

# === Duración media ===
duracion_media = df.groupby("fase")["duration_s"].mean()

# === Comandos ===
comandos_media = df.groupby("fase")["n_commands_total"].mean()

# === Descargas ===
pct_descargas = df.groupby("fase")["attempted_download"].mean() * 100

# === IPs únicas ===
ips_unicas = df.groupby("fase")["src_ip"].nunique()

# ===== GRAFICAS =====

# 1) Sesiones por día
plt.figure(figsize=(12,6))
if "Estatico" in sesiones_por_dia.columns:
    plt.plot(sesiones_por_dia.index, sesiones_por_dia["Estatico"], label="Estático")
else:
    print("Advertencia: no hay fase Estático en los datos.")

if "Dinamico" in sesiones_por_dia.columns:
    plt.plot(sesiones_por_dia.index, sesiones_por_dia["Dinamico"], label="Dinámico")

plt.xticks(rotation=45)
plt.title("Sesiones por día: Estático vs Dinámico")
plt.ylabel("Número de sesiones")
plt.legend()
plt.tight_layout()
plt.savefig("comparativa_sesiones.png")
plt.close()

# 2) Duración media
plt.figure(figsize=(6,5))
duracion_media.plot(kind="bar")
plt.title("Duración media de sesiones (s)")
plt.ylabel("Segundos")
plt.tight_layout()
plt.savefig("duracion_media.png")
plt.close()

# 3) Comandos
plt.figure(figsize=(6,5))
comandos_media.plot(kind="bar")
plt.title("Media de comandos ejecutados por sesión")
plt.ylabel("Comandos")
plt.tight_layout()
plt.savefig("comandos_media.png")
plt.close()

# 4) Descargas
plt.figure(figsize=(6,5))
pct_descargas.plot(kind="bar")
plt.title("Porcentaje de sesiones con descarga")
plt.ylabel("%")
plt.tight_layout()
plt.savefig("descargas_pct.png")
plt.close()

# 5) IPs únicas
plt.figure(figsize=(6,5))
ips_unicas.plot(kind="bar")
plt.title("IPs únicas por fase")
plt.ylabel("Cantidad")
plt.tight_layout()
plt.savefig("ips_unicas.png")
plt.close()

print("=== Gráficas generadas ===")
