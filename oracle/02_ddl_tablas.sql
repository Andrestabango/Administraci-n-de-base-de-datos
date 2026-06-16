-- ============================================================================
-- 02_ddl_tablas.sql  ·  Oracle 19c  ·  schema logistica
-- Modelo transaccional de movimientos de entrada/salida de mercaderia.
-- Ejecutar conectado al schema logistica dentro de ORCLPDB:
--   sqlplus logistica/"Logist1ca#2026"@ORCLPDB @02_ddl_tablas.sql
-- ============================================================================

WHENEVER SQLERROR CONTINUE;
-- Limpieza idempotente
DROP TABLE movimientos_detalle CASCADE CONSTRAINTS;
DROP TABLE movimientos        CASCADE CONSTRAINTS;
DROP SEQUENCE seq_movimientos;
DROP SEQUENCE seq_mov_detalle;
WHENEVER SQLERROR EXIT SQL.SQLCODE;

-- ── Secuencias ─────────────────────────────────────────────────────────────
CREATE SEQUENCE seq_movimientos  START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_mov_detalle  START WITH 1 INCREMENT BY 1 NOCACHE;

-- ── Cabecera de movimiento ─────────────────────────────────────────────────
-- tipo: ENTRADA (recepcion de proveedor) | SALIDA (despacho a farmacia)
--       DEVOLUCION (devolucion a proveedor)
CREATE TABLE movimientos (
  movimiento_id   NUMBER(12)      DEFAULT seq_movimientos.NEXTVAL PRIMARY KEY,
  tipo            VARCHAR2(12)    NOT NULL,
  proveedor_id    NUMBER(8),                       -- ref. logica a MariaDB.proveedores
  bodega_id       NUMBER(6)       NOT NULL,         -- ref. logica a MariaDB.bodegas
  documento       VARCHAR2(30)    NOT NULL,         -- nro. orden/guia
  fecha_mov       DATE            DEFAULT SYSDATE NOT NULL,
  estado          VARCHAR2(12)    DEFAULT 'CONFIRMADO' NOT NULL,
  valor_total     NUMBER(14,2)    DEFAULT 0,
  creado_en       TIMESTAMP       DEFAULT SYSTIMESTAMP,
  CONSTRAINT chk_mov_tipo   CHECK (tipo   IN ('ENTRADA','SALIDA','DEVOLUCION')),
  CONSTRAINT chk_mov_estado CHECK (estado IN ('CONFIRMADO','ANULADO','PENDIENTE'))
);

-- ── Detalle de movimiento (1-N) ────────────────────────────────────────────
CREATE TABLE movimientos_detalle (
  detalle_id      NUMBER(12)      DEFAULT seq_mov_detalle.NEXTVAL PRIMARY KEY,
  movimiento_id   NUMBER(12)      NOT NULL,
  producto_id     NUMBER(8)       NOT NULL,         -- ref. logica a MariaDB.productos
  cantidad        NUMBER(10,3)    NOT NULL,
  precio_unitario NUMBER(12,4)    NOT NULL,
  subtotal        NUMBER(14,2)    GENERATED ALWAYS AS (cantidad * precio_unitario) VIRTUAL,
  lote            VARCHAR2(30),
  fecha_vencimiento DATE,
  CONSTRAINT fk_det_mov FOREIGN KEY (movimiento_id)
       REFERENCES movimientos (movimiento_id) ON DELETE CASCADE,
  CONSTRAINT chk_det_cant CHECK (cantidad > 0)
);

-- ── Indices para el ETL (filtra por fecha y producto) ──────────────────────
CREATE INDEX ix_mov_fecha    ON movimientos (fecha_mov);
CREATE INDEX ix_mov_tipo     ON movimientos (tipo);
CREATE INDEX ix_det_prod     ON movimientos_detalle (producto_id);
CREATE INDEX ix_det_mov      ON movimientos_detalle (movimiento_id);

-- ── Permisos de lectura para la capa de interconexion ──────────────────────
GRANT SELECT ON movimientos        TO sync_reader_ora;
GRANT SELECT ON movimientos_detalle TO sync_reader_ora;

COMMIT;

PROMPT ============================================================
PROMPT  Tablas de Oracle creadas: movimientos, movimientos_detalle
PROMPT ============================================================
