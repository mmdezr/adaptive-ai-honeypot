#!/bin/bash
CONTAINER="cowrie"
RUNTIME="/home/miriam/cowrie-runtime"
TARGET="/home/cowrie/cowrie"

echo "[+] Sincronizando archivos con contenedor ${CONTAINER} ..."

# Esperar hasta que el contenedor esté corriendo (timeout 30s)
for i in {1..30}; do
  if sudo podman ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    break
  fi
  echo "    ⏳ Esperando a que el contenedor ${CONTAINER} esté activo..."
  sleep 1
done

# Verificar que realmente esté en ejecución
if ! sudo podman ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  echo "    ❌ Contenedor ${CONTAINER} no está corriendo. Abortando sincronización."
  exit 1
fi

# Sincronizar archivos (evitando atributos extendidos)
sudo podman cp --relabel=false --quiet "${RUNTIME}/etc/banner.txt" "${CONTAINER}:${TARGET}/etc/banner.txt"
sudo podman cp --relabel=false --quiet "${RUNTIME}/etc/userdb.txt" "${CONTAINER}:${TARGET}/etc/userdb.txt"

# Copiar contenido del directorio home (si existe)
if [ -d "${RUNTIME}/honeyfs/home/root" ]; then
  sudo podman cp --relabel=false --quiet "${RUNTIME}/honeyfs/home/root" "${CONTAINER}:${TARGET}/share/cowrie/fs/home/"
fi

echo "[✓] Sincronización completada sin errores."
