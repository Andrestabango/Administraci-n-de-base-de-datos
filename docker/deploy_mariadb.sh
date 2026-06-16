#!/usr/bin/env bash
# ============================================================================
# deploy_mariadb.sh  ·  Despliega MariaDB 11 en Docker
# Puerto NO-DEFAULT host 3307 -> 3306 contenedor.
# Volumen persistente y red dedicada del proyecto.
# Uso:  ./deploy_mariadb.sh
# ============================================================================
set -euo pipefail

CONTAINER="mariadb_inventarios"
IMAGE="mariadb:11"
HOST_PORT=3307
DATA_DIR="/u02/docker/mariadb/data"
ROOT_PWD="${MARIADB_ROOT_PWD:-RootMaria#2026}"
NET="bd_heterogenea_net"

echo ">> Creando red ${NET} (si no existe)"
docker network inspect "${NET}" >/dev/null 2>&1 || docker network create "${NET}"

echo ">> Preparando volumen ${DATA_DIR}"
sudo mkdir -p "${DATA_DIR}"

echo ">> Eliminando contenedor previo (si existe)"
docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true

echo ">> Levantando ${CONTAINER} en el puerto ${HOST_PORT}"
docker run -d \
  --name "${CONTAINER}" \
  --network "${NET}" \
  --restart unless-stopped \
  -p ${HOST_PORT}:3306 \
  -e MARIADB_ROOT_PASSWORD="${ROOT_PWD}" \
  -e MARIADB_DATABASE=inventarios \
  -e TZ=America/Guayaquil \
  -v "${DATA_DIR}:/var/lib/mysql:Z" \
  "${IMAGE}" \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci \
  --max_connections=200

echo ">> Esperando readiness de MariaDB..."
until docker exec "${CONTAINER}" mariadb -uroot -p"${ROOT_PWD}" -e "SELECT 1" >/dev/null 2>&1; do
  sleep 2; printf '.'
done
echo " listo."

echo ">> Aplicando 00_setup.sql y 01_ddl_tablas.sql"
docker exec -i "${CONTAINER}" mariadb -uroot -p"${ROOT_PWD}" < ../mariadb/00_setup.sql
docker exec -i "${CONTAINER}" mariadb -uroot -p"${ROOT_PWD}" inventarios < ../mariadb/01_ddl_tablas.sql

echo ">> MariaDB desplegado en puerto ${HOST_PORT}"
