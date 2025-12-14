#!/usr/bin/env python3
# ===========================================================
# Random Forest v2 - Entrenamiento robusto y regularizado
# ===========================================================

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib

DATA_PATH = "cowrie_sessions.csv"

# -----------------------------------------------------------
# 1️⃣ Cargar dataset
# -----------------------------------------------------------
df = pd.read_csv(DATA_PATH)
print(f"[+] Dataset cargado: {len(df)} sesiones totales")

# -----------------------------------------------------------
# 2️⃣ Limpieza relajada
#    (solo quitamos sesiones sin duración; mantenemos n_commands=0..2)
# -----------------------------------------------------------
df = df[df["duration_s"] > 0]
print(f"[+] Después de limpiar: {len(df)} sesiones válidas")

df = df.fillna(0)

# -----------------------------------------------------------
# 3️⃣ Etiquetado automático mejorado
# -----------------------------------------------------------
# Heurística extendida:
# - bots: duración <30s o n_unique_commands <=1
# - humanos: duración >120s o n_unique_commands >=4
conditions = [
    (df["duration_s"] < 30) | (df["n_unique_commands"] <= 1),
    (df["duration_s"] > 120) & (df["n_unique_commands"] >= 4)
]
choices = [0, 1]
df["label"] = np.select(conditions, choices, default=0)

print("[+] Etiquetas iniciales aplicadas (0=bot, 1=humano)")
print(df["label"].value_counts())

# -----------------------------------------------------------
# 4️⃣ Selección de features
# -----------------------------------------------------------
features = [
    "duration_s",
    "n_commands_total",
    "n_unique_commands",
    "username_tried_count",
    "attempted_download"
]
X = df[features]
y = df["label"]

# -----------------------------------------------------------
# 5️⃣ Split train/test
# -----------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# -----------------------------------------------------------
# 6️⃣ Entrenamiento con regularización
# -----------------------------------------------------------
rf = RandomForestClassifier(
    n_estimators=300,        # más árboles
    max_depth=8,            # menos profundidad → evita memorizar
    min_samples_split=5,
    min_samples_leaf=4,
    class_weight="balanced", # corrige desbalanceo bots/humanos
    random_state=42,
    n_jobs=-1
)

print("[+] Entrenando modelo RF regularizado...")
rf.fit(X_train, y_train)

# -----------------------------------------------------------
# 7️⃣ Evaluación
# -----------------------------------------------------------
y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:, 1]

print("\n=== Métricas del modelo v2 ===")
print(classification_report(y_test, y_pred, digits=3))
print("AUC:", roc_auc_score(y_test, y_prob))
print("Matriz de confusión:\n", confusion_matrix(y_test, y_pred))

# -----------------------------------------------------------
# 8️⃣ Guardar modelo y dataset etiquetado
# -----------------------------------------------------------
joblib.dump(rf, "rf_cowrie_v2.joblib")
df.to_csv("cowrie_sessions_labeled_v2.csv", index=False)

print("\n[+] Modelo guardado como rf_cowrie_v2.joblib")
print("[+] Dataset etiquetado guardado como cowrie_sessions_labeled_v2.csv")
