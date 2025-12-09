"""
Sistema de Gestión de Ventas de Calzado v1.2
Aplicación Flask Principal

NUEVAS CARACTERÍSTICAS:
- Gestión de Variantes (Código + Cuero + Color + Serie)
- Sistema de Inventario (Stock General + Pedidos Cliente)
- Gestión de Ubicaciones (Casa, Tiendas)
- Movimientos de inventario
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_segura_v1_2'

DATABASE = 'ventas_calzado.db'

# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================

def get_db():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

@app.route('/')
def index():
    """Dashboard principal con estadísticas generales"""
    conn = get_db()
    cursor = conn.cursor()

    # Estadísticas de ventas (mantiene compatibilidad con datos históricos)
    cursor.execute('SELECT COUNT(*) as total FROM ventas')
    total_ventas = cursor.fetchone()['total']

    cursor.execute('SELECT SUM(total_venta) as total FROM ventas')
    ingresos_totales = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT SUM(pares) as total FROM ventas')
    pares_vendidos = cursor.fetchone()['total'] or 0

    # Estadísticas de inventario
    cursor.execute('''
        SELECT
            SUM(CASE WHEN tipo_stock = 'general' THEN cantidad_pares ELSE 0 END) as stock_general,
            SUM(CASE WHEN tipo_stock = 'pedido' THEN cantidad_pares ELSE 0 END) as stock_pedidos
        FROM inventario
    ''')
    stats_inv = cursor.fetchone()
    stock_general = stats_inv['stock_general'] or 0
    stock_pedidos = stats_inv['stock_pedidos'] or 0

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
                         pares_vendidos=pares_vendidos,
                         stock_general=stock_general,
                         stock_pedidos=stock_pedidos,
                         ventas_recientes=ventas_recientes)

# ============================================================================
# MÓDULO: UBICACIONES
# ============================================================================

@app.route('/ubicaciones')
def ubicaciones():
    """Vista de gestión de ubicaciones/almacenes"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ubicaciones ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    # Obtener stock por ubicación
    ubicaciones_con_stock = []
    for ubicacion in ubicaciones:
        cursor.execute('''
            SELECT
                SUM(CASE WHEN tipo_stock = 'general' THEN cantidad_pares ELSE 0 END) as stock_general,
                SUM(CASE WHEN tipo_stock = 'pedido' THEN cantidad_pares ELSE 0 END) as stock_pedidos
            FROM inventario
            WHERE id_ubicacion = ?
        ''', (ubicacion['id_ubicacion'],))

        stock = cursor.fetchone()
        ubicaciones_con_stock.append({
            'id': ubicacion['id_ubicacion'],
            'nombre': ubicacion['nombre'],
            'tipo': ubicacion['tipo'],
            'descripcion': ubicacion['descripcion'],
            'activo': ubicacion['activo'],
            'stock_general': stock['stock_general'] or 0,
            'stock_pedidos': stock['stock_pedidos'] or 0
        })

    conn.close()

    return render_template('ubicaciones.html', ubicaciones=ubicaciones_con_stock)

@app.route('/api/ubicaciones/crear', methods=['POST'])
def crear_ubicacion():
    """API para crear nueva ubicación"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO ubicaciones (nombre, tipo, descripcion)
            VALUES (?, ?, ?)
        ''', (data['nombre'], data['tipo'], data.get('descripcion', '')))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Ubicación creada exitosamente'})

    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Ya existe una ubicación con ese nombre'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ubicaciones/<int:id_ubicacion>', methods=['GET'])
def obtener_ubicacion(id_ubicacion):
    """API para obtener detalles de una ubicación"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ubicaciones WHERE id_ubicacion = ?', (id_ubicacion,))
    ubicacion = cursor.fetchone()

    conn.close()

    if ubicacion:
        return jsonify(dict(ubicacion))
    return jsonify({'error': 'Ubicación no encontrada'}), 404

