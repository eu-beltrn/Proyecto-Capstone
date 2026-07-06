# load.py
import pandas as pd
import sqlite3
import os
from config import ENV, DWH_PATH

def get_connection(log):
    """
    Obtiene la conexión al Data Warehouse dependiendo del entorno.
    Esto permite cambiar de SQLite (Local) a BigQuery/Snowflake (Producción) sin tocar el ETL.
    """
    if ENV == "LOCAL":
        # Asegurar que el directorio del DW local exista
        os.makedirs(os.path.dirname(DWH_PATH), exist_ok=True)
        log.info(f"Conectando al Data Warehouse LOCAL en: {DWH_PATH}")
        return sqlite3.connect(DWH_PATH)
    else:
        # Aquí irá la lógica de producción (Ej: SQLAlchemy para PostgreSQL o google-cloud-bigquery)
        # engine = create_engine(os.getenv("DWH_URI"))
        # return engine.connect()
        log.error("La conexión a PRODUCCIÓN aún no está implementada.")
        raise NotImplementedError("Configurar credenciales de producción.")

def load_table(df, table_name, conn, log, if_exists='replace'):
    """
    Carga un DataFrame individual a una tabla en el Data Warehouse.
    """
    try:
        # En Pandas to_sql, if_exists puede ser 'fail', 'replace', o 'append'
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        log.info(f"  -> Tabla '{table_name}' cargada exitosamente. ({len(df)} filas, modo: {if_exists})")
    except Exception as e:
        log.error(f"  -> Error crítico al cargar la tabla '{table_name}': {str(e)}")
        raise

def load_to_warehouse(dw_tables, log):
    """
    Orquesta la carga de todas las tablas del modelo estrella al Data Warehouse.
    Recibe el diccionario 'dw_tables' generado por transform.py.
    """
    log.info("Iniciando fase de CARGA (LOAD) al Data Warehouse...")
    
    conn = get_connection(log)
    
    try:
        # 1. Cargar Dimensiones
        # Las dimensiones generalmente usan 'replace' en entornos de prueba.
        # En producción, se usaría lógica de tipo SCD (Slowly Changing Dimensions) o un 'MERGE'.
        dimensiones = [
            "DimCliente", 
            "DimProducto", 
            "DimCampana", 
            "DimTiempo", 
            "DimInventarioActual", 
            "DimMovimientosInventario"
        ]
        
        for dim in dimensiones:
            if dim in dw_tables:
                load_table(dw_tables[dim], dim, conn, log, if_exists='replace')
        
        # 2. Cargar Tablas de Hechos
        # Las tablas de hechos crecen con el tiempo. En producción, el modo suele ser 'append'
        # o un UPSERT usando fechas para no duplicar.
        # Para el alcance de este proyecto y las pruebas locales, usaremos 'replace' para 
        # que el equipo pueda correr el script múltiples veces sin duplicar los 100 registros.
        hechos = ["FactVentas"]
        
        for hecho in hechos:
            if hecho in dw_tables:
                # Cambiar a 'append' cuando el pipeline pase a incremental
                load_table(dw_tables[hecho], hecho, conn, log, if_exists='replace')
                
        log.info("==============================================")
        log.info(" ¡FASE DE CARGA (LOAD) COMPLETADA CON ÉXITO! ")
        log.info("==============================================")
        
    finally:
        # Siempre asegurar que la conexión se cierre, incluso si hay un error
        conn.close()
        log.info("Conexión al Data Warehouse cerrada.")