# Arquitectura de la solución

## Objetivo

Describir la arquitectura propuesta para integrar, transformar y almacenar la información proveniente de las diferentes fuentes de datos de DataCommerce GT.

---

## Descripción general

La solución implementa una arquitectura basada en un proceso ETL (Extract, Transform, Load), donde los datos provenientes de múltiples fuentes son extraídos, sometidos a procesos de limpieza y estandarización, integrados en un único conjunto de datos y posteriormente cargados en un Data Warehouse para su análisis.

---

## Componentes de la arquitectura

### 1. Fuentes de datos

La información es obtenida desde cinco orígenes diferentes:

- Ventas (CSV)
- Productos (Excel)
- Clientes (JSON)
- Inventario (SQLite)
- Campañas de marketing (API REST simulada)

---

### 2. Extracción

Los datos son leídos mediante Python utilizando librerías especializadas como Pandas, OpenPyXL, SQLite3 y Requests.

---

### 3. Transformación

Durante esta etapa se aplican reglas de calidad para garantizar la consistencia de la información.

Entre ellas:

- Eliminación de registros duplicados.
- Tratamiento de valores nulos.
- Conversión de tipos de datos.
- Estandarización de fechas.
- Normalización de texto.
- Validación de claves.

---

### 4. Integración

Una vez transformados, los datos provenientes de todas las fuentes se relacionan mediante sus identificadores comunes para construir un conjunto de datos consistente.

---

### 5. Carga

La información integrada se almacena en un Data Warehouse implementado en PostgreSQL (Supabase), utilizando un modelo dimensional tipo estrella.

---

### 6. Consumo de datos

Sobre el Data Warehouse se realizan:

- Consultas SQL analíticas.
- Cálculo de KPIs.
- Visualizaciones con Matplotlib.

---

## Diagrama de arquitectura

                   FUENTES DE DATOS
 ┌──────────┬──────────┬──────────┬────────────┬───────────┐
 │ Ventas   │Productos │Clientes  │Inventario  │Campañas   │
 │   CSV    │  Excel   │  JSON    │  SQLite    │ API REST  │
 └──────────┴──────────┴──────────┴────────────┴───────────┘
                          │
                          ▼
                  EXTRACCIÓN (Python)
                          │
                          ▼
                TRANSFORMACIÓN (Pandas)
         • Limpieza
         • Validación
         • Estandarización
                          │
                          ▼
                  INTEGRACIÓN DE DATOS
                          │
                          ▼
                    DATA WAREHOUSE
                (PostgreSQL - Supabase)  
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
    Consultas SQL                 KPIs y Gráficos
                                         │
                                         ▼
                                  Matplotlib

---

## Flujo general de la solución

Fuentes de datos

↓

Extracción (Python)

↓

Transformación (Pandas)

↓

Integración de datos

↓

 Data Warehouse
 (PostgreSQL - Supabase)

↓

Consultas SQL

↓

KPIs y Visualizaciones

---

## Tecnologías utilizadas

- Python
- Pandas
- SQLAlchemy
- PostgreSQL (Supabase)
- SQLite
- Matplotlib
- Requests