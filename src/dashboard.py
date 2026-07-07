import streamlit as st
import pandas as pd
import pandas_gbq
import sqlite3
import os
import sys
import plotly.express as px
import concurrent.futures

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

def execute_query(query):
    """Ejecuta una consulta individual en BigQuery o SQLite."""
    bq_prefix = f"`{GCP_PROJECT_ID}.{BQ_DATASET}`." if ENV == "PRODUCCION" else ""
    query = query.format(bq_prefix=bq_prefix)
    
    if ENV == "PRODUCCION":
        return pandas_gbq.read_gbq(query, project_id=GCP_PROJECT_ID)
    else:
        conn = sqlite3.connect(DWH_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

@st.cache_data(ttl=3600)
def load_all_data(anio_filtro, categoria_filtro):
    filtros_sql = "1=1" 
    
    if anio_filtro != "Todos":
        filtros_sql += f" AND t.Anio = {anio_filtro}"
    if categoria_filtro != "Todas":
        filtros_sql += f" AND p.Categoria = '{categoria_filtro}'"

    queries = {
        "cat": f"""
            SELECT p.Categoria, SUM(v.Total_Ingreso) as Ingresos_Totales 
            FROM {{bq_prefix}}FactVentas v 
            INNER JOIN {{bq_prefix}}DimProducto p ON v.FK_Producto = p.SK_Producto 
            INNER JOIN {{bq_prefix}}DimTiempo t ON v.Fecha_Key = t.Fecha
            WHERE {filtros_sql}
            GROUP BY p.Categoria ORDER BY Ingresos_Totales DESC LIMIT 10;
        """,
        "cli": f"""
            SELECT c.Segmento, SUM(v.Total_Ingreso) / NULLIF(COUNT(v.ID_Venta), 0) as Ticket_Promedio 
            FROM {{bq_prefix}}FactVentas v 
            INNER JOIN {{bq_prefix}}DimCliente c ON v.FK_Cliente = c.SK_Cliente 
            INNER JOIN {{bq_prefix}}DimProducto p ON v.FK_Producto = p.SK_Producto
            INNER JOIN {{bq_prefix}}DimTiempo t ON v.Fecha_Key = t.Fecha
            WHERE c.SK_Cliente != 999 AND {filtros_sql}
            GROUP BY c.Segmento ORDER BY Ticket_Promedio DESC LIMIT 10;
        """,
        "tendencia": f"""
            SELECT t.Anio, t.Mes, SUM(v.Total_Ingreso) as Ingresos_Mensuales 
            FROM {{bq_prefix}}FactVentas v 
            INNER JOIN {{bq_prefix}}DimProducto p ON v.FK_Producto = p.SK_Producto
            INNER JOIN {{bq_prefix}}DimTiempo t ON v.Fecha_Key = t.Fecha 
            WHERE {filtros_sql}
            GROUP BY t.Anio, t.Mes ORDER BY t.Anio, t.Mes;
        """,
        # SOLUCIÓN SENIOR: CTE para calcular ingresos filtrados antes del LEFT JOIN
        "mkt": f"""
            WITH VentasFiltradas AS (
                SELECT v.FK_Campana, SUM(v.Total_Ingreso) as Ingresos_Generados
                FROM {{bq_prefix}}FactVentas v
                INNER JOIN {{bq_prefix}}DimProducto p ON v.FK_Producto = p.SK_Producto
                INNER JOIN {{bq_prefix}}DimTiempo t ON v.Fecha_Key = t.Fecha
                WHERE {filtros_sql}
                GROUP BY v.FK_Campana
            )
            SELECT 
                cmp.Plataforma, 
                SUM(cmp.Costo) as Costo_Campana, 
                COALESCE(SUM(vf.Ingresos_Generados), 0) as Ingresos_Generados 
            FROM {{bq_prefix}}DimCampana cmp 
            LEFT JOIN VentasFiltradas vf ON CAST(cmp.SK_Campana AS STRING) = CAST(vf.FK_Campana AS STRING) 
            WHERE cmp.SK_Campana != 'SIN_CAMPANA' 
            GROUP BY cmp.Plataforma;
        """,
        "inv": f"""
            SELECT p.Nombre_Producto, i.existencia as Stock_Actual, SUM(v.Cantidad_Unidades) as Unidades_Vendidas 
            FROM {{bq_prefix}}FactVentas v 
            INNER JOIN {{bq_prefix}}DimProducto p ON v.FK_Producto = p.SK_Producto 
            INNER JOIN {{bq_prefix}}DimInventarioActual i ON p.SK_Producto = i.producto_id 
            INNER JOIN {{bq_prefix}}DimTiempo t ON v.Fecha_Key = t.Fecha
            WHERE {filtros_sql}
            GROUP BY p.Nombre_Producto, i.existencia 
            HAVING i.existencia < 50 ORDER BY Unidades_Vendidas DESC LIMIT 10;
        """
    }
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_name = {executor.submit(execute_query, q): name for name, q in queries.items()}
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = future.result()
            except Exception as exc:
                st.error(f"Error en {name}: {exc}")
                results[name] = pd.DataFrame()
                
    return results

def main():
    with st.sidebar:
        st.title("DataCommerce GT")
        st.caption(f"Entorno: **{ENV}**")
        st.markdown("---")
        
        st.subheader("🔍 Filtros Globales")
        filtro_anio = st.selectbox("📅 Año Fiscal", ["Todos", "2026", "2025", "2024"])
        filtro_cat = st.selectbox("🏷️ Categoría de Producto", 
                                  ["Todas", "COMPUTO", "MONITORES", "ACCESORIOS", "IMPRESION", "REDES", "SEGURIDAD"])
        
        st.markdown("---")
        if st.button("🧹 Limpiar Caché"):
            st.cache_data.clear()
            st.success("Caché limpiado")
            st.rerun()

    st.title("📊 Dashboard Ejecutivo Integral")
    
    if filtro_anio != "Todos" or filtro_cat != "Todas":
        st.info(f"Filtros Activos 👉 **Año:** {filtro_anio} | **Categoría:** {filtro_cat}")
    st.divider()

    with st.spinner("Procesando consultas en BigQuery..."):
        data = load_all_data(filtro_anio, filtro_cat)
        
    df_cat = data.get("cat", pd.DataFrame())
    df_cli = data.get("cli", pd.DataFrame())
    df_tendencia = data.get("tendencia", pd.DataFrame())
    df_mkt = data.get("mkt", pd.DataFrame())
    df_inv = data.get("inv", pd.DataFrame())

    if not df_tendencia.empty:
        df_tendencia['Periodo'] = df_tendencia['Anio'].astype(str) + "-" + df_tendencia['Mes'].astype(str).str.zfill(2)
        fig_tendencia = px.line(df_tendencia, x='Periodo', y='Ingresos_Mensuales', markers=True, 
                                title="📈 Tendencia de Ingresos Mensuales",
                                labels={'Ingresos_Mensuales': 'Ingresos ($)', 'Periodo': 'Mes'},
                                color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_tendencia, use_container_width=True)

    col1, col2 = st.columns(2)
    
    with col1:
        if not df_cat.empty:
            fig_cat = px.bar(df_cat, x='Ingresos_Totales', y='Categoria', orientation='h',
                             title="🏆 Top 10 Categorías por Ingreso",
                             color='Ingresos_Totales', color_continuous_scale='Viridis')
            fig_cat.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.warning("No hay ventas para esta combinación de filtros.")

    with col2:
        if not df_cli.empty:
            fig_cli = px.bar(df_cli, x='Segmento', y='Ticket_Promedio',
                             title="🎯 Ticket Promedio por Segmento",
                             color='Ticket_Promedio', color_continuous_scale='Magma')
            fig_cli.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_cli, use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("💡 Rendimiento de Marketing (ROI)")
        if not df_mkt.empty:
            df_mkt['Ingresos_Generados'] = df_mkt['Ingresos_Generados'].fillna(0)
            
            # SOLUCIÓN DE PLOTLY: Eliminamos el 'size' dinámico y lo forzamos a un tamaño visual estándar
            fig_mkt = px.scatter(df_mkt, x='Costo_Campana', y='Ingresos_Generados', color='Plataforma',
                                 hover_data=['Plataforma'],
                                 title="Costo vs Retorno de Campañas")
            
            fig_mkt.update_traces(marker=dict(size=14, line=dict(width=2, color='DarkSlateGrey')))
            
            st.plotly_chart(fig_mkt, use_container_width=True)
            
            if df_mkt['Ingresos_Generados'].sum() == 0:
                st.error("⚠️ Alerta: Las campañas muestran inversión pero 0 conversión cruzada con ventas bajo estos filtros.")
        else:
            st.warning("No hay datos de campañas registrados.")

    with col4:
        st.subheader("📦 Alertas Operativas (Inventario)")
        if not df_inv.empty:
            fig_inv = px.bar(df_inv, x='Stock_Actual', y='Nombre_Producto', orientation='h',
                             title="Top Productos Críticos (Stock < 50)",
                             color_discrete_sequence=['#EF553B'])
            fig_inv.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_inv, use_container_width=True)
        else:
            st.success("✅ Stock saludable para los filtros seleccionados.")

if __name__ == "__main__":
    main()