"""
Sistema de Gestión de Ventas de Calzado v1.3
Aplicación Flask Principal

VERSIÓN 1.3 - FASE 3+4:
- Preparación de Mercadería
- Ventas vinculadas a Preparación
- Actualización automática de Inventario
- Control de Devoluciones
- Registro en Docenas

Incluye todas las funcionalidades de v1.2:
- Gestión de Variantes
- Sistema de Inventario (Stock General + Pedidos)
- Gestión de Ubicaciones
- Movimientos de inventario
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_v1_3_2025'

DATABASE = 'ventas_calzado.db'

# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================

def get_db():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_configuracion(clave, default=None):
    """Obtiene un valor de configuración"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT valor FROM configuracion_sistema WHERE clave = ?', (clave,))
    result = cursor.fetchone()
    conn.close()
    return result['valor'] if result else default

# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

@app.route('/')
def index():
    """Dashboard principal con estadísticas generales"""
    conn = get_db()
    cursor = conn.cursor()

    # Estadísticas de ventas legacy
    cursor.execute('SELECT COUNT(*) as total FROM ventas')
    total_ventas_legacy = cursor.fetchone()['total']

    # Estadísticas de ventas v2
    cursor.execute('SELECT COUNT(*) as total FROM ventas_v2')
    total_ventas_v2 = cursor.fetchone()['total']

    cursor.execute('SELECT SUM(total_final) as total FROM ventas_v2')
    ingresos_v2 = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT SUM(cantidad_pares) as total FROM ventas_v2')
    pares_vendidos_v2 = cursor.fetchone()['total'] or 0

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

    # Preparaciones activas
    cursor.execute('''
        SELECT COUNT(*) as total
        FROM preparaciones
        WHERE estado IN ('preparada', 'en_venta')
    ''')
    preparaciones_activas = cursor.fetchone()['total']

    # Ventas recientes v2
    cursor.execute('''
        SELECT
            v.*,
            va.codigo_producto,
            va.cuero,
            va.color,
            pb.tipo
        FROM ventas_v2 v
        JOIN variantes va ON v.id_variante = va.id_variante
        JOIN productos_base pb ON va.codigo_producto = pb.codigo_producto
        ORDER BY v.fecha_venta DESC, v.hora_venta DESC
        LIMIT 10
    ''')
    ventas_recientes = cursor.fetchall()

    conn.close()

    return render_template('index_v13.html',
                         total_ventas_legacy=total_ventas_legacy,
                         total_ventas_v2=total_ventas_v2,
                         ingresos_v2=ingresos_v2,
                         pares_vendidos_v2=pares_vendidos_v2,
                         stock_general=stock_general,
                         stock_pedidos=stock_pedidos,
                         preparaciones_activas=preparaciones_activas,
                         ventas_recientes=ventas_recientes)

# ============================================================================
# MÓDULO: PREPARACIÓN DE MERCADERÍA
# ============================================================================

