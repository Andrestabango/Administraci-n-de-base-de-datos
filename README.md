# Plataforma de Base de Datos Heterogénea Interconectada

![Oracle](https://img.shields.io/badge/Oracle-19c-F80000?logo=oracle&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-11-003545?logo=mariadb&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2022-CC2927?logo=microsoftsqlserver&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-CE-2496ED?logo=docker&logoColor=white)
![Faker](https://img.shields.io/badge/Faker-25.2.0-4B8BBE)
![Linux](https://img.shields.io/badge/RHEL-8.10-EE0000?logo=redhat&logoColor=white)
![ETL](https://img.shields.io/badge/ETL-cron%20horario%20%2F%20diario-02C39A)
![RC5](https://img.shields.io/badge/RC5-trabajo%20en%20equipo-success)
![Status](https://img.shields.io/badge/build-passing-brightgreen)


## 📋 Información del Proyecto

| Campo | Valor |
|-------|-------|
| **Materia** | ITIZ3201 |
| **RAM / CPU / Disco** | 12 GB / 4 vCPU / 100 GB |
| **Sistema Operativo** | Red Hat 8.10 |
| **IP de la VM** | 192.168.152.191 |
| **Versión** | RC5 Final |
| **Estado** | Producción |

---

## 👥 Equipo de Trabajo

| Iniciales | Nombre | Rol | Responsabilidades |
|-----------|--------|-----|-------------------|
| **GR** | Guillermo Ruales | Líder — Oracle + Interconexión | Oracle 19c, reconfiguración, scripts ETL, orchestración cron |
| **IT** | Israel Tabango | MariaDB + Faker | MariaDB 11, datos maestros, generación con Faker |
| **AM** | Anthony Montalvo | SQL Server + Sync Stock | SQL Server 2022, consolidación de reportes, sincronización horaria |
| **LC** | Luis Cando | Docker + Documentación | Docker Engine, scripts de instalación, documentación |

---

## 🏗️ Arquitectura de la Solución

### Distribución Heterogénea por Motor

```
┌─────────────────────────────────────────────────────────────────┐
│                    VM RED HAT 8.10                              │
│              IP: 192.168.152.191 | 12GB RAM | 4vCPU            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │   ORACLE 19c     │  │   MARIADB 11     │  │  SQL SERVER  │  │
│  │   (NATIVO)       │  │    (DOCKER)      │  │    2022      │  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤  │
│  │ Puerto: 1523     │  │ Puerto: 3307     │  │ Puerto: 1434 │  │
│  │ Schema: logistica│  │ Schema:inventarios│ │ BD: reportes │  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤  │
│  │ • movimientos    │  │ • categorias     │  │ • consolidado│  │
│  │ • mov_detalle    │  │ • proveedores    │  │   _stock     │  │
│  │                  │  │ • productos      │  │ • reporte_   │  │
│  │ DBA: dba_oracle  │  │ • bodegas        │  │   rotacion   │  │
│  │                  │  │ • inventario_    │  │ • reporte_   │  │
│  │ 200K+ movs       │  │   ubicacion      │  │   abastec.   │  │
│  │                  │  │                  │  │              │  │
│  │                  │  │ DBA: dba_mariadb │  │ DBA:         │  │
│  │                  │  │ Reader: sync_r.  │  │ dba_sqlserver│  │
│  │                  │  │                  │  │              │  │
│  │                  │  │ ~13.9K registros │  │ Dinámico via │  │
│  │                  │  │                  │  │ Python ETL   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│          ↓                     ↓                      ↑          │
│  ┌─────────────────────────────┴──────────────────────┐         │
│  │      PYTHON ETL (Cron)                            │         │
│  ├──────────────────────────────────────────────────┤         │
│  │ • sync_stock.py (cada hora)                       │         │
│  │   MariaDB → SQL Server consolidado_stock          │         │
│  │                                                   │         │
│  │ • sync_rotacion.py (diario medianoche)           │         │
│  │   Oracle + MariaDB → SQL Server reporte_rotacion │         │
│  └──────────────────────────────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↑
    DBeaver Community (Windows)
    Conexiones SQL desde cliente gráfico
```

---

## 📦 Estructura del Repositorio

```
proyecto-bd-heterogenea-itiz3201/
│
├── README.md                                 # Este archivo
├── .gitignore                               # Archivos a ignorar
│
├── oracle/                                   # Oracle 19c (Guillermo)
│   ├── 00_limpieza.sql                      # DROP usuarios/roles/tbs de laboratorio
│   ├── 01_setup_oracle.sql                  # CREATE TABLESPACE tbs_logistica
│   │                                        # CREATE USER dba_oracle, logistica
│   ├── 02_ddl_tablas.sql                    # CREATE TABLE movimientos
│   │                                        # CREATE TABLE movimientos_detalle
│   ├── listener.ora                         # Configuración listener puerto 1523
│   └── tnsnames.ora                         # Alias ORCL, ORCLPDB con puerto 1523
│
├── mariadb/                                  # MariaDB 11 (Israel)
│   ├── 00_setup.sql                         # GRANT dba_mariadb, CREATE sync_reader
│   └── 01_ddl_tablas.sql                    # CREATE TABLE categorias, productos,
│                                            # bodegas, inventario_ubicacion
│
├── sqlserver/                                # SQL Server 2022 (Anthony)
│   ├── 00_setup.sql                         # CREATE DATABASE reportes
│   │                                        # CREATE LOGIN dba_sqlserver
│   ├── 01_ddl_tablas.sql                    # CREATE TABLE consolidado_stock
│   │                                        # reporte_rotacion, reporte_abastec.
│   │                                        # PERSISTED columna calculada
│   └── 02_permisos_sync.sql                 # GRANT DELETE a sync_writer
│
├── docker/                                   # Docker (Luis)
│   ├── deploy_mariadb.sh                    # docker run mariadb:11 puerto 3307
│   ├── deploy_sqlserver.sh                  # docker run mssql 2022 puerto 1434
│   └── docker-compose.yml                   # Orquestación completa 2 contenedores
│
├── python/                                   # Scripts Python + Faker
│   ├── requirements.txt                     # Faker, mysql-connector, cx_Oracle
│   │                                        # pyodbc, protobuf (Luis)
│   ├── generar_mariadb.py                   # Carga inicial: 10 categorias
│   │                                        # 1000 proveedores, 8000 productos
│   │                                        # 50 bodegas, ~10K inventario (Israel)
│   ├── generar_oracle.py                    # Carga inicial: 200.000 movimientos
│   │                                        # 1-5 detalles/movimiento (Guillermo)
│   ├── sync_stock.py                        # ETL HORARIO (cron 0 * * * *)
│   │                                        # MariaDB → SQL Server stock (Anthony)
│   ├── sync_rotacion.py                     # ETL DIARIO (cron 0 0 * * *)
│   │                                        # Oracle + MariaDB → SQL Server (Guillermo)
│   └── prueba_carga_5000.py                 # Test: 5000 registros inventario (Anthony)
│
├── scripts/                                  # Scripts de instalación
│   ├── 01_install_docker.sh                 # Remover Podman, instalar Docker CE (Luis)
│   └── crontab.txt                          # Jobs: sync_stock (horario)
│                                            # sync_rotacion (diario) (Guillermo)
│
└── docs/                                     # Documentación
    ├── diagrama_arquitectura.png            # Visualización componentes
    └── informe_cumplimiento.md              # Checklist de requisitos
```

---

## 🔧 Requisitos Previos

- **OS**: Red Hat 8.10 en máquina virtual
- **Hardware**: 12 GB RAM, 4 vCPU, 100 GB disco
- **Oracle**: 19c instalado y funcionando (native)
- **Red Hat**: Acceso root para instalar paquetes
- **Herramientas**:
  - Git instalado (Linux o Windows)
  - DBeaver Community (Windows para conexiones)
  - Python 3.6+ (en Red Hat)

---

## 🚀 Guía de Instalación Paso a Paso

### FASE 1: Limpieza y Reconfiguración de Oracle

```bash
# 1. Ejecutar limpieza (como usuario oracle)
cd /home/oracle/proyecto-bd-heterogenea-itiz3201/oracle
sqlplus / as sysdba
@00_limpieza.sql

# 2. Reconfigurar listener a puerto 1523
# Editar: /u01/app/oracle/product/19.0.0/dbhome_1/network/admin/listener.ora
nano $ORACLE_HOME/network/admin/listener.ora
# Cambiar puerto de 1521 a 1523
lsnrctl stop
lsnrctl start
lsnrctl status

# 3. Crear tablespace, DBA y schema
sqlplus / as sysdba
@01_setup_oracle.sql
```

### FASE 2: Instalar Docker Engine

```bash
# Como root
bash scripts/01_install_docker.sh

# Agregar oracle al grupo docker
usermod -aG docker oracle
# Nueva sesión
newgrp docker

# Crear red Docker
docker network create --driver bridge bd_heterogenea_net

# Crear directorios persistentes
mkdir -p /u02/docker/mariadb/data
mkdir -p /u02/docker/sqlserver/data
chown -R oracle:oinstall /u02/docker/mariadb
chown -R 10001:0 /u02/docker/sqlserver/data
```

### FASE 3: Desplegar MariaDB 11

```bash
# Como oracle
bash docker/deploy_mariadb.sh

# Verificar
docker ps
docker logs mariadb_inventarios

# Conectar y configurar permisos
mysql -h 127.0.0.1 -P 3307 -u root -p"RootMariaDB#2026" inventarios
@mariadb/00_setup.sql
@mariadb/01_ddl_tablas.sql
```

### FASE 4: Desplegar SQL Server 2022

```bash
# Como oracle
bash docker/deploy_sqlserver.sh

# Esperar 30 segundos a que inicie
sleep 30
docker logs sqlserver_reportes | tail -30

# Conectar y crear BD
docker exec -it sqlserver_reportes \
  /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA \
  -P "SqlSrvProj#2026" -No -C
@sqlserver/00_setup.sql
@sqlserver/01_ddl_tablas.sql
@sqlserver/02_permisos_sync.sql
```

### FASE 5: Generar Datos Iniciales con Faker

```bash
# Instalar dependencias Python
pip3 install --user --no-cache-dir -r python/requirements.txt

# Generar datos MariaDB (una sola vez)
python3 python/generar_mariadb.py

# Generar datos Oracle (una sola vez)
python3 python/generar_oracle.py

# Verificar carga
mysql -h 127.0.0.1 -P 3307 -u dba_mariadb -p"MariaDB_Proj#2026" inventarios
SELECT COUNT(*) FROM inventario_ubicacion;
```

### FASE 6: Configurar Python ETL + Cron

```bash
# Hacer ejecutables
chmod +x python/sync_stock.py
chmod +x python/sync_rotacion.py

# Editar crontab
crontab -e

# Pegar contenido de scripts/crontab.txt
# Variables de entorno + 2 jobs
```

### FASE 7: Validación Funcional

```bash
# Prueba de carga 5000 registros
time python3 python/prueba_carga_5000.py

# Ejecutar sincronización manualmente
time python3 python/sync_stock.py
time python3 python/sync_rotacion.py

# Verificar integridad en SQL Server
docker exec -it sqlserver_reportes \
  /opt/mssql-tools18/bin/sqlcmd -S localhost \
  -U dba_sqlserver -P "SqlSrvDBA#2026" -d reportes -No -C
SELECT COUNT(*) FROM reportes.consolidado_stock;
SELECT COUNT(*) FROM reportes.reporte_rotacion;
```

---

## 🗄️ Esquema de Datos

### Oracle: Schema `logistica`

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| `movimientos` | 200.000+ | Transacciones: ENTRADA/SALIDA, fecha, bodega_id (referencia lógica MariaDB) |
| `movimientos_detalle` | 500.000+ | Items detalle de cada movimiento: producto_id, cantidad, lote, vencimiento |

**Índices**: fecha, bodega_id, producto_id, movimiento_id  
**DBA**: `dba_oracle` | **App**: `logistica`

### MariaDB: Schema `inventarios`

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| `categorias` | 10 | Maestro: 10 categorías iniciales |
| `proveedores` | 1.000 | Faker: empresas + contacto |
| `productos` | 8.000 | Faker: SKU-000001 a SKU-008000 + precios |
| `bodegas` | 50 | Faker: BOD-001 a BOD-050 en ciudades Ecuador |
| `inventario_ubicacion` | ~13.910 | Ubicación de cada producto en bodega: qty, stock_min/max |

**Constraints**: UNIQUE (producto_id, bodega_id) en inventario_ubicacion  
**DBA**: `dba_mariadb` | **Read-only**: `sync_reader`

### SQL Server: Schema `reportes.reportes`

| Tabla | Tipo | Actualización | Descripción |
|-------|------|--------------|-------------|
| `consolidado_stock` | Consolidación | Horaria (sync_stock.py) | Stock actual + alertas |
| `reporte_rotacion` | Análisis | Diaria (sync_rotacion.py) | Índice de rotación PERSISTED |
| `reporte_abastecimiento` | Análisis | Diaria (sync_rotacion.py) | Resumen de entradas por proveedor |

---

## 🐍 Python + Faker + ETL

### Dependencias (requirements.txt)
```
Faker==13.15.1
mysql-connector-python==8.0.28
cx_Oracle==8.3.0
pyodbc==4.0.39
protobuf==3.19.6
```

### Scripts Principales

#### `generar_mariadb.py` — Carga Inicial (ejecutar UNA sola vez)
```bash
python3 python/generar_mariadb.py
# Genera: 10 categorías, 1000 proveedores, 8000 productos, 50 bodegas, ~10K inventario
# Tiempo: ~60-90 segundos
```

#### `generar_oracle.py` — Carga Inicial (ejecutar UNA sola vez)
```bash
python3 python/generar_oracle.py
# Genera: 200.000 movimientos en lotes, 1-5 detalles cada uno
# Tiempo: ~3-5 minutos
```

#### `sync_stock.py` — ETL Horario
```bash
python3 python/sync_stock.py
# CRON: 0 * * * * (cada hora en minuto 0)
# Origen: MariaDB.inventario_ubicacion + productos + bodegas
# Destino: SQL Server.consolidado_stock
# Patrón: DELETE día actual + INSERT frescos
# Tiempo: 10-15 segundos (~13.910 registros)
```

#### `sync_rotacion.py` — ETL Diario
```bash
python3 python/sync_rotacion.py
# CRON: 0 0 * * * (medianoche)
# Origen 1: Oracle.movimientos (período actual YYYY-MM)
# Origen 2: MariaDB.productos (enriquecimiento nombres)
# Destino: SQL Server.reporte_rotacion (cálculo índice = salidas/entradas)
# Tiempo: 5-8 segundos
```

#### `prueba_carga_5000.py` — Validación
```bash
time python3 python/prueba_carga_5000.py
# Inserta 5000 registros ÚNICOS en inventario_ubicacion
# Valida: coherencia stock_min ≤ qty ≤ stock_max
# Resultado: ~0.5-1 segundo
```

---

## ⏰ Jobs Programados (Cron)

Editar con `crontab -e` como usuario `oracle`:

```bash
# Variables de entorno (OBLIGATORIAS para cx_Oracle en cron)
ORACLE_HOME=/u01/app/oracle/product/19.0.0/dbhome_1
ORACLE_SID=orcl
LD_LIBRARY_PATH=/u01/app/oracle/product/19.0.0/dbhome_1/lib:/lib:/usr/lib
PATH=/usr/local/bin:/usr/bin:/bin:/home/oracle/.local/bin:/u01/app/oracle/product/19.0.0/dbhome_1/bin

# ============ JOBS ============

# Sincronización de STOCK: cada hora
0 * * * * python3 /home/oracle/proyecto_integrador/scripts/sync_stock.py >> /home/oracle/proyecto_integrador/logs/sync_stock.log 2>&1

# Sincronización de ROTACIÓN: diaria a medianoche
0 0 * * * python3 /home/oracle/proyecto_integrador/scripts/sync_rotacion.py >> /home/oracle/proyecto_integrador/logs/sync_rotacion.log 2>&1
```

**Verificar activos**:
```bash
crontab -l
ps aux | grep sync_
tail -f /home/oracle/proyecto_integrador/logs/sync_stock.log
```

---

## 🔌 Conexiones en DBeaver Community

### Oracle — orclpdb (puerto 1523)
| Parámetro | Valor |
|-----------|-------|
| Tipo | Oracle |
| Host | 192.168.152.191 |
| Port | 1523 |
| Database | orclpdb.lab.local |
| Type | Service Name (NO SID) |
| Username | logistica |
| Password | Logist1ca#2026 |
| Role | Normal (NO SYSDBA) |

### MariaDB — inventarios (puerto 3307)
| Parámetro | Valor |
|-----------|-------|
| Tipo | MySQL |
| Server Host | 192.168.152.191 |
| Port | 3307 |
| Database | inventarios |
| Username | dba_mariadb |
| Password | MariaDB_Proj#2026 |

### SQL Server — reportes (puerto 1434)
| Parámetro | Valor |
|-----------|-------|
| Tipo | MS SQL Server |
| Host | 192.168.152.191 |
| Port | 1434 |
| Database | reportes |
| Username | dba_sqlserver |
| Password | SqlSrvDBA#2026 |
| **✓ Trust Server Certificate** | **OBLIGATORIO** |

---

## 📈 Resultados Esperados

### Volúmenes de Datos
- **MariaDB**: 10 + 1.000 + 8.000 + 50 + 13.910 = **23.970 registros**
- **Oracle**: 200.000 movimientos + 500.000+ detalles = **700.000+ registros**
- **SQL Server**: Se poblará dinámicamente via Python ETL

### Tiempos de Ejecución
| Operación | Tiempo Esperado |
|-----------|-----------------|
| Carga inicial MariaDB (generar_mariadb.py) | 60-90 seg |
| Carga inicial Oracle (generar_oracle.py) | 3-5 min |
| sync_stock.py (13.910 registros) | 10-15 seg |
| sync_rotacion.py (agregación Oracle+MariaDB) | 5-8 seg |
| Prueba carga 5000 (prueba_carga_5000.py) | < 1 seg |

### Validaciones
✓ Todos los 3 SGBD funcionando simultáneamente  
✓ Puertos no-default: 1523 (Oracle), 3307 (MariaDB), 1434 (SQL Server)  
✓ Interconexión Python ETL activa y sincronizando (via cron)  
✓ Integridad referencial (FK en MariaDB, referencias lógicas en Oracle)  
✓ DBeaver conectando sin error los 3 motores  

---

## 📄 Distribución de Responsabilidades por Integrante

### Guillermo Ruales (GR) — Líder Oracle + Interconexión
**Commits**:
- `feat: DDL tablas Oracle movimientos y detalles`
- `data: script Faker Oracle 200.000 movimientos logísticos`
- `sync: script sincronización rotación Oracle+MariaDB a SQL Server (diaria)`
- `config: configuración jobs cron para sincronización automática`
- `config: limpieza y reconfiguración Oracle puerto 1523`

**Archivos**:
- `oracle/00_limpieza.sql`, `01_setup_oracle.sql`, `02_ddl_tablas.sql`
- `oracle/listener.ora`, `tnsnames.ora`
- `python/generar_oracle.py`, `sync_rotacion.py`
- `scripts/crontab.txt`

### Israel Tabango (IT) — MariaDB + Faker
**Commits**:
- `feat: DDL tablas MariaDB categorias, productos, bodegas, inventario`
- `data: script Faker MariaDB 8000 productos + inventarios`
- `feat: despliegue MariaDB 11 en Docker puerto 3307`

**Archivos**:
- `mariadb/00_setup.sql`, `01_ddl_tablas.sql`
- `python/generar_mariadb.py`
- `docker/deploy_mariadb.sh`

### Anthony Montalvo (AM) — SQL Server + Sync Stock
**Commits**:
- `feat: DDL tablas SQL Server consolidado_stock, reportes`
- `sync: script sincronización stock MariaDB a SQL Server (horaria)`
- `test: script prueba de carga 5000 registros inventario_ubicacion`
- `feat: despliegue SQL Server 2022 en Docker puerto 1434`

**Archivos**:
- `sqlserver/00_setup.sql`, `01_ddl_tablas.sql`, `02_permisos_sync.sql`
- `python/sync_stock.py`, `prueba_carga_5000.py`
- `docker/deploy_sqlserver.sh`

### Luis Cando (LC) — Docker + Documentación
**Commits**:
- `config: script instalación Docker Engine en Red Hat 8.10`
- `docs: crear README.md completo del proyecto`
- `config: configuración docker-compose para orquestación`

**Archivos**:
- `scripts/01_install_docker.sh`
- `docker/docker-compose.yml`
- `python/requirements.txt`
- `README.md`
- `docs/*`

---

## 🐛 Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| Listener no inicia Oracle | Permisos en $ORACLE_HOME | `chown -R oracle:oinstall $ORACLE_HOME` |
| Puerto 1523 ya en uso | Otro proceso | `lsof -i :1523` y matar el PID |
| MariaDB container no arranca | Permisos directorio | `chown -R oracle:oinstall /u02/docker/mariadb` |
| SQL Server "Access Denied" | UID incorrecto | `chown -R 10001:0 /u02/docker/sqlserver/data` |
| DBeaver conexión SQL Server falla | SSL no confiable | Marcar **"Trust Server Certificate"** |
| cx_Oracle no funciona en cron | Falta ORACLE_HOME | Agregar variables de entorno en crontab |
| pyodbc "ODBC Driver not found" | Driver no instalado | `dnf install -y msodbcsql18` |
| Cron no ejecuta sync_stock.py | Ruta incorrecta | Verificar `which python3`, usar ruta completa |

---

## ✅ Checklist de Validación

- [ ] Oracle 19c limpio y reconfigurado puerto 1523
- [ ] MariaDB 11 corriendo en Docker puerto 3307
- [ ] SQL Server 2022 corriendo en Docker puerto 1434
- [ ] DDL ejecutado correctamente en los 3 motores
- [ ] Datos iniciales cargados (Faker)
  - [ ] MariaDB: 8000 productos + 50 bodegas
  - [ ] Oracle: 200.000 movimientos
- [ ] Python ETL sincronizando (cron activo)
- [ ] DBeaver conectando los 3 motores sin error
- [ ] Prueba de carga 5000 registros exitosa (< 1 segundo)
- [ ] Validación integridad datos (sin duplicados)
- [ ] Al menos 3-5 commits propios por integrante
- [ ] README.md actualizado con estructura final
- [ ] Todos los archivos DDL, scripts y configuraciones en GitHub

---

## 📚 Referencias Técnicas

- [Oracle 19c Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/)
- [MariaDB 11 Documentation](https://mariadb.com/docs/)
- [SQL Server 2022 Documentation](https://learn.microsoft.com/en-us/sql/)
- [Docker Official Images](https://hub.docker.com/)
- [Python Faker Library](https://faker.readthedocs.io/)
- [Red Hat Enterprise Linux 8](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/)
- [cx_Oracle Documentation](https://cx-oracle.readthedocs.io/)
- [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc)

---

## 🎯 Conclusión

Este proyecto integra **3 SGBD heterogéneos** en una arquitectura empresarial real donde:

- **Oracle** maneja transacciones críticas con máxima consistencia ACID
- **MariaDB** proporciona datos maestros rápidos y accesibles
- **SQL Server** consolida análisis y reportería en tiempo semi-real
- **Python** sincroniza datos entre los 3 motores **automáticamente** via cron

La plataforma es **reproducible desde cero**, **escalable** para agregar más SGBD, y demuestra competencia en:

✓ Administración heterogénea de múltiples SGBD  
✓ Arquitectura distribuida e interconectada  
✓ Automatización con scripts Python y cron  
✓ Gestión de proyectos colaborativos con Git/GitHub  
✓ Control de versiones y mejores prácticas  

---

**Última actualización**: Junio 2026  
**Versión**: RC5 Final  
**Estado**: ✓ Producción  
**Equipo**: GR | IT | AM | LC
