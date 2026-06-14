" bash — como root"

dnf remove -y podman podman-catatonit buildah runc containers-common
dnf clean all
dnf makecache


"Instalar Docker CE desde el repositorio oficial"

dnf config-manager --add-repo \
  https://download.docker.com/linux/rhel/docker-ce.repo

dnf install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin --allowerasing

systemctl enable docker
systemctl start docker
systemctl status docker

docker --version
docker info


"Agregar usuario oracle al grupo docker y activar en la sesión"

usermod -aG docker oracle

"bash — como oracle: activar el grupo en la sesion actual"

newgrp docker

-- Verificar que docker aparece activo
groups
-- Resultado esperado: docker oinstall dba oper backupdba ...

-- Prueba rapida
docker ps

"bash — como oracle"

docker network create --driver bridge bd_heterogenea_net
docker network ls

"Crear directorios persistentes para los datos"

mkdir -p /u02/docker/mariadb/data
mkdir -p /u02/docker/sqlserver/data

-- MariaDB: propietario oracle:oinstall
chown -R oracle:oinstall /u02/docker/mariadb
chmod -R 775 /u02/docker/mariadb

-- SQL Server: REQUIERE UID 10001 (usuario interno del contenedor MSSQL)
chown -R 10001:0 /u02/docker/sqlserver/data
chmod -R 770 /u02/docker/sqlserver/data

-- Verificar
ls -la /u02/docker/