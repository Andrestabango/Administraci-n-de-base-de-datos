# En el archivo adjunto se debe de ejecutar lo siguiente
# nano /home/oracle/proyecto_integrador/scripts/generar_oracle.py
"""
Genera 200.000 movimientos logisticos en Oracle.
Ejecutar UNA SOLA VEZ sobre una base vacia.
"""
import random
from datetime import datetime, timedelta
from faker import Faker
import cx_Oracle

fake = Faker('es_ES')

dsn = cx_Oracle.makedsn('127.0.0.1', 1523, service_name='orclpdb.lab.local')
conn = cx_Oracle.connect(user='logistica', password='Logist1ca#2026', dsn=dsn)
cur = conn.cursor()

BATCH = 1000
fecha_inicio = datetime(2023, 1, 1)

for batch_num in range(200):
    mov_ids = []
    for _ in range(BATCH):
        fecha = fecha_inicio + timedelta(days=random.randint(0, 730))
        var_out = cur.var(cx_Oracle.NUMBER)
        cur.execute("""
            INSERT INTO movimientos (tipo, fecha, bodega_id, estado)
            VALUES (:1, :2, :3, :4)
            RETURNING movimiento_id INTO :5
        """, [
            random.choice(['ENTRADA', 'SALIDA']),
            fecha,
            random.randint(1, 50),
            'PROCESADO',
            var_out
        ])
        # NOTA: getvalue() retorna lista, se accede al primer elemento con [0]
        mov_ids.append(int(var_out.getvalue()[0]))

    detalles = []
    for mov_id in mov_ids:
        for _ in range(random.randint(1, 5)):
            detalles.append((
                mov_id,
                random.randint(1, 8000),
                round(random.uniform(1, 500), 3),
                round(random.uniform(0.5, 9999.99), 2)
            ))

    cur.executemany("""
        INSERT INTO movimientos_detalle
          (movimiento_id, producto_id, cantidad, precio_unitario)
        VALUES (:1, :2, :3, :4)
    """, detalles)

    conn.commit()
    print(f"  Lote {batch_num+1}/200 — {(batch_num+1)*BATCH} movimientos")

cur.close()
conn.close()
print("Datos Oracle generados exitosamente")