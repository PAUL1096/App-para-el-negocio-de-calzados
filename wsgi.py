"""
WSGI entry point for PythonAnywhere
Este archivo es el punto de entrada para PythonAnywhere
"""
import sys
import os

# Agregar el directorio del proyecto al path
project_home = '/home/TU_USUARIO/App-para-el-negocio-de-calzados'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configurar variable de entorno para produccion
os.environ['FLASK_ENV'] = 'production'

# Importar la aplicacion Flask
from app_v2 import app as application
