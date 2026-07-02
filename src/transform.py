import pandas as pd
import numpy as np

def clean_clientes(df):
    """Limpia la fuente de clientes."""
    df = df.copy()
    # Eliminar duplicados exactos por id_cliente
    df = df.drop_duplicates(subset=['id_cliente'], keep='first')
    # Limpieza de texto
    df['nombre'] = df['nombre'].str.strip().str.title()
    df['email'] = df['email'].str.strip().str.lower()
    df['ciudad'] = df['ciudad'].str.strip().replace('', 'No Especificada').fillna('No Especificada')
    return df

def clean_productos(df):
    """Limpia la fuente de productos."""
    df = df.copy()
    # Estandarizar nombres de columnas si vienen con espacios
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates(subset=['ID_Producto'], keep='first')
    df['Nombre'] = df['Nombre'].str.strip()
    df['Categoria'] = df['Categoria'].str.strip().str.upper()
    # Tratar precios vacíos: Imputar con la mediana o 0 para evitar romper el pipeline
    df['Precio_USD'] = pd.to_numeric(df['Precio_USD'], errors='coerce').fillna(0.0)
    return df

def clean_inventario(df):
    """Limpia la fuente de inventario."""
    df = df.copy()
    df['bodega'] = df['bodega'].str.strip()
    # Estandarizar fechas a formato YYYY-MM-DD
    df['fecha_actualizacion'] = pd.to_datetime(df['fecha_actualizacion'], errors='coerce').dt.strftime('%Y-%m-%d')
    return df

def clean_campanas(df):
    """Limpia la fuente de campañas."""
    df = df.copy()
    # Asegurar que las llaves e IDs estén estandarizados
    if 'id' in df.columns:
        df = df.rename(columns={'id': 'id_campana'})
    df['nombre_campana'] = df['nombre_campana'].str.strip()
    df['canal'] = df['canal'].str.strip()
    df['presupuesto'] = pd.to_numeric(df['presupuesto'], errors='coerce').fillna(0.0)
    return df

def clean_ventas(df, df_clientes, df_productos):
    """Limpia la tabla de hechos tentativa de ventas mediante validaciones cruzadas."""
    df = df.copy()
    df = df.drop_duplicates(subset=['ID_Venta'], keep='first')
    
    # Estandarizar fechas en múltiples formatos
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Filtrar cantidades aberrantes (ej. negativas) o corregirlas con valor absoluto
    df['Cantidad'] = df['Cantidad'].apply(lambda x: abs(x) if x < 0 else x)
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(1).astype(int)
    
    # Integridad Referencial Básica frente a Maestros
    # Si el cliente o producto no existe en los maestros limpios, los marcamos como 'Inexistente' o ID genérico 999
    valid_clientes = df_clientes['id_cliente'].unique()
    valid_productos = df_productos['ID_Producto'].unique()
    
    df.loc[~df['ID_Cliente'].isin(valid_clientes), 'ID_Cliente'] = 999
    df.loc[~df['ID_Producto'].isin(valid_productos), 'ID_Producto'] = 999
    
    # Rellenar campañas vacías con un código por defecto "SIN_CAMPANA"
    df['ID_Campana'] = df['ID_Campana'].fillna('SIN_CAMPANA').str.strip()
    df['ID_Campana'] = df['ID_Campana'].replace('', 'SIN_CAMPANA')
    
    return df

