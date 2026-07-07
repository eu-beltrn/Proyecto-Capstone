import os
from dotenv import load_dotenv

# Carga las variables del archivo .env que está en la raíz
load_dotenv()

# Variables Generales y Locales
ENV = os.getenv("ENV", "LOCAL")
RAW_DIR = os.getenv("DATA_RAW_DIR", "data/raw")
PROCESSED_DIR = os.getenv("DATA_PROCESSED_DIR", "data/processed")
DB_PATH = os.getenv("DB_PATH", "data/raw/inventario.db")
DWH_PATH = os.getenv("DWH_PATH", "data/warehouse/dw_ventas.db")  # <-- Esta es la variable que faltaba

# Variables de Google BigQuery
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET = os.getenv("BQ_DATASET")

# Cargar la credencial JSON en el entorno de Python
if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# En config.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/warehouse/dw_ventas.db")