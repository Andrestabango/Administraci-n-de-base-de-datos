"""
prueba_carga_5000.py  ·  Validacion de desempeno de la interconexion.

Cumple los requisitos de validacion de la consigna:
    - Prueba de carga basica: inserta 5.000 registros nuevos de inventario
      en MariaDB con Faker.
    - Tiempos de respuesta: mide la duracion de la insercion y de la
      sincronizacion (sync_stock) que propaga los datos a SQL Server.
    - Validacion de integridad: compara conteos y agregados entre el origen
      (MariaDB) y el destino (SQL Server) tras la sincronizacion.

Uso:
    python prueba_carga_5000.py
"""

import random
import time
from datetime import date, timedelta

from faker import Faker
from db_config import (conectar_mariadb, conectar_sqlserver, log)
import sync_stock

fake = Faker("es_ES")
N_PRUEBA   = 5_000
N_PRODUCTOS = 8_000
N_BODEGAS   = 50


def insertar_5000_mariadb():
    """Inserta 5.000 filas de inventario y devuelve (segundos, filas)."""
    conn = conectar_mariadb()
    cur = conn.cursor()
    hoy = date.today()
    datos = []
    combos = set()
    while len(datos) < N_PRUEBA:
        prod = random.randint(1, N_PRODUCTOS)
        bod = random.randint(1, N_BODEGAS)
        lote = fake.bothify("T-####-??").upper()   # prefijo T = test
        ubic = f"{random.randint(1,20)}-{random.randint(1,10)}-{random.randint(1,5)}"
        clave = (prod, bod, lote, ubic)
        if clave in combos:
            continue
        combos.add(clave)
        venc = hoy + timedelta(days=random.randint(30, 720))
        datos.append((prod, bod, ubic, lote,
                      random.randint(1, 500), venc))

    t0 = time.time()
    cur.executemany(
        "INSERT INTO inventario_ubicacion (producto_id, bodega_id, ubicacion, "
        "lote, stock_actual, fecha_vencimiento) VALUES (%s,%s,%s,%s,%s,%s)",
        datos,
    )
    conn.commit()
    dur = time.time() - t0
    cur.close()
    conn.close()
    return dur, len(datos)


def validar_integridad():
    """Compara stock agregado origen vs destino. Devuelve dict de resultados."""
    # Origen: MariaDB
    src = conectar_mariadb(usar_sync=True)
    cs = src.cursor()
    cs.execute("""
        SELECT COUNT(DISTINCT CONCAT(producto_id,'-',bodega_id)) AS combos,
               COALESCE(SUM(stock_actual),0) AS stock_total
        FROM inventario_ubicacion
    """)
    combos_src, stock_src = cs.fetchone()
    cs.close(); src.close()

    # Destino: SQL Server
    dst = conectar_sqlserver()
    cd = dst.cursor()
    cd.execute("""
        SELECT COUNT(*) AS filas,
               COALESCE(SUM(stock_total),0) AS stock_total
        FROM reportes.consolidado_stock
    """)
    filas_dst, stock_dst = cd.fetchone()
    cd.close(); dst.close()

    return {
        "combos_origen": combos_src,
        "filas_destino": filas_dst,
        "stock_origen": int(stock_src),
        "stock_destino": int(stock_dst),
        "coincide_combos": combos_src == filas_dst,
        "coincide_stock": int(stock_src) == int(stock_dst),
    }


def main():
    log("============================================================")
    log(" PRUEBA DE CARGA Y VALIDACION DE INTEGRIDAD (5.000 registros)")
    log("============================================================")

    # 1) Carga de 5.000 registros
    dur_carga, n = insertar_5000_mariadb()
    log(f"[CARGA] {n} registros insertados en MariaDB en {dur_carga:.3f}s "
        f"({n / dur_carga:,.0f} reg/s)")

    # 2) Sincronizacion a SQL Server (tiempo de respuesta interconexion)
    t0 = time.time()
    sync_stock.main()
    dur_sync = time.time() - t0
    log(f"[SYNC] Interconexion completada en {dur_sync:.3f}s")

    # 3) Validacion de integridad
    r = validar_integridad()
    log("[INTEGRIDAD] Resultados:")
    log(f"   combos origen (MariaDB)   : {r['combos_origen']}")
    log(f"   filas destino (SQLServer) : {r['filas_destino']}")
    log(f"   stock total origen        : {r['stock_origen']}")
    log(f"   stock total destino       : {r['stock_destino']}")
    log(f"   coincide #combos          : {r['coincide_combos']}")
    log(f"   coincide stock total      : {r['coincide_stock']}")

    ok = r["coincide_combos"] and r["coincide_stock"]
    log("------------------------------------------------------------")
    log(f" RESULTADO FINAL: {'INTEGRIDAD OK' if ok else 'REVISAR DISCREPANCIAS'}")
    log("------------------------------------------------------------")


if __name__ == "__main__":
    main()
