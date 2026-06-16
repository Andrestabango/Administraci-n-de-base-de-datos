"""
db_config.py  ·  Configuracion y conexiones a los 3 SGBD heterogeneos.

Centraliza la lectura de credenciales desde .env y expone funciones
de conexion para Oracle, MariaDB y SQL Server. Todos los scripts del
proyecto (generadores, ETL y pruebas) importan desde aqui para evitar
duplicar cadenas de conexion y credenciales.

Requiere un archivo .env junto a este modulo (ver .env.example).
"""

import os
from dotenv import load_dotenv

import cx_Oracle
import mysql.connector
import pyodbc

# Carga las variables del .env ubicado en la misma carpeta
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


# ─────────────────────────────────────────────────────────────
#  Oracle 19c  (nativo, puerto 1523)
# ─────────────────────────────────────────────────────────────
def conectar_oracle(usar_sync=False):
    """Devuelve una conexion a Oracle (schema logistica o sync_reader_ora)."""
    user = os.getenv("ORA_SYNC_USER") if usar_sync else os.getenv("ORA_APP_USER")
    pwd = os.getenv("ORA_SYNC_PWD") if usar_sync else os.getenv("ORA_APP_PWD")
    dsn = cx_Oracle.makedsn(
        os.getenv("ORA_HOST"),
        int(os.getenv("ORA_PORT")),
        service_name=os.getenv("ORA_SERVICE"),
    )
    return cx_Oracle.connect(user=user, password=pwd, dsn=dsn)


# ─────────────────────────────────────────────────────────────
#  MariaDB 11  (Docker, puerto 3307)
# ─────────────────────────────────────────────────────────────
def conectar_mariadb(usar_sync=False):
    """Devuelve una conexion a MariaDB (dba_mariadb o sync_reader)."""
    user = os.getenv("MARIA_SYNC_USER") if usar_sync else os.getenv("MARIA_DBA_USER")
    pwd = os.getenv("MARIA_SYNC_PWD") if usar_sync else os.getenv("MARIA_DBA_PWD")
    return mysql.connector.connect(
        host=os.getenv("MARIA_HOST"),
        port=int(os.getenv("MARIA_PORT")),
        database=os.getenv("MARIA_DB"),
        user=user,
        password=pwd,
        autocommit=False,
    )


# ─────────────────────────────────────────────────────────────
#  SQL Server 2022  (Docker, puerto 1434)
# ─────────────────────────────────────────────────────────────
def conectar_sqlserver():
    """Devuelve una conexion a SQL Server con el usuario de escritura."""
    driver = os.getenv("MSSQL_ODBC_DRIVER")
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={os.getenv('MSSQL_HOST')},{os.getenv('MSSQL_PORT')};"
        f"DATABASE={os.getenv('MSSQL_DB')};"
        f"UID={os.getenv('MSSQL_SYNC_USER')};"
        f"PWD={os.getenv('MSSQL_SYNC_PWD')};"
        # Cifrado de la conexion; TrustServerCertificate por ser cert. autofirmado
        "Encrypt=yes;TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


def log(msg):
    """Log simple con marca de tiempo para los jobs."""
    from datetime import datetime
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)
