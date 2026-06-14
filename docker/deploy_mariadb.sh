#!/bin/bash

docker run -d \
  --name mariadb_inventarios \
  --network bd_heterogenea_net \
  -e MYSQL_ROOT_PASSWORD="RootMariaDB#2026" \
  -e MYSQL_DATABASE=inventarios \
  -e MYSQL_USER=dba_mariadb \
  -e MYSQL_PASSWORD="MariaDB_Proj#2026" \
  -p 3307:3306 \
  -v /u02/docker/mariadb/data:/var/lib/mysql \
  --restart unless-stopped \
  mariadb:11

# Verificación del contenedor

docker ps
docker logs mariadb_inventarios