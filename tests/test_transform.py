import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pandas as pd
from transform import clean_clientes, clean_productos

def test_clean_clientes_sin_nulos_en_municipio():
    # Dato de prueba (Simulando la fuente)
    df_raw = pd.DataFrame({
        "cliente_id": [1, 2],
        "nombre": ["Juan", "Ana"],
        "departamento": ["Guatemala", "Guatemala"],
        "municipio": ["", None] # Simulando errores
    })
    
    df_clean = clean_clientes(df_raw)
    
    # Pruebas (Aserciones)
    assert df_clean['municipio'].iloc[0] == 'No Especificado'
    assert df_clean['municipio'].iloc[1] == 'No Especificado'
    assert not df_clean['municipio'].isnull().any()

def test_no_duplicados_productos():
    df_raw = pd.DataFrame({
        "producto_id": [100, 100],
        "nombre_producto": ["Laptop", "Laptop"],
        "categoria": ["Tech", "Tech"],
        "subcategoria": ["Laptops", "Laptops"], # <-- Faltaba esto
        "marca": ["Genérica", "Genérica"],       # <-- Faltaba esto
        "costo_unitario": [500, 500],
        "precio_lista": [800, 800]
    })
    
    df_clean = clean_productos(df_raw)
    assert len(df_clean) == 1