import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Cargar CSV
df = pd.read_csv("sessions_con_perfil.csv")

# 2. Convertir fecha
df["start"] = pd.to_datetime(df["start"], utc=True).dt.tz_convert(None)

# 3. Filtrar rango
inicio = datetime(2025, 10, 30)
fin    = datetime(2025, 11, 17, 23, 59, 59)

df = df[(df["start"] >= inicio) & (df["start"] <= fin)]

# 4. Crear columna día
df["dia"] = df["start"].dt.date

# 5. Agrupar por día y perfil
tabla = df.groupby(["dia", "perfil"]).size().unstack(fill_value=0)

# 6. Heatmap matplotlib (sin seaborn)
plt.figure(figsize=(10, 6))

plt.imshow(tabla.T, aspect="auto")

plt.colorbar(label="Frecuencia")

plt.yticks(range(len(tabla.columns)), tabla.columns)
plt.xticks(range(len(tabla.index)), tabla.index, rotation=90)

plt.title("Frecuencia diaria de perfiles aplicados (30 oct – 17 nov)")
plt.xlabel("Día")
plt.ylabel("Perfil aplicado")

plt.tight_layout()

# 7. Guardar imagen
plt.savefig("heatmap_perfiles.png", dpi=300)

print("Heatmap generado: heatmap_perfiles.png")
print("\nTabla diaria:\n")
print(tabla)
