# Modelo Dimensional / Esquema Estrella (Data Warehouse / OLAP)

Este modelo representa la arquitectura de la **Capa Oro** en el Data Warehouse (`dw_ventas.db`). Está optimizado para la lectura rápida, cruce de variables y generación de KPIs gerenciales mediante herramientas de Business Intelligence y SQL.

## Diagrama del Esquema Estrella

```mermaid
erDiagram
    FactVentas }|--|| DimCliente : "FK_Cliente"
    FactVentas }|--|| DimProducto : "FK_Producto"
    FactVentas }|--|| DimCampana : "FK_Campana"
    FactVentas }|--|| DimTiempo : "Fecha_Key"

    FactVentas {
        int ID_Venta PK
        string Fecha_Key FK "YYYY-MM-DD"
        int FK_Cliente FK "ID 999 = Huérfano"
        int FK_Producto FK "ID 999 = Genérico"
        string FK_Campana FK "'SIN_CAMPANA' por defecto"
        int Cantidad_Unidades
        float Total_Ingreso
    }

    DimCliente {
        int SK_Cliente PK
        string Nombre
        string Genero
        int Edad
        string Departamento
        string Municipio
        date Fecha_Registro
        string Segmento
    }

    DimProducto {
        int SK_Producto PK
        string Nombre_Producto
        string Categoria
        string Subcategoria
        string Marca
        float Costo_Unitario
        float Precio_Lista
    }

    DimCampana {
        string SK_Campana PK
        date Fecha_Campana
        string Plataforma
        float Costo
        int Impresiones
        int Clics
        int Leads
        int Conversiones
    }

    DimTiempo {
        string Fecha PK "YYYY-MM-DD"
        int Anio
        int Mes
        int Dia
        int Trimestre
    }
```

## Consideraciones de Arquitectura y Calidad
1. **Unificación de Fechas (`DimTiempo`):** Las fechas dispares provenientes de los CSVs y JSONs han sido estandarizadas al formato `YYYY-MM-DD`. `DimTiempo` actúa como la columna vertebral para medir el ROI cruzando `FactVentas` y `DimCampana`.
2. **Early Arriving Facts (Manejo de Nulos):** Si una venta se registra con un cliente o producto inexistente en los catálogos principales, el pipeline ETL le asigna automáticamente la *Surrogate Key* (SK) `999` para no perder la transacción ni romper la integridad referencial.
3. **Integración de Marketing:** Se generó el identificador `'SIN_CAMPANA'` para las ventas orgánicas que no provienen de un esfuerzo de marketing digital directo, permitiendo un cálculo exacto del Costo de Adquisición (CAC) y el Retorno de Inversión (ROI).