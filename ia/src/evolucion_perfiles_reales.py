import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

LOGFILE = "adaptation.log"

# ----------------------------
# 1. Cargar y parsear el log
# ----------------------------
entries = []
with open(LOGFILE) as f:
    for line in f:
        if "Perfil aplicado:" in line:
            try:
                ts_str = line.split(" INFO ")[0]
                perfil = line.split("Perfil aplicado:")[1].strip().split()[0]
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S,%f")
                entries.append((ts, perfil))
            except:
                continue

df = pd.DataFrame(entries, columns=["timestamp", "perfil"])
df = df.sort_values("timestamp").reset_index(drop=True)

# ----------------------------------------
# 2. Detectar cambios reales: salto > 10s
# ----------------------------------------
df["delta"] = df["timestamp"].diff().dt.total_seconds().fillna(9999)

df_real = df[df["delta"] > 10].copy()
df_real.reset_index(drop=True, inplace=True)

print("[+] Cambios reales detectados:", len(df_real))

# ----------------------------------------
# 3. Guardar tabla resumen por día
# ----------------------------------------
df_real["date"] = df_real["timestamp"].dt.date

# Último perfil aplicado ese día = perfil final real
perfiles_por_dia = df_real.groupby("date")["perfil"].last().reset_index()
perfiles_por_dia.to_csv("perfiles_por_dia.csv", index=False)

print("[+] Tabla guardada como perfiles_por_dia.csv")

# ----------------------------------------
# 4. Timeline de cambios reales
# ----------------------------------------
perfil_map = {"conservador": 0, "convincente": 1, "vulnerable": 2}
df_real["perfil_num"] = df_real["perfil"].map(perfil_map)

plt.figure(figsize=(14,6))
plt.scatter(df_real["timestamp"], df_real["perfil_num"],
            c=df_real["perfil_num"], cmap="viridis", s=80)

plt.yticks([0,1,2], ["conservador", "convincente", "vulnerable"])
plt.xlabel("Tiempo")
plt.ylabel("Perfil aplicado")
plt.title("Cambios REALES de perfil aplicados por el honeypot (cron)")
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("timeline_perfiles_reales.png")
print("[+] Gráfica guardada como timeline_perfiles_reales.png")
