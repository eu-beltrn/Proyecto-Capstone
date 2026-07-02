import pandas as pd
import numpy as np
import sqlite3
import json
import os

# Asegurar carpeta para las fuentes de datos
os.makedirs("data/raw/", exist_ok=True)

print("🚀 Iniciando la generación de datos simulados para DataCommerce GT...")

# ==========================================
# 1. PRODUCTOS (Excel) - con errores
# ==========================================
productos_data = {
    "ID_Producto": [101, 102, 103, 104, 105, 106, 107, 107, 109, 110], # 107 duplicado
    "Nombre": [" Laptop ASUS ZenBook", "Smartphone Samsung S24", "Teclado Mecánico RGB ", 
               "Monitor Gamer 27'", "Mouse Inalámbrico Logi", "Audífonos Sony WH", 
               "Impresora HP DeskJet", "Impresora HP DeskJet", "Tablet Lenovo Tab", "Smartwatch Xiaomi"],
    "Categoria": ["TECNOLOGÍA", "tecnologia", "Accesorios", "Monitores", "Accesorios", 
                  "Audio", "IMPRESIÓN", "IMPRESIÓN", "TECNOLOGÍA", "Gadgets"], # Inconsistencia de caja
    "Precio_USD": [1200.50, 899.99, 45.00, np.nan, 25.00, 199.99, 85.00, 85.00, 150.00, np.nan] # Nulos intencionales
}
df_productos = pd.DataFrame(productos_data)
df_productos.to_excel("data/raw/productos.xlsx", index=False)
print("✅ Archivo 'productos.xlsx' generado.")

# ==========================================
# 2. CLIENTES (JSON) - con errores
# ==========================================
clientes_data = [
    {"id_cliente": 1, "nombre": "JUAN PEREZ", "email": "juan.perez@mail.com", "ciudad": "Guatemala"},
    {"id_cliente": 2, "nombre": "maria lopez", "email": "MARIA.LOPEZ@MAIL.COM", "ciudad": "Mixco"}, # Mayúsculas/Minúsculas
    {"id_cliente": 3, "nombre": "Carlos Gómez", "email": "carlos.gomez@mail.com", "ciudad": ""}, # Ciudad vacía
    {"id_cliente": 4, "nombre": "Ana Martínez", "email": "ana.martinez@mail.com", "ciudad": "Villa Nueva"},
    {"id_cliente": 5, "nombre": "Luis Fernando ", "email": "luis.fernando@mail", "ciudad": "Guatemala"}, # Email inválido
    {"id_cliente": 1, "nombre": "JUAN PEREZ", "email": "juan.perez@mail.com", "ciudad": "Guatemala"} # Cliente duplicado
]
with open("data/raw/clientes.json", "w", encoding="utf-8") as f:
    json.dump(clientes_data, f, indent=4, ensure_ascii=False)
print("✅ Archivo 'clientes.json' generado.")

# ==========================================
# 3. INVENTARIO (SQLite)
# ==========================================
conn = sqlite3.connect("data/raw/inventario.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS stock_diario")
cursor.execute("""
    CREATE TABLE stock_diario (
        id_producto INTEGER,
        stock_disponible INTEGER,
        bodega TEXT,
        fecha_actualizacion TEXT
    )
""")
inventario_data = [
    (101, 15, "Bodega Central", "2026-07-01"),
    (102, 0, "Bodega Central", "2026-07-01"), # Sin stock
    (103, 50, "Bodega Auxiliar", "01/07/2026"), # Formato de fecha distinto
    (104, 8, "Bodega Central", "2026-07-01"),
    (105, -5, "Bodega Auxiliar", "2026-07-01"), # Stock negativo (Error)
    (106, 22, "Bodega Central", "2026-07-01")
]
cursor.executemany("INSERT INTO stock_diario VALUES (?, ?, ?, ?)", inventario_data)
conn.commit()
conn.close()
print("✅ Base de datos 'inventario.db' generada.")

# ==========================================
# 4. CAMPAÑAS DE MARKETING (Simulación API REST)
# ==========================================
# Como el requerimiento pide una API REST simulada, creamos una función
# que simula la respuesta de un request de biblioteca 'requests'
def simular_api_marketing():
    campanas = [
        {"id_campana": "C-01", "nombre_campana": "Cyber Monday Tech", "canal": "Facebook Ads", "presupuesto": 1500.00},
        {"id_campana": "C-02", "nombre_campana": "Lanzamiento S24", "canal": "Google Ads", "presupuesto": 3000.00},
        {"id_campana": "C-03", "nombre_campana": "Descuentos Oficina", "canal": "Instagram", "presupuesto": 800.00}
    ]
    return json.dumps(campanas)

with open("data/raw/api_campanas.json", "w", encoding="utf-8") as f:
    f.write(simular_api_marketing())
print("✅ Mock de API REST guardado en 'api_campanas.json'.")

# ==========================================
# 5. VENTAS (CSV) - con errores e integración
# ==========================================
# Generamos una pequeña matriz de transacciones cruzadas
ventas_data = {
    "ID_Venta": [1001, 1002, 1003, 1004, 1005, 1006, 1006, 1008, 1009], # 1006 duplicado
    "Fecha": ["2026-07-01", "2026/07/01", "01-07-2026", "2026-07-01", "2026-07-01", "2026-07-01", "2026-07-01", "2026-07-01", "2026-07-01"], # Fechas inconsistentes
    "ID_Cliente": [1, 2, 3, 4, 5, 1, 1, 99, 2], # ID 99 no existe en clientes.json (Error de integridad)
    "ID_Producto": [101, 102, 103, 104, 105, 106, 106, 101, 999], # ID 999 no existe en productos (Error de integridad)
    "Cantidad": [1, 2, -1, 1, 3, 1, 1, 1, 5], # Cantidad negativa intencional
    "ID_Campana": ["C-01", "C-01", "C-02", "C-03", np.nan, "C-02", "C-02", np.nan, np.nan] # Ventas orgánicas sin campaña (nulos válidos)
}
df_ventas = pd.DataFrame(ventas_data)
df_ventas.to_csv("data/raw/ventas.csv", index=False)
print("✅ Archivo 'ventas.csv' generado.")
print("\n🎉 ¡Todo listo! El entorno simulado para Nicole ha sido construido con éxito.")