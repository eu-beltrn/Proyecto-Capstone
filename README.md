# Proyecto Final Integrador - Ingeniería de Datos

## Plataforma de Integración de Datos para DataCommerce GT

## Integrantes del Grupo 3

- Beatriz Eunice Beltrán López
- Brenda Nicole Henríquez Amaya
- Jonathan Vladimir Montes Rodríguez

---

## Descripción del proyecto

Este proyecto tiene como objetivo diseñar e implementar una plataforma de ingeniería de datos para la empresa ficticia **DataCommerce GT**, dedicada a la comercialización de productos tecnológicos a través de múltiples canales de venta: tiendas físicas, comercio electrónico, ventas corporativas y WhatsApp.

Actualmente la empresa enfrenta problemas debido a que la información se encuentra distribuida en diferentes fuentes de datos, generando inconsistencias, duplicidad de registros, formatos incompatibles y reportes contradictorios entre departamentos.

Como solución, se desarrollará un proceso **ETL (Extract, Transform, Load)** capaz de integrar la información proveniente de diversas fuentes, aplicar reglas de calidad de datos, consolidarla en un **Data Warehouse** y generar indicadores estratégicos para apoyar la toma de decisiones de la gerencia.

---

## Objetivos

### Objetivo General

Diseñar e implementar una solución integral de ingeniería de datos que permita integrar información de múltiples fuentes, garantizar su calidad, almacenarla en un Data Warehouse y generar información confiable para la toma de decisiones empresariales.

### Objetivos Específicos

- Integrar información proveniente de archivos CSV, Excel, JSON, SQLite y una API REST.
- Implementar un proceso ETL reproducible y automatizado.
- Aplicar reglas de limpieza y validación para garantizar la calidad de los datos.
- Diseñar un modelo relacional y un modelo dimensional.
- Construir un Data Warehouse utilizando PostgreSQL (Supabase).
- Elaborar consultas SQL para análisis empresarial.
- Generar indicadores (KPIs) mediante Python y Pandas.
- Visualizar los resultados utilizando gráficos estadísticos.
- Documentar completamente la solución desarrollada.

---

# Tecnologías utilizadas

## Lenguajes

- Python 3
- SQL
- Markdown

## Bases de datos

- ## Bases de datos

- SQLite (fuente de datos)
- PostgreSQL (Supabase) - Data Warehouse

## Herramientas

- Python
- Jupyter Notebook
- Visual Studio Code
- Git
- GitHub
- Supabase

---

# Librerías utilizadas

| Librería       | Descripción                                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **pandas**     | Lectura, manipulación, limpieza e integración de los datos provenientes de las diferentes fuentes.                         |
| **numpy**      | Apoyo en operaciones numéricas y manejo eficiente de datos durante el proceso de transformación.                           |
| **os**         | Gestión y validación de rutas de archivos, verificando su existencia antes de procesarlos.                                 |
| **sqlite3**    | Conexión y extracción de la información almacenada en la base de datos SQLite del inventario.                              |
| **matplotlib** | Generación de gráficos y visualización de los KPIs obtenidos durante el análisis.                                          |
| **logging**    | Registro de eventos y seguimiento de la ejecución del proceso ETL para facilitar la depuración y monitoreo.                |
| **json**       | Lectura y procesamiento de los archivos JSON utilizados como fuente de datos, así como de la respuesta de la API simulada. |



---

# Estructura del proyecto

```
Proyecto-Capstone/

│
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── warehouse/
│
├── notebooks/
│   └── Proyecto_Final_Capstone.ipynb
│
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_inserts.sql
│   ├── 03_views.sql
│   └── 04_consultas.sql
│
├── src/
│   ├── main.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── utils.py
│
├── docs/
│   ├── arquitectura.md
│   ├── modelo_relacional.md
│   ├── modelo_estrella.md
│   ├── diccionario_datos.md
│   ├── reglas_calidad.md
│
├── dashboard/
│
|── reporte/
│   ├── Reporte_Final.pdf
|
├── README.md
├── requirements.txt
├── .gitignore

```

---

# Cómo ejecutar el proyecto

## 1. Clonar el repositorio

```bash
git clone (url-del-repositorio)
```

## 2. Acceder al proyecto

```bash
cd Proyecto-Capstone
```

## 3. Crear un entorno virtual

```bash
python -m venv .venv
```

## 4. Activar el entorno virtual

### Powershell

```bash
.venv\Scripts\activate.ps1
```


## 5. Instalar las dependencias

```bash
pip install -r requirements.txt
```

## 6. Configurar las variables de entorno

Crear un archivo `.env` con las credenciales necesarias para la conexión a la base de datos.

Ejemplo:

```env
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

## 7. Ejecutar el proyecto

```bash
python src/main.py
```

---

# Cronograma de desarrollo

| Día | Actividades |
|------|-------------|
| Día 1 | Comprensión del negocio, análisis del problema, diseño de arquitectura, modelo relacional preliminar y planificación del proceso ETL. |
| Día 2 | Exploración de las fuentes de datos, análisis de calidad, limpieza, estandarización y documentación de hallazgos. |
| Día 3 | Integración de datos, construcción del modelo dimensional, creación del Data Warehouse y carga de información. |
| Día 4 | Desarrollo de consultas SQL analíticas, cálculo de KPIs con Python y generación de visualizaciones. |
| Día 5 | Elaboración del informe técnico, documentación final, dashboard, conclusiones y presentación del proyecto. |

---

# Estado del proyecto

En desarrollo.

Proyecto correspondiente al **Proyecto Final Integrador del curso de Ingeniería de Datos**, cuyo propósito es integrar los conocimientos adquiridos durante el curso en una solución empresarial completa de ingeniería de datos.