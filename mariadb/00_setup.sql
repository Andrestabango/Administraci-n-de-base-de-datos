-- Otorgar todos los permisos al DBA sobre la base inventarios
GRANT ALL PRIVILEGES ON inventarios.* TO 'dba_mariadb'@'%';

-- Crear usuario de solo lectura para la capa de interconexión
CREATE USER IF NOT EXISTS 'sync_reader'@'%' IDENTIFIED BY 'SyncRead#2026';

-- Otorgar permisos mínimos de lectura
GRANT SELECT ON inventarios.* TO 'sync_reader'@'%';

-- Aplicar cambios de privilegios
FLUSH PRIVILEGES;

-- Verificación
SHOW DATABASES;
SELECT user, host FROM mysql.user;