"CAMBIO DEL LISTENER AL PEURTO 1523"

lsnrctl stop
nano $ORACLE_HOME/network/admin/listener.ora

LISTENER =
  (DESCRIPTION_LIST =
    (DESCRIPTION =
      (ADDRESS = (PROTOCOL = TCP)(HOST = oracle.lab.local)(PORT = 1523))
      (ADDRESS = (PROTOCOL = IPC)(KEY = EXTPROC1523))
    )
  )

ADR_BASE_LISTENER = /u01/app/oracle


"EDICIÓN TNSNAMES.ORA"

nano $ORACLE_HOME/network/admin/tnsnames.ora

LISTENER_ORCL =
  (ADDRESS = (PROTOCOL = TCP)(HOST = oracle.lab.local)(PORT = 1523))

ORCL =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = oracle.lab.local)(PORT = 1523))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = orcl.lab.local)
    )
  )

ORCLPDB =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = oracle.lab.local)(PORT = 1523))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = orclpdb.lab.local)
    )
  )

lsnrctl start
lsnrctl status

"REGISTRO DE LA INSTANCIA CON EL NUEVO PUERTO"

sqlplus / as sysdba

ALTER SYSTEM SET LOCAL_LISTENER =
  '(ADDRESS=(PROTOCOL=TCP)(HOST=oracle.lab.local)(PORT=1523))'
  SCOPE=BOTH;

ALTER SYSTEM REGISTER;
EXIT;


"CREACIÓN DE TABLESPACE, DBA DEDICADO y SCHEMA DEL PROYECTO EN ORCLPDB"

sqlplus / as sysdba

ALTER PLUGGABLE DATABASE ORCLPDB OPEN;
ALTER SESSION SET CONTAINER = ORCLPDB;

-- Tablespace dedicado para los datos del proyecto
CREATE TABLESPACE tbs_logistica
  DATAFILE '/u02/oradata/tbs_logistica_01.dbf'
  SIZE 500M AUTOEXTEND ON NEXT 100M MAXSIZE 5G;

-- Usuario DBA del proyecto (administrador de Oracle para este proyecto)
CREATE USER dba_oracle
  IDENTIFIED BY "OracleProj#2026"
  DEFAULT TABLESPACE tbs_logistica
  TEMPORARY TABLESPACE TEMP
  QUOTA UNLIMITED ON tbs_logistica;

GRANT CONNECT, RESOURCE, DBA TO dba_oracle;

-- Schema de aplicacion: aqui viviran las tablas del modelo de datos
CREATE USER logistica
  IDENTIFIED BY "Logist1ca#2026"
  DEFAULT TABLESPACE tbs_logistica
  TEMPORARY TABLESPACE TEMP
  QUOTA UNLIMITED ON tbs_logistica;

GRANT CONNECT, RESOURCE TO logistica;
GRANT CREATE VIEW, CREATE SYNONYM TO logistica;

EXIT;