@app.route('/api/ubicaciones/<int:id_ubicacion>/editar', methods=['PUT'])
def editar_ubicacion(id_ubicacion):
    """API para editar ubicación"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE ubicaciones
            SET nombre = ?, tipo = ?, descripcion = ?, activo = ?
            WHERE id_ubicacion = ?
        ''', (data['nombre'], data['tipo'], data.get('descripcion', ''),
              data.get('activo', 1), id_ubicacion))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Ubicación actualizada'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULO: PRODUCTOS BASE Y VARIANTES
# ============================================================================

@app.route('/productos_base')
def productos_base():
    """Vista de productos base"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            pb.*,
            COUNT(DISTINCT v.id_variante) as num_variantes,
            SUM(CASE WHEN v.activo = 1 THEN 1 ELSE 0 END) as variantes_activas
        FROM productos_base pb
        LEFT JOIN variantes v ON pb.codigo_producto = v.codigo_producto
        GROUP BY pb.codigo_producto
        ORDER BY pb.codigo_producto
    ''')
    productos = cursor.fetchall()

    conn.close()

    return render_template('productos_base.html', productos=productos)

@app.route('/variantes')
def variantes():
    """Vista de todas las variantes"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            v.*,
            pb.tipo,
            pb.nombre as nombre_producto,
            COALESCE(SUM(i.cantidad_pares), 0) as stock_total
        FROM variantes v
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        LEFT JOIN inventario i ON v.id_variante = i.id_variante
        GROUP BY v.id_variante
        ORDER BY v.codigo_producto, v.cuero, v.color
    ''')
    variantes = cursor.fetchall()

    conn.close()

    return render_template('variantes.html', variantes=variantes)

@app.route('/variantes/producto/<int:codigo_producto>')
def variantes_producto(codigo_producto):
    """Vista de variantes de un producto específico"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener producto base
    cursor.execute('SELECT * FROM productos_base WHERE codigo_producto = ?', (codigo_producto,))
    producto = cursor.fetchone()

    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('productos_base'))

    # Obtener variantes del producto
    cursor.execute('''
        SELECT
            v.*,
            COALESCE(SUM(i.cantidad_pares), 0) as stock_total,
            COALESCE(SUM(CASE WHEN i.tipo_stock = 'general' THEN i.cantidad_pares ELSE 0 END), 0) as stock_general,
            COALESCE(SUM(CASE WHEN i.tipo_stock = 'pedido' THEN i.cantidad_pares ELSE 0 END), 0) as stock_pedidos
        FROM variantes v
        LEFT JOIN inventario i ON v.id_variante = i.id_variante
        WHERE v.codigo_producto = ?
        GROUP BY v.id_variante
        ORDER BY v.cuero, v.color
    ''', (codigo_producto,))
    variantes = cursor.fetchall()

    conn.close()

    return render_template('variantes_producto.html', producto=producto, variantes=variantes)

@app.route('/api/variantes/crear', methods=['POST'])
def crear_variante():
    """API para crear nueva variante"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO variantes
            (codigo_producto, cuero, color, serie_tallas, pares_por_docena,
             costo_unitario, precio_sugerido, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['codigo_producto'],
            data['cuero'],
            data['color'],
            data['serie_tallas'],
            data.get('pares_por_docena', 12),
            data['costo_unitario'],
            data['precio_sugerido'],
            data.get('observaciones', '')
        ))

        id_variante = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Variante creada exitosamente',
            'id_variante': id_variante
        })

    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Ya existe una variante con esa combinación'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/variantes/<int:id_variante>', methods=['GET'])
