import pandas as pd
import re

# ======================================================
# 1. CARGAR Y NORMALIZAR metrics_sessions.csv
# ======================================================

df = pd.read_csv("metrics_sessions.csv")

# Convertir fechas mezcladas a datetime
df["start"] = pd.to_datetime(df["start"], format="mixed", errors="coerce")
df["end"]   = pd.to_datetime(df["end"],   format="mixed", errors="coerce")

# Asegurar que todas las fechas sean tz-naive (sin zona horaria)
if df["start"].dt.tz is not None:
    df["start"] = df["start"].dt.tz_convert(None)
if df["end"].dt.tz is not None:
    df["end"] = df["end"].dt.tz_convert(None)

# Filtrar solo periodo adaptativo: octubre-noviembre 2025
df = df[(df["start"] >= "2025-10-01") & (df["start"] < "2025-12-01")]


# ======================================================
# 2. CARGAR Y NORMALIZAR adaptation.log
# ======================================================

pat = re.compile(
    r"^(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Perfil aplicado: (?P<perfil>\w+)"
)

rows = []
with open("adaptation.log", "r") as f:
    for line in f:
        m = pat.search(line)
        if m:
            dt = pd.to_datetime(m.group("datetime"), format="mixed", errors="coerce")
            perfil = m.group("perfil")
            rows.append({"datetime": dt, "perfil": perfil})

df_adapt = pd.DataFrame(rows)

# Eliminar filas inválidas
df_adapt = df_adapt.dropna(subset=["datetime"])

# Convertir a tz-naive
if df_adapt["datetime"].dt.tz is not None:
    df_adapt["datetime"] = df_adapt["datetime"].dt.tz_localize(None)

# Filtrar por periodo adaptativo
df_adapt = df_adapt[
    (df_adapt["datetime"] >= "2025-10-01") &
    (df_adapt["datetime"] < "2025-12-01")
]


# ======================================================
# 3. AGRUPAR POR VENTANA DE 30 MINUTOS
# ======================================================

df_adapt["ventana"] = df_adapt["datetime"].dt.floor("30min")

# Quedarse con LA ÚLTIMA decisión por ventana
df_last = (
    df_adapt.sort_values("datetime")
            .groupby("ventana")
            .tail(1)
            .reset_index(drop=True)
)

# Crear intervalos entre ventanas consecutivas
df_last = df_last.sort_values("ventana").reset_index(drop=True)

valid_from = df_last["ventana"]
valid_to = list(valid_from[1:]) + [pd.Timestamp("2025-12-01 00:00:00")]

df_last["valid_from"] = valid_from
df_last["valid_to"] = valid_to

# Asegurar tz-naive también aquí
df_last["valid_from"] = df_last["valid_from"].dt.tz_localize(None)
df_last["valid_to"]   = df_last["valid_to"].dt.tz_localize(None)


# ======================================================
# 4. ASIGNAR PERFIL A CADA SESIÓN
# ======================================================

def asignar_perfil(ts):
    row = df_last[(ts >= df_last["valid_from"]) & (ts < df_last["valid_to"])]
    if len(row) > 0:
        return row.iloc[0]["perfil"]
    return "desconocido"

df["perfil"] = df["start"].apply(asignar_perfil)


# ======================================================
# 5. MÉTRICAS POR PERFIL
# ======================================================

resumen = (
    df.groupby("perfil")
      .agg(
          sesiones=("session_id", "count"),
          media_comandos=("n_commands_total", "mean"),
          pct_descargas=("attempted_download", "mean"),
          media_duracion=("duration_s", "mean"),
          ips_unicas=("src_ip", lambda x: x.nunique())
      )
)

# Guardar CSVs
df.to_csv("sessions_con_perfil.csv", index=False)
resumen.to_csv("resumen_perfiles.csv")

# ======================================================
# 6. OUTPUT
# ======================================================

print("\n=== Ventanas detectadas (última decisión por ventana) ===")
print(df_last[["ventana", "perfil"]])

print("\n=== Resumen por perfil ===")
print(resumen)

print("\nArchivos generados:")
print(" - sessions_con_perfil.csv")
print(" - resumen_perfiles.csv")
