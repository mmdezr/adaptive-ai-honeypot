import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === 1. Cargar dataset completo reconstruido ===
df = pd.read_csv("metrics_sessions_completo.csv")

# Convertir fechas
df["start"] = pd.to_datetime(df["start"], utc=True)

# === 2. Clasificación en fases ===
fecha_cambio = pd.Timestamp("2025-10-30 12:05:00", tz="UTC")
df["fase"] = np.where(df["start"] < fecha_cambio, "Estatico", "Dinamico")

# Fecha diaria (sin horas)
df["dia"] = df["start"].dt.date

# === 3. Agrupación diaria por fase ===
agrupado = df.groupby(["fase", "dia"]).agg(
    sesiones_dia=("session_id", "count"),
    comandos_dia=("n_commands_total", "sum"),
    descargas_dia=("attempted_download", "sum"),
    ips_dia=("src_ip", "nunique"),
    duracion_media_sesion=("duration_s", "mean"),
).reset_index()

# === 4. Calcular medias diarias por fase ===
medias = agrupado.groupby("fase").agg(
    media_sesiones_dia=("sesiones_dia", "mean"),
    media_comandos_dia=("comandos_dia", "mean"),
    media_descargas_dia=("descargas_dia", "mean"),
    media_ips_dia=("ips_dia", "mean"),
    duracion_media_sesion=("duracion_media_sesion", "mean"),
)

print("\n=== MEDIA DIARIA POR FASE ===")
print(medias)

# === 5. Gráficos (barras) ===

def plot_bar(df, col, titulo, ylabel, filename):
    plt.figure(figsize=(6,4))
    plt.bar(df.index, df[col])
    plt.title(titulo)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"[OK] Generado {filename}")

plot_bar(medias, "media_sesiones_dia",
         "Sesiones por día (media)", "Sesiones/día",
         "media_sesiones_dia.png")

plot_bar(medias, "media_comandos_dia",
         "Comandos por día (media)", "Comandos/día",
         "media_comandos_dia.png")

plot_bar(medias, "media_descargas_dia",
         "Descargas por día (media)", "Descargas/día",
         "media_descargas_dia.png")

plot_bar(medias, "media_ips_dia",
         "IPs únicas por día (media)", "IPs únicas/día",
         "media_ips_dia.png")

plot_bar(medias, "duracion_media_sesion",
         "Duración media de sesión", "Segundos",
         "duracion_media_sesion_RECALCULADA.png")

print("\n=== GRÁFICOS GENERADOS CON MEDIAS DIARIAS ===")
