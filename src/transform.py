import pandas as pd
import numpy as np
import sys
import os
import re
import unicodedata

# Asegura que Python pueda ver la carpeta raíz donde está config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import RAW_DIR, DB_PATH 

# ==============================================================================
# DICCIONARIOS MAESTROS DE NORMALIZACIÓN
# ==============================================================================

MAPEO_CATEGORIAS = {
    'COMPUTACION': 'COMPUTO', 'CMPUTO': 'COMPUTO', 'COMPUTOO': 'COMPUTO', 
    'COMUPTO': 'COMPUTO', 'PC': 'COMPUTO', 'EQUIPO DE COMPUTO': 'COMPUTO',
    'ORDENADORES': 'COMPUTO', 'COMPU': 'COMPUTO', 'COMP': 'COMPUTO',
    'MONITOR': 'MONITORES', 'MONITORS': 'MONITORES', 'MNT': 'MONITORES',
    'PANTALLAS': 'MONITORES', 'PANTALLA': 'MONITORES', 'MONITORE': 'MONITORES',
    'ACCESORIO': 'ACCESORIOS', 'ACCESORI': 'ACCESORIOS', 'ACCS': 'ACCESORIOS',
    'ACESORIOS': 'ACCESORIOS', 'ACCESORIS': 'ACCESORIOS', 'PERIFERICOS': 'ACCESORIOS',
    'IMPRESORA': 'IMPRESION', 'IMPRESORAS': 'IMPRESION', 'IMPRESIONES': 'IMPRESION',
    'IMPR': 'IMPRESION', 'PRINT': 'IMPRESION', 'IMPRESIN': 'IMPRESION',
    'RED': 'REDES', 'NETWORK': 'REDES', 'NETWORKING': 'REDES',
    'CONECTIVIDAD': 'REDES', 'ROUTERS': 'REDES', 'REDE': 'REDES',
    'SEGURIDA': 'SEGURIDAD', 'SECURITY': 'SEGURIDAD', 'CAMARAS': 'SEGURIDAD',
    'CCTV': 'SEGURIDAD', 'SGURIDAD': 'SEGURIDAD', 'SEG': 'SEGURIDAD'
}

MAPEO_MARCAS = {
    'TEC ONE': 'TECHONE', 'TECH ONE': 'TECHONE', 'TECHON': 'TECHONE', 'TCHONE': 'TECHONE',
    'VISION X': 'VISIONX', 'VSIONX': 'VISIONX', 'VISION': 'VISIONX', 'VISONX': 'VISIONX',
    'CLICK IT': 'CLICKIT', 'CLIKIT': 'CLICKIT', 'CLICKT': 'CLICKIT', 'CLICK': 'CLICKIT',
    'SECURE ID': 'SECUREID', 'SECURID': 'SECUREID', 'SECURE': 'SECUREID', 'SCUREID': 'SECUREID',
    'PRINT MAX': 'PRINTMAX', 'PRNTMAX': 'PRINTMAX', 'PRINTM': 'PRINTMAX', 'PRINTMAXS': 'PRINTMAX',
    'DEL': 'DELL', 'DELLL': 'DELL',
    'H P': 'HP', 'HEWLETT PACKARD': 'HP'
}

MAPEO_PLATAFORMAS = {
    'FACEBOO': 'FACEBOOK', 'FACEBOOK ADS': 'FACEBOOK', 'FB': 'FACEBOOK', 'F': 'FACEBOOK',
    'FACEBOK': 'FACEBOOK', 'FACE': 'FACEBOOK', 'FCBK': 'FACEBOOK', 'META': 'FACEBOOK',
    'INST': 'INSTAGRAM', 'INSTA': 'INSTAGRAM', 'INSTAGRA': 'INSTAGRAM', 'IG': 'INSTAGRAM',
    'I': 'INSTAGRAM', 'INSTGRAM': 'INSTAGRAM', 'INTAGRAM': 'INSTAGRAM',
    'GOOGL': 'GOOGLE', 'GOOGLE ADS': 'GOOGLE', 'GGL': 'GOOGLE', 'GADS': 'GOOGLE',
    'GOGLE': 'GOOGLE', 'SEARCH': 'GOOGLE', 'SEM': 'GOOGLE',
    'TIK TOK': 'TIKTOK', 'TKTOK': 'TIKTOK', 'TT': 'TIKTOK', 'TIKTO': 'TIKTOK',
    'LINKED IN': 'LINKEDIN', 'LKD': 'LINKEDIN', 'IN': 'LINKEDIN',
    'X': 'TWITTER', 'TWITER': 'TWITTER', 'TWT': 'TWITTER'
}

