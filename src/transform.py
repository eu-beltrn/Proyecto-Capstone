import pandas as pd
import numpy as np
import os

def clean_clientes(df):
    """Limpia la fuente de clientes (clientes.json)."""
    df = df.copy()
    # Eliminar duplicados exactos por cliente_id según el esquema real
    df = df.drop_duplicates(subset=['cliente_id'], keep='first')
    
    # Limpieza de texto y manejo de vacíos ocultos ("")
    df['nombre'] = df['nombre'].str.strip().str.title()
    df['departamento'] = df['departamento'].str.strip().str.title()
    df['municipio'] = df['municipio'].str.strip().replace('', 'No Especificado').fillna('No Especificado')
    return df

def clean_productos(df):
    """Limpia la fuente de productos (productos.xlsx)."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    
    # Validar duplicados usando el nombre de columna real 'producto_id'
    df = df.drop_duplicates(subset=['producto_id'], keep='first')
    df['nombre_producto'] = df['nombre_producto'].str.strip()
    df['categoria'] = df['categoria'].str.strip().str.upper()
    df['subcategoria'] = df['subcategoria'].str.strip().str.upper()
    df['marca'] = df['marca'].str.strip().str.upper()
    
    # Convertir métricas financieras de forma segura
    df['costo_unitario'] = pd.to_numeric(df['costo_unitario'], errors='coerce').fillna(0.0)
    df['precio_lista'] = pd.to_numeric(df['precio_lista'], errors='coerce').fillna(0.0)
    return df

def clean_inventario_actual(df):
    """Limpia la tabla de stock estático del inventario."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df['bodega'] = df['bodega'].str.strip().str.upper()
    df['existencia'] = pd.to_numeric(df['existencia'], errors='coerce').fillna(0).astype(int)
    return df

def clean_movimientos_inventario(df):
    """Limpia la tabla histórica de flujos del inventario."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df['tipo'] = df['tipo'].str.strip().str.upper()
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
    return df

def clean_campanas(df):
    """Limpia la fuente de campañas expandiendo correctamente la estructura anidada."""
    df = df.copy()
    
    # Si detectamos que el DataFrame tiene la columna anidada 'campaigns',
    # la aplanamos por completo para recuperar la estructura de tabla
    if 'campaigns' in df.columns:
        # En caso de que venga como una serie de diccionarios, la normalizamos
        if isinstance(df['campaigns'].iloc[0], dict):
            df = pd.json_normalize(df['campaigns'])
        else:
            # Si en extract.py cambió y viene la lista cruda
            lista_campanas = df['campaigns'].tolist()
            df = pd.DataFrame(lista_campanas)
            
    # Estandarizamos los nombres de las columnas por seguridad
    df.columns = df.columns.str.strip()
    
    # Ahora sí aplicamos las reglas del Día 2 con total seguridad
    if 'plataforma' in df.columns:
        df['plataforma'] = df['plataforma'].str.strip().str.upper()
        
    if 'costo' in df.columns:
        df['costo'] = pd.to_numeric(df['costo'], errors='coerce').fillna(0.0)
        
    return df

def clean_ventas(df, df_clientes, df_productos, log):
    """Limpia la tabla de hechos con validación cruzada usando nombres de columna reales."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    
    # Evitar duplicados en transacciones
    df = df.drop_duplicates(subset=['venta_id'], keep='first')
    
    # Homogeneizar los múltiples formatos de fecha detectados en la exploración
    df['fecha_venta'] = pd.to_datetime(df['fecha_venta'], errors='coerce', dayfirst=False).dt.strftime('%Y-%m-%d')
    
    # Tratamiento de cantidades monetarias y físicas
    df['cantidad'] = df['cantidad'].apply(lambda x: abs(x) if x < 0 else x)
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(1).astype(int)
    df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce').fillna(0.0)
    df['total_venta'] = pd.to_numeric(df['total_venta'], errors='coerce').fillna(0.0)
    
    # Validaciones cruzadas de Integridad Referencial
    valid_clientes = df_clientes['cliente_id'].unique()
    valid_productos = df_productos['producto_id'].unique()
    
    df.loc[~df['cliente_id'].isin(valid_clientes), 'cliente_id'] = 999
    df.loc[~df['producto_id'].isin(valid_productos), 'producto_id'] = 999

    invalid_clientes = ~df['cliente_id'].isin(valid_clientes)
    if invalid_clientes.sum() > 0:
        log.warning(f"Se encontraron {invalid_clientes.sum()} ventas con clientes huérfanos. Asignando ID 999.")
    df.loc[invalid_clientes, 'cliente_id'] = 999
    
    # Mapeo preventivo de campañas vacías
    if 'campaña_id' in df.columns:
        df['campaña_id'] = df['campaña_id'].fillna('SIN_CAMPANA').astype(str).str.strip()
        df['campaña_id'] = df['campaña_id'].replace(['', 'nan', 'None'], 'SIN_CAMPANA')
    else:
        df['campaña_id'] = 'SIN_CAMPANA'
        
    return df

