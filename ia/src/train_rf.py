#!/usr/bin/env python3
# ===========================================================
# Entrenamiento del modelo Random Forest para sesiones Cowrie
# ===========================================================
# - Carga el dataset generado por extract_sessions_es.py
# - Limpia sesiones vacías (sin duración o sin comandos)
# - Crea etiquetas automáticas (bot/humano)
# - Entrena y guarda rf_cowrie.joblib
# ===========================================================

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import numpy as np
import os

# ===========================================================
# 1️⃣ Carga de datos
# ===========================================================
DATA_PATH = "cowrie_sessions.csv"
df = pd.read_csv(DATA_PATH)

print(f"[+] Dataset cargado: {len(df)} sesiones totales")

# ===========================================================
# 2️⃣ Limpieza básica
# ===========================================================
# Quitamos sesiones sin duración o sin comandos
df = df[(df["duration_s"] > 0) & (df["n_commands_total"] > 0)]
print(f"[+] Después de limpiar: {len(df)} sesiones válidas")

# Rellenamos posibles nulos
df = df.fillna(0)

# ===========================================================
# 3️⃣ Etiquetado inicial (automático)
# ===========================================================
# Heurística inicial:
# - bots: sesiones cortas (<30 s) o muy repetitivas (n_unique_commands <= 2)
# - humanos: sesiones largas (>60 s) con más diversidad de comandos
conditions = [
    (df["duration_s"] < 30) | (df["n_unique_commands"] <= 2),
    (df["duration_s"] >= 60) & (df["n_unique_commands"] > 2)
]
choices = [0, 1]  # 0=bot, 1=humano
df["label"] = np.select(conditions, choices, default=0)

print("[+] Etiquetado inicial aplicado (0=bot, 1=humano)")
print(df["label"].value_counts())

# ===========================================================
# 4️⃣ Selección de features
# ===========================================================
features = [
    "duration_s",
    "n_commands_total",
    "n_unique_commands",
    "username_tried_count",
    "attempted_download"
]
X = df[features]
y = df["label"]

# ===========================================================
# 5️⃣ División del dataset y entrenamiento
# ===========================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

print("[+] Entrenando modelo RF...")
rf.fit(X_train, y_train)

# ===========================================================
# 6️⃣ Evaluación
# ===========================================================
y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:, 1]

print("\n=== Resultados del modelo ===")
print(classification_report(y_test, y_pred, digits=3))
print("AUC:", roc_auc_score(y_test, y_prob))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# ===========================================================
# 7️⃣ Guardar modelo
# ===========================================================
MODEL_PATH = "rf_cowrie.joblib"
joblib.dump(rf, MODEL_PATH)
print(f"[+] Modelo guardado en {MODEL_PATH}")

# ===========================================================
# 8️⃣ Export opcional: dataset limpio etiquetado
# ===========================================================
CLEAN_DATA = "cowrie_sessions_labeled.csv"
df.to_csv(CLEAN_DATA, index=False)
print(f"[+] Dataset etiquetado guardado en {CLEAN_DATA}")
