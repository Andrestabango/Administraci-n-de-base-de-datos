-- ============================================================================
-- 02_permisos_sync.sql  ·  SQL Server 2022  ·  base reportes
-- Otorga al usuario sync_writer los permisos minimos que necesita el ETL:
-- INSERT y DELETE (patron DELETE+INSERT por tabla destino) y SELECT para
-- las validaciones de integridad.
-- Ejecutar:
--   sqlcmd -S localhost,1434 -U dba_sqlserver -P "SqlProj#2026" -C -d reportes -i 02_permisos_sync.sql
-- ============================================================================

USE reportes;
GO

GRANT SELECT, INSERT, DELETE ON reportes.consolidado_stock      TO sync_writer;
GRANT SELECT, INSERT, DELETE ON reportes.reporte_rotacion       TO sync_writer;
GRANT SELECT, INSERT, DELETE ON reportes.reporte_abastecimiento TO sync_writer;
GO

PRINT 'Permisos de sync_writer otorgados (SELECT, INSERT, DELETE)';
GO