def obtener_variante(id_variante):
    """API para obtener detalles de una variante"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT v.*, pb.tipo, pb.nombre
        FROM variantes v
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        WHERE v.id_variante = ?
    ''', (id_variante,))
    variante = cursor.fetchone()

    conn.close()

    if variante:
        return jsonify(dict(variante))
    return jsonify({'error': 'Variante no encontrada'}), 404

@app.route('/api/variantes/<int:id_variante>/editar', methods=['PUT'])
def editar_variante(id_variante):
    """API para editar variante"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE variantes
            SET cuero = ?, color = ?, serie_tallas = ?, pares_por_docena = ?,
                costo_unitario = ?, precio_sugerido = ?, observaciones = ?, activo = ?
            WHERE id_variante = ?
        ''', (
            data['cuero'],
            data['color'],
            data['serie_tallas'],
            data.get('pares_por_docena', 12),
            data['costo_unitario'],
            data['precio_sugerido'],
            data.get('observaciones', ''),
            data.get('activo', 1),
            id_variante
        ))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Variante actualizada'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULO: INVENTARIO
# ============================================================================

@app.route('/inventario')
def inventario():
    """Vista general del inventario"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener inventario completo agrupado por variante
    cursor.execute('''
        SELECT
            v.id_variante,
            v.codigo_producto,
            pb.tipo,
            pb.nombre,
            v.cuero,
            v.color,
            v.serie_tallas,
            v.precio_sugerido,
            SUM(CASE WHEN i.tipo_stock = 'general' THEN i.cantidad_pares ELSE 0 END) as stock_general,
            SUM(CASE WHEN i.tipo_stock = 'pedido' THEN i.cantidad_pares ELSE 0 END) as stock_pedidos,
            SUM(i.cantidad_pares) as stock_total
        FROM variantes v
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        LEFT JOIN inventario i ON v.id_variante = i.id_variante
        WHERE v.activo = 1
        GROUP BY v.id_variante
        HAVING stock_total > 0 OR stock_total IS NULL
        ORDER BY v.codigo_producto, v.cuero, v.color
    ''')
    inventario_data = cursor.fetchall()

    # Obtener ubicaciones
    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    conn.close()

    return render_template('inventario.html',
                         inventario=inventario_data,
                         ubicaciones=ubicaciones)

@app.route('/inventario/detalle/<int:id_variante>')
def inventario_detalle(id_variante):
    """Vista detallada del inventario de una variante"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener información de la variante
    cursor.execute('''
        SELECT v.*, pb.tipo, pb.nombre
        FROM variantes v
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        WHERE v.id_variante = ?
    ''', (id_variante,))
    variante = cursor.fetchone()

    if not variante:
        flash('Variante no encontrada', 'danger')
        return redirect(url_for('inventario'))

    # Obtener inventario por ubicación
    cursor.execute('''
        SELECT
            i.*,
            u.nombre as nombre_ubicacion,
            pc.cliente,
            pc.fecha_entrega_estimada
        FROM inventario i
        JOIN ubicaciones u ON i.id_ubicacion = u.id_ubicacion
        LEFT JOIN pedidos_cliente pc ON i.id_pedido_cliente = pc.id_pedido
        WHERE i.id_variante = ?
        ORDER BY u.nombre, i.tipo_stock
    ''', (id_variante,))
    inventario_detalle = cursor.fetchall()

    # Obtener movimientos recientes
    cursor.execute('''
        SELECT
            m.*,
            uo.nombre as ubicacion_origen,
            ud.nombre as ubicacion_destino
        FROM movimientos_inventario m
        LEFT JOIN ubicaciones uo ON m.id_ubicacion_origen = uo.id_ubicacion
        LEFT JOIN ubicaciones ud ON m.id_ubicacion_destino = ud.id_ubicacion
        WHERE m.id_variante = ?
        ORDER BY m.fecha_movimiento DESC
        LIMIT 20
    ''', (id_variante,))
    movimientos = cursor.fetchall()

    conn.close()

    return render_template('inventario_detalle.html',
                         variante=variante,
                         inventario=inventario_detalle,
                         movimientos=movimientos)

@app.route('/api/inventario/ingresar', methods=['POST'])
def ingresar_inventario():
    """API para ingresar stock (producción)"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        id_variante = data['id_variante']
        id_ubicacion = data['id_ubicacion']
        cantidad_pares = data['cantidad_pares']
        tipo_stock = data.get('tipo_stock', 'general')

        # Verificar si ya existe registro de inventario
        cursor.execute('''
            SELECT id_inventario, cantidad_pares
            FROM inventario
            WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = ?
            AND (id_pedido_cliente IS NULL OR id_pedido_cliente = ?)
        ''', (id_variante, id_ubicacion, tipo_stock, data.get('id_pedido_cliente')))

        inventario_actual = cursor.fetchone()

        if inventario_actual:
            # Actualizar cantidad existente
            nueva_cantidad = inventario_actual['cantidad_pares'] + cantidad_pares
            cursor.execute('''
                UPDATE inventario
                SET cantidad_pares = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_inventario = ?
            ''', (nueva_cantidad, inventario_actual['id_inventario']))
        else:
            # Crear nuevo registro
            cursor.execute('''
                INSERT INTO inventario
                (id_variante, id_ubicacion, tipo_stock, cantidad_pares, id_pedido_cliente)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_variante, id_ubicacion, tipo_stock, cantidad_pares,
                  data.get('id_pedido_cliente')))

        # Registrar movimiento
        cursor.execute('''
            INSERT INTO movimientos_inventario
            (tipo_movimiento, id_variante, id_ubicacion_destino, cantidad_pares,
             tipo_stock, id_pedido_cliente, motivo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('ingreso', id_variante, id_ubicacion, cantidad_pares,
              tipo_stock, data.get('id_pedido_cliente'),
              data.get('motivo', 'Ingreso de producción')))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Inventario ingresado exitosamente'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/inventario/trasladar', methods=['POST'])
def trasladar_inventario():
    """API para trasladar stock entre ubicaciones"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        id_variante = data['id_variante']
        id_ubicacion_origen = data['id_ubicacion_origen']
        id_ubicacion_destino = data['id_ubicacion_destino']
        cantidad_pares = data['cantidad_pares']
        tipo_stock = data.get('tipo_stock', 'general')

        # Verificar stock disponible en origen
        cursor.execute('''
            SELECT cantidad_pares
            FROM inventario
            WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = ?
        ''', (id_variante, id_ubicacion_origen, tipo_stock))

        stock_origen = cursor.fetchone()

        if not stock_origen or stock_origen['cantidad_pares'] < cantidad_pares:
            return jsonify({
                'success': False,
                'error': 'Stock insuficiente en ubicación de origen'
            }), 400

        # Descontar de origen
        nueva_cantidad_origen = stock_origen['cantidad_pares'] - cantidad_pares
        cursor.execute('''
            UPDATE inventario
            SET cantidad_pares = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = ?
        ''', (nueva_cantidad_origen, id_variante, id_ubicacion_origen, tipo_stock))

        # Agregar a destino
        cursor.execute('''
            SELECT id_inventario, cantidad_pares
            FROM inventario
            WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = ?
        ''', (id_variante, id_ubicacion_destino, tipo_stock))

        inventario_destino = cursor.fetchone()

        if inventario_destino:
            nueva_cantidad_destino = inventario_destino['cantidad_pares'] + cantidad_pares
            cursor.execute('''
                UPDATE inventario
                SET cantidad_pares = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_inventario = ?
            ''', (nueva_cantidad_destino, inventario_destino['id_inventario']))
        else:
            cursor.execute('''
                INSERT INTO inventario
                (id_variante, id_ubicacion, tipo_stock, cantidad_pares)
                VALUES (?, ?, ?, ?)
            ''', (id_variante, id_ubicacion_destino, tipo_stock, cantidad_pares))

        # Registrar movimiento
        cursor.execute('''
            INSERT INTO movimientos_inventario
            (tipo_movimiento, id_variante, id_ubicacion_origen, id_ubicacion_destino,
             cantidad_pares, tipo_stock, motivo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('traslado', id_variante, id_ubicacion_origen, id_ubicacion_destino,
              cantidad_pares, tipo_stock, data.get('motivo', 'Traslado entre ubicaciones')))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Traslado realizado exitosamente'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULO: PEDIDOS DE CLIENTES
# ============================================================================

@app.route('/pedidos_cliente')
def pedidos_cliente():
    """Vista de pedidos de clientes"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM pedidos_cliente
        ORDER BY
            CASE estado
                WHEN 'pendiente' THEN 1
                WHEN 'en_preparacion' THEN 2
                WHEN 'entregado' THEN 3
                WHEN 'cancelado' THEN 4
            END,
            fecha_entrega_estimada
    ''')
    pedidos = cursor.fetchall()

    conn.close()

    return render_template('pedidos_cliente.html', pedidos=pedidos)

@app.route('/pedidos_cliente/<int:id_pedido>')
def pedido_detalle(id_pedido):
    """Vista detallada de un pedido"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM pedidos_cliente WHERE id_pedido = ?', (id_pedido,))
    pedido = cursor.fetchone()

    if not pedido:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('pedidos_cliente'))

    cursor.execute('''
        SELECT
            pd.*,
            v.codigo_producto,
            v.cuero,
            v.color,
            v.serie_tallas,
            pb.tipo
        FROM pedidos_detalle pd
        JOIN variantes v ON pd.id_variante = v.id_variante
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        WHERE pd.id_pedido = ?
    ''', (id_pedido,))
    detalles = cursor.fetchall()

    conn.close()

    return render_template('pedido_detalle.html', pedido=pedido, detalles=detalles)

