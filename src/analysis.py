import pandas as pd
import pandas_gbq
import sqlite3
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

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
    print(f"==============================================\n INICIANDO GENERACIÓN DE DASHBOARD - {ENV}\n==============================================")
    os.makedirs("reports", exist_ok=True)
    bq_prefix = f"`{GCP_PROJECT_ID}.{BQ_DATASET}`." if ENV == "PRODUCCION" else ""

    # 1. Ventas por Categoría (Top 10)
    query_cat = f"SELECT p.Categoria, SUM(v.Total_Ingreso) as Ingresos_Totales FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimProducto p ON v.FK_Producto = p.SK_Producto GROUP BY p.Categoria ORDER BY Ingresos_Totales DESC LIMIT 10;"
    df_cat = execute_query(query_cat, "-> 1/5 Generando KPI: Top Categorías...")
    if not df_cat.empty:
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_cat, y='Categoria', x='Ingresos_Totales', hue='Categoria', palette='viridis', legend=False)
        plt.title('Top 10 Categorías por Ingreso Total')
        plt.xlabel('Ingresos ($)')
        plt.tight_layout()
        plt.savefig('reports/1_kpi_categorias.png')
        plt.close()

    # 2. Ticket Promedio por Segmento (Top 10)
    query_cli = f"SELECT c.Segmento, SUM(v.Total_Ingreso) / NULLIF(COUNT(v.ID_Venta), 0) as Ticket_Promedio FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimCliente c ON v.FK_Cliente = c.SK_Cliente WHERE c.SK_Cliente != 999 GROUP BY c.Segmento ORDER BY Ticket_Promedio DESC LIMIT 10;"
    df_cli = execute_query(query_cli, "-> 2/5 Generando KPI: Ticket Promedio...")
    if not df_cli.empty:
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_cli, x='Segmento', y='Ticket_Promedio', hue='Segmento', palette='magma', legend=False)
        plt.title('Top 10 Segmentos con Mayor Ticket Promedio')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Ticket Promedio ($)')
        plt.tight_layout()
        plt.savefig('reports/2_kpi_ticket_promedio.png')
        plt.close()

    # 3. Tendencia de Ventas en el Tiempo (Por Mes)
    query_tendencia = f"SELECT t.Anio, t.Mes, SUM(v.Total_Ingreso) as Ingresos_Mensuales FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimTiempo t ON v.Fecha_Key = t.Fecha GROUP BY t.Anio, t.Mes ORDER BY t.Anio, t.Mes;"
    df_tendencia = execute_query(query_tendencia, "-> 3/5 Generando KPI: Tendencia de Ventas...")
    if not df_tendencia.empty:
        df_tendencia['Periodo'] = df_tendencia['Anio'].astype(str) + "-" + df_tendencia['Mes'].astype(str).str.zfill(2)
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df_tendencia, x='Periodo', y='Ingresos_Mensuales', marker='o', linewidth=2, color='b')
        plt.title('Tendencia de Ingresos Mensuales')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Ingresos ($)')
        plt.tight_layout()
        plt.savefig('reports/3_kpi_tendencia_ventas.png')
        plt.close()

    # 4. Rendimiento de Marketing (ACTUALIZADO PARA FORZAR GRÁFICO)
    query_mkt = f"""
        SELECT c.Plataforma, c.Costo as Costo_Campana, COALESCE(SUM(v.Total_Ingreso), 0) as Ingresos_Generados 
        FROM {bq_prefix}DimCampana c 
        LEFT JOIN {bq_prefix}FactVentas v ON CAST(c.SK_Campana AS STRING) = CAST(v.FK_Campana AS STRING) 
        WHERE c.SK_Campana != 'SIN_CAMPANA' 
        GROUP BY c.Plataforma, c.Costo;
    """
    df_mkt = execute_query(query_mkt, "-> 4/5 Generando KPI: ROI Marketing...")
    
    if not df_mkt.empty:
        # Llenamos cualquier posible vacío con 0 para asegurar que se grafique
        df_mkt['Ingresos_Generados'] = df_mkt['Ingresos_Generados'].fillna(0)
        
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_mkt, x='Costo_Campana', y='Ingresos_Generados', hue='Plataforma', s=200)
        plt.title('Costo de Campaña vs Ingresos Generados (Alerta de ROI)')
        plt.ylabel('Ingresos Generados ($)')
        plt.xlabel('Costo de la Campaña ($)')
        plt.tight_layout()
        plt.savefig('reports/4_kpi_marketing_roi.png')
        plt.close()
        print("   [Gráfico 4 generado: Mostrando ingresos nulos como $0]")
    else:
        print("   [!] Aviso: No hay datos de campañas en absoluto.")
    
    # 5. Alerta de Inventario (Top 10 Productos con Ventas Altas y Stock Bajo)
    query_inv = f"SELECT p.Nombre_Producto, i.existencia as Stock_Actual, SUM(v.Cantidad_Unidades) as Unidades_Vendidas FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimProducto p ON v.FK_Producto = p.SK_Producto INNER JOIN {bq_prefix}DimInventarioActual i ON p.SK_Producto = i.producto_id GROUP BY p.Nombre_Producto, i.existencia HAVING i.existencia < 50 ORDER BY Unidades_Vendidas DESC LIMIT 10;"
    df_inv = execute_query(query_inv, "-> 5/5 Generando KPI: Alerta de Inventario...")
    if not df_inv.empty:
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_inv, y='Nombre_Producto', x='Stock_Actual', color='salmon')
        plt.title('Alerta: Top 10 Productos Más Vendidos con Stock Crítico (< 50)')
        plt.xlabel('Stock Actual (Unidades)')
        plt.tight_layout()
        plt.savefig('reports/5_kpi_alerta_inventario.png')
        plt.close()

    print("\n==============================================")
    print(" ¡Dashboard completado! 5 gráficas listas en 'reports/'.")
    print("==============================================")

if __name__ == "__main__":
    run_analysis()