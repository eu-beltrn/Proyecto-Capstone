import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "LOCAL")
RAW_DIR = os.getenv("DATA_RAW_DIR", "data/raw")
PROCESSED_DIR = os.getenv("DATA_PROCESSED_DIR", "data/processed")
DB_PATH = os.getenv("DB_PATH", "data/raw/inventario.db")

# Configuración de Supabase
DB_HOST = os.getenv("SUPABASE_HOST")
DB_PORT = os.getenv("SUPABASE_PORT", "5432")
DB_NAME = os.getenv("SUPABASE_DB", "postgres")
DB_USER = os.getenv("SUPABASE_USER", "postgres")
DB_PASS = os.getenv("SUPABASE_PASSWORD")

# Construcción de la URI de conexión para SQLAlchemy
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"