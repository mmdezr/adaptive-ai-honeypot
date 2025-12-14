import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================
#   CARGA DE DATOS
# ============================
df = pd.read_csv("metrics_sessions_completo.csv")

# Asegurar formato datetime con zona horaria
df["start"] = pd.to_datetime(df["start"], utc=True)

# ============================
#   FILTRO MIXTO
#   (duración >= 2s OR >=1 comando)
# ============================

df_filtrado = df[
    (df["duration_s"] >= 2) | 
    (df["n_commands_total"] >= 1)
].copy()

print(f"Sesiones totales originales: {len(df)}")
print(f"Sesiones tras filtro mixto:  {len(df_filtrado)}")

# ============================
#   DIVISIÓN EN FASES
# ============================

fecha_cambio = pd.Timestamp("2025-10-30 12:05:00", tz="UTC")

df_filtrado["fase"] = np.where(
    df_filtrado["start"] < fecha_cambio,
    "Estatico",
    "Dinamico"
)

# ============================
#   IGUALAR DURACIÓN TEMPORAL
# ============================

# Intervalo estatico (fin)
fecha_fin_estatico = fecha_cambio

# Intervalo dinamico (fin del dataset)
fecha_fin_dinamico = df_filtrado["start"].max()

# Duración de la fase estática
duracion_estatico = (fecha_fin_estatico - df_filtrado[df_filtrado["fase"] == "Estatico"]["start"].min())

# Nueva fecha fin para la fase dinámica para igualar duración
fecha_inicio_dinamico = df_filtrado[df_filtrado["fase"] == "Dinamico"]["start"].min()
fecha_limite_dinamico = fecha_inicio_dinamico + duracion_estatico

df_filtrado["usar_en_comparacion"] = np.where(
    (df_filtrado["fase"] == "Estatico") |
    ((df_filtrado["fase"] == "Dinamico") & (df_filtrado["start"] <= fecha_limite_dinamico)),
    True,
    False
)

df_comp = df_filtrado[df_filtrado["usar_en_comparacion"]].copy()

print("\n=== Fases igualadas temporalmente ===")
print(f"Estático: desde {df_comp[df_comp['fase']=='Estatico']['start'].min()} "
      f"hasta {df_comp[df_comp['fase']=='Estatico']['start'].max()}")
print(f"Dinámico: desde {df_comp[df_comp['fase']=='Dinamico']['start'].min()} "
      f"hasta {df_comp[df_comp['fase']=='Dinamico']['start'].max()}")


# ============================
#   FUNCIONES
# ============================

def media_truncada(series, trim=0.05):
    """Media sin outliers (5% por cada lado)."""
    s = series.sort_values()
    n = len(s)
    k = int(n * trim)
    if n <= 2*k:
        return s.mean()
    return s.iloc[k:-k].mean()


# ============================
#   CÁLCULO DE MÉTRICAS
# ============================

resultados = {}

for fase in ["Estatico", "Dinamico"]:
    df_fase = df_comp[df_comp["fase"] == fase]

    total_sesiones = len(df_fase)

    # ---- DESCARGAS ----
    total_descargas = df_fase["attempted_download"].sum()
    dias_con_descargas = df_fase[df_fase["attempted_download"] > 0]["start"].dt.date.nunique()
    descargas_por_sesion = total_descargas / total_sesiones if total_sesiones > 0 else 0
    descargas_por_1000 = descargas_por_sesion * 1000

    # ---- IPs ÚNICAS ----
    ips_unicas = df_fase["src_ip"].nunique()
    ips_por_1000 = ips_unicas / total_sesiones * 1000 if total_sesiones > 0 else 0

    # ---- DURACIÓN ----
    dur = df_fase["duration_s"]
    dur_mediana = dur.median()
    dur_p90 = dur.quantile(0.90)
    dur_media_truncada = media_truncada(dur, 0.05)

    resultados[fase] = {
        "Sesiones totales": total_sesiones,
        "Descargas totales": total_descargas,
        "Días con descargas": dias_con_descargas,
        "Descargas por sesión": descargas_por_sesion,
        "Descargas por 1000 sesiones": descargas_por_1000,
        "IPs únicas totales": ips_unicas,
        "IPs por 1000 sesiones": ips_por_1000,
        "Duración mediana (s)": dur_mediana,
        "Duración p90 (s)": dur_p90,
        "Duración media truncada (s)": dur_media_truncada,
    }

# ============================
#   EXPORTAR CSV
# ============================

df_res = pd.DataFrame(resultados).T
df_res.to_csv("comparativa_fases_avanzada_filtrada.csv")

print("\n=== RESULTADOS GUARDADOS EN comparativa_fases_avanzada_filtrada.csv ===")
print(df_res)

# ============================
#   GRÁFICAS
# ============================

def grafico_barra(metric):
    plt.figure(figsize=(7,4))
    plt.bar(df_res.index, df_res[metric], color=["steelblue", "darkorange"])
    plt.title(metric)
    plt.ylabel(metric)
    plt.tight_layout()
    plt.savefig(metric.replace(" ", "_").replace("(", "").replace(")", "") + "_filtrado.png")
    plt.close()

for col in df_res.columns:
    grafico_barra(col)

print("\n=== Gráficas (filtradas) generadas ===")
