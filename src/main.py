# main.py
from src.utils import setup_logging, init_directories
from src.extract import run_extraction
from src.transform import run_transformation
from src.load import load_to_warehouse

def main():
    log = setup_logging()
    init_directories()
    
    log.info("INICIANDO PIPELINE ETL")
    
    try:
        raw_data = run_extraction(log)
        dw_tables = run_transformation(raw_data, log)
        
        # Ya no necesitamos pasarle ninguna variable extra
        load_to_warehouse(dw_tables, log)
        
        log.info("¡PROCESO COMPLETADO EXITOSAMENTE!")
    except Exception as e:
        log.error(f"Fallo crítico: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()