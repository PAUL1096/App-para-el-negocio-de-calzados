# 🚀 GUÍA DE INICIO RÁPIDO
## Sistema de Gestión de Ventas de Calzado

---

## ⚡ PUESTA EN MARCHA EN 5 MINUTOS

### 1️⃣ Verificar Requisitos (30 segundos)

¿Tienes Python instalado?
```bash
python --version
```

Si ves algo como "Python 3.8" o superior → ✅ Listo  
Si no → Descarga de https://www.python.org/downloads/

### 2️⃣ Instalar Dependencias (1 minuto)

Abre terminal/CMD en la carpeta del sistema y ejecuta:
```bash
pip install -r requirements.txt
```

### 3️⃣ Iniciar el Sistema (10 segundos)

```bash
python app.py
```

Verás algo como:
```
* Running on http://127.0.0.1:5000
```

### 4️⃣ Abrir en el Navegador (5 segundos)

Abre tu navegador favorito y ve a:
```
http://localhost:5000
```

¡LISTO! 🎉 El sistema está funcionando.

---

## 📱 PRIMEROS PASOS

### 1. Explora el Dashboard
- Ve las estadísticas generales
- Revisa las últimas ventas registradas
- Familiarízate con la navegación

### 2. Registra tu Primera Venta
1. Click en "Registrar Venta" en el menú
2. Completa el formulario:
   - Fecha (hoy por defecto)
   - Cliente
   - Destino
   - Selecciona producto (autocompleta precio)
   - Cantidad de pares
   - Método de pago
3. Click "Guardar Venta"

### 3. Revisa el Análisis
- Click en "Análisis" en el menú
- Explora los gráficos interactivos
- Cambia el año en el filtro
- Revisa productos más vendidos

### 4. Gestiona Productos
- Click en "Productos" en el menú
- Revisa el catálogo completo
- Observa costos y márgenes

---

## 🔧 COMANDOS ÚTILES

### Iniciar el Sistema
```bash
python app.py
```

### Detener el Sistema
Presiona `Ctrl + C` en la terminal

### Importar Nuevos Datos desde Excel
```bash
python import_data.py
```

### Ver la Base de Datos
```bash
# Instalar sqlite3 (si no lo tienes)
sqlite3 ventas_calzado.db
```

---

## 💾 BACKUP DE TUS DATOS

### Backup Manual (Recomendado: Diario)
Simplemente copia el archivo:
```bash
cp ventas_calzado.db backups/ventas_FECHA.db
```

O en Windows:
```cmd
copy ventas_calzado.db backups\ventas_FECHA.db
```

### Restaurar desde Backup
```bash
cp backups/ventas_FECHA.db ventas_calzado.db
```

---

## 🌐 ACCESO DESDE OTROS DISPOSITIVOS

### En la Misma Red WiFi:

1. **Obtén tu IP local**:
   - Windows: Abre CMD y escribe `ipconfig`
   - Mac/Linux: Abre terminal y escribe `ifconfig`
   - Busca algo como: `192.168.1.X`

2. **Desde otro dispositivo**:
   Abre el navegador y ve a:
   ```
   http://TU_IP_LOCAL:5000
   ```
   Ejemplo: `http://192.168.1.105:5000`

---

## ❓ SOLUCIÓN RÁPIDA DE PROBLEMAS

### ❌ "No se puede conectar a la página"
**Solución**: 
- Verifica que el servidor esté corriendo (deberías ver mensajes en la terminal)
- Asegúrate de usar `localhost:5000` no solo `localhost`

### ❌ "ModuleNotFoundError: No module named 'flask'"
**Solución**: 
```bash
pip install -r requirements.txt
```

### ❌ "Database is locked"
**Solución**: 
- Cierra todas las instancias de la aplicación
- Reinicia el servidor

### ❌ "Los gráficos no se muestran"
**Solución**: 
- Verifica tu conexión a internet (Chart.js se carga desde CDN)
- Abre la consola del navegador (F12) para ver errores

