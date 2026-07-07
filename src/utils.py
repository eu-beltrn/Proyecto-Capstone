import logging
from datetime import datetime

# Corrección en src/utils.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import RAW_DIR, PROCESSED_DIR

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