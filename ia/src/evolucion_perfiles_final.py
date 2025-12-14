import re
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

LOGFILE = "adaptation.log"

# -------------------------------------------------------------
# 1. Leer y parsear adaptation.log
# -------------------------------------------------------------
pat = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ INFO Perfil aplicado: (?P<perf>\w+)'
)

rows = []
with open(LOGFILE, "r") as f:
    for line in f:
        m = pat.search(line)
        if m:
            ts = datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S")
            perfil = m.group("perf")
            rows.append((ts, perfil))

df = pd.DataFrame(rows, columns=["timestamp", "perfil"])

# -------------------------------------------------------------
# 2. Filtrar fechas: 1 noviembre → 14 noviembre
# -------------------------------------------------------------
start = datetime(2025, 11, 1)
end = datetime(2025, 11, 14, 23, 59, 59)
df = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]

df["date"] = df["timestamp"].dt.date

# Orden deseado
perfil_order = ["conservador", "convincente", "vulnerable"]
df["perfil"] = pd.Categorical(df["perfil"], categories=perfil_order, ordered=True)

# -------------------------------------------------------------
# 3. FIGURA A — Heatmap por día
# -------------------------------------------------------------
counts = df.groupby(["date", "perfil"]).size().unstack(fill_value=0)

plt.figure(figsize=(14, 5))
sns.heatmap(counts.T, cmap="YlOrRd", linewidths=0.2, annot=False)
plt.title("Actividad diaria de perfiles aplicados (1–14 noviembre)")
plt.ylabel("Perfil")
plt.xlabel("Fecha")
plt.tight_layout()
plt.savefig("heatmap_perfiles.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# 4. FIGURA B — Timeline simplificado
# -------------------------------------------------------------
plt.figure(figsize=(14, 4))
colors = {"conservador": "steelblue",
          "convincente": "green",
          "vulnerable": "red"}

for perfil in perfil_order:
    sub = df[df["perfil"] == perfil]
    plt.scatter(sub["timestamp"], [perfil] * len(sub), 
                s=10, color=colors[perfil], label=perfil)

plt.yticks(perfil_order)
plt.title("Cambios de perfil aplicados por el honeypot (1–14 noviembre)")
plt.xlabel("Tiempo")
plt.tight_layout()
plt.savefig("timeline_perfiles.png", dpi=300)
plt.close()

print("[+] Figuras generadas: heatmap_perfiles.png, timeline_perfiles.png")