def build_dimensional_model(dfs):
    """Construye las tablas del modelo Estrella listo para el Data Warehouse."""
    
    # 1. DimCliente
    dim_cliente = dfs['clientes'].rename(columns={
        'cliente_id': 'SK_Cliente', 'nombre': 'Nombre', 'genero': 'Genero', 
        'edad': 'Edad', 'departamento': 'Departamento', 'municipio': 'Municipio',
        'fecha_registro': 'Fecha_Registro', 'segmento_cliente': 'Segmento'
    })
    comodin_cliente = pd.DataFrame([{'SK_Cliente': 999, 'Nombre': 'Cliente Inexistente', 'Genero': 'N/A', 'Edad': 0, 'Departamento': 'Desconocido', 'Municipio': 'No Especificado', 'Fecha_Registro': '2026-01-01', 'Segmento': 'Regular'}])
    dim_cliente = pd.concat([dim_cliente, comodin_cliente], ignore_index=True)
    
    # 2. DimProducto
    dim_producto = dfs['productos'].rename(columns={
        'producto_id': 'SK_Producto', 'nombre_producto': 'Nombre_Producto', 'categoria': 'Categoria',
        'subcategoria': 'Subcategoria', 'marca': 'Marca', 'costo_unitario': 'Costo_Unitario', 'precio_lista': 'Precio_Lista'
    })
    comodin_producto = pd.DataFrame([{'SK_Producto': 999, 'Nombre_Producto': 'Producto Genérico', 'Categoria': 'DESCONOCIDA', 'Subcategoria': 'DESCONOCIDA', 'Marca': 'DESCONOCIDA', 'Costo_Unitario': 0.0, 'Precio_Lista': 0.0}])
    dim_producto = pd.concat([dim_producto, comodin_producto], ignore_index=True)
    
    # 3. DimCampana
    dim_campana = dfs['campanas'].rename(columns={
        'campaña_id': 'SK_Campana', 'fecha': 'Fecha_Campana', 'plataforma': 'Plataforma', 'costo': 'Costo',
        'impresiones': 'Impresiones', 'clics': 'Clics', 'leads': 'Leads', 'conversiones': 'Conversiones'
    })
    dim_campana['SK_Campana'] = dim_campana['SK_Campana'].astype(str)
    comodin_campana = pd.DataFrame([{'SK_Campana': 'SIN_CAMPANA', 'Fecha_Campana': '2026-01-01', 'Plataforma': 'ORGANICO', 'Costo': 0.0, 'Impresiones': 0, 'Clics': 0, 'Leads': 0, 'Conversiones': 0}])
    dim_campana = pd.concat([dim_campana, comodin_campana], ignore_index=True)
    
    # 4. DimTiempo
    fechas_unicas = pd.to_datetime(dfs['ventas']['fecha_venta']).dropna().unique()
    dim_tiempo = pd.DataFrame({'Fecha': fechas_unicas})
    dim_tiempo['Fecha_Key'] = dim_tiempo['Fecha'].dt.strftime('%Y-%m-%d')
    dim_tiempo['Anio'] = dim_tiempo['Fecha'].dt.year
    dim_tiempo['Mes'] = dim_tiempo['Fecha'].dt.month
    dim_tiempo['Dia'] = dim_tiempo['Fecha'].dt.day
    dim_tiempo['Trimestre'] = dim_tiempo['Fecha'].dt.quarter
    dim_tiempo = dim_tiempo.drop(columns=['Fecha']).rename(columns={'Fecha_Key': 'Fecha'})
    
    # 5. FactVentas
    fact_ventas = dfs['ventas'].copy()
    fact_ventas = fact_ventas.rename(columns={
        'venta_id': 'ID_Venta',
        'fecha_venta': 'Fecha_Key',
        'cliente_id': 'FK_Cliente',
        'producto_id': 'FK_Producto',
        'campaña_id': 'FK_Campana',
        'cantidad': 'Cantidad_Unidades',
        'total_venta': 'Total_Ingreso'
    })[['ID_Venta', 'Fecha_Key', 'FK_Cliente', 'FK_Producto', 'FK_Campana', 'Cantidad_Unidades', 'Total_Ingreso']]
    
    fact_ventas['FK_Campana'] = fact_ventas['FK_Campana'].astype(str)

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
    cleaned_dfs['inventario_actual'] = clean_inventario_actual(raw_data['inventario_actual'])
    cleaned_dfs['movimientos_inventario'] = clean_movimientos_inventario(raw_data['movimientos_inventario'])
    
    # Esta función ahora manejará la estructura de forma interna y segura
    cleaned_dfs['campanas'] = clean_campanas(raw_data['campanas'])
    
    cleaned_dfs['ventas'] = clean_ventas(raw_data['ventas'], cleaned_dfs['clientes'], cleaned_dfs['productos'], log)
    
    # Guardar auditoría intermedia
    for name, df in cleaned_dfs.items():
        df.to_csv(f"data/processed/cleaned_{name}.csv", index=False)
        log.info(f"-> Datos limpios guardados en 'data/processed/cleaned_{name}.csv'")
        
    dw_tables = build_dimensional_model(cleaned_dfs)
    
    # Enviar las tablas de inventario procesadas directo al Data Warehouse
    dw_tables['DimInventarioActual'] = cleaned_dfs['inventario_actual']
    dw_tables['DimMovimientosInventario'] = cleaned_dfs['movimientos_inventario']
    
    return dw_tables