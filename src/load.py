from sqlalchemy import create_engine
from src.config import DATABASE_URL

def load_to_warehouse(dw_tables, log):
    """
    Carga el modelo estrella y las tablas de inventario directamente en la nube de Supabase (PostgreSQL).
    
    :param dw_tables: Diccionario de DataFrames limpios y modelados.
    :param log: Instancia del logger para la auditoría de carga.
    """
    log.info("Iniciando fase de CARGA (LOAD) en la nube de Supabase...")
    
    # Crear el motor de conexión a PostgreSQL
    engine = None
    try:
        engine = create_engine(DATABASE_URL)
        log.info("-> Conexión establecida exitosamente con el servidor de Supabase.")
        
        # Iterar sobre cada DataFrame e inyectarlo en Supabase
        for table_name, df in dw_tables.items():
            # Forzar el nombre de la tabla a minúsculas por convención de PostgreSQL
            table_name_pg = table_name.lower()
            
            log.info(f"   Inyectando tabla '{table_name_pg}' ({df.shape[0]} registros) en Supabase...")
            
            # pandas se encarga de convertir tipos de datos y estructurar la tabla en PostgreSQL
            df.to_sql(
                name=table_name_pg,
                con=engine,
                if_exists='replace',  # Recrea la tabla limpia en cada ejecución del pipeline
                index=False
            )
            
        log.info("¡Todas las tablas del modelo estrella han sido persistidas en Supabase con éxito!")
        
    except Exception as e:
        log.error(f"Error crítico durante la carga en Supabase: {str(e)}")
        raise e
        
    finally:
        if engine:
            engine.dispose()
            log.info("-> Conexión a Supabase cerrada y liberada con seguridad.")