@app.route('/preparaciones')
def preparaciones():
    """Vista de preparaciones de mercadería"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener todas las preparaciones con su información completa
    cursor.execute('''
        SELECT
            p.*,
            u.nombre as ubicacion_origen,
            COUNT(DISTINCT pd.id_variante) as total_variantes_real,
            SUM(pd.cantidad_pares) as total_pares_real,
            SUM(pd.cantidad_vendida) as total_vendido,
            SUM(pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) as pendiente_vender
        FROM preparaciones p
        LEFT JOIN ubicaciones u ON p.id_ubicacion_origen = u.id_ubicacion
        LEFT JOIN preparaciones_detalle pd ON p.id_preparacion = pd.id_preparacion
        GROUP BY p.id_preparacion
        ORDER BY p.fecha_preparacion DESC, p.id_preparacion DESC
    ''')
    preparaciones = cursor.fetchall()

    # Obtener ubicaciones disponibles
    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    # Obtener días de venta configurados
    dias_venta = obtener_configuracion('dias_venta', 'Jueves,Viernes,Sábado').split(',')

    conn.close()

    return render_template('preparaciones.html',
                         preparaciones=preparaciones,
                         ubicaciones=ubicaciones,
                         dias_venta=dias_venta)

@app.route('/preparaciones/nueva')
def preparacion_nueva():
    """Formulario para crear nueva preparación"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener ubicaciones
    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    # Obtener variantes con stock disponible
    cursor.execute('''
        SELECT
            v.id_variante,
            v.codigo_producto,
            v.cuero,
            v.color,
            v.serie_tallas,
            v.pares_por_docena,
            pb.tipo,
            pb.nombre as nombre_producto,
            COALESCE(SUM(CASE WHEN i.tipo_stock = 'general' THEN i.cantidad_pares ELSE 0 END), 0) as stock_general,
            COALESCE(SUM(CASE WHEN i.tipo_stock = 'pedido' THEN i.cantidad_pares ELSE 0 END), 0) as stock_pedidos
        FROM variantes v
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        LEFT JOIN inventario i ON v.id_variante = i.id_variante
        WHERE v.activo = 1
        GROUP BY v.id_variante
        HAVING stock_general > 0 OR stock_pedidos > 0
        ORDER BY v.codigo_producto, v.cuero, v.color
    ''')
    variantes_disponibles = cursor.fetchall()

    # Obtener pedidos pendientes
    cursor.execute('''
        SELECT
            pc.*,
            COUNT(DISTINCT pd.id_variante) as num_variantes
        FROM pedidos_cliente pc
        LEFT JOIN pedidos_detalle pd ON pc.id_pedido = pd.id_pedido
        WHERE pc.estado IN ('pendiente', 'en_preparacion')
        GROUP BY pc.id_pedido
        ORDER BY pc.fecha_entrega_estimada
    ''')
    pedidos_pendientes = cursor.fetchall()

    # Días de venta
    dias_venta = obtener_configuracion('dias_venta', 'Jueves,Viernes,Sábado').split(',')

    conn.close()

    return render_template('preparacion_nueva.html',
                         ubicaciones=ubicaciones,
                         variantes_disponibles=variantes_disponibles,
                         pedidos_pendientes=pedidos_pendientes,
                         dias_venta=dias_venta)

