"""
Genera datos iniciales para el schema inventarios en MariaDB.
IMPORTANTE: ejecutar UNA SOLA VEZ sobre una base vacia.
"""
import random
from faker import Faker
import mysql.connector

fake = Faker('es_ES')

conn = mysql.connector.connect(
    host='127.0.0.1', port=3307,
    user='dba_mariadb', password='MariaDB_Proj#2026',
    database='inventarios'
)
cur = conn.cursor()

# Categorias
CATEGORIAS = [
    'Electronica','Alimentos','Bebidas','Ferreteria',
    'Textiles','Farmacia','Automotriz','Oficina',
    'Limpieza','Jardineria'
]
for cat in CATEGORIAS:
    cur.execute("INSERT IGNORE INTO categorias (nombre) VALUES (%s)", (cat,))
conn.commit()
print("Categorias: OK")

# Proveedores (1000)
for _ in range(1000):
    cur.execute("""
        INSERT INTO proveedores (nombre, ruc, email, telefono, ciudad)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        fake.company(),
        fake.numerify('##########001'),
        fake.company_email(),
        fake.phone_number()[:20],
        fake.city()
    ))
conn.commit()
print("Proveedores: OK")

# Bodegas (50)
ciudades = ['Quito','Guayaquil','Cuenca','Ambato','Loja',
            'Manta','Ibarra','Riobamba','Esmeraldas','Machala']
for i in range(1, 51):
    cur.execute("""
        INSERT INTO bodegas (codigo, nombre, ciudad, capacidad_m3)
        VALUES (%s, %s, %s, %s)
    """, (
        f'BOD-{i:03d}',
        f'Bodega {fake.city()} {i}',
        random.choice(ciudades),
        round(random.uniform(500, 5000), 2)
    ))
conn.commit()
print("Bodegas: OK")

# Productos (8000)
cur.execute("SELECT categoria_id FROM categorias")
cat_ids = [r[0] for r in cur.fetchall()]
cur.execute("SELECT proveedor_id FROM proveedores")
prov_ids = [r[0] for r in cur.fetchall()]

for i in range(8000):
    cur.execute("""
        INSERT INTO productos
          (sku, nombre, precio_unitario, peso_kg, categoria_id, proveedor_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        f'SKU-{i+1:06d}',
        fake.catch_phrase()[:200],
        round(random.uniform(0.50, 9999.99), 2),
        round(random.uniform(0.01, 50.0), 3),
        random.choice(cat_ids),
        random.choice(prov_ids)
    ))
    if i % 500 == 0:
        conn.commit()
        print(f"  Productos: {i}/8000")
conn.commit()
print("Productos: OK")

# Inventario por ubicacion
# stock_minimo <= cantidad <= stock_maximo para mantener consistencia logica
cur.execute("SELECT producto_id FROM productos LIMIT 5000")
prod_ids = [r[0] for r in cur.fetchall()]
cur.execute("SELECT bodega_id FROM bodegas")
bod_ids = [r[0] for r in cur.fetchall()]

combinaciones = set()
insertados = 0
intentos = 0
while insertados < 10000 and intentos < 100000:
    p = random.choice(prod_ids)
    b = random.choice(bod_ids)
    intentos += 1
    if (p, b) in combinaciones:
        continue
    combinaciones.add((p, b))
    stock_minimo = round(random.uniform(10, 100), 3)
    cantidad = round(random.uniform(stock_minimo, stock_minimo + 500), 3)
    stock_maximo = round(random.uniform(cantidad, cantidad + 500), 3)
    cur.execute("""
        INSERT INTO inventario_ubicacion
          (producto_id, bodega_id, cantidad, stock_minimo, stock_maximo)
        VALUES (%s, %s, %s, %s, %s)
    """, (p, b, cantidad, stock_minimo, stock_maximo))
    insertados += 1
    if insertados % 1000 == 0:
        conn.commit()
        print(f"  Inventario: {insertados}/10000")

conn.commit()
print(f"Inventario: {insertados} registros - OK")
cur.close()
conn.close()
print("Datos MariaDB generados exitosamente")