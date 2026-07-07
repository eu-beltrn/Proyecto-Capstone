import streamlit as st
import pandas as pd
import pandas_gbq
import sqlite3
import os
import sys
import plotly.express as px

# Asegura que Python pueda ver la carpeta raíz donde está config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import ENV, DWH_PATH, GCP_PROJECT_ID, BQ_DATASET

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="DataCommerce GT | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# FUNCIÓN DE CONSULTA CON CACHÉ (NIVEL SENIOR)
# ==========================================
# El caché evita volver a consultar BigQuery (ahorrando dinero y tiempo) 
# a menos que pase 1 hora (3600 segundos) o se limpie manualmente.
@st.cache_data(ttl=3600)
def execute_query(query):
    bq_prefix = f"`{GCP_PROJECT_ID}.{BQ_DATASET}`." if ENV == "PRODUCCION" else ""
    query = query.format(bq_prefix=bq_prefix)
    
    if ENV == "PRODUCCION":
        return pandas_gbq.read_gbq(query, project_id=GCP_PROJECT_ID)
    else:
        conn = sqlite3.connect(DWH_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

# ==========================================
# INTERFAZ DE USUARIO (UI)
# ==========================================
def main():
    # BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2942/2942269.png", width=100) # Icono de ejemplo
        st.title("DataCommerce GT")
        st.caption(f"Entorno actual: **{ENV}**")
        st.markdown("---")
        st.markdown("Panel de control ejecutivo conectado directamente al Data Warehouse.")
        
        if st.button("🔄 Actualizar Datos"):
            st.cache_data.clear()
            st.rerun()

    # ENCABEZADO PRINCIPAL
    st.title("📊 Dashboard Ejecutivo Integral")
    st.markdown("Análisis de Ventas, Marketing e Inventario")
    st.divider()

    # ==========================================
    # EXTRACCIÓN DE DATOS (KPIs)
    # ==========================================
    with st.spinner("Cargando datos desde el Data Warehouse..."):
        
        # Consultas SQL optimizadas
        df_cat = execute_query("SELECT p.Categoria, SUM(v.Total_Ingreso) as Ingresos_Totales FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimProducto p ON v.FK_Producto = p.SK_Producto GROUP BY p.Categoria ORDER BY Ingresos_Totales DESC LIMIT 10;")
        df_cli = execute_query("SELECT c.Segmento, SUM(v.Total_Ingreso) / NULLIF(COUNT(v.ID_Venta), 0) as Ticket_Promedio FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimCliente c ON v.FK_Cliente = c.SK_Cliente WHERE c.SK_Cliente != 999 GROUP BY c.Segmento ORDER BY Ticket_Promedio DESC LIMIT 10;")
        df_tendencia = execute_query("SELECT t.Anio, t.Mes, SUM(v.Total_Ingreso) as Ingresos_Mensuales FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimTiempo t ON v.Fecha_Key = t.Fecha GROUP BY t.Anio, t.Mes ORDER BY t.Anio, t.Mes;")
        df_mkt = execute_query("SELECT c.Plataforma, c.Costo as Costo_Campana, COALESCE(SUM(v.Total_Ingreso), 0) as Ingresos_Generados FROM {bq_prefix}DimCampana c LEFT JOIN {bq_prefix}FactVentas v ON CAST(c.SK_Campana AS STRING) = CAST(v.FK_Campana AS STRING) WHERE c.SK_Campana != 'SIN_CAMPANA' GROUP BY c.Plataforma, c.Costo;")
        df_inv = execute_query("SELECT p.Nombre_Producto, i.existencia as Stock_Actual, SUM(v.Cantidad_Unidades) as Unidades_Vendidas FROM {bq_prefix}FactVentas v INNER JOIN {bq_prefix}DimProducto p ON v.FK_Producto = p.SK_Producto INNER JOIN {bq_prefix}DimInventarioActual i ON p.SK_Producto = i.producto_id GROUP BY p.Nombre_Producto, i.existencia HAVING i.existencia < 50 ORDER BY Unidades_Vendidas DESC LIMIT 10;")

    # ==========================================
    # CONSTRUCCIÓN DE GRÁFICOS (PLOTLY) Y LAYOUT
    # ==========================================
    
    # FILA 1: TENDENCIA TEMPORAL (Ancho completo)
    if not df_tendencia.empty:
        df_tendencia['Periodo'] = df_tendencia['Anio'].astype(str) + "-" + df_tendencia['Mes'].astype(str).str.zfill(2)
        fig_tendencia = px.line(df_tendencia, x='Periodo', y='Ingresos_Mensuales', markers=True, 
                                title="📈 Tendencia de Ingresos Mensuales",
                                labels={'Ingresos_Mensuales': 'Ingresos ($)'},
                                color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_tendencia, use_container_width=True)

    # FILA 2: CATEGORÍAS Y SEGMENTOS (2 Columnas)
    col1, col2 = st.columns(2)
    
    with col1:
        if not df_cat.empty:
            fig_cat = px.bar(df_cat, x='Ingresos_Totales', y='Categoria', orientation='h',
                             title="🏆 Top 10 Categorías por Ingreso",
                             labels={'Ingresos_Totales': 'Ingresos ($)', 'Categoria': ''},
                             color='Ingresos_Totales', color_continuous_scale='Viridis')
            fig_cat.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        if not df_cli.empty:
            fig_cli = px.bar(df_cli, x='Segmento', y='Ticket_Promedio',
                             title="🎯 Ticket Promedio por Segmento",
                             labels={'Ticket_Promedio': 'Ticket Promedio ($)', 'Segmento': ''},
                             color='Ticket_Promedio', color_continuous_scale='Magma')
            fig_cli.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_cli, use_container_width=True)

    # FILA 3: MARKETING Y OPERACIONES (2 Columnas)
    st.divider()
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("💡 Rendimiento de Marketing (ROI)")
        if not df_mkt.empty:
            df_mkt['Ingresos_Generados'] = df_mkt['Ingresos_Generados'].fillna(0)
            fig_mkt = px.scatter(df_mkt, x='Costo_Campana', y='Ingresos_Generados', color='Plataforma',
                                 size='Costo_Campana', hover_data=['Plataforma'],
                                 title="Costo de Campaña vs Ingresos Generados",
                                 labels={'Costo_Campana': 'Inversión ($)', 'Ingresos_Generados': 'Retorno ($)'})
            st.plotly_chart(fig_mkt, use_container_width=True)
            
            # Alerta visual en Streamlit si el ROI es 0
            if df_mkt['Ingresos_Generados'].sum() == 0:
                st.error("⚠️ **Alerta Crítica:** Las campañas muestran inversión pero 0 conversión cruzada con ventas. Revisar integraciones de UTMs.")

    with col4:
        st.subheader("📦 Alertas Operativas (Inventario)")
        if not df_inv.empty:
            fig_inv = px.bar(df_inv, x='Stock_Actual', y='Nombre_Producto', orientation='h',
                             title="Top Productos Más Vendidos con Stock < 50",
                             labels={'Stock_Actual': 'Unidades Disponibles', 'Nombre_Producto': ''},
                             color_discrete_sequence=['#EF553B'])
            fig_inv.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_inv, use_container_width=True)
        else:
            st.success("✅ No hay alertas críticas de inventario actualmente.")

if __name__ == "__main__":
    main()