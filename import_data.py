"""
Script para importar datos desde el archivo Excel de simulación
"""

import pandas as pd
import sqlite3
from datetime import datetime

def importar_datos_excel(archivo_excel, db_name='ventas_calzado.db'):
    """
    Importa datos desde el archivo Excel a la base de datos SQLite
    """
    print("Iniciando importación de datos...")
    
    # Leer el archivo Excel
    df_productos = pd.read_excel(archivo_excel, sheet_name='productos')
    df_ventas = pd.read_excel(archivo_excel, sheet_name='ventas')
    df_logistica = pd.read_excel(archivo_excel, sheet_name='logistica')
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Importar productos
    print(f"\nImportando {len(df_productos)} productos...")
    for _, row in df_productos.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO productos 
            (codigo_calzado, tipo, cuero, color, serie_tallas, costo_unitario, precio_sugerido, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['codigo_calzado'],
            row['tipo'],
            row['cuero'],
            row['color'],
            row['serie_tallas'],
            row['costo_unitario'],
            row['precio_sugerido'],
            row['observaciones']
        ))
    print(f"✓ {len(df_productos)} productos importados")
    
    # Procesar y importar ventas
    print(f"\nImportando {len(df_ventas)} ventas...")
    df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'], format='%d/%m/%Y')
    df_ventas['año'] = df_ventas['fecha'].dt.year
    df_ventas['semana'] = df_ventas['fecha'].dt.isocalendar().week
    df_ventas['dia_semana'] = df_ventas['fecha'].dt.day_name()
    
    for _, row in df_ventas.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO ventas 
            (id_venta, fecha, cliente, destino, codigo_calzado, cuero, color, calidad,
             precio_unitario, pares, total_venta, estado_pago, metodo_pago, comentario,
             año, semana, dia_semana)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['id_venta'],
            row['fecha'].strftime('%Y-%m-%d'),
            row['cliente'],
            row['destino'],
            row['codigo_calzado'],
            row['cuero'],
            row['color'],
            row['calidad'],
            row['precio_unitario'],
            row['pares'],
            row['total_venta'],
            row['estado_pago'],
            row['metodo_pago'],
            row['comentario'] if pd.notna(row['comentario']) else '',
            row['año'],
            row['semana'],
            row['dia_semana']
        ))
    print(f"✓ {len(df_ventas)} ventas importadas")
    
    # Procesar y importar logística
    print(f"\nImportando {len(df_logistica)} registros de logística...")
    df_logistica['fecha_envio'] = pd.to_datetime(df_logistica['fecha_envio'], format='%d/%m/%Y')
    
    for _, row in df_logistica.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO logistica 
            (id_envio, id_venta, costo_envio, destino, agencia, fecha_envio, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['id_envio'],
            row['id_venta'],
            row['costo_envio'],
            row['destino'],
            row['agencia'],
            row['fecha_envio'].strftime('%Y-%m-%d'),
            row['observaciones'] if pd.notna(row['observaciones']) else ''
        ))
    print(f"✓ {len(df_logistica)} registros de logística importados")
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("\n✓ ¡Importación completada exitosamente!")
    print("\nResumen:")
    print(f"  - Productos: {len(df_productos)}")
    print(f"  - Ventas: {len(df_ventas)}")
    print(f"  - Logística: {len(df_logistica)}")

if __name__ == '__main__':
    # Ejecutar importación
    archivo = '/mnt/user-data/uploads/datos_simulados_calzado.xlsx'
    importar_datos_excel(archivo)
