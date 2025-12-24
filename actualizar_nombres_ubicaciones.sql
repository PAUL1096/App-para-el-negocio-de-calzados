-- Script para actualizar nombres de ubicaciones
-- Ejecutar con: python -c "import sqlite3; conn = sqlite3.connect('calzado.db'); conn.executescript(open('actualizar_nombres_ubicaciones.sql').read()); conn.commit(); conn.close()"

-- Actualizar Tienda Principal a "Tienda en Calzaplaza"
UPDATE ubicaciones
SET nombre = 'Tienda en Calzaplaza',
    descripcion = 'Tienda principal ubicada en Calzaplaza'
WHERE nombre LIKE '%Tienda Principal%' OR nombre LIKE '%tienda principal%';

-- Actualizar Tienda Secundaria a "Tienda en CalzaPe"
UPDATE ubicaciones
SET nombre = 'Tienda en CalzaPe',
    descripcion = 'Tienda secundaria ubicada en CalzaPe'
WHERE nombre LIKE '%Tienda Secundaria%' OR nombre LIKE '%tienda secundaria%';

-- Verificar cambios
SELECT id_ubicacion, nombre, tipo, descripcion, activo FROM ubicaciones ORDER BY nombre;