### ❌ "Error al guardar venta"
**Solución**: 
- Verifica que todos los campos requeridos estén completos
- Revisa la consola del navegador (F12) para ver el error específico

---

## 📋 CHECKLIST DIARIO

**Al Inicio del Día:**
- [ ] Hacer backup de la base de datos
- [ ] Iniciar el sistema (`python app.py`)
- [ ] Verificar que abre correctamente en el navegador

**Durante el Día:**
- [ ] Registrar ventas conforme ocurran
- [ ] Verificar que los datos se guarden correctamente

**Al Finalizar el Día:**
- [ ] Revisar estadísticas del día en Dashboard
- [ ] Hacer backup final
- [ ] Cerrar el sistema (Ctrl + C)

---

## 🎯 ATAJOS Y TIPS

### Navegación Rápida:
- **Inicio**: `/` o click en logo
- **Registrar Venta**: `/registro`
- **Análisis**: `/analisis`
- **Productos**: `/productos`

### Tips de Productividad:
1. **Usa Tab** para navegar entre campos del formulario
2. **Enter** en el último campo guarda la venta
3. Los **productos autocompletan** precio y características
4. El **cálculo de total es automático** al cambiar pares o precio
5. Puedes **filtrar por año** en análisis

### Atajos de Teclado:
- `F5`: Recargar página
- `F12`: Abrir consola del navegador (para debugging)
- `Ctrl + Shift + R`: Recarga forzada (ignora caché)

---

## 📊 INTERPRETACIÓN RÁPIDA DE DATOS

### Dashboard:
- **Total Ventas**: Número de operaciones registradas
- **Ingresos Totales**: Suma de todas las ventas (S/.)
- **Pares Totales**: Cantidad total de pares vendidos
- **Venta Promedio**: Ingreso promedio por operación

### Análisis:
- **Gráfico de Ingresos**: Barras verdes = semanas con más ventas
- **Gráfico de Pares**: Línea azul = tendencia de ventas físicas
- **Top Productos**: Tabla ordenada por pares vendidos
- **Distribución por Tipo**: Círculo = proporción de cada tipo
- **Ventas por Destino**: Barras = ciudades con más actividad
- **Logística**: Tabla = eficiencia y costos por agencia

---

## 🎓 RECURSOS ADICIONALES

### Documentación Completa:
- `README.md`: Guía completa del sistema
- `PLAN_DESARROLLO.md`: Plan de evolución por fases
- `ARQUITECTURA_TECNICA.md`: Detalles técnicos profundos

### Soporte:
- Revisa la documentación primero
- Anota el mensaje de error específico
- Verifica la consola del navegador (F12)

---

## ✨ SIGUIENTES PASOS RECOMENDADOS

Una vez te familiarices con el sistema:

1. **Personaliza**:
   - Ajusta los destinos a tus ciudades específicas
   - Modifica colores/estilos en `static/css/style.css`
   - Agrega campos específicos de tu negocio

2. **Explora Fases Futuras**:
   - Revisa `PLAN_DESARROLLO.md`
   - Decide qué funcionalidad añadir siguiente
   - Planifica sesión con la IA

3. **Respalda Regularmente**:
   - Establece rutina de backup diario
   - Guarda copias en la nube (Google Drive, Dropbox)
   - Prueba restaurar desde backup

---

## 🏁 ¡ESTÁS LISTO!

El sistema está **100% funcional** y listo para usar.

**Recuerda:**
- Hacer backups regularmente
- Registrar ventas consistentemente
- Revisar análisis para tomar mejores decisiones
- Consultar la documentación cuando tengas dudas

**¡Éxito con tu negocio!** 🚀

---

**Última Actualización**: Noviembre 2024  
**Versión**: 1.0  
**Estado**: Sistema Operativo y Listo para Producción
