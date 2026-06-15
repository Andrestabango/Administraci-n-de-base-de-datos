-- ============================================================================
-- 01_setup_oracle.sql  ·  Oracle 19c
-- Crea el tablespace del proyecto, el DBA dedicado (dba_oracle) y el schema
-- de aplicacion (logistica). Tambien registra la instancia en el puerto 1523.
-- Ejecutar como SYSDBA:
--   sqlplus / as sysdba @01_setup_oracle.sql
-- ============================================================================

WHENEVER SQL ERROR EXIT SQL.SQLCODE;

-- ── Registrar la instancia en el listener del puerto no-default 1523 ───────
ALTER SYSTEM SET LOCAL_LISTENER =
  '(ADDRESS=(PROTOCOL=TCP)(HOST=oracle.lab.local)(PORT=1523))'
  SCOPE=BOTH;
ALTER SYSTEM REGISTER;

ALTER PLUGGABLE DATABASE ORCLPDB OPEN;
ALTER SESSION SET CONTAINER = ORCLPDB;

-- ── Tablespace dedicado para los datos del proyecto ────────────────────────
CREATE TABLESPACE tbs_logistica
  DATAFILE '/u02/oradata/tbs_logistica_01.dbf'
  SIZE 500M AUTOEXTEND ON NEXT 100M MAXSIZE 5G;

-- ── DBA del sistema Oracle (administrador del proyecto en Oracle) ──────────
CREATE USER dba_oracle
  IDENTIFIED BY "OracleProj#2026"
  DEFAULT TABLESPACE tbs_logistica
  TEMPORARY TABLESPACE TEMP
  QUOTA UNLIMITED ON tbs_logistica;
GRANT CONNECT, RESOURCE, DBA TO dba_oracle;

-- ── Schema de aplicacion: aqui viven las tablas de movimientos ─────────────
CREATE USER logistica
  IDENTIFIED BY "Logist1ca#2026"
  DEFAULT TABLESPACE tbs_logistica
  TEMPORARY TABLESPACE TEMP
  QUOTA UNLIMITED ON tbs_logistica;
GRANT CONNECT, RESOURCE       TO logistica;
GRANT CREATE VIEW, CREATE SYNONYM TO logistica;

-- ── Usuario de solo lectura para la capa de interconexion (ETL) ────────────
-- El ETL diario lee los movimientos de Oracle con privilegios minimos.
CREATE USER sync_reader_ora
  IDENTIFIED BY "SyncRead#2026"
  DEFAULT TABLESPACE tbs_logistica
  TEMPORARY TABLESPACE TEMP;
GRANT CREATE SESSION TO sync_reader_ora;
-- (los GRANT SELECT sobre las tablas se otorgan en 02_ddl_tablas.sql)

PROMPT ============================================================
PROMPT  Setup de Oracle completado (tbs_logistica, dba_oracle,
PROMPT  logistica, sync_reader_ora). Continuar con 02_ddl_tablas.sql
PROMPT ============================================================
