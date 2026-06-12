sqlplus / as sysdba

ALTER PLUGGABLE DATABASE ORCLPDB OPEN;
ALTER SESSION SET CONTAINER = ORCLPDB;

-- Eliminar usuarios (CASCADE borra todos sus objetos asociados)
DROP USER udla_usr_gjrc   CASCADE;
DROP USER hmwk_usr_gjrc   CASCADE;

-- Eliminar roles creados en laboratorio
DROP ROLE udla_rol_gjrc;
DROP ROLE hmwk_rol_gjrc;

-- Eliminar tablespaces y sus archivos fisicos del disco
DROP TABLESPACE udla_tbs_gjrc INCLUDING CONTENTS AND DATAFILES;
DROP TABLESPACE hmwk_tbs_gjrc INCLUDING CONTENTS AND DATAFILES;