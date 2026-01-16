"""
Test para verificar la lógica de extracción de números de códigos de venta
"""

# Código de venta regular: V20251226-001
codigo_regular = "V20251226-001"
print("="*60)
print("CÓDIGO REGULAR:")
print(f"Código: {codigo_regular}")
print(f"Longitud: {len(codigo_regular)}")
print(f"Posiciones: {', '.join([f'{i+1}:{c}' for i, c in enumerate(codigo_regular)])}")
print(f"SUBSTR desde 11: '{codigo_regular[10:]}'")  # Python usa índice 0, SQL usa 1
print(f"Número extraído: {codigo_regular[10:] if codigo_regular[10:].isdigit() else 'ERROR'}")

# Código de venta directa: VD20251226-001
codigo_directo = "VD20251226-001"
print("\n" + "="*60)
print("CÓDIGO VENTA DIRECTA:")
print(f"Código: {codigo_directo}")
print(f"Longitud: {len(codigo_directo)}")
print(f"Posiciones: {', '.join([f'{i+1}:{c}' for i, c in enumerate(codigo_directo)])}")
print(f"SUBSTR desde 11: '{codigo_directo[10:]}'")  # Esto daría "-001"
print(f"SUBSTR desde 12: '{codigo_directo[11:]}'")  # Esto daría "001"
print(f"Número correcto extraído: {codigo_directo[11:]}")

print("\n" + "="*60)
print("CONCLUSIÓN:")
print("  V20251226-001  → SUBSTR(codigo_venta, 11) = '001' ✓")
print("  VD20251226-001 → SUBSTR(codigo_venta, 11) = '-001' ✗")
print("  VD20251226-001 → SUBSTR(codigo_venta, 12) = '001' ✓")
print("="*60)
