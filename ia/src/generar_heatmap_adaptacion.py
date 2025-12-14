import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re

# Ruta del adaptation.log
LOG_PATH = "/home/miriam/honeypot-ai/adaptation.log"

# Expresión regular para extraer timestamp y perfil
regex = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),.*Perfil aplicado: (\w+)")

registros = []

with open(LOG_PATH, "r") as f:
    for line in f:
        match = regex.match(line)
        if match:
            timestamp = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
            perfil = match.group(2).lower()  # conservador, convincente, vulnerable
            registros.append((timestamp, perfil))

# Convertir a DataFrame
df = pd.DataFrame(registros, columns=["timestamp", "perfil"])

# Filtrar rango
inicio = datetime(2025, 10, 30)
fin = datetime(2025, 11, 17, 23, 59, 59)
df = df[(df["timestamp"] >= inicio) & (df["timestamp"] <= fin)]

# Columna día
df["dia"] = df["timestamp"].dt.date

# Crear tabla de frecuencias por día
tabla = df.groupby(["dia", "perfil"]).size().unstack(fill_value=0)

# Asegurar que todos los días existan en el índice
todos_los_dias = pd.date_range(inicio, fin).date
tabla = tabla.reindex(todos_los_dias, fill_value=0)

# Orden correcto de perfiles
orden = ["conservador", "convincente", "vulnerable"]
tabla = tabla.reindex(columns=orden, fill_value=0)

print("\n=== TABLA DE PERFILES POR DÍA ===\n")
print(tabla)

# Crear heatmap
plt.figure(figsize=(14, 6))
plt.imshow(tabla.T, aspect="auto", cmap="viridis")

plt.colorbar(label="Frecuencia diaria")
plt.xticks(range(len(tabla.index)), tabla.index, rotation=90, fontsize=8)
plt.yticks(range(len(tabla.columns)), tabla.columns)

plt.title("Frecuencia diaria de perfiles aplicados (30 oct – 17 nov)")
plt.xlabel("Día")
plt.ylabel("Perfil aplicado")

plt.tight_layout()
plt.savefig("heatmap_perfiles_adaptacion.png", dpi=300)

print("\n[OK] Heatmap generado: heatmap_perfiles_adaptacion.png")
