#!/usr/bin/env python3
# ===========================================================
# Controlador adaptativo LinUCB para honeypot Cowrie
# ===========================================================
# - Consulta rf_service.py -> prob(bot/humano)
# - Selecciona acción (perfil Cowrie)
# - Invoca actuador_cowrie.py para aplicar perfil real
# - Aprende de la recompensa obtenida
# ===========================================================

import numpy as np
import requests
import json
import os
import subprocess
from datetime import datetime

# -----------------------------------------------------------
# Configuración general
# -----------------------------------------------------------
RF_API = "http://127.0.0.1:8001/predict"
ACTUADOR_PATH = "/home/miriam/honeypot-ai/actuador_cowrie.py"
PROFILES_PATH = "/home/miriam/cowrie-runtime/profiles"

# Perfiles disponibles
ACTIONS = ["conservador", "convincente", "vulnerable"]
N_ACTIONS = len(ACTIONS)
N_FEATURES = 6  # 5 features + 1 (bias para prob_human)

# Parámetro de exploración
ALPHA = 1.2

# -----------------------------------------------------------
# Inicialización del modelo LinUCB
# -----------------------------------------------------------
A = [np.identity(N_FEATURES) for _ in range(N_ACTIONS)]
b = [np.zeros((N_FEATURES, 1)) for _ in range(N_ACTIONS)]

# -----------------------------------------------------------
# Funciones auxiliares
# -----------------------------------------------------------

def get_rf_prob(session_features):
    """Consulta el servicio RF y obtiene prob(humano)"""
    try:
        # Convertir valores NumPy o no nativos a tipos estándar
        clean_features = {
            k: (float(v) if isinstance(v, (np.floating, float))
                else int(v) if isinstance(v, (np.integer, int))
                else float(v))
            for k, v in session_features.items()
        }
        # Timeout ampliado a 5 s
        res = requests.post(RF_API, json=clean_features, timeout=5)
        data = res.json()
        return data.get("human_prob", 0.0)
    except Exception as e:
        print("[!] Error al contactar con RF:", e)
        return 0.0


def select_action(x):
    """Selecciona la acción óptima según LinUCB"""
    p = []
    for a in range(N_ACTIONS):
        A_inv = np.linalg.inv(A[a])
        theta = np.dot(A_inv, b[a])
        value = np.dot(theta.T, x) + ALPHA * np.sqrt(np.dot(np.dot(x.T, A_inv), x))
        p_t = float(value.item())  # evita DeprecationWarning
        p.append(p_t)
    return int(np.argmax(p))


def update(a, x, reward):
    """Actualiza los parámetros del modelo LinUCB"""
    global A, b
    A[a] += np.dot(x, x.T)
    b[a] += reward * x


def apply_profile(profile_name):
    """Invoca el actuador para aplicar un perfil real en Cowrie"""
    print(f"[+] Aplicando perfil: {profile_name}")
    try:
        if not os.path.exists(ACTUADOR_PATH):
            print(f"    ⚠️  Actuador no encontrado en {ACTUADOR_PATH}")
            return
        if not os.path.exists(PROFILES_PATH):
            print(f"    ⚠️  Directorio de perfiles no encontrado: {PROFILES_PATH}")
            return

        # Ejecutar actuador y capturar salida
        proc = subprocess.run(
            ["python3", ACTUADOR_PATH, profile_name],
            capture_output=True, text=True, timeout=10
        )

        if proc.returncode == 0:
            print(f"    ✅ Actuador OK: {proc.stdout.strip()}")
        else:
            print(f"    ⚠️ Fallo (rc={proc.returncode}): {proc.stderr.strip()}")

    except subprocess.TimeoutExpired:
        print("    ⚠️  Actuador: tiempo de ejecución excedido (>10s)")
    except Exception as e:
        print(f"[!] Error aplicando perfil via actuador: {e}")


def compute_reward(session_info):
    """Calcula la recompensa según interacción simulada"""
    base = session_info.get("n_commands_total", 0)
    dur = session_info.get("duration_s", 0)
    reward = (base / 10.0) + (dur / 300.0)
    return min(reward, 1.0)


# -----------------------------------------------------------
# Bucle principal (modo simulación)
# -----------------------------------------------------------
def run_controller(simulations=10):
    for i in range(simulations):
        print(f"\n=== Sesión simulada #{i+1} ===")

        # Datos de sesión simulada
        session = {
            "duration_s": np.random.randint(10, 200),
            "n_commands_total": np.random.randint(0, 30),
            "n_unique_commands": np.random.randint(0, 10),
            "username_tried_count": np.random.randint(1, 3),
            "attempted_download": np.random.choice([0, 1])
        }

        # 1️⃣ Consultar RF
        prob_human = get_rf_prob(session)
        session["prob_human"] = prob_human

        # 2️⃣ Construir vector de contexto
        x = np.array([
            session["duration_s"] / 300.0,
            session["n_commands_total"] / 50.0,
            session["n_unique_commands"] / 20.0,
            session["username_tried_count"] / 5.0,
            session["attempted_download"],
            prob_human
        ]).reshape(-1, 1)

        # 3️⃣ Seleccionar acción (perfil)
        a = select_action(x)
        profile = ACTIONS[a]
        apply_profile(profile)

        # 4️⃣ Simular recompensa
        reward = compute_reward(session)
        print(f"    Recompensa obtenida: {reward:.3f}")

        # 5️⃣ Actualizar modelo
        update(a, x, reward)

    print("\n[✓] Simulación completada. Bandit LinUCB entrenado parcialmente.")


if __name__ == "__main__":
    run_controller(simulations=10)
