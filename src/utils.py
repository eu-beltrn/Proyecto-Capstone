import os
import logging

def setup_logging():
    """Configura el sistema de logs para el pipeline ETL."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ETL_Logger")

def init_directories():
    """Asegura que la estructura de carpetas data/ exista antes de ejecutar."""
    directories = [
        "data/raw",
        "data/processed",
        "data/warehouse"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)