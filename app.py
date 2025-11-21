"""
Sistema de Gestión de Ventas de Calzado
Aplicación Flask Principal
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_123'

DATABASE = 'ventas_calzado.db'

def get_db():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            codigo_calzado INTEGER PRIMARY KEY,
            tipo TEXT,
            cuero TEXT,
            color TEXT,
            serie_tallas TEXT,
            costo_unitario REAL,
            precio_sugerido REAL,
            observaciones TEXT
        )
    ''')
    
    # Tabla de ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta TEXT PRIMARY KEY,
            fecha DATE,
            cliente TEXT,
            destino TEXT,
            codigo_calzado INTEGER,
            cuero TEXT,
            color TEXT,
            calidad TEXT,
            precio_unitario REAL,
            pares INTEGER,
            total_venta REAL,
            estado_pago TEXT,
            metodo_pago TEXT,
            comentario TEXT,
            año INTEGER,
            semana INTEGER,
            dia_semana TEXT,
            FOREIGN KEY (codigo_calzado) REFERENCES productos (codigo_calzado)
        )
    ''')
    
    # Tabla de logística
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logistica (
            id_envio TEXT PRIMARY KEY,
            id_venta TEXT,
            costo_envio REAL,
            destino TEXT,
            agencia TEXT,
            fecha_envio DATE,
            observaciones TEXT,
            FOREIGN KEY (id_venta) REFERENCES ventas (id_venta)
        )
    ''')
    
    conn.commit()
    conn.close()

# Rutas principales

@app.route('/')
def index():
    """Dashboard principal"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Estadísticas generales
    cursor.execute('SELECT COUNT(*) as total FROM ventas')
    total_ventas = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(total_venta) as total FROM ventas')
    ingresos_totales = cursor.fetchone()['total'] or 0
    
    cursor.execute('SELECT SUM(pares) as total FROM ventas')
    pares_totales = cursor.fetchone()['total'] or 0
    
    cursor.execute('SELECT AVG(total_venta) as promedio FROM ventas')
    venta_promedio = cursor.fetchone()['promedio'] or 0
    
    # Ventas recientes
    cursor.execute('''
        SELECT v.*, p.tipo 
        FROM ventas v 
        LEFT JOIN productos p ON v.codigo_calzado = p.codigo_calzado 
        ORDER BY v.fecha DESC 
        LIMIT 10
    ''')
    ventas_recientes = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html',
                         total_ventas=total_ventas,
                         ingresos_totales=ingresos_totales,
                         pares_totales=pares_totales,
                         venta_promedio=venta_promedio,
                         ventas_recientes=ventas_recientes)

@app.route('/registro')
def registro():
    """Módulo de registro de ventas"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Obtener lista de productos
    cursor.execute('SELECT * FROM productos ORDER BY codigo_calzado')
    productos = cursor.fetchall()
    
    # Generar siguiente ID de venta
    cursor.execute('SELECT id_venta FROM ventas ORDER BY id_venta DESC LIMIT 1')
    ultima_venta = cursor.fetchone()
    
    if ultima_venta:
        num = int(ultima_venta['id_venta'][1:]) + 1
        siguiente_id = f"V{num:04d}"
    else:
        siguiente_id = "V0001"
    
    # Obtener lista de destinos únicos existentes
    cursor.execute('SELECT DISTINCT destino FROM ventas ORDER BY destino')
    destinos_existentes = [row['destino'] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('registro_venta.html', 
                         productos=productos,
                         siguiente_id=siguiente_id,
                         destinos_existentes=destinos_existentes)

@app.route('/api/producto/<int:codigo>')
def get_producto(codigo):
    """API para obtener información de un producto"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM productos WHERE codigo_calzado = ?', (codigo,))
    producto = cursor.fetchone()
    
    conn.close()
    
    if producto:
        return jsonify(dict(producto))
    return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/api/guardar_venta', methods=['POST'])
