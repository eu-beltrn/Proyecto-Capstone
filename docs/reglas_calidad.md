## Reglas de Limpieza y Calidad Aplicadas

Para corregir las anomalías detectadas y garantizar la estabilidad del Data Warehouse, el componente `transform.py` implementa de manera estricta las siguientes reglas de negocio y calidad:

### 1. Normalización de Cadenas y Categorías
* **Manejo de Espacios Transaccionales:** Se aplica `.str.strip()` en todas las dimensiones y encabezados para eliminar espacios fantasmas que impidan cruces exitosos de llaves primarias o foráneas (FK/PK).
* **Consistencia de Texto:** Las categorías de productos y bodegas se fuerzan a mayúsculas sostenidas (`.str.upper()`), mientras que los nombres de clientes se estandarizan a formato título (`.str.title()`).
* **Aplanamiento de Estructuras API (JSON):** Se detectó que la fuente api_marketing_response.json encapsulaba la información en un nodo raíz llamado campaigns. El pipeline aplica (`pd.json_normalize()`) para deserializar y expandir dinámicamente este objeto en filas y columnas tabulares limpias antes de procesar sus métricas.

### 2. Tratamiento de Datos Faltantes e Imputación
* **Campos Geográficos Vacíos:** Se interceptan las cadenas vacías (`""`) en la columna `municipio` de los clientes y se reemplazan por el valor por defecto `"No Especificado"`. Esto previene nulos en reportes de inteligencia de negocios.
* **Métricas Monetarias y de Conteo:** Se utiliza `pd.to_numeric(..., errors='coerce')` combinado con `.fillna()` (con 0.0 para costos/precios y 0 con conversión a .astype(int) para unidades y existencias). Esto blinda los cálculos analíticos del inventario y las ventas contra caracteres no numéricos o valores vacíos.

### 3. Estandarización de Fechas (Time-Series Alignment)
* **Validación de Múltiples Formatos:** La columna `fecha_venta` de las transacciones se parsea mediante un motor inteligente que unifica formatos heterogéneos (guiones, barras diagonales y orden día/mes) bajo el estándar ISO 8601 (`YYYY-MM-DD`). Las transacciones inviables se convierten en registros corregidos.

### 4. Integridad Referencial y Manejo de Huérfanos
* **Estrategia del Registro Comodín (ID 999):** Para evitar que el proceso de carga falle por violaciones de claves foráneas en el Data Warehouse, se realiza una validación cruzada. Si un `cliente_id` o `producto_id` presente en las ventas no se encuentra en las dimensiones maestras limpias, el pipeline reasigna automáticamente el ID de la transacción a `999` (Cliente/Producto Inexistente) en lugar de descartar la fila de ventas.
* **Mapeo de Campañas:** Los registros transaccionales que no contienen una campaña de marketing asociada se rellenan explícitamente con la etiqueta `"SIN_CAMPANA"`, enlazándose con un registro orgánico estático en la dimensión correspondiente.