from src.utils import setup_logging, init_directories
from src.extract import run_extraction
from src.transform import run_transformation
# Comentado por hoy Día 2
# from load import load_to_warehouse
# main.py (Actualización de la sección final)
from src.load import load_to_warehouse

def main():
    # 1. Configuración Inicial de Logs y Directorios
    log = setup_logging()
    init_directories()

    log.info("INICIANDO PIPELINE ETL END-TO-END")
    
    log.info("==============================================")
    log.info("INICIANDO PIPELINE ETL - FASE DE CALIDAD (DÍA 2)")
    log.info("==============================================")
    
    try:
        # 1. Extraer (Nicole)
        raw_data = run_extraction(log)

        # 2. Transformar (Eunice)
        dw_tables = run_transformation(raw_data, log)

        # 3. Cargar (Jonathan)
        load_to_warehouse(dw_tables, log)

        log.info("¡PIPELINE EJECUTADO CORRECTAMENTE!")
        
    except Exception as e:
        log.error(f"¡El Pipeline falló de manera crítica!: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()