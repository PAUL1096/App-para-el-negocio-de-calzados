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
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
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
