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
            v.segmento,
            COALESCE(SUM(i.cantidad_pares), 0) as stock_actual,
            COALESCE(SUM(CASE WHEN i.tipo_stock = 'general' THEN i.cantidad_pares ELSE 0 END), 0) as stock_general,
            COALESCE(SUM(CASE WHEN i.tipo_stock = 'pedido' THEN i.cantidad_pares ELSE 0 END), 0) as stock_pedido,
            COUNT(i.id_inventario) as tiene_registros_inventario
        FROM productos_producidos p
        JOIN variantes_base v ON p.id_variante_base = v.id_variante_base
        LEFT JOIN inventario i ON p.id_producto = i.id_producto
        GROUP BY p.id_producto
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

    # Obtener lista de clientes para el selector
    cursor.execute('SELECT * FROM clientes WHERE activo = 1 ORDER BY nombre')
    clientes = cursor.fetchall()

    conn.close()

    return render_template('venta_nueva_v2.html',
                         preparacion=preparacion,
                         productos_disponibles=productos_disponibles,
                         clientes=clientes)

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
            (codigo_venta, id_preparacion, id_producto, id_cliente, cliente, cantidad_pares,
             cantidad_docenas, precio_unitario, subtotal, descuento, total_final,
             estado_pago, metodo_pago, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            codigo_venta,
            data['id_preparacion'],
            data['id_producto'],
            data.get('id_cliente'),
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

        id_venta = cursor.lastrowid

        # Actualizar preparaciones_detalle
        cursor.execute('''
            UPDATE preparaciones_detalle
            SET cantidad_vendida = cantidad_vendida + ?
            WHERE id_preparacion = ? AND id_producto = ?
        ''', (data['cantidad_pares'], data['id_preparacion'], data['id_producto']))

        # Si es venta a crédito, crear cuenta por cobrar automáticamente
        if data.get('estado_pago') == 'credito' and data.get('id_cliente'):
            # Obtener días de crédito del cliente
            cursor.execute('SELECT dias_credito FROM clientes WHERE id_cliente = ?', (data['id_cliente'],))
            cliente_data = cursor.fetchone()
            dias_credito = cliente_data['dias_credito'] if cliente_data else 30

            # Generar código de cuenta
            cursor.execute('SELECT MAX(id_cuenta) FROM cuentas_por_cobrar')
            max_id = cursor.fetchone()[0] or 0
            codigo_cuenta = f"CC-{max_id + 1:06d}"

            # Crear cuenta por cobrar
            cursor.execute('''
                INSERT INTO cuentas_por_cobrar
                (id_cliente, id_venta, codigo_cuenta, concepto, monto_total, saldo_pendiente,
                 fecha_emision, fecha_vencimiento, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, DATE('now'), DATE('now', '+' || ? || ' days'), ?)
            ''', (
                data['id_cliente'],
                id_venta,
                codigo_cuenta,
                f'Venta {codigo_venta}',
                total_final,
                total_final,
                dias_credito,
                f"Cuenta generada automáticamente desde venta {codigo_venta}"
            ))

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
# MÓDULO: VENTA DIRECTA (Sin preparación)
# ============================================================================

@app.route('/ventas/nueva-directa')
def venta_directa_nueva():
    """Formulario para venta directa desde inventario"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener ubicaciones activas
    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    # Obtener lista de clientes para el selector
    cursor.execute('SELECT * FROM clientes WHERE activo = 1 ORDER BY nombre')
    clientes = cursor.fetchall()

    conn.close()

    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    return render_template('venta_directa_nueva.html',
                         ubicaciones=ubicaciones,
                         clientes=clientes,
                         fecha_hoy=fecha_hoy)

@app.route('/api/inventario/por-ubicacion/<int:id_ubicacion>')
def inventario_por_ubicacion(id_ubicacion):
    """API para obtener inventario disponible de una ubicación"""
    try:
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
                p.pares_por_docena,
                vb.codigo_interno,
                vb.tipo_calzado,
                u.nombre as ubicacion_nombre
            FROM inventario i
            JOIN productos_producidos p ON i.id_producto = p.id_producto
            JOIN variantes_base vb ON p.id_variante_base = vb.id_variante_base
            JOIN ubicaciones u ON i.id_ubicacion = u.id_ubicacion
            WHERE i.id_ubicacion = ? AND i.cantidad_pares > 0 AND i.tipo_stock = 'general'
            ORDER BY vb.codigo_interno, p.cuero, p.color_cuero
        ''', (id_ubicacion,))

        inventario = cursor.fetchall()
        conn.close()

        # Convertir a lista de diccionarios
        items = []
        for row in inventario:
            items.append({
                'id_inventario': row['id_inventario'],
                'id_producto': row['id_producto'],
                'codigo_interno': row['codigo_interno'],
                'tipo_calzado': row['tipo_calzado'],
                'cuero': row['cuero'],
                'color_cuero': row['color_cuero'],
                'suela': row['suela'],
                'forro': row['forro'],
                'serie_tallas': row['serie_tallas'],
                'cantidad_pares': row['cantidad_pares'],
                'precio_sugerido': row['precio_sugerido'],
                'pares_por_docena': row['pares_por_docena']
            })

        return jsonify({'success': True, 'inventario': items})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ventas/registrar-directa', methods=['POST'])
def registrar_venta_directa():
    """API para registrar venta directa (sin preparación)"""
    conn = None
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # Iniciar transacción INMEDIATA
        cursor.execute('BEGIN IMMEDIATE')

        # Generar código de venta único
        fecha_hoy = datetime.now().strftime('%Y%m%d')
        cursor.execute('''
            SELECT COALESCE(MAX(CAST(SUBSTR(codigo_venta, 11) AS INTEGER)), 0) as ultimo
            FROM ventas_v2
            WHERE codigo_venta LIKE ?
        ''', (f"VD{fecha_hoy}-%",))

        ultimo_numero = cursor.fetchone()['ultimo']
        nuevo_numero = ultimo_numero + 1
        codigo_venta = f"VD{fecha_hoy}-{nuevo_numero:03d}"  # VD = Venta Directa

        cantidad_docenas = data['cantidad_pares'] / data.get('pares_por_docena', 12)
        subtotal = data['cantidad_pares'] * data['precio_unitario']
        total_final = subtotal - data.get('descuento', 0)

        # Verificar stock disponible
        cursor.execute('''
            SELECT cantidad_pares FROM inventario
            WHERE id_inventario = ? AND tipo_stock = 'general'
        ''', (data['id_inventario'],))

        inventario = cursor.fetchone()
        if not inventario:
            raise Exception('Inventario no encontrado')

        if inventario['cantidad_pares'] < data['cantidad_pares']:
            raise Exception(f'Stock insuficiente. Disponible: {inventario["cantidad_pares"]} pares')

        # Crear venta (sin id_preparacion)
        cursor.execute('''
            INSERT INTO ventas_v2
            (codigo_venta, id_preparacion, id_producto, id_cliente, cliente, cantidad_pares,
             cantidad_docenas, precio_unitario, subtotal, descuento, total_final,
             estado_pago, metodo_pago, observaciones)
            VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            codigo_venta,
            data['id_producto'],
            data.get('id_cliente'),
            data['cliente'],
            data['cantidad_pares'],
            cantidad_docenas,
            data['precio_unitario'],
            subtotal,
            data.get('descuento', 0),
            total_final,
            data.get('estado_pago', 'pagado'),
            data.get('metodo_pago', 'efectivo'),
            data.get('observaciones', 'Venta directa desde inventario')
        ))

        id_venta = cursor.lastrowid

        # Descontar del inventario
        cursor.execute('''
            UPDATE inventario
            SET cantidad_pares = cantidad_pares - ?
            WHERE id_inventario = ?
        ''', (data['cantidad_pares'], data['id_inventario']))

        # Si es venta a crédito, crear cuenta por cobrar automáticamente
        if data.get('estado_pago') == 'credito' and data.get('id_cliente'):
            # Obtener días de crédito del cliente
            cursor.execute('SELECT dias_credito FROM clientes WHERE id_cliente = ?', (data['id_cliente'],))
            cliente_data = cursor.fetchone()
            dias_credito = cliente_data['dias_credito'] if cliente_data else 30

            # Generar código de cuenta
            cursor.execute('SELECT MAX(id_cuenta) FROM cuentas_por_cobrar')
            max_id = cursor.fetchone()[0] or 0
            codigo_cuenta = f"CC-{max_id + 1:06d}"

            # Crear cuenta por cobrar
            cursor.execute('''
                INSERT INTO cuentas_por_cobrar
                (id_cliente, id_venta, codigo_cuenta, concepto, monto_total, saldo_pendiente,
                 fecha_emision, fecha_vencimiento, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, DATE('now'), DATE('now', '+' || ? || ' days'), ?)
            ''', (
                data['id_cliente'],
                id_venta,
                codigo_cuenta,
                f'Venta {codigo_venta}',
                total_final,
                total_final,
                dias_credito,
                f"Cuenta generada automáticamente desde venta {codigo_venta}"
            ))

        conn.commit()

        return jsonify({
            'success': True,
            'message': 'Venta directa registrada exitosamente',
            'codigo_venta': codigo_venta
        })

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        if conn:
            conn.close()

# ============================================================================
# MÓDULO: UBICACIONES
# ============================================================================

@app.route('/ubicaciones')
def ubicaciones():
    """Vista de ubicaciones con stock calculado"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener ubicaciones con stock agregado
    cursor.execute('''
        SELECT
            u.*,
            COALESCE(SUM(CASE WHEN i.tipo_stock = 'general' THEN i.cantidad_pares ELSE 0 END), 0) as stock_general,
            COALESCE(SUM(CASE WHEN i.tipo_stock = 'pedido' THEN i.cantidad_pares ELSE 0 END), 0) as stock_pedidos,
            COALESCE(SUM(i.cantidad_pares), 0) as stock_total,
            COUNT(DISTINCT i.id_producto) as productos_diferentes
        FROM ubicaciones u
        LEFT JOIN inventario i ON u.id_ubicacion = i.id_ubicacion
        GROUP BY u.id_ubicacion
        ORDER BY u.nombre
    ''')
    ubicaciones_list = cursor.fetchall()

    conn.close()

    return render_template('ubicaciones.html', ubicaciones=ubicaciones_list)

# ============================================================================
# MÓDULO: CUENTAS POR COBRAR
# ============================================================================

@app.route('/cuentas-por-cobrar')
def cuentas_por_cobrar():
    """Dashboard de cuentas por cobrar"""
    conn = get_db()
    cursor = conn.cursor()

    # Estadísticas generales
    cursor.execute('''
        SELECT
            COUNT(*) as total_cuentas,
            COALESCE(SUM(saldo_pendiente), 0) as total_por_cobrar,
            COALESCE(SUM(CASE WHEN estado = 'vencida' THEN saldo_pendiente ELSE 0 END), 0) as total_vencido,
            COALESCE(SUM(CASE WHEN estado = 'pendiente' THEN saldo_pendiente ELSE 0 END), 0) as total_al_dia
        FROM cuentas_por_cobrar
        WHERE saldo_pendiente > 0
    ''')
    stats = dict(cursor.fetchone())

    # Cuentas vencidas
    cursor.execute('''
        SELECT
            c.*,
            cl.nombre,
            cl.apellido,
            cl.nombre_comercial
        FROM cuentas_por_cobrar c
        JOIN clientes cl ON c.id_cliente = cl.id_cliente
        WHERE c.estado = 'vencida' AND c.saldo_pendiente > 0
        ORDER BY c.dias_mora DESC, c.saldo_pendiente DESC
        LIMIT 10
    ''')
    cuentas_vencidas = cursor.fetchall()

    # Clientes con mayor deuda
    cursor.execute('''
        SELECT
            cl.id_cliente,
            cl.nombre,
            cl.apellido,
            cl.nombre_comercial,
            COALESCE(SUM(c.saldo_pendiente), 0) as deuda_total,
            COUNT(c.id_cuenta) as num_cuentas
        FROM clientes cl
        LEFT JOIN cuentas_por_cobrar c ON cl.id_cliente = c.id_cliente
        WHERE c.saldo_pendiente > 0
        GROUP BY cl.id_cliente
        ORDER BY deuda_total DESC
        LIMIT 5
    ''')
    top_deudores = cursor.fetchall()

    # Lista de clientes para el modal de nueva cuenta
    cursor.execute('SELECT * FROM clientes ORDER BY nombre')
    clientes = cursor.fetchall()

    conn.close()

    return render_template('cuentas_por_cobrar.html',
                         stats=stats,
                         cuentas_vencidas=cuentas_vencidas,
                         top_deudores=top_deudores,
                         clientes=clientes)

@app.route('/clientes')
def clientes():
    """Lista de clientes"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            cl.*,
            COALESCE(SUM(c.saldo_pendiente), 0) as deuda_total,
            COUNT(c.id_cuenta) as num_cuentas_pendientes
        FROM clientes cl
        LEFT JOIN cuentas_por_cobrar c ON cl.id_cliente = c.id_cliente AND c.saldo_pendiente > 0
        GROUP BY cl.id_cliente
        ORDER BY cl.fecha_registro DESC
    ''')
    clientes_list = cursor.fetchall()

    conn.close()

    return render_template('clientes.html', clientes=clientes_list)

@app.route('/api/clientes/crear', methods=['POST'])
def crear_cliente():
    """API para crear nuevo cliente"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO clientes
            (nombre, apellido, nombre_comercial, tipo_documento, numero_documento,
             telefono, email, direccion, limite_credito, dias_credito, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['nombre'],
            data.get('apellido', ''),
            data.get('nombre_comercial', ''),
            data.get('tipo_documento', 'DNI'),
            data.get('numero_documento', ''),
            data.get('telefono', ''),
            data.get('email', ''),
            data.get('direccion', ''),
            data.get('limite_credito', 0),
            data.get('dias_credito', 30),
            data.get('observaciones', '')
        ))

        id_cliente = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Cliente creado exitosamente',
            'id_cliente': id_cliente
        })

    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'El número de documento ya existe'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cuentas/crear', methods=['POST'])
