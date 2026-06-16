"""
generar_oracle.py  ·  Carga inicial de Oracle con datos realistas (Faker).

Pobla las tablas transaccionales del schema `logistica`:
    - 200.000 movimientos (ENTRADA / SALIDA / DEVOLUCION)
    - 1 a 5 lineas de detalle por movimiento

Las referencias (proveedor_id, bodega_id, producto_id) son IDs logicos que
coinciden con los rangos generados en MariaDB para que el ETL pueda cruzarlos.

Uso:
    python generar_oracle.py
"""

import random
from datetime import datetime, timedelta

from faker import Faker
from db_config import conectar_oracle, log

fake = Faker("es_ES")
Faker.seed(2026)
random.seed(2026)

N_MOVIMIENTOS = 200_000
N_PROVEEDORES = 1_000     # debe coincidir con generar_mariadb.py
N_BODEGAS     = 50
N_PRODUCTOS   = 8_000
LOTE          = 5_000     # batch para executemany

TIPOS = ["ENTRADA", "SALIDA", "DEVOLUCION"]
PESOS = [0.45, 0.45, 0.10]


def main():
    conn = conectar_oracle(usar_sync=False)   # schema logistica (escritura)
    cur = conn.cursor()
    try:
        log("Limpiando tablas previas (movimientos_detalle, movimientos)...")
        cur.execute("DELETE FROM movimientos_detalle")
        cur.execute("DELETE FROM movimientos")
        conn.commit()

        log(f"Generando {N_MOVIMIENTOS} movimientos...")
        inicio = datetime.now() - timedelta(days=365)

        # Insertamos cabecera por lotes y recuperamos los IDs para el detalle.
        movimiento_id = 0
        for base in range(0, N_MOVIMIENTOS, LOTE):
            cabeceras = []
            n = min(LOTE, N_MOVIMIENTOS - base)
            for _ in range(n):
                tipo = random.choices(TIPOS, weights=PESOS)[0]
                fecha = inicio + timedelta(
                    days=random.randint(0, 364),
                    seconds=random.randint(0, 86399),
                )
                cabeceras.append((
                    tipo,
                    random.randint(1, N_PROVEEDORES) if tipo != "SALIDA" else None,
                    random.randint(1, N_BODEGAS),
                    fake.bothify("DOC-########").upper(),
                    fecha,
                    "CONFIRMADO",
                ))
            cur.executemany(
                "INSERT INTO movimientos (tipo, proveedor_id, bodega_id, "
                "documento, fecha_mov, estado) "
                "VALUES (:1, :2, :3, :4, :5, :6)",
                cabeceras,
            )
            conn.commit()

            # Detalle del lote recien insertado
            detalles = []
            for k in range(n):
                movimiento_id += 1
                for _ in range(random.randint(1, 5)):
                    cant = round(random.uniform(1, 200), 3)
                    precio = round(random.uniform(0.5, 80.0), 4)
                    venc = datetime.now() + timedelta(days=random.randint(30, 720))
                    detalles.append((
                        movimiento_id,
                        random.randint(1, N_PRODUCTOS),
                        cant, precio,
                        fake.bothify("L-####-??").upper(),
                        venc,
                    ))
            cur.executemany(
                "INSERT INTO movimientos_detalle (movimiento_id, producto_id, "
                "cantidad, precio_unitario, lote, fecha_vencimiento) "
                "VALUES (:1, :2, :3, :4, :5, :6)",
                detalles,
            )
            conn.commit()
            log(f"  {base + n}/{N_MOVIMIENTOS} movimientos cargados")

        # Recalcular valor_total de cada cabecera a partir del detalle
        log("Recalculando valor_total de las cabeceras...")
        cur.execute("""
            MERGE INTO movimientos m
            USING (
                SELECT movimiento_id, SUM(subtotal) AS total
                FROM movimientos_detalle
                GROUP BY movimiento_id
            ) d ON (m.movimiento_id = d.movimiento_id)
            WHEN MATCHED THEN UPDATE SET m.valor_total = d.total
        """)
        conn.commit()
        log("Carga de Oracle completada y confirmada.")
    except Exception as e:
        conn.rollback()
        log(f"ERROR, rollback aplicado: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
