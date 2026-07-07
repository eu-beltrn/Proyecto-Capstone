import pandas as pd
import json
import sqlite3
import sys
import os

# Asegura que Python pueda ver la carpeta raíz donde está config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# IMPORTACIÓN CORREGIDA: Traemos las rutas que usa run_extraction
from config import RAW_DIR, DB_PATH 

def extract_csv(file_path):
    """Extrae datos de ventas desde un archivo CSV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo de ventas: {file_path}")
    return pd.read_csv(file_path)

def extract_excel(file_path):
    """Extrae datos de productos."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo de productos: {file_path}")
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    return pd.read_excel(file_path)

def extract_json(file_path):
    """Extrae datos de clientes desde un archivo JSON."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo de clientes: {file_path}")
    return pd.read_json(file_path)

def extract_sqlite(db_path, log, table_name="stock_diario"):
    """Extrae datos de inventario desde SQLite."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"No se encontró la DB de inventario: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    available_tables = [row[0] for row in cursor.fetchall()]
    
    if not available_tables:
        conn.close()
        raise ValueError(f"El archivo SQLite en {db_path} no contiene ninguna tabla.")
    
    if table_name not in available_tables:
        selected_table = available_tables[0]
        log.warning(f"La tabla '{table_name}' no existe. Extrayendo de '{selected_table}'.")
    else:
        selected_table = table_name

    query = f"SELECT * FROM [{selected_table}]"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def extract_api_mock(file_path):
    """Simula la extracción desde una API REST."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el mock de la API: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def run_extraction(log):
    log.info("Iniciando fase de EXTRACCIÓN masiva...")
    
    # En src/extract.py, dentro de run_extraction:
    data = {
        "ventas": extract_csv(os.path.join(RAW_DIR, "ventas_masivo.csv")),
        "productos": extract_excel(os.path.join(RAW_DIR, "productos_masivo.xlsx")),
        "clientes": extract_json(os.path.join(RAW_DIR, "clientes_masivo.json")),
        "inventario_actual": extract_sqlite(os.path.join(RAW_DIR, "inventario_masivo.db"), log, "inventario_actual"),
        # "movimientos_inventario": extract_sqlite(..., "movimientos_inventario"), # <-- Comenta esto si el archivo ya no lo contiene
        "campanas": extract_api_mock(os.path.join(RAW_DIR, "api_marketing_response_masivo.json"))
    }
    return data