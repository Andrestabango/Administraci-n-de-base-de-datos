# Informe de Cumplimiento — Proyecto Integrador ITIZ3201 (RC5)

**Caso:** FarmaDistrib S.A. — plataforma de base de datos heterogénea interconectada
**Equipo:** Guillermo Ruales (líder), Israel Tabango, Anthony Montalvo, Luis Cando

---

## 1. Checklist de requisitos de la consigna

| # | Requisito | Estado | Evidencia |
|---|-----------|:------:|-----------|
| 1 | Plataforma heterogénea con 3 SGBD | ✅ | Oracle 19c, MariaDB 11, SQL Server 2022 |
| 2 | VM con Linux | ✅ | Red Hat 8.10 (12 GB RAM / 4 vCPU / 100 GB) |
| 3 | Últimas versiones de los motores | ✅ | `mariadb:11`, `mssql/server:2022-latest`, Oracle 19c |
| 4 | Instalación según el proveedor | ✅ | Oracle nativo; imágenes oficiales en Docker |
| 5 | Buenas prácticas de ubicación de binarios/archivos | ✅ | `tbs_logistica` en `/u02/oradata`; volúmenes en `/u02/docker` |
| 6 | Puertos NO-default | ✅ | Oracle 1523, MariaDB 3307, SQL Server 1434 |
| 7 | Gestión segura de credenciales | ✅ | `.env` no versionado, `.env.example` plantilla |
| 8 | Restricción de accesos a nivel de red | ✅ | Red Docker dedicada; usuarios `sync_*` de mínimo privilegio |
| 9 | Cifrado de conexiones | ✅ | `REQUIRE SSL` (MariaDB), `Encrypt=yes` (SQL Server) |
| 10 | Un DBA por SGBD | ✅ | `dba_oracle`, `dba_mariadb`, `dba_sqlserver` |
| 11 | Cliente gráfico SQL | ✅ | DBeaver en el host (defensa) |
| 12 | Cada BD en usuario/esquema propio | ✅ | `logistica`, `inventarios`, `reportes` |
| 13 | Datos generados con Python + Faker | ✅ | `generar_mariadb.py`, `generar_oracle.py` |
| 14 | Capa de interconexión justificada | ✅ | ETL en Python (ver sección 3) |
| 15 | Jobs / tareas programadas | ✅ | cron horario y diario (`scripts/crontab.txt`) |
| 16 | Evidencias de funcionamiento | ✅ | Logs de `sync_stock` / `sync_rotacion` |
| 17 | Prueba de carga de 5.000 registros | ✅ | `prueba_carga_5000.py` |
| 18 | Validación de integridad | ✅ | Comparación origen/destino en la prueba |
| 19 | Tiempos de respuesta de interconexión | ✅ | Medición en la prueba de carga |
| 20 | Repositorio GitHub con commits por integrante | ✅ | Historial de commits del repositorio |

---

## 2. Criterios de desempeño del trabajo en equipo (RC5)

| Criterio | % Cumplimiento | Evidencia |
|----------|:--------------:|-----------|
| Definición de objetivos de trabajo | 100% | Sección de objetivos del README |
| Definición de cronograma | 100% | Tablero/Issues del repositorio |
| Definición de roles | 100% | Sección de roles del README |
| Asignación de roles | 100% | Tabla de roles por integrante |
| Asignación de responsabilidades | 100% | Commits por módulo y responsable |
| Cronograma de reuniones de trabajo | 100% | Actas / minutas en `docs/` |
| Cumplimiento de objetivos de trabajo | 100% | Plataforma operativa en la defensa |
| Registro de actividades realizadas | 100% | Historial de commits con autoría |

---

## 3. Justificación técnica de la capa de interconexión (ETL en Python)

Se eligió un **ETL programado en Python** frente a colas, herramientas de
integración a nivel de capa de datos o suites ETL comerciales, por:

- **Escalabilidad:** los scripts procesan por lotes (`executemany`, `fast_executemany`)
  y separan la carga horaria (ligera) de la diaria (pesada), permitiendo crecer
  en volumen sin rediseñar la arquitectura.
- **Rendimiento:** la agregación se delega a cada motor en su propio SQL (lo que
  mejor sabe hacer), y solo viajan los resultados consolidados por la red.
- **Seguridad:** usuarios dedicados de mínimo privilegio (`sync_reader`,
  `sync_reader_ora`, `sync_writer`), credenciales fuera del código y conexiones
  cifradas.
- **Facilidad de mantenimiento:** un único lenguaje, dependencias declaradas en
  `requirements.txt`, configuración centralizada en `db_config.py` y lógica
  idempotente (DELETE+INSERT) fácil de re-ejecutar.

**Frecuencias:** `consolidado_stock` se sincroniza **cada hora** porque el stock
físico cambia de forma continua y la gerencia requiere una foto reciente; los
reportes de `rotacion` y `abastecimiento` se recalculan **cada noche** porque
agregan grandes volúmenes históricos y conviene hacerlo fuera del horario operativo.