def crear_cuenta():
    """API para crear nueva cuenta por cobrar"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # Generar código de cuenta
        cursor.execute('SELECT MAX(id_cuenta) FROM cuentas_por_cobrar')
        max_id = cursor.fetchone()[0] or 0
        codigo_cuenta = f"CC-{max_id + 1:06d}"

        saldo_pendiente = data['monto_total']

        cursor.execute('''
            INSERT INTO cuentas_por_cobrar
            (id_cliente, id_venta, codigo_cuenta, concepto, monto_total, saldo_pendiente,
             fecha_emision, fecha_vencimiento, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id_cliente'],
            data.get('id_venta'),
            codigo_cuenta,
            data['concepto'],
            data['monto_total'],
            saldo_pendiente,
            data['fecha_emision'],
            data['fecha_vencimiento'],
            data.get('observaciones', '')
        ))

        id_cuenta = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Cuenta creada exitosamente',
            'id_cuenta': id_cuenta,
            'codigo_cuenta': codigo_cuenta
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/pagos/registrar', methods=['POST'])
def registrar_pago():
    """API para registrar pago"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # Generar código de pago
        cursor.execute('SELECT MAX(id_pago) FROM pagos')
        max_id = cursor.fetchone()[0] or 0
        codigo_pago = f"PAG-{max_id + 1:06d}"

        # Insertar pago
        cursor.execute('''
            INSERT INTO pagos
            (id_cuenta, codigo_pago, monto_pago, metodo_pago, fecha_pago,
             numero_comprobante, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id_cuenta'],
            codigo_pago,
            data['monto_pago'],
            data.get('metodo_pago', 'efectivo'),
            data['fecha_pago'],
            data.get('numero_comprobante', ''),
            data.get('observaciones', '')
        ))

        # Actualizar cuenta por cobrar
        cursor.execute('''
            UPDATE cuentas_por_cobrar
            SET monto_pagado = monto_pagado + ?,
                saldo_pendiente = monto_total - (monto_pagado + ?),
                estado = CASE
                    WHEN monto_total - (monto_pagado + ?) <= 0 THEN 'pagada'
                    WHEN DATE('now') > fecha_vencimiento THEN 'vencida'
                    ELSE 'pendiente'
                END
            WHERE id_cuenta = ?
        ''', (data['monto_pago'], data['monto_pago'], data['monto_pago'], data['id_cuenta']))

        # Obtener datos de la cuenta para actualizar la venta vinculada
        cursor.execute('''
            SELECT id_venta, saldo_pendiente, monto_total
            FROM cuentas_por_cobrar
            WHERE id_cuenta = ?
        ''', (data['id_cuenta'],))

        cuenta = cursor.fetchone()

        # Si la cuenta está vinculada a una venta, actualizar su estado
        if cuenta and cuenta['id_venta']:
            nuevo_saldo = cuenta['monto_total'] - (cuenta['saldo_pendiente'] + data['monto_pago'])

            if nuevo_saldo <= 0:
                # Deuda completamente pagada
                cursor.execute('''
                    UPDATE ventas_v2
                    SET estado_pago = 'pagado'
                    WHERE id_venta = ?
                ''', (cuenta['id_venta'],))
            else:
                # Pago parcial
                cursor.execute('''
                    UPDATE ventas_v2
                    SET estado_pago = 'parcial'
                    WHERE id_venta = ?
                ''', (cuenta['id_venta'],))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Pago registrado exitosamente',
            'codigo_pago': codigo_pago
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

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
