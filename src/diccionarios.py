# ==============================================================================
# DICCIONARIOS MAESTROS DE NORMALIZACIÓN DE NEGOCIO (DATACOMMERCE)
# ==============================================================================

# 1. CATEGORÍAS DE PRODUCTO (KPI 1)
MAPEO_CATEGORIAS = {
    # Typos para "COMPUTO"
    'COMPUTACION': 'COMPUTO', 'CMPUTO': 'COMPUTO', 'COMPUTOO': 'COMPUTO', 
    'COMUPTO': 'COMPUTO', 'PC': 'COMPUTO', 'EQUIPO DE COMPUTO': 'COMPUTO',
    'ORDENADORES': 'COMPUTO', 'COMPU': 'COMPUTO', 'COMP': 'COMPUTO',
    
    # Typos para "MONITORES"
    'MONITOR': 'MONITORES', 'MONITORS': 'MONITORES', 'MNT': 'MONITORES',
    'PANTALLAS': 'MONITORES', 'PANTALLA': 'MONITORES', 'MONITORE': 'MONITORES',
    
    # Typos para "ACCESORIOS"
    'ACCESORIO': 'ACCESORIOS', 'ACCESORI': 'ACCESORIOS', 'ACCS': 'ACCESORIOS',
    'ACESORIOS': 'ACCESORIOS', 'ACCESORIS': 'ACCESORIOS', 'PERIFERICOS': 'ACCESORIOS',
    
    # Typos para "IMPRESION"
    'IMPRESORA': 'IMPRESION', 'IMPRESORAS': 'IMPRESION', 'IMPRESIONES': 'IMPRESION',
    'IMPR': 'IMPRESION', 'PRINT': 'IMPRESION', 'IMPRESIN': 'IMPRESION',
    
    # Typos para "REDES"
    'RED': 'REDES', 'NETWORK': 'REDES', 'NETWORKING': 'REDES',
    'CONECTIVIDAD': 'REDES', 'ROUTERS': 'REDES', 'REDE': 'REDES',
    
    # Typos para "SEGURIDAD"
    'SEGURIDA': 'SEGURIDAD', 'SECURITY': 'SEGURIDAD', 'CAMARAS': 'SEGURIDAD',
    'CCTV': 'SEGURIDAD', 'SGURIDAD': 'SEGURIDAD', 'SEG': 'SEGURIDAD'
}

# 2. MARCAS (KPI 1 y 5)
MAPEO_MARCAS = {
    'TEC ONE': 'TECHONE', 'TECH ONE': 'TECHONE', 'TECHON': 'TECHONE', 'TCHONE': 'TECHONE',
    'VISION X': 'VISIONX', 'VSIONX': 'VISIONX', 'VISION': 'VISIONX', 'VISONX': 'VISIONX',
    'CLICK IT': 'CLICKIT', 'CLIKIT': 'CLICKIT', 'CLICKT': 'CLICKIT', 'CLICK': 'CLICKIT',
    'SECURE ID': 'SECUREID', 'SECURID': 'SECUREID', 'SECURE': 'SECUREID', 'SCUREID': 'SECUREID',
    'PRINT MAX': 'PRINTMAX', 'PRNTMAX': 'PRINTMAX', 'PRINTM': 'PRINTMAX', 'PRINTMAXS': 'PRINTMAX',
    'DEL': 'DELL', 'DELLL': 'DELL',
    'H P': 'HP', 'HEWLETT PACKARD': 'HP'
}

# 3. PLATAFORMAS DE MARKETING (KPI 4)
MAPEO_PLATAFORMAS = {
    # Ecosistema Meta
    'FACEBOO': 'FACEBOOK', 'FACEBOOK ADS': 'FACEBOOK', 'FB': 'FACEBOOK', 'F': 'FACEBOOK',
    'FACEBOK': 'FACEBOOK', 'FACE': 'FACEBOOK', 'FCBK': 'FACEBOOK', 'META': 'FACEBOOK',
    'INST': 'INSTAGRAM', 'INSTA': 'INSTAGRAM', 'INSTAGRA': 'INSTAGRAM', 'IG': 'INSTAGRAM',
    'I': 'INSTAGRAM', 'INSTGRAM': 'INSTAGRAM', 'INTAGRAM': 'INSTAGRAM',
    
    # Ecosistema Google
    'GOOGL': 'GOOGLE', 'GOOGLE ADS': 'GOOGLE', 'GGL': 'GOOGLE', 'GADS': 'GOOGLE',
    'GOGLE': 'GOOGLE', 'SEARCH': 'GOOGLE', 'SEM': 'GOOGLE',
    
    # Otros
    'TIK TOK': 'TIKTOK', 'TKTOK': 'TIKTOK', 'TT': 'TIKTOK', 'TIKTO': 'TIKTOK',
    'LINKED IN': 'LINKEDIN', 'LKD': 'LINKEDIN', 'IN': 'LINKEDIN',
    'X': 'TWITTER', 'TWITER': 'TWITTER', 'TWT': 'TWITTER'
}

# 4. SEGMENTOS DE CLIENTE (KPI 2 y 3)
MAPEO_SEGMENTOS = {
    # Note: La función de clientes usa is_name=True, así que vendrán en formato Título (Capitalizado)
    'Corporativ': 'Corporativo', 'Corp': 'Corporativo', 'Corporativos': 'Corporativo', 'Empresa': 'Corporativo',
    'Frecuent': 'Frecuente', 'Frecuentes': 'Frecuente', 'Recurrente': 'Frecuente', 'Regular': 'Frecuente',
    'Premiu': 'Premium', 'Prem': 'Premium', 'Vip': 'Premium', 'Oro': 'Premium',
    'Nuev': 'Nuevo', 'Nuevos': 'Nuevo', 'Reciente': 'Nuevo', 'New': 'Nuevo',
    'Inactiv': 'Inactivo', 'Inactivos': 'Inactivo', 'Baja': 'Inactivo', 'Perdido': 'Inactivo'
}

# 5. GÉNEROS (Para análisis demográficos si te los piden)
MAPEO_GENEROS = {
    'MASCULINO': 'M', 'HOMBRE': 'M', 'MASC': 'M', 'H': 'M',
    'FEMENINO': 'F', 'MUJER': 'F', 'FEM': 'F',
    'NO ESPECIFICADO': 'N/A', 'OTRO': 'N/A', 'DESCONOCIDO': 'N/A'
}

# 6. TIPOS DE MOVIMIENTO DE INVENTARIO
MAPEO_MOVIMIENTOS = {
    'ENTRADAS': 'ENTRADA', 'IN': 'ENTRADA', 'COMPRA': 'ENTRADA', 'INGRESO': 'ENTRADA',
    'SALIDAS': 'SALIDA', 'OUT': 'SALIDA', 'VENTA': 'SALIDA', 'EGRESO': 'SALIDA',
    'AJUSTES': 'AJUSTE', 'MERMA': 'AJUSTE', 'DEVOLUCION': 'AJUSTE', 'CORRECCION': 'AJUSTE'
}