def guardar_venta():
    """API para guardar una nueva venta"""
    try:
        data = request.json
        
        # Procesar fecha
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d')
        año = fecha.year
        semana = fecha.isocalendar()[1]
        dia_semana = fecha.strftime('%A')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Insertar venta
        cursor.execute('''
            INSERT INTO ventas 
            (id_venta, fecha, cliente, destino, codigo_calzado, cuero, color, calidad,
             precio_unitario, pares, total_venta, estado_pago, metodo_pago, comentario,
             año, semana, dia_semana)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id_venta'],
            data['fecha'],
            data['cliente'],
            data['destino'],
            data['codigo_calzado'],
            data.get('cuero', ''),
            data.get('color', ''),
            data.get('calidad', 'primera'),
            data['precio_unitario'],
            data['pares'],
            data['total_venta'],
            data['estado_pago'],
            data['metodo_pago'],
            data.get('comentario', ''),
            año,
            semana,
            dia_semana
        ))
        
        # Si hay información de logística, insertarla
        if data.get('incluir_logistica'):
            id_envio = f"E{data['id_venta'][1:]}"
            cursor.execute('''
                INSERT INTO logistica 
                (id_envio, id_venta, costo_envio, destino, agencia, fecha_envio, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                id_envio,
                data['id_venta'],
                data.get('costo_envio', 0),
                data['destino'],
                data.get('agencia', ''),
                data['fecha'],
                data.get('obs_logistica', '')
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Venta registrada correctamente'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/analisis')
def analisis():
    """Módulo de análisis y visualización"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Filtros de fecha (últimos 6 meses por defecto)
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=180)
    
    año_actual = fecha_fin.year
    
    conn.close()
    
    return render_template('analisis.html', 
                         año_actual=año_actual,
                         fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
                         fecha_fin=fecha_fin.strftime('%Y-%m-%d'))

@app.route('/api/analisis/ventas_semanales')
def api_ventas_semanales():
    """API para obtener ventas por semana"""
    año = request.args.get('año', datetime.now().year, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            semana,
            COUNT(*) as num_ventas,
            SUM(pares) as total_pares,
            SUM(total_venta) as total_ingresos,
            AVG(total_venta) as venta_promedio
        FROM ventas
        WHERE año = ?
        GROUP BY semana
        ORDER BY semana
    ''', (año,))
    
    resultados = cursor.fetchall()
    conn.close()
    
    data = {
        'semanas': [r['semana'] for r in resultados],
        'num_ventas': [r['num_ventas'] for r in resultados],
        'total_pares': [r['total_pares'] for r in resultados],
        'total_ingresos': [round(r['total_ingresos'], 2) for r in resultados],
        'venta_promedio': [round(r['venta_promedio'], 2) for r in resultados]
    }
    
    return jsonify(data)

@app.route('/api/analisis/productos_top')
def api_productos_top():
    """API para obtener productos más vendidos"""
    limite = request.args.get('limite', 10, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            v.codigo_calzado,
            p.tipo,
            p.cuero,
            p.color,
            SUM(v.pares) as total_pares,
            SUM(v.total_venta) as total_ingresos,
            COUNT(*) as num_ventas
        FROM ventas v
        LEFT JOIN productos p ON v.codigo_calzado = p.codigo_calzado
        GROUP BY v.codigo_calzado
        ORDER BY total_pares DESC
        LIMIT ?
    ''', (limite,))
    
    resultados = cursor.fetchall()
    conn.close()
    
    data = []
    for r in resultados:
        data.append({
            'codigo': r['codigo_calzado'],
            'tipo': r['tipo'],
            'cuero': r['cuero'],
            'color': r['color'],
            'pares': r['total_pares'],
            'ingresos': round(r['total_ingresos'], 2),
            'ventas': r['num_ventas']
        })
    
    return jsonify(data)

@app.route('/api/analisis/destinos')
def api_destinos():
    """API para obtener análisis por destino"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            destino,
            COUNT(*) as num_ventas,
            SUM(pares) as total_pares,
            SUM(total_venta) as total_ingresos
        FROM ventas
        GROUP BY destino
        ORDER BY total_ingresos DESC
    ''')
    
    resultados = cursor.fetchall()
    conn.close()
    
    data = []
    for r in resultados:
        data.append({
            'destino': r['destino'],
            'ventas': r['num_ventas'],
            'pares': r['total_pares'],
            'ingresos': round(r['total_ingresos'], 2)
        })
    
    return jsonify(data)

@app.route('/api/analisis/logistica')
def api_logistica():
    """API para obtener análisis de logística"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            agencia,
            COUNT(*) as num_envios,
            SUM(costo_envio) as costo_total,
            AVG(costo_envio) as costo_promedio
        FROM logistica
        GROUP BY agencia
        ORDER BY num_envios DESC
    ''')
    
    resultados = cursor.fetchall()
    conn.close()
    
    data = []
    for r in resultados:
        data.append({
            'agencia': r['agencia'],
            'envios': r['num_envios'],
            'costo_total': round(r['costo_total'], 2),
            'costo_promedio': round(r['costo_promedio'], 2)
        })
    
    return jsonify(data)

