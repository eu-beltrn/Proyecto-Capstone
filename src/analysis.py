import pandas as pd
import pandas_gbq
import sqlite3
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

# Añadir la ruta raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import ENV, DWH_PATH, GCP_PROJECT_ID, BQ_DATASET

sns.set_theme(style="whitegrid")

def execute_query(query, log_msg="Ejecutando consulta..."):
    print(log_msg)
    if ENV == "PRODUCCION":
        return pandas_gbq.read_gbq(query, project_id=GCP_PROJECT_ID)
    else:
        conn = sqlite3.connect(DWH_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

def run_analysis():
    print(f"==============================================\n INICIANDO ANÁLISIS Y KPIs - {ENV}\n==============================================")
    os.makedirs("reports", exist_ok=True)
    bq_prefix = f"`{GCP_PROJECT_ID}.{BQ_DATASET}`." if ENV == "PRODUCCION" else ""

    # 1. KPI 1: Ventas por Categoría
    query_cat = f"SELECT p.Categoria, SUM(v.Cantidad_Unidades) as Unidades_Vendidas, SUM(v.Total_Ingreso) as Ingresos_Totales FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimProducto p ON v.FK_Producto = p.SK_Producto GROUP BY p.Categoria ORDER BY Ingresos_Totales DESC;"
    df_cat = execute_query(query_cat, "-> Calculando KPI 1: Ventas por Categoría...")
    
    if not df_cat.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_cat, x='Categoria', y='Ingresos_Totales', hue='Categoria', palette='viridis', legend=False)
        plt.title('Ingresos Totales por Categoría')
        plt.savefig('reports/kpi_ventas_categoria.png')
        plt.close()

    # 2. KPI 2: Rendimiento de Marketing
    query_mkt = f"SELECT c.Plataforma, c.Costo as Costo_Campana, COUNT(v.ID_Venta) as Total_Transacciones, SUM(v.Total_Ingreso) as Ingresos_Generados FROM {bq_prefix}DimCampana c LEFT JOIN {bq_prefix}FactVentas v ON CAST(c.SK_Campana AS STRING) = CAST(v.FK_Campana AS STRING) WHERE c.SK_Campana != 'SIN_CAMPANA' GROUP BY c.Plataforma, c.Costo;"
    df_mkt = execute_query(query_mkt, "-> Calculando KPI 2: Rendimiento de Marketing...")
    
    if not df_mkt.empty and df_mkt['Ingresos_Generados'].notna().any():
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_mkt, x='Costo_Campana', y='Ingresos_Generados', hue='Plataforma', s=200)
        plt.title('Costo de Campaña vs Ingresos Generados')
        plt.savefig('reports/kpi_marketing_roi.png')
        plt.close()

    # 3. KPI 3: Segmentación de Clientes
    query_cli = f"SELECT c.Segmento, COUNT(DISTINCT c.SK_Cliente) as Cantidad_Clientes, SUM(v.Total_Ingreso) as Ingresos_Totales, SUM(v.Total_Ingreso) / NULLIF(COUNT(v.ID_Venta), 0) as Ticket_Promedio FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimCliente c ON v.FK_Cliente = c.SK_Cliente WHERE c.SK_Cliente != 999 GROUP BY c.Segmento;"
    df_cli = execute_query(query_cli, "-> Calculando KPI 3: Análisis de Segmentos...")
    
    if not df_cli.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_cli, x='Segmento', y='Ticket_Promedio', hue='Segmento', palette='magma')
        plt.title('Ticket Promedio por Segmento de Cliente')
        plt.savefig('reports/kpi_ticket_promedio.png')
        plt.close()
        print("   [Gráficos guardados en carpeta 'reports/']")

    print("\n¡Análisis completado!")

if __name__ == "__main__":
    run_analysis()