@app.route('/api/pedidos/crear', methods=['POST'])
def crear_pedido():
    """API para crear nuevo pedido de cliente"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # Crear pedido
        cursor.execute('''
            INSERT INTO pedidos_cliente
            (cliente, fecha_pedido, fecha_entrega_estimada, observaciones)
            VALUES (?, ?, ?, ?)
        ''', (
            data['cliente'],
            data['fecha_pedido'],
            data['fecha_entrega_estimada'],
            data.get('observaciones', '')
        ))

        id_pedido = cursor.lastrowid

        # Agregar detalles del pedido
        total_pares = 0
        for item in data['items']:
            cursor.execute('''
                INSERT INTO pedidos_detalle
                (id_pedido, id_variante, cantidad_pares, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                id_pedido,
                item['id_variante'],
                item['cantidad_pares'],
                item['precio_unitario'],
                item['cantidad_pares'] * item['precio_unitario']
            ))
            total_pares += item['cantidad_pares']

        # Actualizar total de pares en el pedido
        cursor.execute('''
            UPDATE pedidos_cliente SET total_pares = ? WHERE id_pedido = ?
        ''', (total_pares, id_pedido))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Pedido creado exitosamente',
            'id_pedido': id_pedido
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULOS LEGACY (Compatibilidad con datos históricos)
# ============================================================================

@app.route('/ventas_historicas')
def ventas_historicas():
    """Vista de ventas históricas"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT v.*, p.tipo
        FROM ventas v
        LEFT JOIN productos p ON v.codigo_calzado = p.codigo_calzado
        ORDER BY v.fecha DESC
    ''')
    ventas = cursor.fetchall()

    conn.close()

    return render_template('ventas_historicas.html', ventas=ventas)

@app.route('/analisis')
def analisis():
    """Módulo de análisis (mantiene compatibilidad)"""
    return render_template('analisis.html', año_actual=datetime.now().year)

# ============================================================================
# INICIALIZACIÓN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SISTEMA DE GESTIÓN DE CALZADO v1.2")
    print("="*60)
    print("\n⚠️  IMPORTANTE: Ejecuta primero 'python migracion_v1_2.py'")
    print("   si aún no has migrado la base de datos.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
