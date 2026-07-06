import os
import logging
from datetime import datetime
# CORRECCIÓN AQUÍ: Importar desde el paquete src para que main.py lo resuelva bien
from src.config import RAW_DIR, PROCESSED_DIR

def setup_logging():
    """Configura el sistema de logs para el pipeline ETL, guardando un historial en archivo."""
    os.makedirs("logs", exist_ok=True)
    
    log_filename = f"logs/etl_run_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_filename, mode='a')
        ]
    )
    return logging.getLogger("ETL_Logger")

def init_directories():
    """Asegura que la estructura completa de carpetas del proyecto exista antes de ejecutar."""
    # Nota: Si ya importaste RAW_DIR y PROCESSED_DIR arriba, puedes usar las variables directamente aquí
    directories = [
        RAW_DIR,
        PROCESSED_DIR,
        "data/warehouse",
        "logs"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)