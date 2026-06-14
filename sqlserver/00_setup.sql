CREATE DATABASE reportes;
GO

USE reportes;
GO

CREATE LOGIN dba_sqlserver
  WITH PASSWORD = 'SqlSrvDBA#2026';
GO

CREATE USER dba_sqlserver FOR LOGIN dba_sqlserver;
GO

ALTER ROLE db_owner ADD MEMBER dba_sqlserver;
GO

CREATE SCHEMA reportes AUTHORIZATION dba_sqlserver;
GO

CREATE LOGIN sync_writer
  WITH PASSWORD = 'SyncWrite#2026';
GO

CREATE USER sync_writer FOR LOGIN sync_writer;
GO

GRANT INSERT, UPDATE, SELECT ON SCHEMA::reportes TO sync_writer;
GO

SELECT name FROM sys.databases;
GO

EXIT