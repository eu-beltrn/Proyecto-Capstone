import sqlite3
import os

def load_to_warehouse(dw_tables, db_path, log):
    """Carga los DataFrames transformados en la base de datos SQLite del Data Warehouse."""
    log.info(f"Iniciando fase de CARGA en el Data Warehouse: {db_path}...")
    
    # Remover DW viejo si existe para permitir ejecuciones limpias de prueba
    if os.path.exists(db_path):
        os.remove(db_path)
        log.info("Data Warehouse previo eliminado para sobreescritura limpia.")
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Habilitar soporte de llaves foráneas en SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Crear tablas explícitamente con tipos de datos e integridad relacional
    log.info("Creando esquemas DDL del Modelo Estrella...")
    
    cursor.execute("""
    CREATE TABLE DimCliente (
        SK_Cliente INTEGER PRIMARY KEY,
        Nombre TEXT,
        Email TEXT,
        Ciudad TEXT
    );
    """)
    
    cursor.execute("""
    CREATE TABLE DimProducto (
        SK_Producto INTEGER PRIMARY KEY,
        Nombre_Producto TEXT,
        Categoria TEXT,
        Precio_Unitario REAL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE DimCampana (
        SK_Campana TEXT PRIMARY KEY,
        Nombre_Campana TEXT,
        Canal TEXT,
        Presupuesto REAL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE DimTiempo (
        Fecha TEXT PRIMARY KEY,
        Anio INTEGER,
        Mes INTEGER,
        Dia INTEGER,
        Trimestre INTEGER
    );
    """)
    
    cursor.execute("""
    CREATE TABLE FactVentas (
        ID_Venta INTEGER PRIMARY KEY,
        Fecha_Key TEXT,
        FK_Cliente INTEGER,
        FK_Producto INTEGER,
        FK_Campana TEXT,
        Cantidad_Unidades INTEGER,
        Total_Ingreso REAL,
        FOREIGN KEY (Fecha_Key) REFERENCES DimTiempo(Fecha),
        FOREIGN KEY (FK_Cliente) REFERENCES DimCliente(SK_Cliente),
        FOREIGN KEY (FK_Producto) REFERENCES DimProducto(SK_Producto),
        FOREIGN KEY (FK_Campana) REFERENCES DimCampana(SK_Campana)
    );
    """)
    
    conn.commit()
    
    # Insertar los datos usando el método rápido to_sql orientándolo a la estructura
    for table_name, df in dw_tables.items():
        # Usamos append ya que las estructuras de las tablas ya fueron creadas arriba
        df.to_sql(table_name, conn, if_exists='append', index=False)
        log.info(f"   -> Tabla '{table_name}' cargada con éxito. ({df.shape[0]} registros)")
        
    conn.close()
    log.info("¡Carga del Data Warehouse completada exitosamente!")