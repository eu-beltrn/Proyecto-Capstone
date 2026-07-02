from utils import setup_logging, init_directories
from extract import run_extraction
from transform import run_transformation
from load import load_to_warehouse

def main():
    # 1. Configuración Inicial de Logs y Directorios
    log = setup_logging()
    init_directories()
    
    log.info("==============================================")
    log.info("INICIANDO PIPELINE ETL DE LA EMPRESA (PROTOTIPO)")
    log.info("==============================================")
    
    try:
        # 2. Fase de Extracción
        raw_data = run_extraction(log)
        
        # 3. Fase de Transformación y Limpieza
        dw_tables = run_transformation(raw_data, log)
        
        # 4. Fase de Carga al DW final
        warehouse_db = "data/warehouse/dw_ventas.db"
        load_to_warehouse(dw_tables, warehouse_db, log)
        
        log.info("==============================================")
        log.info("   ¡PIPELINE EJECUTADO CON ÉXITO SIN ERRORES! ")
        log.info("==============================================")
        
    except Exception as e:
        log.error(f"¡El Pipeline falló de manera crítica!: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()