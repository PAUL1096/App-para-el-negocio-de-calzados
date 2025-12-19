"""
Sistema de Gestión de Calzado v2.0
Modelo correcto: Variantes Base → Productos Producidos → Inventario
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'calzado.db'

def get_db():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE, timeout=30.0)  # 30 segundos de timeout
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging para mejor concurrencia
    return conn

# ============================================================================
# DASHBOARD
# ============================================================================

@app.route('/')
def index():
    """Dashboard principal"""
    conn = get_db()
    cursor = conn.cursor()

    # Estadísticas
    cursor.execute('SELECT COUNT(*) as total FROM variantes_base WHERE activo = 1')
    total_variantes = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as total FROM productos_producidos WHERE activo = 1')
    total_productos = cursor.fetchone()['total']

    cursor.execute('SELECT COALESCE(SUM(cantidad_pares), 0) as total FROM inventario')
    total_stock = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as total FROM ventas_v2 WHERE DATE(fecha_venta) = DATE("now")')
    ventas_hoy = cursor.fetchone()['total']

    conn.close()

    stats = {
        'variantes': total_variantes,
        'productos': total_productos,
        'stock': total_stock,
        'ventas_hoy': ventas_hoy
    }

    return render_template('index_v2.html', stats=stats)

# ============================================================================
# MÓDULO: CATÁLOGO DE VARIANTES BASE
# ============================================================================

@app.route('/catalogo-variantes')
def catalogo_variantes():
    """Vista de catálogo de variantes base"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM variantes_base
        ORDER BY activo DESC, codigo_interno
    ''')
    variantes = cursor.fetchall()

    conn.close()

    return render_template('catalogo_variantes.html', variantes=variantes)

@app.route('/api/variantes-base/crear', methods=['POST'])
def crear_variante_base():
    """API para crear nueva variante base"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO variantes_base
            (codigo_interno, tipo_calzado, tipo_horma, segmento, descripcion)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['codigo_interno'],
            data['tipo_calzado'],
            data['tipo_horma'],
            data['segmento'],
            data.get('descripcion', '')
        ))

        id_variante_base = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Variante base creada exitosamente',
            'id_variante_base': id_variante_base
        })

    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'El código interno ya existe'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/variantes-base/<int:id_variante_base>', methods=['GET'])
def obtener_variante_base(id_variante_base):
    """API para obtener detalles de una variante base"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM variantes_base
            WHERE id_variante_base = ?
        ''', (id_variante_base,))
        variante = cursor.fetchone()

        conn.close()

        if variante:
            return jsonify({'success': True, 'variante': dict(variante)})
        return jsonify({'success': False, 'error': 'Variante no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/variantes-base/<int:id_variante_base>/editar', methods=['PUT'])
def editar_variante_base(id_variante_base):
    """API para editar variante base"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE variantes_base
            SET codigo_interno = ?, tipo_calzado = ?, tipo_horma = ?,
                segmento = ?, descripcion = ?, activo = ?
            WHERE id_variante_base = ?
        ''', (
            data['codigo_interno'],
            data['tipo_calzado'],
            data['tipo_horma'],
            data['segmento'],
            data.get('descripcion', ''),
            data.get('activo', 1),
            id_variante_base
        ))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Variante base actualizada exitosamente'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULO: PRODUCCIÓN
# ============================================================================

@app.route('/produccion')
def produccion():
    """Vista de productos producidos"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            p.*,
            v.codigo_interno,
            v.tipo_calzado,
            v.tipo_horma,
            v.segmento
        FROM productos_producidos p
        JOIN variantes_base v ON p.id_variante_base = v.id_variante_base
        ORDER BY p.fecha_produccion DESC, p.id_producto DESC
    ''')
    productos = cursor.fetchall()

    conn.close()

    return render_template('produccion.html', productos=productos)

@app.route('/produccion/nueva/<int:id_variante_base>')
def produccion_nueva(id_variante_base):
    """Formulario para nueva producción"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM variantes_base
        WHERE id_variante_base = ?
    ''', (id_variante_base,))
    variante = cursor.fetchone()

    conn.close()

    if not variante:
        flash('Variante base no encontrada', 'danger')
        return redirect(url_for('catalogo_variantes'))

    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    return render_template('produccion_nueva.html', variante=variante, fecha_hoy=fecha_hoy)