@app.route('/api/preparaciones/crear', methods=['POST'])
def crear_preparacion():
    """API para crear nueva preparación"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # Crear preparación
        cursor.execute('''
            INSERT INTO preparaciones
            (fecha_preparacion, dia_venta, id_ubicacion_origen, responsable, observaciones)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['fecha_preparacion'],
            data['dia_venta'],
            data['id_ubicacion_origen'],
            data.get('responsable', ''),
            data.get('observaciones', '')
        ))

        id_preparacion = cursor.lastrowid

        total_pares = 0
        total_variantes = 0

        # Procesar variantes del stock general
        if 'variantes_general' in data:
            for item in data['variantes_general']:
                id_variante = item['id_variante']
                cantidad = item['cantidad_pares']
                id_ubicacion = data['id_ubicacion_origen']

                # Verificar stock disponible
                cursor.execute('''
                    SELECT cantidad_pares
                    FROM inventario
                    WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = 'general'
                ''', (id_variante, id_ubicacion))

                stock = cursor.fetchone()
                if not stock or stock['cantidad_pares'] < cantidad:
                    conn.rollback()
                    conn.close()
                    return jsonify({
                        'success': False,
                        'error': f'Stock insuficiente para variante {id_variante}'
                    }), 400

                # Descontar del inventario (descuento temporal)
                cursor.execute('''
                    UPDATE inventario
                    SET cantidad_pares = cantidad_pares - ?
                    WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = 'general'
                ''', (cantidad, id_variante, id_ubicacion))

                # Agregar al detalle de preparación
                cursor.execute('''
                    INSERT INTO preparaciones_detalle
                    (id_preparacion, id_variante, tipo_stock, cantidad_pares)
                    VALUES (?, ?, 'general', ?)
                ''', (id_preparacion, id_variante, cantidad))

                # Registrar movimiento
                cursor.execute('''
                    INSERT INTO movimientos_inventario
                    (tipo_movimiento, id_variante, id_ubicacion_origen, cantidad_pares,
                     tipo_stock, id_preparacion, motivo)
                    VALUES ('preparacion', ?, ?, ?, 'general', ?, 'Preparación para venta')
                ''', (id_variante, id_ubicacion, cantidad, id_preparacion))

                total_pares += cantidad
                total_variantes += 1

        # Procesar pedidos a entregar
        if 'pedidos_entregar' in data:
            for pedido_info in data['pedidos_entregar']:
                id_pedido = pedido_info['id_pedido']

                # Obtener detalles del pedido
                cursor.execute('''
                    SELECT pd.*, v.id_variante
                    FROM pedidos_detalle pd
                    JOIN variantes v ON pd.id_variante = v.id_variante
                    WHERE pd.id_pedido = ?
                ''', (id_pedido,))

                detalles = cursor.fetchall()

                for detalle in detalles:
                    id_variante = detalle['id_variante']
                    cantidad = detalle['cantidad_pares']

                    # Agregar al detalle de preparación
                    cursor.execute('''
                        INSERT INTO preparaciones_detalle
                        (id_preparacion, id_variante, tipo_stock, id_pedido_cliente, cantidad_pares)
                        VALUES (?, ?, 'pedido', ?, ?)
                    ''', (id_preparacion, id_variante, id_pedido, cantidad))

                    total_pares += cantidad

                # Actualizar estado del pedido
                cursor.execute('''
                    UPDATE pedidos_cliente
                    SET estado = 'en_preparacion'
                    WHERE id_pedido = ?
                ''', (id_pedido,))

        # Actualizar totales de la preparación
        cursor.execute('''
            UPDATE preparaciones
            SET total_pares = ?, total_variantes = ?
            WHERE id_preparacion = ?
        ''', (total_pares, total_variantes, id_preparacion))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Preparación creada exitosamente',
            'id_preparacion': id_preparacion
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/preparaciones/<int:id_preparacion>')
def preparacion_detalle(id_preparacion):
    """Vista detallada de una preparación"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener preparación
    cursor.execute('''
        SELECT p.*, u.nombre as ubicacion_origen
        FROM preparaciones p
        LEFT JOIN ubicaciones u ON p.id_ubicacion_origen = u.id_ubicacion
        WHERE p.id_preparacion = ?
    ''', (id_preparacion,))

    preparacion = cursor.fetchone()

    if not preparacion:
        flash('Preparación no encontrada', 'danger')
        return redirect(url_for('preparaciones'))

    # Obtener detalles
    cursor.execute('''
        SELECT
            pd.*,
            v.codigo_producto,
            v.cuero,
            v.color,
            v.serie_tallas,
            v.precio_sugerido,
            pb.tipo,
            pc.cliente as cliente_pedido
        FROM preparaciones_detalle pd
        JOIN variantes v ON pd.id_variante = v.id_variante
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        LEFT JOIN pedidos_cliente pc ON pd.id_pedido_cliente = pc.id_pedido
        WHERE pd.id_preparacion = ?
        ORDER BY pd.tipo_stock, v.codigo_producto
    ''', (id_preparacion,))

    detalles = cursor.fetchall()

    # Obtener ventas realizadas de esta preparación
    cursor.execute('''
        SELECT
            v.*,
            va.codigo_producto,
            va.cuero,
            va.color
        FROM ventas_v2 v
        JOIN variantes va ON v.id_variante = va.id_variante
        WHERE v.id_preparacion = ?
        ORDER BY v.fecha_venta DESC, v.hora_venta DESC
    ''', (id_preparacion,))

    ventas = cursor.fetchall()

    conn.close()

    return render_template('preparacion_detalle.html',
                         preparacion=preparacion,
                         detalles=detalles,
                         ventas=ventas)

# ============================================================================
# MÓDULO: VENTAS V2 (Vinculadas a Preparación)
# ============================================================================

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
        return redirect(url_for('preparaciones'))

    # Obtener variantes disponibles en la preparación
    cursor.execute('''
        SELECT
            pd.*,
            v.codigo_producto,
            v.cuero,
            v.color,
            v.serie_tallas,
            v.pares_por_docena,
            v.precio_sugerido,
            pb.tipo,
            (pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) as disponible
        FROM preparaciones_detalle pd
        JOIN variantes v ON pd.id_variante = v.id_variante
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        WHERE pd.id_preparacion = ?
        AND (pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) > 0
        ORDER BY pd.tipo_stock, v.codigo_producto
    ''', (id_preparacion,))

    variantes_disponibles = cursor.fetchall()

    # Generar código de venta
    fecha_hoy = datetime.now().strftime('%Y%m%d')
    cursor.execute('SELECT COUNT(*) as total FROM ventas_v2 WHERE DATE(fecha_venta) = DATE(?)', (datetime.now(),))
    num_ventas_hoy = cursor.fetchone()['total'] + 1
    codigo_venta = f"V{fecha_hoy}-{num_ventas_hoy:03d}"

    conn.close()

    return render_template('venta_nueva.html',
                         preparacion=preparacion,
                         variantes_disponibles=variantes_disponibles,
                         codigo_venta=codigo_venta)

