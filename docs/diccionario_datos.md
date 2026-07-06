# Diccionario de Datos - DataCommerce GT (Capa Oro)

## Tabla de Hechos: `FactVentas`
Almacena las métricas transaccionales a nivel de línea de venta.
* **ID_Venta (PK):** Identificador único de la transacción.
* **Fecha_Key (FK):** Fecha de la venta (formato YYYY-MM-DD). Conecta con `DimTiempo`.
* **FK_Cliente (FK):** ID del cliente. Conecta con `DimCliente`. (ID 999 = Cliente Huérfano).
* **FK_Producto (FK):** ID del producto. Conecta con `DimProducto`.
* **FK_Campana (FK):** ID de la campaña de marketing asociada. Conecta con `DimCampana`.
* **Cantidad_Unidades:** Número de unidades físicas vendidas.
* **Total_Ingreso:** Valor monetario total de la línea de venta.

## Dimensiones
* **DimCliente:** `SK_Cliente` (PK), `Nombre`, `Genero`, `Edad`, `Departamento`, `Municipio`, `Fecha_Registro`, `Segmento`.
* **DimProducto:** `SK_Producto` (PK), `Nombre_Producto`, `Categoria`, `Subcategoria`, `Marca`, `Costo_Unitario`, `Precio_Lista`.
* **DimCampana:** `SK_Campana` (PK), `Fecha_Campana`, `Plataforma`, `Costo`, `Impresiones`, `Clics`, `Leads`, `Conversiones`.
* **DimTiempo:** `Fecha` (PK), `Anio`, `Mes`, `Dia`, `Trimestre`.