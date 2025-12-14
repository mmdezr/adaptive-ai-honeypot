#!/usr/bin/env python3
# actuador_cowrie.py
# Aplica perfiles en Cowrie: banner, userdb, archivos honeyfs, y registra backups.
# Uso: python3 actuador_cowrie.py <perfil_nombre>
# Ej: python3 actuador_cowrie.py convincente

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import shutil
import tempfile
import logging

# RUTAS (ajusta si tu montaje es distinto)
COWRIE_RUNTIME = Path("/home/miriam/cowrie-runtime")
PROFILES_DIR = COWRIE_RUNTIME / "profiles"
ETC_DIR = COWRIE_RUNTIME / "etc"
HONEYFS_ROOT = COWRIE_RUNTIME / "honeyfs"  # se crearán ficheros en home del honeypot aquí
BACKUP_DIR = Path("/home/miriam/honeypot-ai/backups")
LOG_FILE = Path("/home/miriam/honeypot-ai/adaptation.log")

# Archivos objetivo dentro de etc
BANNER_FILE = ETC_DIR / "banner.txt"
USERDB_FILE = ETC_DIR / "userdb.txt"

# Configurar logging
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def ensure_dirs():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    ETC_DIR.mkdir(parents=True, exist_ok=True)
    HONEYFS_ROOT.mkdir(parents=True, exist_ok=True)

def backup_file(src: Path):
    if not src.exists():
        return None
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dst = BACKUP_DIR / f"{src.name}.{ts}.bak"
    shutil.copy2(str(src), str(dst))
    return dst

def atomic_write(path: Path, content: str, mode: str = "w"):
    # write to temp file then move
    fd, tmp = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, mode) as f:
            f.write(content)
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass

def apply_banner(banner_text: str):
    backup = backup_file(BANNER_FILE)
    if backup:
        logging.info(f"Backup banner -> {backup}")
    atomic_write(BANNER_FILE, banner_text + "\n")
    logging.info(f"Banner escrito en {BANNER_FILE}")

def apply_userdb(users_list):
    """
    users_list: lista de strings tipo "user:x:password" o "user:x:hash"
    Se escriben líneas en userdb.txt (sobrescribe)
    """
    backup = backup_file(USERDB_FILE)
    if backup:
        logging.info(f"Backup userdb -> {backup}")
    content = "\n".join(users_list) + "\n"
    atomic_write(USERDB_FILE, content)
    logging.info(f"userdb escrito en {USERDB_FILE}")

def ensure_fake_files(fake_files):
    """
    Crea archivos ficticios en el home del honeypot (honeyfs).
    Se colocan bajo honeyfs/home/root/ por defecto.
    """
    target_home = HONEYFS_ROOT / "home" / "root"
    target_home.mkdir(parents=True, exist_ok=True)
    created = []
    for fname in fake_files:
        fpath = target_home / fname
        if not fpath.exists():
            atomic_write(fpath, f"# placeholder file {fname}\n# created by actuador at {datetime.utcnow().isoformat()}\n")
            created.append(str(fpath))
            # permisos moderados
            try:
                fpath.chmod(0o644)
            except Exception:
                pass
    if created:
        logging.info(f"Archivos ficticios creados: {created}")
    else:
        logging.info("No se crearon archivos nuevos (ya existían).")

def record_action(profile_name, profile_path):
    logging.info(f"Perfil aplicado: {profile_name} ({profile_path})")

def load_profile(profile_name):
    profile_file = PROFILES_DIR / f"profile_{profile_name}.json"
    if not profile_file.exists():
        raise FileNotFoundError(f"Perfil no encontrado: {profile_file}")
    with open(profile_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data, profile_file

def main(argv):
    if len(argv) < 2:
        print("Uso: actuador_cowrie.py <perfil_nombre>")
        sys.exit(2)
    profile_name = argv[1]
    try:
        ensure_dirs()
        profile, profile_path = load_profile(profile_name)
    except Exception as e:
        logging.error(f"Error cargando perfil {profile_name}: {e}")
        print(f"[!] Error: {e}")
        sys.exit(1)

    # Aplicar banner
    banner = profile.get("banner")
    if banner:
        try:
            apply_banner(banner)
        except Exception as e:
            logging.error(f"Fallo aplicando banner: {e}")

    # Aplicar userdb (si viene)
    users = profile.get("users")
    if users:
        try:
            apply_userdb(users)
        except Exception as e:
            logging.error(f"Fallo aplicando userdb: {e}")

    # Crear archivos ficticios
    fake_files = profile.get("fake_files", [])
    try:
        ensure_fake_files(fake_files)
    except Exception as e:
        logging.error(f"Fallo creando fake_files: {e}")

    # Registrar
    record_action(profile_name, profile_path)
    print(f"[+] Perfil {profile_name} aplicado correctamente.")
    logging.info(f"[+] Perfil {profile_name} aplicado correctamente.")

if __name__ == "__main__":
    main(sys.argv)
