# Modelo Relacional (Sistemas de Origen / OLTP)

Este modelo representa la estructura de los datos tal cual se extraen de las distintas fuentes operacionales de **DataCommerce GT** (Sistemas transaccionales, archivos planos y APIs). Representa la Capa Bronce/Cruda.

## Diagrama Entidad-Relación (Origen)

```mermaid
erDiagram
    CLIENTES ||--o{ VENTAS : "realiza"
    PRODUCTOS ||--o{ VENTAS : "incluye"
    PRODUCTOS ||--o{ INVENTARIO_ACTUAL : "tiene"
    PRODUCTOS ||--o{ MOVIMIENTOS_INVENTARIO : "registra"
    
    CLIENTES {
        int cliente_id PK
        string nombre
        string genero
        int edad
        string departamento
        string municipio
        date fecha_registro
        string segmento_cliente
    }

    PRODUCTOS {
        int producto_id PK
        string nombre_producto
        string categoria
        string subcategoria
        string marca
        float costo_unitario
        float precio_lista
        int proveedor_id
    }

    VENTAS {
        int venta_id PK
        date fecha_venta
        int cliente_id FK
        int producto_id FK
        int sucursal_id
        string canal_venta
        int cantidad
        float precio_unitario
        float descuento
        float total_venta
        string metodo_pago
    }

    INVENTARIO_ACTUAL {
        int producto_id FK
        string bodega
        int existencia
    }

    MOVIMIENTOS_INVENTARIO {
        int id PK
        int producto_id FK
        date fecha
        string tipo
        int cantidad
    }

    CAMPANAS_MARKETING {
        int campana_id PK
        date fecha
        string plataforma
        int impresiones
        int clics
        float costo
        int leads
        int conversiones
    }
```

## Descripción de Fuentes (Data Catalog Crudo)
* **`ventas.csv`**: Tabla transaccional central. Contiene inconsistencias en formatos de fecha.
* **`productos.xlsx`**: Catálogo de productos.
* **`clientes.json`**: Base de datos de clientes con perfiles demográficos.
* **`inventario.db`**: Base de datos SQLite operacional con stock estático (`inventario_actual`) e histórico de flujos (`movimientos_inventario`).
* **`api_marketing_response.json`**: Respuesta de la API REST del equipo de marketing digital. (No relacionada directamente en el origen con ventas).