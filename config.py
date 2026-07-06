import os
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno
ENV = os.getenv("ENV", "LOCAL")
RAW_DIR = os.getenv("DATA_RAW_DIR", "data/raw")
PROCESSED_DIR = os.getenv("DATA_PROCESSED_DIR", "data/processed")
DB_PATH = os.getenv("DB_PATH", "data/raw/inventario.db")
DWH_PATH = os.getenv("DWH_PATH", "data/warehouse/dw_ventas.db")