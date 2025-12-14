#!/usr/bin/env python3
# ===========================================================
# Servicio de inferencia del modelo Random Forest Cowrie
# ===========================================================
# - Carga rf_cowrie_v2.joblib
# - Recibe features de una sesión (JSON)
# - Devuelve probabilidad de bot (0-1)
# ===========================================================

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import uvicorn

# -----------------------------------------------------------
# 1️⃣ Cargar modelo
# -----------------------------------------------------------
MODEL_PATH = "rf_cowrie_v2.joblib"
print(f"[+] Cargando modelo {MODEL_PATH} ...")
model = joblib.load(MODEL_PATH)
print("[+] Modelo cargado correctamente.")

# -----------------------------------------------------------
# 2️⃣ Inicializar API
# -----------------------------------------------------------
app = FastAPI(title="RF Cowrie Service", version="2.0")

# Estructura esperada en el POST
class SessionFeatures(BaseModel):
    duration_s: float
    n_commands_total: int
    n_unique_commands: int
    username_tried_count: int
    attempted_download: int

# -----------------------------------------------------------
# 3️⃣ Endpoint principal
# -----------------------------------------------------------
@app.post("/predict")
def predict(features: SessionFeatures):
    x = np.array([[features.duration_s,
                   features.n_commands_total,
                   features.n_unique_commands,
                   features.username_tried_count,
                   features.attempted_download]])
    bot_prob = model.predict_proba(x)[0, 0]
    human_prob = model.predict_proba(x)[0, 1]
    return {
        "bot_prob": float(bot_prob),
        "human_prob": float(human_prob),
        "prediction": "human" if human_prob > 0.5 else "bot"
    }

# -----------------------------------------------------------
# 4️⃣ Arranque local
# -----------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
