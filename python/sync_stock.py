"""
Sincronizacion de stock consolidado: MariaDB -> SQL Server
Ejecucion: cada minuto (cron: * * * * *)
Protegido con archivo lock para evitar ejecuciones solapadas.
"""
import mysql.connector
import pyodbc
from datetime import date
import logging
import os
import sys

LOCK_FILE = '/tmp/sync_stock.lock'

logging.basicConfig(
    filename='/home/oracle/proyecto_integrador/logs/sync_stock.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def acquire_lock():
    if os.path.exists(LOCK_FILE):
        logging.warning("Ejecucion anterior en curso, saltando este ciclo")
        sys.exit(0)
    open(LOCK_FILE, 'w').close()

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def get_stock_mariadb():
    conn = mysql.connector.connect(
        host='127.0.0.1', port=3307,
        user='sync_reader', password='SyncRead#2026',
        database='inventarios'
    )
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            p.producto_id, p.sku, p.nombre AS nombre_producto,
            b.bodega_id, b.nombre AS nombre_bodega,
            i.cantidad AS cantidad_actual, i.stock_minimo,
            (i.cantidad <= i.stock_minimo) AS alerta_reposicion
        FROM inventario_ubicacion i
        JOIN productos p ON i.producto_id = p.producto_id
        JOIN bodegas   b ON i.bodega_id   = b.bodega_id
        WHERE p.activo = 1
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def upsert_sqlserver(rows):
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=127.0.0.1,1434;"
        "DATABASE=reportes;"
        "UID=sync_writer;PWD=SyncWrite#2026;"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cur = conn.cursor()
    hoy = date.today()
    cur.execute(
        "DELETE FROM reportes.consolidado_stock WHERE fecha_corte = ?", hoy
    )
    for r in rows:
        cur.execute("""
            INSERT INTO reportes.consolidado_stock
              (producto_id, sku, nombre_producto, bodega_id,
               nombre_bodega, cantidad_actual, stock_minimo,
               alerta_reposicion, fecha_corte)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            r['producto_id'], r['sku'], r['nombre_producto'],
            r['bodega_id'], r['nombre_bodega'],
            r['cantidad_actual'], r['stock_minimo'],
            1 if r['alerta_reposicion'] else 0, hoy
        ))
    conn.commit()
    cur.close()
    conn.close()
    return len(rows)

if __name__ == '__main__':
    acquire_lock()
    try:
        logging.info("Iniciando sync_stock")
        rows = get_stock_mariadb()
        n = upsert_sqlserver(rows)
        logging.info("sync_stock finalizado: %d registros", n)
        print(f"Stock sincronizado: {n} registros")
    except Exception as e:
        logging.error("Error en sync_stock: %s", str(e))
        raise
    finally:
        release_lock()
