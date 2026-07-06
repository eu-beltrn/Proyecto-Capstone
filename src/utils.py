import os
import logging
from datetime import datetime

def setup_logging():
    """Configura el sistema de logs para el pipeline ETL, guardando un historial en archivo."""
    # Asegurar que la carpeta de logs exista antes de inicializar el handler
    os.makedirs("logs", exist_ok=True)
    
    log_filename = f"logs/etl_run_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),                      # Muestra en la terminal
            logging.FileHandler(log_filename, mode='a')   # Persiste en archivo físico (append)
        ]
    )
    return logging.getLogger("ETL_Logger")

def init_directories():
    """Asegura que la estructura completa de carpetas del proyecto exista antes de ejecutar."""
    from config import RAW_DIR, PROCESSED_DIR
    directories = [
        RAW_DIR, 
        PROCESSED_DIR, 
        "data/warehouse", 
        "logs", 
        "reports", 
        "docs"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)