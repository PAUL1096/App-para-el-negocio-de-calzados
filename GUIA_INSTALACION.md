# 📦 Guía de Instalación - Sistema de Gestión de Calzado v2.0

Guía paso a paso para instalar el sistema en cualquier computadora.

---

## 📋 Requisitos Previos

### Software Necesario:

1. **Python 3.8 o superior**
   - Descargar desde: https://www.python.org/downloads/
   - ✅ Durante la instalación: **Marcar "Add Python to PATH"**

2. **Git** (solo si vas a clonar el repositorio)
   - Descargar desde: https://git-scm.com/downloads

3. **Navegador Web** (Chrome, Firefox, Edge)

---

## 🚀 Opción 1: Instalación desde GitHub (Recomendado)

### Paso 1: Clonar el Repositorio

Abre una terminal (CMD en Windows, Terminal en Mac/Linux) y ejecuta:

```bash
git clone https://github.com/PAUL1096/App-para-el-negocio-de-calzados.git
cd App-para-el-negocio-de-calzados
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**¿Qué se instala?**
- Flask 3.0.0 - Framework web
- pandas 2.1.3 - Manejo de datos (opcional)
- openpyxl 3.1.2 - Excel (opcional)

### Paso 3: Inicializar Base de Datos

**Si es instalación nueva (sin datos):**

```bash
python datos_iniciales.py
```

Esto crea:
- Base de datos vacía `calzado.db`
- Ubicación inicial "Almacén Central"

**Si tienes una base de datos existente:**
- Copia tu archivo `calzado.db` a la carpeta del proyecto

### Paso 4: Iniciar la Aplicación

```bash
python app_v2.py
```

Verás un mensaje como:
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.X:5000
```

### Paso 5: Abrir en el Navegador

Abre tu navegador y ve a:
```
http://localhost:5000
```

✅ **¡Listo! El sistema está funcionando**

---

## 📁 Opción 2: Instalación desde Carpeta ZIP

Si recibiste el sistema como archivo ZIP:

### Paso 1: Extraer Archivos

1. Descomprime el archivo ZIP en una carpeta
   Ejemplo: `C:\Calzado\` o `~/Documentos/Calzado/`

### Paso 2: Abrir Terminal en la Carpeta

**Windows:**
1. Abre la carpeta del proyecto
2. Shift + Click derecho → "Abrir ventana de PowerShell aquí"

**Mac/Linux:**
1. Abre Terminal
2. Navega a la carpeta: `cd /ruta/a/la/carpeta`

### Paso 3: Instalar Dependencias

```bash
pip install flask
```

(Flask es la única dependencia crítica)

### Paso 4: Inicializar Base de Datos

```bash
python datos_iniciales.py
```

### Paso 5: Iniciar Aplicación

```bash
python app_v2.py
```

### Paso 6: Abrir Navegador

```
http://localhost:5000
```

---

## 🔧 Configuración Inicial (Primera Vez)

### 1. Crear Ubicaciones

Ruta: `/ubicaciones`

Crea las ubicaciones de tu negocio:
- ✅ Almacén Central (ya existe)
- Tienda 1
- Tienda 2
- Bodega
- etc.

### 2. Crear Variantes Base (Modelos)

Ruta: `/catalogo-variantes`

Crea los modelos de calzado que produces:
- Código interno
- Tipo (zapato, sandalia, bota)
- Horma
- Segmento (hombre, mujer, niño)

### 3. (Opcional) Crear Clientes

Ruta: `/clientes`

Pre-carga clientes frecuentes con:
- Nombre y apellido
- Teléfono
- Días de crédito

---

## 🌐 Acceso desde Otras Computadoras (Red Local)

Si quieres acceder al sistema desde otras computadoras en la misma red:

### Paso 1: Obtener IP de la Computadora Servidor

**Windows:**
```bash
ipconfig
```
Busca "Dirección IPv4": Ejemplo: 192.168.1.100

**Mac/Linux:**
```bash
ifconfig
```
Busca "inet": Ejemplo: 192.168.1.100

### Paso 2: Modificar app_v2.py (Opcional)

Abre `app_v2.py` y busca la última línea:

```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

Si dice `host='127.0.0.1'`, cámbialo a `host='0.0.0.0'`

### Paso 3: Configurar Firewall (Windows)

