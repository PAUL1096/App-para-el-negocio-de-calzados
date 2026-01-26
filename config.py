"""
Configuracion para diferentes entornos
Soporta SQLite (desarrollo) y PostgreSQL (produccion/Render)
"""
import os

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Configuracion base"""
    # IMPORTANTE: Cambia esta clave en produccion
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cambia-esta-clave-secreta-en-produccion-2024'

    # DATABASE_URL es proporcionada por Render automaticamente
    # Si existe, usamos PostgreSQL; si no, usamos SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Ruta a SQLite (solo para desarrollo local)
    SQLITE_PATH = os.path.join(BASE_DIR, 'calzado.db')
    SQLITE_TIMEOUT = 30.0

    @property
    def USE_POSTGRES(self):
        """Determina si usar PostgreSQL o SQLite"""
        return self.DATABASE_URL is not None

    @property
    def DATABASE(self):
        """Retorna la configuracion de base de datos apropiada"""
        if self.USE_POSTGRES:
            return self.DATABASE_URL
        return self.SQLITE_PATH


class DevelopmentConfig(Config):
    """Configuracion para desarrollo local (SQLite)"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuracion para produccion (PostgreSQL en Render)"""
    DEBUG = False


# Selector de configuracion
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuracion segun el entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])()
