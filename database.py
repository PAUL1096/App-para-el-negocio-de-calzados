"""
Modulo de base de datos con soporte dual: SQLite (desarrollo) y PostgreSQL (produccion)
Incluye wrapper para compatibilidad de consultas SQL
"""
import os
import sqlite3
import re

# Intentar importar psycopg2 para PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from config import get_config

# Obtener configuracion
config = get_config()


class PostgresWrapper:
    """
    Wrapper para hacer que psycopg2 se comporte similar a sqlite3
    Convierte placeholders ? a %s y funciones de fecha SQLite a PostgreSQL
    """

    def __init__(self, conn):
        self.conn = conn
        self._cursor = None

    def cursor(self):
        self._cursor = PostgresCursorWrapper(self.conn.cursor())
        return self._cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def execute(self, sql, params=None):
        cursor = self.cursor()
        cursor.execute(sql, params)
        return cursor


class PostgresCursorWrapper:
    """
    Wrapper para cursor de PostgreSQL que convierte sintaxis SQLite a PostgreSQL
    """

    def __init__(self, cursor):
        self.cursor = cursor
        self.description = cursor.description

    def execute(self, sql, params=None):
        # Convertir sintaxis SQLite a PostgreSQL
        sql = self._convert_sql(sql)
        # Convertir placeholders ? a %s
        sql = self._convert_placeholders(sql)

        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)

        self.description = self.cursor.description
        return self

    def executemany(self, sql, params_list):
        sql = self._convert_sql(sql)
        sql = self._convert_placeholders(sql)
        self.cursor.executemany(sql, params_list)
        return self

    def executescript(self, sql):
        """PostgreSQL no tiene executescript, ejecutamos cada statement"""
        statements = sql.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                self.execute(stmt)
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        # Convertir RealDictRow a algo indexable como sqlite3.Row
        return DictRow(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [DictRow(row) for row in rows]

    def fetchmany(self, size=None):
        rows = self.cursor.fetchmany(size) if size else self.cursor.fetchmany()
        return [DictRow(row) for row in rows]

    @property
    def lastrowid(self):
        """PostgreSQL no tiene lastrowid directamente, usamos RETURNING"""
        return getattr(self.cursor, 'lastrowid', None)

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def _convert_placeholders(self, sql):
        """Convierte ? a %s para PostgreSQL"""
        # Evitar convertir ?? (escape) y ? dentro de strings
        result = []
        in_string = False
        string_char = None
        i = 0
        while i < len(sql):
            char = sql[i]

            # Detectar inicio/fin de string
            if char in ("'", '"') and (i == 0 or sql[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None

            # Convertir ? a %s solo fuera de strings
            if char == '?' and not in_string:
                result.append('%s')
            else:
                result.append(char)
            i += 1

        return ''.join(result)

    def _convert_sql(self, sql):
        """Convierte funciones SQLite a PostgreSQL"""

        # BEGIN IMMEDIATE -> BEGIN (PostgreSQL no soporta IMMEDIATE)
        sql = re.sub(r'\bBEGIN\s+IMMEDIATE\b', 'BEGIN', sql, flags=re.IGNORECASE)

        # DATE("now") -> CURRENT_DATE
        sql = re.sub(r'DATE\s*\(\s*["\']now["\']\s*\)', 'CURRENT_DATE', sql, flags=re.IGNORECASE)

        # DATE('now') -> CURRENT_DATE
        sql = re.sub(r"DATE\s*\(\s*'now'\s*\)", 'CURRENT_DATE', sql, flags=re.IGNORECASE)

        # datetime('now') -> CURRENT_TIMESTAMP
        sql = re.sub(r"datetime\s*\(\s*['\"]now['\"]\s*\)", 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)

        # strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
        # -> TO_CHAR(fecha, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
        sql = re.sub(
            r"strftime\s*\(\s*'%Y-%m'\s*,\s*(\w+)\s*\)\s*=\s*strftime\s*\(\s*'%Y-%m'\s*,\s*'now'\s*\)",
            r"TO_CHAR(\1, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')",
            sql,
            flags=re.IGNORECASE
        )

        # strftime('%Y-%m', campo) -> TO_CHAR(campo, 'YYYY-MM')
        sql = re.sub(
            r"strftime\s*\(\s*'%Y-%m'\s*,\s*(\w+)\s*\)",
            r"TO_CHAR(\1, 'YYYY-MM')",
            sql,
            flags=re.IGNORECASE
        )

        # strftime('%Y-%m', 'now') -> TO_CHAR(CURRENT_DATE, 'YYYY-MM')
        sql = re.sub(
            r"strftime\s*\(\s*'%Y-%m'\s*,\s*'now'\s*\)",
            "TO_CHAR(CURRENT_DATE, 'YYYY-MM')",
            sql,
            flags=re.IGNORECASE
        )

        # strftime('%Y-%m-%d', campo) -> TO_CHAR(campo, 'YYYY-MM-DD')
        sql = re.sub(
            r"strftime\s*\(\s*'%Y-%m-%d'\s*,\s*(\w+)\s*\)",
            r"TO_CHAR(\1, 'YYYY-MM-DD')",
            sql,
            flags=re.IGNORECASE
        )

        # AUTOINCREMENT no existe en PostgreSQL (usa SERIAL)
        sql = re.sub(r'\bAUTOINCREMENT\b', '', sql, flags=re.IGNORECASE)

        # GROUP_CONCAT(campo, separador) -> STRING_AGG(campo::text, separador)
        # Ejemplo: GROUP_CONCAT(codigo, ', ') -> STRING_AGG(codigo::text, ', ')
        sql = re.sub(
            r"GROUP_CONCAT\s*\(\s*([^,]+)\s*,\s*(['\"][^'\"]+['\"])\s*\)",
            r"STRING_AGG(\1::text, \2)",
            sql,
            flags=re.IGNORECASE
        )

        # GROUP_CONCAT(campo) -> STRING_AGG(campo::text, ',')
        sql = re.sub(
            r"GROUP_CONCAT\s*\(\s*([^)]+)\s*\)",
            r"STRING_AGG(\1::text, ',')",
            sql,
            flags=re.IGNORECASE
        )

        # IFNULL -> COALESCE (PostgreSQL usa COALESCE)
        sql = re.sub(r'\bIFNULL\b', 'COALESCE', sql, flags=re.IGNORECASE)

        # JULIANDAY('now') -> EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)/86400
        # Para calcular diferencia de dias: JULIANDAY(a) - JULIANDAY(b) -> (a::date - b::date)
        sql = re.sub(
            r"JULIANDAY\s*\(\s*'now'\s*\)\s*-\s*JULIANDAY\s*\(\s*(\w+(?:\.\w+)?)\s*\)",
            r"(CURRENT_DATE - \1::date)",
            sql,
            flags=re.IGNORECASE
        )
        sql = re.sub(
            r"JULIANDAY\s*\(\s*(\w+(?:\.\w+)?)\s*\)\s*-\s*JULIANDAY\s*\(\s*'now'\s*\)",
            r"(\1::date - CURRENT_DATE)",
            sql,
            flags=re.IGNORECASE
        )
        # CAST(JULIANDAY(a) - JULIANDAY(b) AS INTEGER) -> (a::date - b::date)
        sql = re.sub(
            r"CAST\s*\(\s*JULIANDAY\s*\(\s*(\w+(?:\.\w+)?)\s*\)\s*-\s*JULIANDAY\s*\(\s*'now'\s*\)\s*AS\s+INTEGER\s*\)",
            r"(\1::date - CURRENT_DATE)",
            sql,
            flags=re.IGNORECASE
        )
        # JULIANDAY('now') solo -> EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)/86400
        sql = re.sub(
            r"JULIANDAY\s*\(\s*'now'\s*\)",
            "EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)/86400",
            sql,
            flags=re.IGNORECASE
        )
        # JULIANDAY(campo) -> EXTRACT(EPOCH FROM campo::timestamp)/86400
        sql = re.sub(
            r"JULIANDAY\s*\(\s*(\w+(?:\.\w+)?)\s*\)",
            r"EXTRACT(EPOCH FROM \1::timestamp)/86400",
            sql,
            flags=re.IGNORECASE
        )

        # INTEGER PRIMARY KEY en PostgreSQL necesita ser SERIAL
        # (esto es para CREATE TABLE, manejado en init_postgres)

        return sql


class DictRow:
    """
    Clase que simula sqlite3.Row para PostgreSQL
    Permite acceso por indice y por nombre de columna
    """

    def __init__(self, data):
        if isinstance(data, dict):
            self._data = data
            self._keys = list(data.keys())
        else:
            # Si ya es un objeto similar a Row
            self._data = dict(data) if hasattr(data, 'keys') else {}
            self._keys = list(self._data.keys())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._data[self._keys[key]]
        return self._data[key]

    def __contains__(self, key):
        return key in self._data

    def keys(self):
        return self._keys

    def values(self):
        return [self._data[k] for k in self._keys]

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        return self._data.get(key, default)


def get_db():
    """
    Obtiene conexion a la base de datos.
    Usa PostgreSQL si DATABASE_URL esta configurada, sino usa SQLite.
    """
    if config.USE_POSTGRES and POSTGRES_AVAILABLE:
        return get_postgres_connection()
    else:
        return get_sqlite_connection()


def get_sqlite_connection():
    """Conexion a SQLite para desarrollo local"""
    conn = sqlite3.connect(config.SQLITE_PATH, timeout=config.SQLITE_TIMEOUT)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


def get_postgres_connection():
    """Conexion a PostgreSQL para produccion (con wrapper de compatibilidad)"""
    database_url = config.DATABASE_URL

    # Render usa 'postgres://' pero psycopg2 necesita 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return PostgresWrapper(conn)


def init_database():
    """
    Inicializa la base de datos creando todas las tablas necesarias.
    Detecta automaticamente si usar SQLite o PostgreSQL.
    """
    if config.USE_POSTGRES and POSTGRES_AVAILABLE:
        init_postgres()
    else:
        init_sqlite()


def init_sqlite():
    """Crea las tablas en SQLite"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS variantes_base (
            id_variante_base INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_interno TEXT UNIQUE NOT NULL,
            tipo_calzado TEXT NOT NULL,
            tipo_horma TEXT,
            segmento TEXT,
            descripcion TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS productos_producidos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_variante_base INTEGER NOT NULL,
            cuero TEXT,
            color_cuero TEXT,
            suela TEXT,
            forro TEXT,
            material_plantilla TEXT,
            serie_tallas TEXT,
            pares_por_docena INTEGER DEFAULT 12,
            costo_unitario REAL DEFAULT 0,
            precio_sugerido REAL DEFAULT 0,
            cantidad_total_pares INTEGER DEFAULT 0,
            cantidad_ingresada INTEGER DEFAULT 0,
            fecha_produccion DATE,
            observaciones TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_variante_base) REFERENCES variantes_base(id_variante_base)
        );

        CREATE TABLE IF NOT EXISTS ubicaciones (
            id_ubicacion INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT DEFAULT 'almacen',
            direccion TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS inventario (
            id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL,
            id_ubicacion INTEGER NOT NULL,
            cantidad_pares INTEGER DEFAULT 0,
            tipo_stock TEXT DEFAULT 'general',
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto),
            FOREIGN KEY (id_ubicacion) REFERENCES ubicaciones(id_ubicacion)
        );

        CREATE TABLE IF NOT EXISTS preparaciones (
            id_preparacion INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_preparacion TEXT,
            id_ubicacion_origen INTEGER,
            id_ubicacion_destino INTEGER,
            dia_venta TEXT,
            fecha_preparacion DATE,
            estado TEXT DEFAULT 'pendiente',
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_ubicacion_origen) REFERENCES ubicaciones(id_ubicacion),
            FOREIGN KEY (id_ubicacion_destino) REFERENCES ubicaciones(id_ubicacion)
        );

        CREATE TABLE IF NOT EXISTS preparaciones_detalle (
            id_detalle_prep INTEGER PRIMARY KEY AUTOINCREMENT,
            id_preparacion INTEGER NOT NULL,
            id_producto INTEGER,
            id_inventario INTEGER,
            tipo_stock TEXT DEFAULT 'general',
            cantidad_pares INTEGER NOT NULL,
            FOREIGN KEY (id_preparacion) REFERENCES preparaciones(id_preparacion),
            FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto),
            FOREIGN KEY (id_inventario) REFERENCES inventario(id_inventario)
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_cliente TEXT UNIQUE,
            nombre TEXT NOT NULL,
            apellido TEXT,
            nombre_comercial TEXT,
            tipo_documento TEXT,
            numero_documento TEXT UNIQUE,
            email TEXT UNIQUE,
            telefono TEXT,
            direccion TEXT,
            limite_credito REAL DEFAULT 0,
            dias_credito INTEGER DEFAULT 30,
            activo INTEGER DEFAULT 1,
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ventas_v2 (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_venta TEXT UNIQUE,
            id_cliente INTEGER,
            id_preparacion INTEGER,
            id_ubicacion INTEGER,
            fecha_venta DATE,
            estado_pago TEXT DEFAULT 'pendiente',
            total_final REAL DEFAULT 0,
            descuento_total REAL DEFAULT 0,
            modalidad_pago TEXT DEFAULT 'contado',
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_preparacion) REFERENCES preparaciones(id_preparacion),
            FOREIGN KEY (id_ubicacion) REFERENCES ubicaciones(id_ubicacion)
        );

        CREATE TABLE IF NOT EXISTS ventas_detalle (
            id_detalle_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad_pares INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            descuento REAL DEFAULT 0,
            FOREIGN KEY (id_venta) REFERENCES ventas_v2(id_venta),
            FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto)
        );

        CREATE TABLE IF NOT EXISTS cuentas_por_cobrar (
            id_cuenta INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_cuenta TEXT UNIQUE,
            id_cliente INTEGER,
            id_venta INTEGER,
            concepto TEXT,
            monto_total REAL NOT NULL,
            saldo_pendiente REAL NOT NULL,
            monto_pagado REAL DEFAULT 0,
            fecha_emision DATE,
            fecha_vencimiento DATE,
            estado TEXT DEFAULT 'pendiente',
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_venta) REFERENCES ventas_v2(id_venta)
        );

        CREATE TABLE IF NOT EXISTS pagos (
            id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_pago TEXT UNIQUE,
            id_cuenta INTEGER NOT NULL,
            monto_pago REAL NOT NULL,
            metodo_pago TEXT DEFAULT 'efectivo',
            fecha_pago DATE,
            numero_comprobante TEXT,
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_cuenta) REFERENCES cuentas_por_cobrar(id_cuenta)
        );
    ''')

    conn.commit()
    conn.close()
    print("Base de datos SQLite inicializada correctamente")


def init_postgres():
    """Crea las tablas en PostgreSQL"""
    database_url = config.DATABASE_URL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variantes_base (
            id_variante_base SERIAL PRIMARY KEY,
            codigo_interno VARCHAR(100) UNIQUE NOT NULL,
            tipo_calzado VARCHAR(100) NOT NULL,
            tipo_horma VARCHAR(100),
            segmento VARCHAR(100),
            descripcion TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos_producidos (
            id_producto SERIAL PRIMARY KEY,
            id_variante_base INTEGER NOT NULL REFERENCES variantes_base(id_variante_base),
            cuero VARCHAR(100),
            color_cuero VARCHAR(100),
            suela VARCHAR(100),
            forro VARCHAR(100),
            material_plantilla VARCHAR(100),
            serie_tallas VARCHAR(100),
            pares_por_docena INTEGER DEFAULT 12,
            costo_unitario DECIMAL(10,2) DEFAULT 0,
            precio_sugerido DECIMAL(10,2) DEFAULT 0,
            cantidad_total_pares INTEGER DEFAULT 0,
            cantidad_ingresada INTEGER DEFAULT 0,
            fecha_produccion DATE,
            observaciones TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ubicaciones (
            id_ubicacion SERIAL PRIMARY KEY,
            nombre VARCHAR(200) NOT NULL,
            tipo VARCHAR(50) DEFAULT 'almacen',
            direccion TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id_inventario SERIAL PRIMARY KEY,
            id_producto INTEGER NOT NULL REFERENCES productos_producidos(id_producto),
            id_ubicacion INTEGER NOT NULL REFERENCES ubicaciones(id_ubicacion),
            cantidad_pares INTEGER DEFAULT 0,
            tipo_stock VARCHAR(50) DEFAULT 'general',
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preparaciones (
            id_preparacion SERIAL PRIMARY KEY,
            codigo_preparacion VARCHAR(50),
            id_ubicacion_origen INTEGER REFERENCES ubicaciones(id_ubicacion),
            id_ubicacion_destino INTEGER REFERENCES ubicaciones(id_ubicacion),
            dia_venta VARCHAR(50),
            fecha_preparacion DATE,
            estado VARCHAR(50) DEFAULT 'pendiente',
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preparaciones_detalle (
            id_detalle_prep SERIAL PRIMARY KEY,
            id_preparacion INTEGER NOT NULL REFERENCES preparaciones(id_preparacion),
            id_producto INTEGER REFERENCES productos_producidos(id_producto),
            id_inventario INTEGER REFERENCES inventario(id_inventario),
            tipo_stock VARCHAR(50) DEFAULT 'general',
            cantidad_pares INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente SERIAL PRIMARY KEY,
            codigo_cliente VARCHAR(50) UNIQUE,
            nombre VARCHAR(200) NOT NULL,
            apellido VARCHAR(200),
            nombre_comercial VARCHAR(200),
            tipo_documento VARCHAR(50),
            numero_documento VARCHAR(50) UNIQUE,
            email VARCHAR(200) UNIQUE,
            telefono VARCHAR(50),
            direccion TEXT,
            limite_credito DECIMAL(10,2) DEFAULT 0,
            dias_credito INTEGER DEFAULT 30,
            activo INTEGER DEFAULT 1,
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas_v2 (
            id_venta SERIAL PRIMARY KEY,
            codigo_venta VARCHAR(50) UNIQUE,
            id_cliente INTEGER REFERENCES clientes(id_cliente),
            id_preparacion INTEGER REFERENCES preparaciones(id_preparacion),
            id_ubicacion INTEGER REFERENCES ubicaciones(id_ubicacion),
            fecha_venta DATE,
            estado_pago VARCHAR(50) DEFAULT 'pendiente',
            total_final DECIMAL(10,2) DEFAULT 0,
            descuento_total DECIMAL(10,2) DEFAULT 0,
            modalidad_pago VARCHAR(50) DEFAULT 'contado',
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas_detalle (
            id_detalle_venta SERIAL PRIMARY KEY,
            id_venta INTEGER NOT NULL REFERENCES ventas_v2(id_venta),
            id_producto INTEGER NOT NULL REFERENCES productos_producidos(id_producto),
            cantidad_pares INTEGER NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            descuento DECIMAL(10,2) DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cuentas_por_cobrar (
            id_cuenta SERIAL PRIMARY KEY,
            codigo_cuenta VARCHAR(50) UNIQUE,
            id_cliente INTEGER REFERENCES clientes(id_cliente),
            id_venta INTEGER REFERENCES ventas_v2(id_venta),
            concepto TEXT,
            monto_total DECIMAL(10,2) NOT NULL,
            saldo_pendiente DECIMAL(10,2) NOT NULL,
            monto_pagado DECIMAL(10,2) DEFAULT 0,
            fecha_emision DATE,
            fecha_vencimiento DATE,
            estado VARCHAR(50) DEFAULT 'pendiente',
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id_pago SERIAL PRIMARY KEY,
            codigo_pago VARCHAR(50) UNIQUE,
            id_cuenta INTEGER NOT NULL REFERENCES cuentas_por_cobrar(id_cuenta),
            monto_pago DECIMAL(10,2) NOT NULL,
            metodo_pago VARCHAR(50) DEFAULT 'efectivo',
            fecha_pago DATE,
            numero_comprobante VARCHAR(100),
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Base de datos PostgreSQL inicializada correctamente")


def insert_initial_data():
    """Inserta datos iniciales si no existen"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM ubicaciones')
    result = cursor.fetchone()
    total = result['total']

    if total == 0:
        cursor.execute('''
            INSERT INTO ubicaciones (nombre, tipo, direccion, activo)
            VALUES (?, ?, ?, ?)
        ''', ('Almacen Central', 'almacen', 'Direccion del almacen principal', 1))

        conn.commit()
        print("Datos iniciales insertados: Almacen Central creado")
    else:
        print(f"Ya existen {total} ubicacion(es), no se insertan datos iniciales")

    conn.close()


def is_postgres():
    """Indica si estamos usando PostgreSQL"""
    return config.USE_POSTGRES and POSTGRES_AVAILABLE
