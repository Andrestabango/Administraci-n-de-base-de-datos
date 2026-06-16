-- ============================================================================
-- 00_setup.sql  ·  SQL Server 2022  ·  base reportes
-- Crea la base de datos, el DBA dedicado (dba_sqlserver), el schema reportes
-- y el login de escritura (sync_writer) que usara la capa de interconexion.
-- Ejecutar como SA (puerto NO-DEFAULT 1434; default era 1433):
--   sqlcmd -S localhost,1434 -U sa -P "<sa_pwd>" -C -i 00_setup.sql
-- ============================================================================

-- ── Base de datos del proyecto ─────────────────────────────────────────────
IF DB_ID('reportes') IS NULL
    CREATE DATABASE reportes;
GO

-- ── DBA del sistema SQL Server (administrador del proyecto) ────────────────
IF SUSER_ID('dba_sqlserver') IS NULL
    CREATE LOGIN dba_sqlserver WITH PASSWORD = 'SqlProj#2026', CHECK_POLICY = ON;
GO

-- ── Login de escritura para el ETL (sync_stock / sync_rotacion) ────────────
IF SUSER_ID('sync_writer') IS NULL
    CREATE LOGIN sync_writer WITH PASSWORD = 'SyncWrite#2026', CHECK_POLICY = ON;
GO

USE reportes;
GO

-- ── Schema propio del proyecto ─────────────────────────────────────────────
IF SCHEMA_ID('reportes') IS NULL
    EXEC('CREATE SCHEMA reportes');
GO

-- ── Mapear logins a usuarios de la base ────────────────────────────────────
IF USER_ID('dba_sqlserver') IS NULL
    CREATE USER dba_sqlserver FOR LOGIN dba_sqlserver WITH DEFAULT_SCHEMA = reportes;
ALTER ROLE db_owner ADD MEMBER dba_sqlserver;
GO

IF USER_ID('sync_writer') IS NULL
    CREATE USER sync_writer FOR LOGIN sync_writer WITH DEFAULT_SCHEMA = reportes;
GO

PRINT 'Setup de SQL Server completado: reportes, dba_sqlserver, sync_writer';
GO
