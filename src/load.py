# src/load.py
import pandas as pd
import pandas_gbq  # <--- IMPORTANTE: Importar esto registra el método to_gbq
import sys
import os
from google.oauth2 import service_account

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import GCP_PROJECT_ID, BQ_DATASET

def load_to_warehouse(dw_tables, log):
    log.info("Iniciando fase de CARGA hacia BigQuery...")
    
    key_path = "gcp_key.json"
    credentials = service_account.Credentials.from_service_account_file(key_path)
    
    try:
        for table_name, df in dw_tables.items():
            destination_table = f"{BQ_DATASET}.{table_name}"
            log.info(f"   Inyectando tabla '{destination_table}' ({df.shape[0]} registros)...")
            
            # Usamos pandas_gbq.to_gbq directamente como función, es más seguro
            pandas_gbq.to_gbq(
                df, 
                destination_table=destination_table, 
                project_id=GCP_PROJECT_ID, 
                credentials=credentials, 
                if_exists='replace'
            )
            
        log.info("¡Todas las tablas persistidas en BigQuery con éxito!")
            
    except Exception as e:
        log.error(f"Error crítico durante la carga: {str(e)}")
        raise e