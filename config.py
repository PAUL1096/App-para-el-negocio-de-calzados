"""
Configuracion para diferentes entornos
"""
import os

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Configuracion base"""
    # IMPORTANTE: Cambia esta clave en produccion
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cambia-esta-clave-secreta-en-produccion-2024'

    # Ruta absoluta a la base de datos
    DATABASE = os.path.join(BASE_DIR, 'calzado.db')

    # SQLite settings
    SQLITE_TIMEOUT = 30.0


class DevelopmentConfig(Config):
    """Configuracion para desarrollo local"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuracion para produccion (PythonAnywhere)"""
    DEBUG = False

    # En PythonAnywhere, la BD estara en el directorio del proyecto
    # Puedes cambiar esto si quieres guardarla en otro lugar
    # DATABASE = '/home/TU_USUARIO/data/calzado.db'


# Selector de configuracion
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuracion segun el entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
