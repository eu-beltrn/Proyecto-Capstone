import pandas as pd
import json
import sqlite3
import os
# CORRECCIÓN: Importamos correctamente desde el paquete de la carpeta src
from src.config import RAW_DIR, DB_PATH

def extract_csv(file_path):
    """Extrae datos de ventas desde un archivo CSV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo de ventas: {file_path}")
    return pd.read_csv(file_path)

def extract_excel(file_path):
    """Extrae datos de productos (soporta tanto .xlsx como .csv de respaldo)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo de productos: {file_path}")
    # Si viene como CSV debido a la conversión, usamos read_csv, sino read_excel
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    return pd.read_excel(file_path)

def extract_json(file_path):
    """Extrae datos de clientes desde un archivo JSON."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo de clientes: {file_path}")
    return pd.read_json(file_path)

def extract_sqlite(db_path, log, table_name="stock_diario"):
    """Extrae datos de inventario desde SQLite de forma dinámica si el nombre cambia."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"No se encontró la DB de inventario: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Listar todas las tablas disponibles
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    available_tables = [row[0] for row in cursor.fetchall()]
    
    if not available_tables:
        conn.close()
        raise ValueError(f"El archivo SQLite en {db_path} no contiene ninguna tabla.")
    
    # Si 'stock_diario' no está, tomamos la primera tabla que exista de forma inteligente
    if table_name not in available_tables:
        selected_table = available_tables[0]
        log.warning(f"La tabla esperada '{table_name}' no existe. Extrayendo dinámicamente de '{selected_table}'.")
    else:
        selected_table = table_name

    query = f"SELECT * FROM [{selected_table}]"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def extract_api_mock(file_path):
    """Simula la extracción desde una API REST leyendo un archivo JSON de campañas."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el mock de la API de campañas: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def run_extraction(log):
    """Ejecuta todo el bloque de extracción dinámicamente."""
    log.info("Iniciando fase de EXTRACCIÓN...")
    
    # AJUSTE: Cambiar 'Sheet1.csv' por 'Sheet.csv' para coincidir con el archivo real
    prod_path = os.path.join(RAW_DIR, "productos.xlsx - Sheet.csv")
    if not os.path.exists(prod_path):
        prod_path = os.path.join(RAW_DIR, "productos.xlsx")

    data = {
        "ventas": extract_csv(os.path.join(RAW_DIR, "ventas.csv")),
        "productos": extract_excel(prod_path),
        "clientes": extract_json(os.path.join(RAW_DIR, "clientes.json")),
        "inventario_actual": extract_sqlite(DB_PATH, log, "inventario_actual"),
        "movimientos_inventario": extract_sqlite(DB_PATH, log, "movimientos_inventario"),
        "campanas": extract_api_mock(os.path.join(RAW_DIR, "api_marketing_response.json"))
    }
    
    for key, df in data.items():
        log.info(f"-> Extraído con éxito: {key} ({df.shape[0]} registros originales)")
        
    return data