MAPEO_SEGMENTOS = {
    'Corporativ': 'Corporativo', 'Corp': 'Corporativo', 'Corporativos': 'Corporativo', 'Empresa': 'Corporativo',
    'Frecuent': 'Frecuente', 'Frecuentes': 'Frecuente', 'Recurrente': 'Frecuente', 'Regular': 'Frecuente',
    'Premiu': 'Premium', 'Prem': 'Premium', 'Vip': 'Premium', 'Oro': 'Premium',
    'Nuev': 'Nuevo', 'Nuevos': 'Nuevo', 'Reciente': 'Nuevo', 'New': 'Nuevo',
    'Inactiv': 'Inactivo', 'Inactivos': 'Inactivo', 'Baja': 'Inactivo', 'Perdido': 'Inactivo'
}

MAPEO_MOVIMIENTOS = {
    'ENTRADAS': 'ENTRADA', 'IN': 'ENTRADA', 'COMPRA': 'ENTRADA', 'INGRESO': 'ENTRADA',
    'SALIDAS': 'SALIDA', 'OUT': 'SALIDA', 'VENTA': 'SALIDA', 'EGRESO': 'SALIDA',
    'AJUSTES': 'AJUSTE', 'MERMA': 'AJUSTE', 'DEVOLUCION': 'AJUSTE', 'CORRECCION': 'AJUSTE'
}

# ==============================================================================
# FUNCIONES DE TRANSFORMACIÓN Y LIMPIEZA
# ==============================================================================

def normalize_text(text_series, is_name=False):
    """
    Función de nivel corporativo para limpieza profunda de strings.
    Elimina tildes, caracteres especiales, espacios múltiples y estandariza mayúsculas/minúsculas.
    """
    s = text_series.astype(str).fillna('DESCONOCIDO')
    s = s.apply(lambda x: unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode('utf-8'))
    s = s.str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
    s = s.str.replace(r'\s+', ' ', regex=True).str.strip()
    
    if is_name:
        s = s.str.title()
    else:
        s = s.str.upper()
        
    return s

def clean_clientes(df):
    """Limpia la fuente de clientes con normalización profunda."""
    df = df.copy()
    df = df.drop_duplicates(subset=['cliente_id'], keep='first')
    
    df['nombre'] = normalize_text(df['nombre'], is_name=True)
    df['departamento'] = normalize_text(df['departamento'], is_name=True)
    df['municipio'] = normalize_text(df['municipio'], is_name=True)
    df['municipio'] = df['municipio'].replace(['', 'Nan', 'Desconocido'], 'No Especificado')
    
    # Normalización del segmento
    df['segmento_cliente'] = normalize_text(df['segmento_cliente'], is_name=True)
    df['segmento_cliente'] = df['segmento_cliente'].replace(MAPEO_SEGMENTOS)
    
    return df

def clean_productos(df):
    """Limpia productos y corrige errores ortográficos masivamente."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates(subset=['producto_id'], keep='first')
    
    df['nombre_producto'] = normalize_text(df['nombre_producto'])
    df['categoria'] = normalize_text(df['categoria'])
    df['subcategoria'] = normalize_text(df['subcategoria'])
    df['marca'] = normalize_text(df['marca'])
    
    # Aplicar diccionarios
    df['categoria'] = df['categoria'].replace(MAPEO_CATEGORIAS)
    df['marca'] = df['marca'].replace(MAPEO_MARCAS)
    
    df['costo_unitario'] = pd.to_numeric(df['costo_unitario'], errors='coerce').fillna(0.0)
    df['precio_lista'] = pd.to_numeric(df['precio_lista'], errors='coerce').fillna(0.0)
    
    return df

def clean_inventario_actual(df):
    """Limpia la tabla de stock estático del inventario."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df['bodega'] = normalize_text(df['bodega'], is_name=True)
    
    df['existencia'] = pd.to_numeric(df['existencia'], errors='coerce').fillna(0).astype(int)
    df['existencia'] = df['existencia'].apply(lambda x: abs(x) if x < 0 else x)
    return df

