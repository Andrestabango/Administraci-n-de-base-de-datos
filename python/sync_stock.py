"""
sync_stock.py  ·  ETL HORARIO  ·  MariaDB  ->  SQL Server

Consolida el stock fisico de MariaDB (inventario_ubicacion + productos +
bodegas) y lo carga en reportes.consolidado_stock de SQL Server.

Estrategia: DELETE + INSERT (full refresh) sobre la tabla destino dentro de
una transaccion. El stock cambia constantemente, por lo que se reconstruye la
foto consolidada cada hora; el volumen (decenas de miles de filas agregadas)
hace que el full refresh sea simple, seguro y suficientemente rapido.

Programado por cron:  0 * * * *   (ver scripts/crontab.txt)

Uso manual:
    python sync_stock.py
"""

import time
from db_config import conectar_mariadb, conectar_sqlserver, log

# Agregacion en origen: stock por producto/bodega + alerta + caducidad proxima
QUERY_ORIGEN = """
    SELECT
        iu.producto_id,
        p.nombre                         AS nombre_producto,
        iu.bodega_id,
        b.nombre                         AS nombre_bodega,
        b.provincia,
        SUM(iu.stock_actual)             AS stock_total,
        p.precio_venta,
        MAX(iu.alerta_stock)             AS en_alerta,
        MIN(iu.fecha_vencimiento)        AS proxima_caducidad
    FROM inventario_ubicacion iu
    JOIN productos p ON p.producto_id = iu.producto_id
    JOIN bodegas   b ON b.bodega_id   = iu.bodega_id
    GROUP BY iu.producto_id, p.nombre, iu.bodega_id,
             b.nombre, b.provincia, p.precio_venta
"""

INSERT_DESTINO = """
    INSERT INTO reportes.consolidado_stock
        (producto_id, nombre_producto, bodega_id, nombre_bodega, provincia,
         stock_total, precio_venta, en_alerta, proxima_caducidad)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def main():
    t0 = time.time()
    log("=== sync_stock (HORARIO) iniciado ===")

    # 1) Extraer de MariaDB con el usuario de solo lectura
    src = conectar_mariadb(usar_sync=True)
    cur_src = src.cursor()
    cur_src.execute(QUERY_ORIGEN)
    filas = cur_src.fetchall()
    cur_src.close()
    src.close()
    log(f"Extraidas {len(filas)} filas agregadas de MariaDB")

    # 2) Cargar en SQL Server con patron DELETE + INSERT transaccional
    dst = conectar_sqlserver()
    cur_dst = dst.cursor()
    cur_dst.fast_executemany = True
    try:
        cur_dst.execute("DELETE FROM reportes.consolidado_stock")
        # normalizar tipos (en_alerta a BIT)
        datos = [
            (f[0], f[1], f[2], f[3], f[4], int(f[5] or 0),
             float(f[6] or 0), int(f[7] or 0), f[8])
            for f in filas
        ]
        cur_dst.executemany(INSERT_DESTINO, datos)
        dst.commit()
        log(f"Cargadas {len(datos)} filas en consolidado_stock")
    except Exception as e:
        dst.rollback()
        log(f"ERROR, rollback aplicado: {e}")
        raise
    finally:
        cur_dst.close()
        dst.close()

    log(f"=== sync_stock finalizado en {time.time() - t0:.2f}s ===")


if __name__ == "__main__":
    main()