@app.route('/productos')
def productos():
    """Vista de gestión de productos"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM productos ORDER BY codigo_calzado')
    productos = cursor.fetchall()
    
    conn.close()
    
    return render_template('productos.html', productos=productos)

@app.route('/productos/nuevo')
def producto_nuevo():
    """Formulario para agregar nuevo producto"""
    return render_template('producto_form.html', producto=None, accion='nuevo')

@app.route('/productos/editar/<int:codigo>')
def producto_editar(codigo):
    """Formulario para editar producto existente"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM productos WHERE codigo_calzado = ?', (codigo,))
    producto = cursor.fetchone()
    
    conn.close()
    
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('productos'))
    
    return render_template('producto_form.html', producto=producto, accion='editar')

@app.route('/api/productos/guardar', methods=['POST'])
def guardar_producto():
    """API para guardar producto (nuevo o editado)"""
    try:
        data = request.json
        accion = data.get('accion')
        
        conn = get_db()
        cursor = conn.cursor()
        
        if accion == 'nuevo':
            # Obtener el siguiente código disponible
            cursor.execute('SELECT MAX(codigo_calzado) as max_codigo FROM productos')
            result = cursor.fetchone()
            siguiente_codigo = (result['max_codigo'] or 0) + 1
            
            cursor.execute('''
                INSERT INTO productos 
                (codigo_calzado, tipo, cuero, color, serie_tallas, costo_unitario, precio_sugerido, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                siguiente_codigo,
                data['tipo'],
                data['cuero'],
                data['color'],
                data['serie_tallas'],
                data['costo_unitario'],
                data['precio_sugerido'],
                data.get('observaciones', '')
            ))
            
            mensaje = f'Producto código {siguiente_codigo} creado exitosamente'
            
        elif accion == 'editar':
            cursor.execute('''
                UPDATE productos 
                SET tipo = ?, cuero = ?, color = ?, serie_tallas = ?,
                    costo_unitario = ?, precio_sugerido = ?, observaciones = ?
                WHERE codigo_calzado = ?
            ''', (
                data['tipo'],
                data['cuero'],
                data['color'],
                data['serie_tallas'],
                data['costo_unitario'],
                data['precio_sugerido'],
                data.get('observaciones', ''),
                data['codigo_calzado']
            ))
            
            mensaje = f'Producto código {data["codigo_calzado"]} actualizado exitosamente'
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': mensaje})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/productos/eliminar/<int:codigo>', methods=['DELETE'])
def eliminar_producto(codigo):
    """API para eliminar producto"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Verificar si tiene ventas asociadas
        cursor.execute('SELECT COUNT(*) as count FROM ventas WHERE codigo_calzado = ?', (codigo,))
        result = cursor.fetchone()
        
        if result['count'] > 0:
            conn.close()
            return jsonify({
                'success': False, 
                'error': f'No se puede eliminar. Este producto tiene {result["count"]} ventas asociadas.'
            }), 400
        
        # Eliminar producto
        cursor.execute('DELETE FROM productos WHERE codigo_calzado = ?', (codigo,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Producto código {codigo} eliminado'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