@app.route('/api/productos/crear', methods=['POST'])
def crear_producto():
    """API para crear nuevo producto"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO productos_producidos
            (id_variante_base, cuero, color_cuero, suela, forro, serie_tallas,
             pares_por_docena, costo_unitario, precio_sugerido, fecha_produccion,
             cantidad_total_pares, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id_variante_base'],
            data['cuero'],
            data['color_cuero'],
            data['suela'],
            data.get('forro', ''),
            data['serie_tallas'],
            data.get('pares_por_docena', 12),
            data['costo_unitario'],
            data['precio_sugerido'],
            data.get('fecha_produccion', datetime.now().strftime('%Y-%m-%d')),
            data['cantidad_total_pares'],
            data.get('observaciones', '')
        ))

        id_producto = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Producto creado exitosamente',
            'id_producto': id_producto
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULO: INVENTARIO
# ============================================================================

@app.route('/inventario')
def inventario():
    """Vista de inventario de productos"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            i.*,
            p.cuero,
            p.color_cuero,
            p.suela,
            p.forro,
            p.serie_tallas,
            p.precio_sugerido,
            vb.codigo_interno,
            vb.tipo_calzado,
            vb.tipo_horma,
            vb.segmento,
            u.nombre as ubicacion_nombre
        FROM inventario i
        JOIN productos_producidos p ON i.id_producto = p.id_producto
        JOIN variantes_base vb ON p.id_variante_base = vb.id_variante_base
        JOIN ubicaciones u ON i.id_ubicacion = u.id_ubicacion
        ORDER BY u.nombre, vb.codigo_interno, p.cuero, p.color_cuero
    ''')
    items_inventario = cursor.fetchall()

    # Obtener ubicaciones
    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    conn.close()

    return render_template('inventario_v2.html',
                         items=items_inventario,
                         ubicaciones=ubicaciones)

@app.route('/inventario/ingresar/<int:id_producto>')
def inventario_ingresar_form(id_producto):
    """Formulario para ingresar producto al inventario"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener producto
    cursor.execute('''
        SELECT
            p.*,
            vb.codigo_interno,
            vb.tipo_calzado,
            vb.tipo_horma,
            vb.segmento
        FROM productos_producidos p
        JOIN variantes_base vb ON p.id_variante_base = vb.id_variante_base
        WHERE p.id_producto = ?
    ''', (id_producto,))
    producto = cursor.fetchone()

    # Obtener ubicaciones
    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    conn.close()

    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('produccion'))

    return render_template('inventario_ingresar.html',
                         producto=producto,
                         ubicaciones=ubicaciones)

@app.route('/api/inventario/ingresar', methods=['POST'])
def ingresar_inventario():
    """API para ingresar producto al inventario"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO inventario
            (id_producto, id_ubicacion, tipo_stock, cantidad_pares)
            VALUES (?, ?, ?, ?)
        ''', (
            data['id_producto'],
            data['id_ubicacion'],
            data.get('tipo_stock', 'general'),
            data['cantidad_pares']
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Producto ingresado al inventario exitosamente'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULO: PREPARACIONES
# ============================================================================

@app.route('/preparaciones')
def preparaciones():
    """Vista de preparaciones de mercadería"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener todas las preparaciones
    cursor.execute('''
        SELECT
            p.*,
            u.nombre as ubicacion_origen,
            COUNT(DISTINCT pd.id_producto) as total_productos,
            SUM(pd.cantidad_pares) as total_pares,
            SUM(pd.cantidad_vendida) as total_vendido,
            SUM(pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) as pendiente_vender
        FROM preparaciones p
        LEFT JOIN ubicaciones u ON p.id_ubicacion_origen = u.id_ubicacion
        LEFT JOIN preparaciones_detalle pd ON p.id_preparacion = pd.id_preparacion
        GROUP BY p.id_preparacion
        ORDER BY p.fecha_preparacion DESC, p.id_preparacion DESC
    ''')
    preparaciones = cursor.fetchall()

    conn.close()

    return render_template('preparaciones_v2.html', preparaciones=preparaciones)

@app.route('/preparaciones/nueva')
def preparacion_nueva():
    """Formulario para crear nueva preparación"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener ubicaciones
    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    # Obtener productos con stock disponible en inventario
    cursor.execute('''
        SELECT
            i.id_inventario,
            i.id_producto,
            i.id_ubicacion,
            i.tipo_stock,
            i.cantidad_pares,
            p.cuero,
            p.color_cuero,
            p.suela,
            p.forro,
            p.serie_tallas,
            p.precio_sugerido,
            vb.codigo_interno,
            vb.tipo_calzado,
            vb.tipo_horma,
            vb.segmento,
            u.nombre as ubicacion_nombre
        FROM inventario i
        JOIN productos_producidos p ON i.id_producto = p.id_producto
        JOIN variantes_base vb ON p.id_variante_base = vb.id_variante_base
        JOIN ubicaciones u ON i.id_ubicacion = u.id_ubicacion
        WHERE i.cantidad_pares > 0
        ORDER BY u.nombre, vb.codigo_interno, p.cuero
    ''')
    productos_disponibles = cursor.fetchall()

    conn.close()

    # Días de venta por defecto
    dias_venta = ['Jueves', 'Viernes', 'Sábado']

    return render_template('preparacion_nueva_v2.html',
                         ubicaciones=ubicaciones,
                         productos_disponibles=productos_disponibles,
                         dias_venta=dias_venta)

@app.route('/api/preparaciones/crear', methods=['POST'])
def crear_preparacion():
    """API para crear nueva preparación"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # Generar código de preparación
        fecha_hoy = datetime.now().strftime('%Y%m%d')
        cursor.execute('SELECT COUNT(*) as total FROM preparaciones WHERE DATE(fecha_preparacion) = DATE(?)', (datetime.now(),))
        num_preps_hoy = cursor.fetchone()['total'] + 1
        codigo_preparacion = f"P{fecha_hoy}-{num_preps_hoy:03d}"

        # Crear preparación
        cursor.execute('''
            INSERT INTO preparaciones
            (codigo_preparacion, id_ubicacion_origen, dia_venta, fecha_preparacion, observaciones, estado)
            VALUES (?, ?, ?, ?, ?, 'pendiente')
        ''', (
            codigo_preparacion,
            data['id_ubicacion_origen'],
            data['dia_venta'],
            data.get('fecha_preparacion', datetime.now().strftime('%Y-%m-%d')),
            data.get('observaciones', '')
        ))

        id_preparacion = cursor.lastrowid

        # Agregar productos a la preparación
        for item in data.get('productos', []):
            cursor.execute('''
                INSERT INTO preparaciones_detalle
                (id_preparacion, id_producto, tipo_stock, cantidad_pares)
                VALUES (?, ?, ?, ?)
            ''', (
                id_preparacion,
                item['id_producto'],
                item.get('tipo_stock', 'general'),
                item['cantidad_pares']
            ))

            # Reducir del inventario
            cursor.execute('''
                UPDATE inventario
                SET cantidad_pares = cantidad_pares - ?
                WHERE id_inventario = ?
            ''', (item['cantidad_pares'], item['id_inventario']))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Preparación creada exitosamente',
            'id_preparacion': id_preparacion,
            'codigo': codigo_preparacion
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULO: VENTAS
# ============================================================================

@app.route('/ventas')
def ventas():
    """Vista de todas las ventas v2"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener ventas
    cursor.execute('''
        SELECT
            v.*,
            p.cuero,
            p.color_cuero,
            p.suela,
            vb.codigo_interno,
            vb.tipo_calzado,
            prep.dia_venta,
            prep.fecha_preparacion
        FROM ventas_v2 v
        JOIN productos_producidos p ON v.id_producto = p.id_producto
        JOIN variantes_base vb ON p.id_variante_base = vb.id_variante_base
        JOIN preparaciones prep ON v.id_preparacion = prep.id_preparacion
        ORDER BY v.fecha_venta DESC, v.hora_venta DESC
        LIMIT 100
    ''')
    ventas = cursor.fetchall()

    # Obtener preparaciones con stock disponible para vender
    cursor.execute('''
        SELECT
            p.*,
            u.nombre as ubicacion_origen,
            SUM(pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) as pendiente_vender
        FROM preparaciones p
        LEFT JOIN ubicaciones u ON p.id_ubicacion_origen = u.id_ubicacion
        LEFT JOIN preparaciones_detalle pd ON p.id_preparacion = pd.id_preparacion
        WHERE p.estado IN ('pendiente', 'en_proceso')
        GROUP BY p.id_preparacion
        HAVING pendiente_vender > 0
        ORDER BY p.fecha_preparacion DESC, p.dia_venta
    ''')
    preparaciones_disponibles = cursor.fetchall()

    conn.close()

    return render_template('ventas_v2.html', ventas=ventas, preparaciones_disponibles=preparaciones_disponibles)

@app.route('/ventas/nueva/<int:id_preparacion>')
def venta_nueva(id_preparacion):
    """Formulario para registrar venta desde preparación"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener preparación
    cursor.execute('SELECT * FROM preparaciones WHERE id_preparacion = ?', (id_preparacion,))
    preparacion = cursor.fetchone()

    if not preparacion:
        flash('Preparación no encontrada', 'danger')
        return redirect(url_for('ventas'))

    # Obtener productos disponibles en la preparación
    cursor.execute('''
        SELECT
            pd.*,
            p.cuero,
            p.color_cuero,
            p.suela,
            p.forro,
            p.serie_tallas,
            p.pares_por_docena,
            p.precio_sugerido,
            vb.codigo_interno,
            vb.tipo_calzado,
            (pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) as disponible
        FROM preparaciones_detalle pd
        JOIN productos_producidos p ON pd.id_producto = p.id_producto
        JOIN variantes_base vb ON p.id_variante_base = vb.id_variante_base
        WHERE pd.id_preparacion = ?
        AND (pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) > 0
        ORDER BY pd.tipo_stock, vb.codigo_interno
    ''', (id_preparacion,))

    productos_disponibles = cursor.fetchall()

    conn.close()

    return render_template('venta_nueva_v2.html',
                         preparacion=preparacion,
                         productos_disponibles=productos_disponibles)

@app.route('/api/ventas/registrar', methods=['POST'])
def registrar_venta():
    """API para registrar nueva venta"""
    conn = None
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # Iniciar transacción INMEDIATA para evitar race conditions
        cursor.execute('BEGIN IMMEDIATE')

        # Generar código de venta único usando MAX en lugar de COUNT (más seguro)
        fecha_hoy = datetime.now().strftime('%Y%m%d')
        cursor.execute('''
            SELECT COALESCE(MAX(CAST(SUBSTR(codigo_venta, 11) AS INTEGER)), 0) as ultimo
            FROM ventas_v2
            WHERE codigo_venta LIKE ?
        ''', (f"V{fecha_hoy}-%",))

        ultimo_numero = cursor.fetchone()['ultimo']
        nuevo_numero = ultimo_numero + 1
        codigo_venta = f"V{fecha_hoy}-{nuevo_numero:03d}"

        cantidad_docenas = data['cantidad_pares'] / data.get('pares_por_docena', 12)
        subtotal = data['cantidad_pares'] * data['precio_unitario']
        total_final = subtotal - data.get('descuento', 0)

        # Crear venta
        cursor.execute('''
            INSERT INTO ventas_v2
            (codigo_venta, id_preparacion, id_producto, cliente, cantidad_pares,
             cantidad_docenas, precio_unitario, subtotal, descuento, total_final,
             estado_pago, metodo_pago, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            codigo_venta,
            data['id_preparacion'],
            data['id_producto'],
            data['cliente'],
            data['cantidad_pares'],
            cantidad_docenas,
            data['precio_unitario'],
            subtotal,
            data.get('descuento', 0),
            total_final,
            data.get('estado_pago', 'pendiente'),
            data.get('metodo_pago', ''),
            data.get('observaciones', '')
        ))

        # Actualizar preparaciones_detalle
        cursor.execute('''
            UPDATE preparaciones_detalle
            SET cantidad_vendida = cantidad_vendida + ?
            WHERE id_preparacion = ? AND id_producto = ?
        ''', (data['cantidad_pares'], data['id_preparacion'], data['id_producto']))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Venta registrada exitosamente',
            'codigo_venta': codigo_venta
        })

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULO: UBICACIONES
# ============================================================================

@app.route('/ubicaciones')
def ubicaciones():
    """Vista de ubicaciones"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ubicaciones ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    conn.close()

    return render_template('ubicaciones.html', ubicaciones=ubicaciones)

# ============================================================================
# SERVIDOR
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Sistema de Gestión de Calzado v2.0")
    print("="*70)
    print("📦 Modelo: Variantes Base → Productos → Inventario")
    print("🌐 Servidor: http://localhost:5000")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
