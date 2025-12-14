import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# === 1️⃣ Leer métricas base ===
df = pd.read_csv("metrics_sessions.csv", parse_dates=["start"])
df = df.sort_values("start")

# === 2️⃣ Leer adaptation.log de forma segura ===
log_entries = []
with open("adaptation.log", "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "Perfil aplicado:" in line:
            try:
                ts = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
                perfil = line.split("Perfil aplicado:")[-1].split("(")[0].strip()
                log_entries.append({"timestamp": ts, "perfil": perfil})
            except Exception:
                continue

log = pd.DataFrame(log_entries)
if log.empty:
    print("⚠️ No se encontraron líneas de 'Perfil aplicado' en adaptation.log")
    exit(0)

# === 3️⃣ Ordenar por tiempo ===
log = log.sort_values("timestamp")

# === 4️⃣ Convertir perfil a categoría ordenada ===
order = ["conservador", "convincente", "vulnerable"]
colors = {"conservador": "#1f77b4", "convincente": "#ff7f0e", "vulnerable": "#d62728"}
log["perfil"] = pd.Categorical(log["perfil"], categories=order, ordered=True)

# === 5️⃣ Gráfico 1: evolución temporal ===
plt.figure(figsize=(10, 5))
for perfil, subset in log.groupby("perfil"):
    plt.plot(subset["timestamp"], subset["perfil"], "o-", color=colors[perfil], label=perfil, alpha=0.8)

plt.title("Evolución temporal de perfiles aplicados", fontsize=14, fontweight="bold")
plt.xlabel("Tiempo")
plt.ylabel("Perfil")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.4)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("evolucion_perfiles_color.png", dpi=150)
print("📈 Gráfico temporal guardado como evolucion_perfiles_color.png")

# === 6️⃣ Gráfico 2: frecuencia de uso ===
plt.figure(figsize=(6, 4))
log["perfil"].value_counts().reindex(order).plot(kind="bar", color=[colors[p] for p in order])
plt.title("Frecuencia de perfiles aplicados", fontsize=13, fontweight="bold")
plt.xlabel("Perfil")
plt.ylabel("Número de veces aplicado")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig("frecuencia_perfiles.png", dpi=150)
print("📊 Gráfico de frecuencias guardado como frecuencia_perfiles.png")