def clean_movimientos_inventario(df):
    """Limpia la tabla histórica de flujos del inventario."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    
    df['tipo'] = normalize_text(df['tipo'])
    df['tipo'] = df['tipo'].replace(MAPEO_MOVIMIENTOS)
    
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
    df['cantidad'] = df['cantidad'].apply(lambda x: abs(x) if x < 0 else x)
    return df

def clean_campanas(df):
    """Limpia la fuente de campañas y estandariza plataformas."""
    df = df.copy()
    
    if 'campaigns' in df.columns:
        if isinstance(df['campaigns'].iloc[0], dict):
            df = pd.json_normalize(df['campaigns'])
        else:
            lista_campanas = df['campaigns'].tolist()
            df = pd.DataFrame(lista_campanas)
            
    df.columns = df.columns.str.strip()
    
    if 'plataforma' in df.columns:
        df['plataforma'] = normalize_text(df['plataforma'])
        df['plataforma'] = df['plataforma'].replace(MAPEO_PLATAFORMAS)
        
    if 'costo' in df.columns:
        df['costo'] = pd.to_numeric(df['costo'], errors='coerce').fillna(0.0)
        df['costo'] = df['costo'].apply(lambda x: abs(x) if x < 0 else x)
        
    return df

def clean_ventas(df, df_clientes, df_productos, log):
    """Limpia la tabla de hechos y separa registros corruptos en cuarentena (DLQ)."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates(subset=['venta_id'], keep='first')
    
    df['fecha_venta'] = pd.to_datetime(df['fecha_venta'], errors='coerce', format='mixed').dt.strftime('%Y-%m-%d')
    
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
    df['cantidad'] = df['cantidad'].apply(lambda x: abs(x) if x < 0 else x).astype(int)
    df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce').fillna(0.0)
    df['total_venta'] = pd.to_numeric(df['total_venta'], errors='coerce').fillna(0.0)
    df['total_venta'] = df['total_venta'].apply(lambda x: abs(x) if x < 0 else x)
    
    # Validaciones de Integridad Referencial
    valid_clientes = df_clientes['cliente_id'].unique()
    valid_productos = df_productos['producto_id'].unique()
    
    invalid_mask = (~df['cliente_id'].isin(valid_clientes)) | (~df['producto_id'].isin(valid_productos))
    
    df_cuarentena = df[invalid_mask].copy()
    df_valido = df[~invalid_mask].copy()
    
    if not df_cuarentena.empty:
        log.warning(f"¡ALERTA DE GOBIERNO DE DATOS! {len(df_cuarentena)} transacciones enviadas a cuarentena por falta de integridad referencial.")
        df_cuarentena['motivo_rechazo'] = 'Cliente o Producto Inexistente'
        
    if 'campaña_id' in df_valido.columns:
        df_valido['campaña_id'] = df_valido['campaña_id'].fillna('SIN_CAMPANA').astype(str).str.strip()
        df_valido['campaña_id'] = df_valido['campaña_id'].replace(['', 'nan', 'None'], 'SIN_CAMPANA')
    else:
        df_valido['campaña_id'] = 'SIN_CAMPANA'
        
    return df_valido, df_cuarentena

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
    comodin_producto = pd.DataFrame([{'SK_Producto': 999, 'Nombre_Producto': 'Producto Generico', 'Categoria': 'DESCONOCIDA', 'Subcategoria': 'DESCONOCIDA', 'Marca': 'DESCONOCIDA', 'Costo_Unitario': 0.0, 'Precio_Lista': 0.0}])
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
    
    if 'movimientos_inventario' in raw_data and raw_data['movimientos_inventario'] is not None:
        cleaned_dfs['movimientos_inventario'] = clean_movimientos_inventario(raw_data['movimientos_inventario'])
        log.info("-> 'movimientos_inventario' procesado correctamente.")
    else:
        log.warning("-> 'movimientos_inventario' no encontrado en datos crudos. Saltando transformación.")
    
    cleaned_dfs['campanas'] = clean_campanas(raw_data['campanas'])
    
    cleaned_dfs['ventas'], df_cuarentena = clean_ventas(raw_data['ventas'], cleaned_dfs['clientes'], cleaned_dfs['productos'], log)
    
    if not df_cuarentena.empty:
        df_cuarentena.to_csv("data/processed/dlq_ventas_cuarentena.csv", index=False)
        log.info(f"-> Auditoría: Archivo DLQ generado en 'data/processed/dlq_ventas_cuarentena.csv'")
    
    # Guardar auditoría intermedia
    for name, df in cleaned_dfs.items():
        df.to_csv(f"data/processed/cleaned_{name}.csv", index=False)
        log.info(f"-> Datos limpios guardados en 'data/processed/cleaned_{name}.csv'")
        
    dw_tables = build_dimensional_model(cleaned_dfs)
    
    # Carga condicional al DWH
    dw_tables['DimInventarioActual'] = cleaned_dfs['inventario_actual']
    if 'movimientos_inventario' in cleaned_dfs:
        dw_tables['DimMovimientosInventario'] = cleaned_dfs['movimientos_inventario']
        
    # Enviar la tabla de cuarentena a BigQuery para el Dashboard de Calidad
    if not df_cuarentena.empty:
        dw_tables['DLQ_Ventas_Cuarentena'] = df_cuarentena
        
    return dw_tables