import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

LOG_PATH = "adaptation.log"

pattern = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ INFO Perfil aplicado: (?P<perfil>\w+)"
)

timestamps = []
perfiles = []

with open(LOG_PATH, "r") as f:
    for line in f:
        m = pattern.search(line)
        if m:
            timestamps.append(datetime.strptime(m.group("timestamp"), "%Y-%m-%d %H:%M:%S"))
            perfiles.append(m.group("perfil"))

df = pd.DataFrame({"timestamp": timestamps, "perfil": perfiles})
df = df.sort_values("timestamp")

# Mapa de colores
color_map = {
    "conservador": "#1f77b4",
    "convincente": "#2ca02c",
    "vulnerable":  "#d62728",
}

plt.figure(figsize=(12, 5))
plt.scatter(df["timestamp"], df["perfil"], c=df["perfil"].map(color_map), s=80)

plt.title("Evolución temporal de los perfiles aplicados por el controlador LinUCB")
plt.xlabel("Tiempo")
plt.ylabel("Perfil aplicado")

# mejora visual: líneas
plt.plot(df["timestamp"], df["perfil"], alpha=0.3, color="gray")

plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig("evolucion_perfiles_actualizada.png", dpi=300)

print("[+] Gráfica guardada como evolucion_perfiles_actualizada.png")
