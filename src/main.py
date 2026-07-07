from utils import setup_logging, init_directories
from extract import run_extraction
from transform import run_transformation
# Comentado por hoy Día 2
# from load import load_to_warehouse

def main():
    # 1. Configuración Inicial de Logs y Directorios
    log = setup_logging()
    init_directories()
    
    log.info("==============================================")
    log.info("INICIANDO PIPELINE ETL - FASE DE CALIDAD (DÍA 2)")
    log.info("==============================================")
    
    try:
        # 2. Fase de Extracción
        raw_data = run_extraction(log)
        
        # 3. Fase de Transformación y Limpieza
        dw_tables = run_transformation(raw_data, log)
        
        # 4. Fase de Carga al DW final (POSTERGADO PARA EL DÍA 3)
        log.info("Fase de Carga omitida por diseño del cronograma (Día 2).")
        # warehouse_db = "data/warehouse/dw_ventas.db"
        load_to_warehouse(dw_tables, warehouse_db, log)
        
        log.info("==============================================")
        log.info(" ¡ETL DÍA 2: EXTRACCIÓN Y CALIDAD COMPLETADAS! ")
        log.info("==============================================")
        
    except Exception as e:
        log.error(f"¡El Pipeline falló de manera crítica!: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()