def build_dimensional_model(dfs):
    """Construye las tablas del modelo Estrella listo para el Data Warehouse."""
    # 1. DimCliente
    dim_cliente = dfs['clientes'].rename(columns={
        'id_cliente': 'SK_Cliente', 'nombre': 'Nombre', 'email': 'Email', 'ciudad': 'Ciudad'
    })
    # Añadir registro comodín para IDs no encontrados
    comodin_cliente = pd.DataFrame([{'SK_Cliente': 999, 'Nombre': 'Cliente Anónimo/Inexistente', 'Email': 'n/a', 'Ciudad': 'Desconocida'}])
    dim_cliente = pd.concat([dim_cliente, comodin_cliente], ignore_index=True)
    
    # 2. DimProducto
    dim_producto = dfs['productos'].rename(columns={
        'ID_Producto': 'SK_Producto', 'Nombre': 'Nombre_Producto', 'Categoria': 'Categoria', 'Precio_USD': 'Precio_Unitario'
    })
    comodin_producto = pd.DataFrame([{'SK_Producto': 999, 'Nombre_Producto': 'Producto Inexistente', 'Categoria': 'DESCONOCIDA', 'Precio_Unitario': 0.0}])
    dim_producto = pd.concat([dim_producto, comodin_producto], ignore_index=True)
    
    # 3. DimCampana
    dim_campana = dfs['campanas'].rename(columns={
        'id_campana': 'SK_Campana', 'nombre_campana': 'Nombre_Campana', 'canal': 'Canal', 'presupuesto': 'Presupuesto'
    })
    comodin_campana = pd.DataFrame([{'SK_Campana': 'SIN_CAMPANA', 'Nombre_Campana': 'Sin Campaña Orgánico', 'Canal': 'Ninguno', 'Presupuesto': 0.0}])
    dim_campana = pd.concat([dim_campana, comodin_campana], ignore_index=True)
    
    # 4. DimTiempo (Generada a partir de las fechas únicas de ventas)
    fechas_unicas = pd.to_datetime(dfs['ventas']['Fecha']).dropna().unique()
    dim_tiempo = pd.DataFrame({'Fecha_Key': fechas_unicas})
    dim_tiempo['Fecha'] = dim_tiempo['Fecha_Key'].dt.strftime('%Y-%m-%d')
    dim_tiempo['Anio'] = dim_tiempo['Fecha_Key'].dt.year
    dim_tiempo['Mes'] = dim_tiempo['Fecha_Key'].dt.month
    dim_tiempo['Dia'] = dim_tiempo['Fecha_Key'].dt.day
    dim_tiempo['Trimestre'] = dim_tiempo['Fecha_Key'].dt.quarter
    dim_tiempo = dim_tiempo.drop(columns=['Fecha_Key'])
    
    # 5. FactVentas (Uniendo precios para calcular ingresos derivativos)
    fact_ventas = dfs['ventas'].copy()
    # Traer el precio unitario mapeado para calcular el Total Venta en el DW
    fact_ventas = fact_ventas.merge(dim_producto[['SK_Producto', 'Precio_Unitario']], left_on='ID_Producto', right_on='SK_Producto', how='left')
    fact_ventas['Total_Ingreso'] = fact_ventas['Cantidad'] * fact_ventas['Precio_Unitario']
    
    # Seleccionar y renombrar columnas finales de la Fact Table
    fact_ventas = fact_ventas.rename(columns={
        'ID_Venta': 'ID_Venta',
        'Fecha': 'Fecha_Key',
        'ID_Cliente': 'FK_Cliente',
        'ID_Producto': 'FK_Producto',
        'ID_Campana': 'FK_Campana',
        'Cantidad': 'Cantidad_Unidades'
    })[['ID_Venta', 'Fecha_Key', 'FK_Cliente', 'FK_Producto', 'FK_Campana', 'Cantidad_Unidades', 'Total_Ingreso']]
    
    return {
        "DimCliente": dim_cliente,
        "DimProducto": dim_producto,
        "DimCampana": dim_campana,
        "DimTiempo": dim_tiempo,
        "FactVentas": fact_ventas
    }

def run_transformation(raw_data, log):
    """Ejecuta toda la lógica secuencial de transformación y limpieza."""
    log.info("Iniciando fase de TRANSFORMACIÓN y LIMPIEZA...")
    
    cleaned_dfs = {}
    cleaned_dfs['clientes'] = clean_clientes(raw_data['clientes'])
    cleaned_dfs['productos'] = clean_productos(raw_data['productos'])
    cleaned_dfs['inventario'] = clean_inventario(raw_data['inventario'])
    cleaned_dfs['campanas'] = clean_campanas(raw_data['campanas'])
    
    # Ventas requiere validación cruzada con clientes y productos limpios
    cleaned_dfs['ventas'] = clean_ventas(raw_data['ventas'], cleaned_dfs['clientes'], cleaned_dfs['productos'])
    
    # Guardar pasos intermedios en data/processed/ por auditoría
    for name, df in cleaned_dfs.items():
        df.to_csv(f"data/processed/cleaned_{name}.csv", index=False)
        log.info(f"-> Datos limpios guardados en 'data/processed/cleaned_{name}.csv'")
        
    # Construcción del modelo estrella final
    log.info("Modelando la arquitectura multidimensional (Estrella)...")
    dw_tables = build_dimensional_model(cleaned_dfs)
    
    return dw_tables