import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === 1. Cargar datos ===
df = pd.read_csv("metrics_sessions.csv")

df["start"] = pd.to_datetime(df["start"], errors="coerce")
df["end"] = pd.to_datetime(df["end"], errors="coerce")

# Fecha clave: paso a dinámico
fecha_cambio = pd.Timestamp("2025-10-30 12:05:00")

df["fase"] = np.where(df["start"] < fecha_cambio, "Estatico", "Dinamico")

# === 2. Métricas agregadas por día ===
df["dia"] = df["start"].dt.date

sesiones_por_dia = df.groupby(["dia", "fase"]).size().unstack(fill_value=0)

# === 3. Duración media por fase ===
duracion_media = df.groupby("fase")["duration_s"].mean()

# === 4. Número medio de comandos ===
comandos_media = df.groupby("fase")["n_commands_total"].mean()

# === 5. Porcentaje de descargas ===
pct_descargas = df.groupby("fase")["attempted_download"].mean() * 100

# === 6. IPs únicas por fase ===
ips_unicas = df.groupby("fase")["src_ip"].nunique()

# ==========================
# ====  GENERAR GRÁFICAS ===
# ==========================

plt.figure(figsize=(12,6))
plt.plot(sesiones_por_dia.index, sesiones_por_dia["Estatico"], label="Estático")
plt.plot(sesiones_por_dia.index, sesiones_por_dia["Dinamico"], label="Dinámico")
plt.xticks(rotation=45)
plt.title("Sesiones por día: Estático vs Dinámico")
plt.ylabel("Número de sesiones")
plt.legend()
plt.tight_layout()
plt.savefig("comparativa_sesiones.png")
plt.close()

# Duración media
plt.figure(figsize=(6,5))
plt.bar(duracion_media.index, duracion_media.values)
plt.title("Duración media de las sesiones (s)")
plt.ylabel("Segundos")
plt.tight_layout()
plt.savefig("duracion_media.png")
plt.close()

# Comandos por fase
plt.figure(figsize=(6,5))
plt.bar(comandos_media.index, comandos_media.values)
plt.title("Comandos ejecutados (media por sesión)")
plt.ylabel("Comandos")
plt.tight_layout()
plt.savefig("comandos_media.png")
plt.close()

# Descargas por fase
plt.figure(figsize=(6,5))
plt.bar(pct_descargas.index, pct_descargas.values)
plt.title("Descargas detectadas (%)")
plt.ylabel("Porcentaje")
plt.tight_layout()
plt.savefig("descargas_pct.png")
plt.close()

# IPs únicas
plt.figure(figsize=(6,5))
plt.bar(ips_unicas.index, ips_unicas.values)
plt.title("IPs únicas por fase")
plt.ylabel("Número de IPs")
plt.tight_layout()
plt.savefig("ips_unicas.png")
plt.close()

print("=== Gráficas generadas correctamente ===")