1. Panel de Control → Firewall de Windows
2. Configuración avanzada → Reglas de entrada
3. Nueva regla → Puerto → TCP → 5000
4. Permitir conexión → Aplicar

### Paso 4: Acceder desde Otras PCs

En cualquier navegador de la red local:
```
http://192.168.1.100:5000
```
(Reemplaza 192.168.1.100 con tu IP)

---

## 🔄 Actualizar el Sistema

Si hay una nueva versión del sistema:

### Con Git:
```bash
cd App-para-el-negocio-de-calzados
git pull origin claude/check-latest-branch-RaeFz
python app_v2.py
```

### Sin Git:
1. Descarga la nueva versión
2. **RESPALDA tu base de datos** (`calzado.db`)
3. Reemplaza archivos (excepto `calzado.db`)
4. Ejecuta `python app_v2.py`

---

## 🆘 Solución de Problemas

### Problema: "Python no se reconoce como comando"

**Solución:**
1. Reinstala Python
2. ✅ Marca "Add Python to PATH"
3. Reinicia la terminal

### Problema: "No module named 'flask'"

**Solución:**
```bash
pip install flask
```

Si no funciona:
```bash
python -m pip install flask
```

### Problema: "Address already in use"

**Solución:**
Otro programa está usando el puerto 5000.

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID [número] /F
```

**Mac/Linux:**
```bash
lsof -i :5000
kill -9 [PID]
```

O cambia el puerto en `app_v2.py`:
```python
app.run(debug=False, port=5001)  # Usar puerto 5001
```

### Problema: No puedo acceder desde otra PC

**Solución:**
1. Verifica que `host='0.0.0.0'` en `app_v2.py`
2. Desactiva temporalmente el firewall para probar
3. Asegúrate de estar en la misma red WiFi

### Problema: Base de datos bloqueada

**Solución:**
1. Cierra todas las instancias de la aplicación
2. Reinicia el servidor
3. Si persiste, elimina archivos `calzado.db-journal` y `calzado.db-wal`

---

## 📂 Estructura de Archivos

```
App-para-el-negocio-de-calzados/
├── app_v2.py                 # Aplicación principal ⭐
├── calzado.db                # Base de datos 💾
├── requirements.txt          # Dependencias
│
├── datos_iniciales.py        # Script de inicialización
├── limpiar_datos_prueba.py   # Script de limpieza
│
├── templates/                # Vistas HTML
│   ├── base.html
│   ├── index_v2.html
│   └── ... (30+ archivos)
│
├── static/                   # CSS, JS, imágenes (si existe)
│
└── *.md                      # Documentación
```

---

## ✅ Verificación de Instalación

Después de instalar, verifica que funciona:

1. ✅ Dashboard carga correctamente
2. ✅ Puedes crear una variante base
3. ✅ Puedes crear un producto
4. ✅ Puedes ingresar a inventario
5. ✅ Puedes hacer una venta

---

## 💾 Respaldo de Datos

**IMPORTANTE:** Respalda tu base de datos regularmente.

### Método Manual:

Copia el archivo `calzado.db` a un lugar seguro:
```
C:\Respaldos\calzado_2026-01-16.db
```

### Método Automático (Windows):

Crea un archivo `respaldo.bat`:
```batch
@echo off
set fecha=%date:~-4,4%%date:~-7,2%%date:~-10,2%
copy calzado.db "C:\Respaldos\calzado_%fecha%.db"
echo Respaldo creado: calzado_%fecha%.db
```

Ejecútalo manualmente o programa una tarea en Windows.

---

## 📞 Soporte

**Documentación adicional:**
- `INICIO_RAPIDO.md` - Guía rápida de uso
- `PREPARAR_PARA_PRODUCCION.md` - Cómo limpiar datos
- `REVISION_FINAL.md` - Funcionalidades del sistema

**Problemas técnicos:**
- Revisa la consola donde ejecutas `python app_v2.py`
- Los errores aparecen ahí

---

## 🎯 Checklist de Instalación Exitosa

- [ ] Python instalado y funcionando
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos inicializada
- [ ] Aplicación inicia sin errores
- [ ] Dashboard accesible en http://localhost:5000
- [ ] Ubicaciones creadas
- [ ] Variantes base creadas (modelos)
- [ ] Sistema probado (crear producto, venta)

---

**Versión:** 2.0.0
**Última actualización:** 2026-01-16
