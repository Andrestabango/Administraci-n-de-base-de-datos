-- ============================================================================
-- 01_ddl_tablas.sql  ·  SQL Server 2022  ·  base reportes · schema reportes
-- Tablas destino consolidadas que alimenta la capa de interconexion (ETL):
--   consolidado_stock       <- MariaDB (horario)
--   reporte_rotacion        <- Oracle + MariaDB (diario)
--   reporte_abastecimiento  <- Oracle + MariaDB (diario)
-- Ejecutar:
--   sqlcmd -S localhost,1434 -U dba_sqlserver -P "SqlProj#2026" -C -d reportes -i 01_ddl_tablas.sql
-- ============================================================================

USE reportes;
GO

DROP TABLE IF EXISTS reportes.consolidado_stock;
DROP TABLE IF EXISTS reportes.reporte_rotacion;
DROP TABLE IF EXISTS reportes.reporte_abastecimiento;
GO

-- ── Stock consolidado (sincronizacion HORARIA desde MariaDB) ───────────────
-- valor_inventario es columna calculada PERSISTED (se guarda en disco).
CREATE TABLE reportes.consolidado_stock (
    consolidado_id     BIGINT IDENTITY(1,1) PRIMARY KEY,
    producto_id        INT            NOT NULL,
    nombre_producto    NVARCHAR(150)  NOT NULL,
    bodega_id          INT            NOT NULL,
    nombre_bodega      NVARCHAR(100)  NOT NULL,
    provincia          NVARCHAR(60)   NOT NULL,
    stock_total        INT            NOT NULL,
    precio_venta       DECIMAL(12,4)  NOT NULL,
    valor_inventario   AS (stock_total * precio_venta) PERSISTED,
    en_alerta          BIT            NOT NULL DEFAULT 0,
    proxima_caducidad  DATE           NULL,
    sincronizado_en    DATETIME2      NOT NULL DEFAULT SYSDATETIME()
);
GO
CREATE INDEX ix_cons_prod ON reportes.consolidado_stock (producto_id);
CREATE INDEX ix_cons_bod  ON reportes.consolidado_stock (bodega_id);
GO

-- ── Rotacion de inventario (sincronizacion DIARIA, Oracle + MariaDB) ───────
CREATE TABLE reportes.reporte_rotacion (
    rotacion_id        BIGINT IDENTITY(1,1) PRIMARY KEY,
    producto_id        INT            NOT NULL,
    nombre_producto    NVARCHAR(150)  NOT NULL,
    categoria          NVARCHAR(80)   NULL,
    total_entradas     DECIMAL(14,3)  NOT NULL DEFAULT 0,
    total_salidas      DECIMAL(14,3)  NOT NULL DEFAULT 0,
    rotacion_neta      AS (total_entradas - total_salidas) PERSISTED,
    periodo            NVARCHAR(7)     NOT NULL,    -- YYYY-MM
    sincronizado_en    DATETIME2      NOT NULL DEFAULT SYSDATETIME()
);
GO
CREATE INDEX ix_rot_prod ON reportes.reporte_rotacion (producto_id);
GO

-- ── Abastecimiento por proveedor (sincronizacion DIARIA) ───────────────────
CREATE TABLE reportes.reporte_abastecimiento (
    abast_id               BIGINT IDENTITY(1,1) PRIMARY KEY,
    proveedor_id           INT            NOT NULL,
    nombre_proveedor       NVARCHAR(150)  NOT NULL,
    total_unidades_entrada DECIMAL(14,3)  NOT NULL DEFAULT 0,
    total_valor            DECIMAL(16,2)  NOT NULL DEFAULT 0,
    periodo                NVARCHAR(7)     NOT NULL,  -- YYYY-MM
    sincronizado_en        DATETIME2      NOT NULL DEFAULT SYSDATETIME()
);
GO
CREATE INDEX ix_abast_prov ON reportes.reporte_abastecimiento (proveedor_id);
GO

PRINT 'Tablas de SQL Server creadas: consolidado_stock, reporte_rotacion, reporte_abastecimiento';
GO
