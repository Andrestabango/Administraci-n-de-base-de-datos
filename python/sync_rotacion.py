"""
sync_rotacion.py  ·  ETL DIARIO  ·  Oracle + MariaDB  ->  SQL Server

Construye dos reportes consolidados en SQL Server a partir de los movimientos
de Oracle, enriquecidos con los maestros (productos/proveedores/categorias) de
MariaDB:

    reportes.reporte_rotacion        entradas vs salidas por producto y periodo
    reportes.reporte_abastecimiento  unidades y valor por proveedor y periodo

Estrategia: por cada periodo procesado se hace DELETE de ese periodo en el
destino y luego INSERT de los datos recien calculados (refresh idempotente),
todo dentro de una transaccion. Se ejecuta de noche porque agrega grandes
volumenes de movimientos y conviene hacerlo fuera del horario operativo.

Programado por cron:  0 0 * * *   (ver scripts/crontab.txt)

Uso manual:
    python sync_rotacion.py
"""

import time
from collections import defaultdict
from db_config import conectar_oracle, conectar_mariadb, conectar_sqlserver, log

# ── Origen Oracle: rotacion (entradas/salidas) por producto y periodo ──────
Q_ROTACION_ORA = """
    SELECT d.producto_id,
           TO_CHAR(m.fecha_mov, 'YYYY-MM')                         AS periodo,
           SUM(CASE WHEN m.tipo = 'ENTRADA'    THEN d.cantidad ELSE 0 END) AS entradas,
           SUM(CASE WHEN m.tipo IN ('SALIDA','DEVOLUCION')
                    THEN d.cantidad ELSE 0 END)                    AS salidas
    FROM movimientos m
    JOIN movimientos_detalle d ON d.movimiento_id = m.movimiento_id
    WHERE m.estado = 'CONFIRMADO'
    GROUP BY d.producto_id, TO_CHAR(m.fecha_mov, 'YYYY-MM')
"""

# ── Origen Oracle: abastecimiento (solo ENTRADAS) por proveedor y periodo ──
Q_ABASTO_ORA = """
    SELECT m.proveedor_id,
           TO_CHAR(m.fecha_mov, 'YYYY-MM')   AS periodo,
           SUM(d.cantidad)                   AS unidades,
           SUM(d.subtotal)                   AS valor
    FROM movimientos m
    JOIN movimientos_detalle d ON d.movimiento_id = m.movimiento_id
    WHERE m.tipo = 'ENTRADA' AND m.estado = 'CONFIRMADO'
          AND m.proveedor_id IS NOT NULL
    GROUP BY m.proveedor_id, TO_CHAR(m.fecha_mov, 'YYYY-MM')
"""


def cargar_maestros_mariadb():
    """Devuelve diccionarios de enriquecimiento desde MariaDB."""
    conn = conectar_mariadb(usar_sync=True)
    cur = conn.cursor()

    cur.execute("""
        SELECT p.producto_id, p.nombre, c.nombre
        FROM productos p JOIN categorias c ON c.categoria_id = p.categoria_id
    """)
    productos = {r[0]: (r[1], r[2]) for r in cur.fetchall()}

    cur.execute("SELECT proveedor_id, nombre FROM proveedores")
    proveedores = {r[0]: r[1] for r in cur.fetchall()}

    cur.close()
    conn.close()
    log(f"Maestros MariaDB: {len(productos)} productos, "
        f"{len(proveedores)} proveedores")
    return productos, proveedores


def sync_rotacion(cur_ora, cur_dst, productos):
    cur_ora.execute(Q_ROTACION_ORA)
    filas = cur_ora.fetchall()
    log(f"Rotacion: {len(filas)} grupos producto/periodo desde Oracle")

    periodos = {f[1] for f in filas}
    for p in periodos:
        cur_dst.execute(
            "DELETE FROM reportes.reporte_rotacion WHERE periodo = ?", p)

    datos = []
    for prod_id, periodo, entradas, salidas in filas:
        nombre, categoria = productos.get(prod_id, (f"Producto {prod_id}", None))
        datos.append((prod_id, nombre, categoria,
                      float(entradas or 0), float(salidas or 0), periodo))

    cur_dst.executemany(
        "INSERT INTO reportes.reporte_rotacion "
        "(producto_id, nombre_producto, categoria, total_entradas, "
        " total_salidas, periodo) VALUES (?, ?, ?, ?, ?, ?)",
        datos,
    )
    log(f"Rotacion: {len(datos)} filas insertadas")


def sync_abastecimiento(cur_ora, cur_dst, proveedores):
    cur_ora.execute(Q_ABASTO_ORA)
    filas = cur_ora.fetchall()
    log(f"Abastecimiento: {len(filas)} grupos proveedor/periodo desde Oracle")

    periodos = {f[1] for f in filas}
    for p in periodos:
        cur_dst.execute(
            "DELETE FROM reportes.reporte_abastecimiento WHERE periodo = ?", p)

    datos = []
    for prov_id, periodo, unidades, valor in filas:
        nombre = proveedores.get(prov_id, f"Proveedor {prov_id}")
        datos.append((prov_id, nombre,
                      float(unidades or 0), float(valor or 0), periodo))

    cur_dst.executemany(
        "INSERT INTO reportes.reporte_abastecimiento "
        "(proveedor_id, nombre_proveedor, total_unidades_entrada, "
        " total_valor, periodo) VALUES (?, ?, ?, ?, ?)",
        datos,
    )
    log(f"Abastecimiento: {len(datos)} filas insertadas")


def main():
    t0 = time.time()
    log("=== sync_rotacion (DIARIO) iniciado ===")

    productos, proveedores = cargar_maestros_mariadb()

    ora = conectar_oracle(usar_sync=True)   # sync_reader_ora (solo lectura)
    cur_ora = ora.cursor()
    cur_ora.arraysize = 5_000

    dst = conectar_sqlserver()
    cur_dst = dst.cursor()
    cur_dst.fast_executemany = True

    try:
        sync_rotacion(cur_ora, cur_dst, productos)
        sync_abastecimiento(cur_ora, cur_dst, proveedores)
        dst.commit()
        log("Reportes diarios confirmados en SQL Server")
    except Exception as e:
        dst.rollback()
        log(f"ERROR, rollback aplicado: {e}")
        raise
    finally:
        cur_ora.close(); ora.close()
        cur_dst.close(); dst.close()

    log(f"=== sync_rotacion finalizado en {time.time() - t0:.2f}s ===")


if __name__ == "__main__":
    main()
