# Guia de Despliegue en PythonAnywhere

Esta guia te ayudara a desplegar el Sistema de Gestion de Calzado en PythonAnywhere.

## Requisitos Previos

- Cuenta en PythonAnywhere (gratuita o de pago)
- El repositorio clonado en tu PC o acceso al codigo

---

## Paso 1: Crear cuenta en PythonAnywhere

1. Ve a [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Crea una cuenta gratuita (Beginner) o de pago
3. Inicia sesion en tu dashboard

---

## Paso 2: Subir el codigo

### Opcion A: Clonar desde GitHub (Recomendado)

1. En PythonAnywhere, ve a **Consoles** > **Bash**
2. Ejecuta:
```bash
cd ~
git clone https://github.com/PAUL1096/App-para-el-negocio-de-calzados.git
cd App-para-el-negocio-de-calzados
```

### Opcion B: Subir archivo ZIP

1. Descarga el repositorio como ZIP
2. En PythonAnywhere, ve a **Files**
3. Sube el ZIP a tu directorio home
4. En una consola Bash:
```bash
cd ~
unzip App-para-el-negocio-de-calzados.zip
```

---

## Paso 3: Instalar dependencias

En la consola Bash de PythonAnywhere:

```bash
cd ~/App-para-el-negocio-de-calzados
pip3 install --user -r requirements.txt
```

---

## Paso 4: Configurar el archivo WSGI

1. Ve a **Web** en el menu de PythonAnywhere
2. Click en **Add a new web app**
3. Selecciona **Manual configuration** (NO Flask)
4. Selecciona **Python 3.10** (o la version mas reciente disponible)
5. Click en **Next** hasta terminar

### Editar el archivo WSGI:

1. En la seccion **Code**, click en el enlace del archivo WSGI
   (algo como `/var/www/TU_USUARIO_pythonanywhere_com_wsgi.py`)

2. **Borra todo el contenido** y reemplazalo con:

```python
import sys
import os

# Ruta a tu proyecto - CAMBIA TU_USUARIO por tu nombre de usuario
project_home = '/home/TU_USUARIO/App-para-el-negocio-de-calzados'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configurar entorno de produccion
os.environ['FLASK_ENV'] = 'production'

# Importar la aplicacion
from app_v2 import app as application
```

3. **IMPORTANTE**: Reemplaza `TU_USUARIO` con tu nombre de usuario de PythonAnywhere

---

## Paso 5: Configurar rutas

En la pagina **Web**, configura:

### Source code:
```
/home/TU_USUARIO/App-para-el-negocio-de-calzados
```

### Working directory:
```
/home/TU_USUARIO/App-para-el-negocio-de-calzados
```

---

## Paso 6: Inicializar la base de datos

En una consola Bash:

```bash
cd ~/App-para-el-negocio-de-calzados
python3 datos_iniciales.py
```

Esto creara la base de datos `calzado.db` con la estructura necesaria.

---

## Paso 7: Recargar la aplicacion

1. Ve a la pagina **Web**
2. Click en el boton verde **Reload**
3. Espera unos segundos

---

## Paso 8: Acceder a tu aplicacion

Tu aplicacion estara disponible en:
```
https://TU_USUARIO.pythonanywhere.com
```

---

## Solucion de Problemas

### Error: "No module named 'config'"
- Verifica que el archivo `config.py` este en el directorio del proyecto
- Verifica la ruta en el archivo WSGI

### Error: "No module named 'flask'"
- Ejecuta: `pip3 install --user Flask`

### Error de base de datos
- Verifica que `calzado.db` exista en el directorio del proyecto
- Ejecuta `python3 datos_iniciales.py` nuevamente

### La pagina no carga
1. Ve a **Web** > **Error log**
2. Revisa los ultimos errores
3. Corrige y haz **Reload**

### Ver logs en tiempo real
En una consola Bash:
```bash
tail -f /var/log/TU_USUARIO.pythonanywhere.com.error.log
```

---

## Actualizaciones Futuras

Para actualizar tu aplicacion despues de hacer cambios:

### Si clonaste desde GitHub:
```bash
cd ~/App-para-el-negocio-de-calzados
git pull origin main
```

### Luego:
1. Ve a **Web**
2. Click en **Reload**

---

## Respaldos de la Base de Datos

Es importante hacer respaldos periodicos de tu base de datos:

```bash
cd ~/App-para-el-negocio-de-calzados
cp calzado.db calzado_backup_$(date +%Y%m%d).db
```

Para descargar el respaldo:
1. Ve a **Files**
2. Navega a tu proyecto
3. Click en el archivo `.db` y descargalo

---

## Configuracion Avanzada (Opcional)

### Clave secreta personalizada

Para mayor seguridad, configura una clave secreta:

1. En una consola Bash:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

2. Copia el resultado

3. En **Web** > **WSGI configuration file**, agrega antes del import:
```python
os.environ['SECRET_KEY'] = 'tu-clave-generada-aqui'
```

### Dominio personalizado (Solo cuentas de pago)

1. Ve a **Web**
2. En la seccion **Domains**, agrega tu dominio
3. Configura los DNS de tu dominio para apuntar a PythonAnywhere

---

## Limitaciones de la Cuenta Gratuita

- Solo 1 aplicacion web
- Dominio: `tu_usuario.pythonanywhere.com`
- 512 MB de espacio
- CPU limitada
- La aplicacion puede "dormirse" despues de 3 meses sin login

Para un negocio real, considera la cuenta **Hacker** ($5/mes) que ofrece:
- Mas recursos
- Sin caducidad
- Acceso SSH
- Tareas programadas

---

## Contacto y Soporte

- Documentacion PythonAnywhere: https://help.pythonanywhere.com
- Foros: https://www.pythonanywhere.com/forums/

---

Desarrollado para el Sistema de Gestion de Calzado v2.0
