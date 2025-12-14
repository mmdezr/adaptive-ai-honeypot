#!/usr/bin/env python3
# ===========================================================
# Validación Estadística Rigurosa (Ventanas Temporales Iguales)
# ===========================================================

import pandas as pd
from scipy.stats import mannwhitneyu
import numpy as np

# 1. Cargar datos
df = pd.read_csv("metrics_sessions_completo.csv")
df["start"] = pd.to_datetime(df["start"], utc=True)

# 2. Definir fecha de corte
fecha_cambio = pd.Timestamp("2025-10-30 12:05:00", tz="UTC")

# 3. Lógica de Ventanas Temporales (Igual que en comparativa_fases_avanzada.py)
# -------------------------------------------------------------------------
# Calculamos la duración exacta de la fase estática para proyectarla en la dinámica
fecha_fin_estatico = fecha_cambio
# Filtramos primero la fase estática real para saber cuándo empezó
inicio_estatico = df[df["start"] < fecha_cambio]["start"].min()
duracion_fase = fecha_fin_estatico - inicio_estatico

# Definimos el límite de la fase dinámica para que dure lo mismo
inicio_dinamico = df[df["start"] >= fecha_cambio]["start"].min()
fecha_limite_dinamico = inicio_dinamico + duracion_fase

print(f"--- Ventanas de Análisis ({duracion_fase.days} días) ---")
print(f"Fase Estática: {inicio_estatico} a {fecha_fin_estatico}")
print(f"Fase Dinámica: {inicio_dinamico} a {fecha_limite_dinamico}")

# 4. Filtrar los datos exactos
# Fase Estática
datos_estaticos = df[df["start"] < fecha_cambio]["duration_s"]

# Fase Dinámica (¡OJO! Aplicamos el recorte de fecha límite)
datos_dinamicos = df[
    (df["start"] >= fecha_cambio) & 
    (df["start"] <= fecha_limite_dinamico)
]["duration_s"]

# -------------------------------------------------------------------------

print(f"\nMuestras Estáticas: {len(datos_estaticos)}")
print(f"Muestras Dinámicas: {len(datos_dinamicos)}")

# 5. Aplicar Test U de Mann-Whitney
stat, p_value = mannwhitneyu(datos_estaticos, datos_dinamicos, alternative='two-sided')

print("\n=== Resultados del Test U de Mann-Whitney (Ventanas Igualadas) ===")
print(f"Estadístico U: {stat}")
print(f"P-valor: {p_value:.5e}") # Notación científica

# 6. Verificación de Medianas (Deben coincidir con Tabla 4.2)
mediana_est = np.median(datos_estaticos)
mediana_din = np.median(datos_dinamicos)

print(f"\nMediana Estática: {mediana_est:.2f}s")
print(f"Mediana Dinámica: {mediana_din:.2f}s")

if p_value < 0.05:
    print("\n[CONCLUSIÓN] Diferencia estadísticamente significativa.")
else:
    print("\n[CONCLUSIÓN] No se rechaza la hipótesis nula.")
