from src.utils import setup_logging, init_directories
from src.extract import run_extraction
from src.transform import run_transformation
from src.load import load_to_warehouse

def main():
    # 1. Configuración Inicial de Logs y Directorios
    log = setup_logging()
    init_directories()

    log.info("=====================================================")
    log.info("INICIANDO PIPELINE ETL END-TO-END - SUPABASE (DÍA 3)")
    log.info("=====================================================")
    
    try:
        # FASE 1: Extraer
        raw_data = run_extraction(log)

        # FASE 2: Transformar y Limpiar
        dw_tables = run_transformation(raw_data, log)

        # FASE 3: Cargar en Cloud Warehouse
        load_to_warehouse(dw_tables, log)

        log.info("=====================================================")
        log.info(" ¡PIPELINE ETL CLOUD COMPLETO EJECUTADO CON ÉXITO! ")
        log.info("=====================================================")
        
    except Exception as e:
        log.error(f"¡El Pipeline falló de manera crítica!: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()