import pandas as pd
import sqlite3
import json
import os

def explorar_fuente(nombre, df):
    """Imprime un diagnóstico rápido de calidad sobre cualquier DataFrame."""
    print(f"\n" + "="*50)
    print(f"EXPLORANDO FUENTE: {nombre.upper()}")
    print(f"="*50)
    
    # 1. Dimensiones basicas
    print(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
    
    # 2. Tipos de datos y Nulos
    print("\nColumnas, Tipos y Valores Nulos:")
    info_df = pd.DataFrame({
        'Tipo': df.dtypes,
        'Nulos (NaN)': df.isnull().sum(),
        'Vacíos ("")': (df == "").sum() if df.dtypes.astype(str).str.contains('object').any() else 0
    })
    print(info_df)
    
    # 3. Muestra de Datos
    print("\nPrimeros 3 registros:")
    print(df.head(3))
    
    # 4. Alertas de Calidad Básicas
    print("\nAlertas de Calidad:")
    # Verificar duplicados en columnas ID típicas
    id_cols = [c for c in df.columns if 'id' in c.lower() or 'venta' in c.lower() or 'sk' in c.lower()]
    for col in id_cols:
        dups = df.duplicated(subset=[col]).sum()
        if dups > 0:
            print(f"  -> ¡Alerta! Columna '{col}' tiene {dups} valores duplicados.")
            
    # Verificar si hay números negativos donde no debería
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    for col in num_cols:
        if (df[col] < 0).any():
            print(f"  -> ¡Alerta! Columna numérica '{col}' contiene valores negativos.")

def main():
    print("Iniciando auto-descubrimiento de datos...")
    
    # Adaptar nombres si usas las versiones '_2' o las renombradas
    path_ventas = "data/raw/ventas_2.csv" if os.path.exists("data/raw/ventas_2.csv") else "data/raw/ventas.csv"
    path_productos = "data/raw/productos_2.xlsx" if os.path.exists("data/raw/productos_2.xlsx") else "data/raw/productos.xlsx"
    path_clientes = "data/raw/clientes_2.json" if os.path.exists("data/raw/clientes_2.json") else "data/raw/clientes.json"
    path_api = "data/raw/api_marketing_response.json"
    path_db = "data/raw/inventario_2.db" if os.path.exists("data/raw/inventario_2.db") else "data/raw/inventario.db"

    # --- 1. Ventas ---
    if os.path.exists(path_ventas):
        explorar_fuente("Ventas CSV", pd.read_csv(path_ventas))
        
    # --- 2. Productos ---
    if os.path.exists(path_productos):
        # Soporte por si Nicole te lo pasó en formato .csv por error
        df_prod = pd.read_csv(path_productos) if path_productos.endswith('.csv') else pd.read_excel(path_productos)
        explorar_fuente("Productos Excel", df_prod)
        
    # --- 3. Clientes ---
    if os.path.exists(path_clientes):
        explorar_fuente("Clientes JSON", pd.read_json(path_clientes))
        
    # --- 4. API Marketing ---
    if os.path.exists(path_api):
        with open(path_api, 'r', encoding='utf-8') as f:
            raw_api = json.load(f)
        # Aquí descubres si viene envuelto en 'campaigns' o no
        if 'campaigns' in raw_api:
            df_api = pd.DataFrame(raw_api['campaigns'])
        else:
            df_api = pd.DataFrame(raw_api)
        explorar_fuente("API Marketing JSON", df_api)
        
    # --- 5. Base de Datos de Inventario ---
    if os.path.exists(path_db):
        conn = sqlite3.connect(path_db)
        # Descubrir tablas e inspeccionarlas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [r[0] for r in cursor.fetchall()]
        
        for tabla in tablas:
            df_table = pd.read_sql_query(f"SELECT * FROM [{tabla}]", conn)
            explorar_fuente(f"SQLite - Tabla: {tabla}", df_table)
        conn.close()

if __name__ == "__main__":
    main()