@app.route('/api/ventas/registrar', methods=['POST'])
def registrar_venta():
    """API para registrar nueva venta"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        id_preparacion = data['id_preparacion']
        id_variante = data['id_variante']
        cantidad_pares = data['cantidad_pares']
        precio_unitario = data['precio_unitario']
        cliente = data['cliente']

        # Calcular docenas
        pares_por_docena = float(obtener_configuracion('pares_por_docena', '12'))
        cantidad_docenas = cantidad_pares / pares_por_docena

        # Calcular totales
        total_venta = cantidad_pares * precio_unitario
        descuento = data.get('descuento', 0)
        total_final = total_venta - descuento

        # Obtener fecha/hora actual
        fecha_venta = datetime.now().strftime('%Y-%m-%d')
        hora_venta = datetime.now().strftime('%H:%M:%S')

        # Calcular año, semana, mes
        fecha_obj = datetime.now()
        año = fecha_obj.year
        semana = fecha_obj.isocalendar()[1]
        mes = fecha_obj.month

        # Verificar disponibilidad en preparación
        cursor.execute('''
            SELECT
                pd.id_detalle,
                pd.cantidad_pares,
                pd.cantidad_vendida,
                pd.cantidad_devuelta,
                pd.tipo_stock,
                pd.id_pedido_cliente,
                (pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) as disponible
            FROM preparaciones_detalle pd
            WHERE pd.id_preparacion = ? AND pd.id_variante = ?
        ''', (id_preparacion, id_variante))

        detalle_prep = cursor.fetchone()

        if not detalle_prep or detalle_prep['disponible'] < cantidad_pares:
            conn.rollback()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Cantidad no disponible en la preparación'
            }), 400

        # Crear venta
        cursor.execute('''
            INSERT INTO ventas_v2
            (codigo_venta, id_preparacion, fecha_venta, hora_venta, cliente, destino,
             id_variante, cantidad_pares, cantidad_docenas, precio_unitario, total_venta,
             descuento, total_final, metodo_pago, estado_pago, monto_pagado,
             es_pedido_cliente, id_pedido_cliente, observaciones, año, semana, mes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['codigo_venta'],
            id_preparacion,
            fecha_venta,
            hora_venta,
            cliente,
            data.get('destino', ''),
            id_variante,
            cantidad_pares,
            cantidad_docenas,
            precio_unitario,
            total_venta,
            descuento,
            total_final,
            data.get('metodo_pago', 'efectivo'),
            data.get('estado_pago', 'pagado'),
            data.get('monto_pagado', total_final),
            1 if detalle_prep['tipo_stock'] == 'pedido' else 0,
            detalle_prep['id_pedido_cliente'],
            data.get('observaciones', ''),
            año,
            semana,
            mes
        ))

        id_venta = cursor.lastrowid

        # Actualizar cantidad vendida en preparación
        cursor.execute('''
            UPDATE preparaciones_detalle
            SET cantidad_vendida = cantidad_vendida + ?
            WHERE id_detalle = ?
        ''', (cantidad_pares, detalle_prep['id_detalle']))

        # Si es un pedido, marcar como entregado si se completó
        if detalle_prep['tipo_stock'] == 'pedido' and detalle_prep['id_pedido_cliente']:
            # Verificar si se entregó todo el pedido
            cursor.execute('''
                SELECT
                    SUM(pd.cantidad_pares) as total_pedido,
                    SUM(CASE WHEN prep_det.cantidad_vendida >= pd.cantidad_pares THEN pd.cantidad_pares ELSE 0 END) as total_entregado
                FROM pedidos_detalle pd
                LEFT JOIN preparaciones_detalle prep_det ON pd.id_pedido = prep_det.id_pedido_cliente
                    AND pd.id_variante = prep_det.id_variante
                WHERE pd.id_pedido = ?
            ''', (detalle_prep['id_pedido_cliente'],))

            pedido_stats = cursor.fetchone()
            if pedido_stats['total_pedido'] == pedido_stats['total_entregado']:
                cursor.execute('''
                    UPDATE pedidos_cliente
                    SET estado = 'entregado'
                    WHERE id_pedido = ?
                ''', (detalle_prep['id_pedido_cliente'],))

        # Actualizar estado de preparación
        cursor.execute('''
            UPDATE preparaciones
            SET estado = 'en_venta'
            WHERE id_preparacion = ?
        ''', (id_preparacion,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Venta registrada exitosamente',
            'id_venta': id_venta,
            'codigo_venta': data['codigo_venta']
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/ventas')
def ventas():
    """Vista de todas las ventas v2"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            v.*,
            va.codigo_producto,
            va.cuero,
            va.color,
            pb.tipo,
            p.dia_venta,
            p.fecha_preparacion
        FROM ventas_v2 v
        JOIN variantes va ON v.id_variante = va.id_variante
        JOIN productos_base pb ON va.codigo_producto = pb.codigo_producto
        JOIN preparaciones p ON v.id_preparacion = p.id_preparacion
        ORDER BY v.fecha_venta DESC, v.hora_venta DESC
        LIMIT 100
    ''')

    ventas = cursor.fetchall()

    conn.close()

    return render_template('ventas.html', ventas=ventas)

# ============================================================================
# MÓDULO: FINALIZAR PREPARACIÓN (Devoluciones)
# ============================================================================

@app.route('/preparaciones/<int:id_preparacion>/finalizar')
def finalizar_preparacion_form(id_preparacion):
    """Formulario para finalizar preparación y procesar devoluciones"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener preparación
    cursor.execute('''
        SELECT p.*, u.nombre as ubicacion_origen
        FROM preparaciones p
        LEFT JOIN ubicaciones u ON p.id_ubicacion_origen = u.id_ubicacion
        WHERE p.id_preparacion = ?
    ''', (id_preparacion,))

    preparacion = cursor.fetchone()

    if not preparacion:
        flash('Preparación no encontrada', 'danger')
        return redirect(url_for('preparaciones'))

    # Obtener detalles con pendientes
    cursor.execute('''
        SELECT
            pd.*,
            v.codigo_producto,
            v.cuero,
            v.color,
            pb.tipo,
            (pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) as pendiente
        FROM preparaciones_detalle pd
        JOIN variantes v ON pd.id_variante = v.id_variante
        JOIN productos_base pb ON v.codigo_producto = pb.codigo_producto
        WHERE pd.id_preparacion = ?
        AND (pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) > 0
    ''', (id_preparacion,))

    pendientes = cursor.fetchall()

    # Obtener ubicaciones para devolución
    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    conn.close()

    return render_template('finalizar_preparacion.html',
                         preparacion=preparacion,
                         pendientes=pendientes,
                         ubicaciones=ubicaciones)

@app.route('/api/preparaciones/<int:id_preparacion>/finalizar', methods=['POST'])
def finalizar_preparacion(id_preparacion):
    """API para finalizar preparación y procesar devoluciones"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # Procesar devoluciones
        if 'devoluciones' in data:
            for dev in data['devoluciones']:
                id_detalle = dev['id_detalle']
                cantidad_devolver = dev['cantidad_pares']
                id_ubicacion_destino = dev['id_ubicacion_destino']
                id_variante = dev['id_variante']

                # Registrar devolución
                cursor.execute('''
                    INSERT INTO devoluciones
                    (id_preparacion, id_detalle_preparacion, fecha_devolucion,
                     cantidad_pares, motivo, id_ubicacion_destino, procesada)
                    VALUES (?, ?, DATE('now'), ?, ?, ?, 1)
                ''', (id_preparacion, id_detalle, cantidad_devolver,
                      dev.get('motivo', 'Mercadería no vendida'), id_ubicacion_destino))

                # Actualizar detalle de preparación
                cursor.execute('''
                    UPDATE preparaciones_detalle
                    SET cantidad_devuelta = cantidad_devuelta + ?
                    WHERE id_detalle = ?
                ''', (cantidad_devolver, id_detalle))

                # Devolver al inventario
                cursor.execute('''
                    SELECT cantidad_pares
                    FROM inventario
                    WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = 'general'
                ''', (id_variante, id_ubicacion_destino))

                inv_existente = cursor.fetchone()

                if inv_existente:
                    cursor.execute('''
                        UPDATE inventario
                        SET cantidad_pares = cantidad_pares + ?
                        WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = 'general'
                    ''', (cantidad_devolver, id_variante, id_ubicacion_destino))
                else:
                    cursor.execute('''
                        INSERT INTO inventario (id_variante, id_ubicacion, tipo_stock, cantidad_pares)
                        VALUES (?, ?, 'general', ?)
                    ''', (id_variante, id_ubicacion_destino, cantidad_devolver))

                # Registrar movimiento
                cursor.execute('''
                    INSERT INTO movimientos_inventario
                    (tipo_movimiento, id_variante, id_ubicacion_destino, cantidad_pares,
                     tipo_stock, id_preparacion, motivo)
                    VALUES ('egreso', ?, ?, ?, 'general', ?, 'Devolución de preparación')
                ''', (id_variante, id_ubicacion_destino, cantidad_devolver, id_preparacion))

        # Marcar preparación como finalizada
        cursor.execute('''
            UPDATE preparaciones
            SET estado = 'finalizada'
            WHERE id_preparacion = ?
        ''', (id_preparacion,))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Preparación finalizada exitosamente'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# MÓDULOS DE V1.2 (Mantenidos para compatibilidad)
# ============================================================================

@app.route('/ubicaciones')
def ubicaciones():
    """Vista de gestión de ubicaciones/almacenes"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ubicaciones ORDER BY nombre')
    ubicaciones = cursor.fetchall()

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

@app.route('/inventario')
def inventario():
    """Vista general del inventario"""
    conn = get_db()
    cursor = conn.cursor()

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

    cursor.execute('SELECT * FROM ubicaciones WHERE activo = 1 ORDER BY nombre')
    ubicaciones = cursor.fetchall()

    conn.close()

    return render_template('inventario.html',
                         inventario=inventario_data,
                         ubicaciones=ubicaciones)

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

        cursor.execute('''
            SELECT id_inventario, cantidad_pares
            FROM inventario
            WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = ?
            AND (id_pedido_cliente IS NULL OR id_pedido_cliente = ?)
        ''', (id_variante, id_ubicacion, tipo_stock, data.get('id_pedido_cliente')))

        inventario_actual = cursor.fetchone()

        if inventario_actual:
            nueva_cantidad = inventario_actual['cantidad_pares'] + cantidad_pares
            cursor.execute('''
                UPDATE inventario
                SET cantidad_pares = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_inventario = ?
            ''', (nueva_cantidad, inventario_actual['id_inventario']))
        else:
            cursor.execute('''
                INSERT INTO inventario
                (id_variante, id_ubicacion, tipo_stock, cantidad_pares, id_pedido_cliente)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_variante, id_ubicacion, tipo_stock, cantidad_pares,
                  data.get('id_pedido_cliente')))

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

        nueva_cantidad_origen = stock_origen['cantidad_pares'] - cantidad_pares
        cursor.execute('''
            UPDATE inventario
            SET cantidad_pares = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id_variante = ? AND id_ubicacion = ? AND tipo_stock = ?
        ''', (nueva_cantidad_origen, id_variante, id_ubicacion_origen, tipo_stock))

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

@app.route('/analisis')
def analisis():
    """Módulo de análisis"""
    return render_template('analisis.html', año_actual=datetime.now().year)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SISTEMA DE GESTIÓN DE CALZADO v1.3")
    print("="*60)
    print("\n⚠️  IMPORTANTE: Ejecuta primero:")
    print("   1. python migracion_v1_2.py")
    print("   2. python migracion_fase_3_4.py")
    print("   si aún no has migrado la base de datos.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
