import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# 1. Configuración de la página
st.set_page_config(page_title="Mapa Geográfico EMECU", layout="wide")

# Estética de cabecera
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 1, 1])
with col_logo_2:
    st.image("https://i.postimg.cc/NfBWMzGC/Gran14-Napoleon-blanco.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>🗺️ Sistema de Gestión Territorial EMECU</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Visualización de Integrantes y Análisis de Datos - Táchira 2026</p>", unsafe_allow_html=True)

# 2. Coordenadas de Referencia
COORDENADAS_MUNICIPIOS = {
    "San Cristóbal": [7.7667, -72.2250],
    "Rubio": [7.7000, -72.3500],
    "Táriba": [7.8200, -72.2200],
    "Cárdenas": [7.8000, -72.2000],
    "Junín": [7.6800, -72.3600]
}

# 3. Carga de Datos (ID de tu hoja)
SHEET_ID = "1r-U_9tbE4Q1OK0QllaM14yseq1T-eppb9cfrXo0lq3c"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def cargar_datos():
    try:
        df = pd.read_csv(URL_CSV)
        # Limpieza básica de nombres de columnas por si acaso
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

df_raw = cargar_datos()

if df_raw is not None:
    # --- BARRA LATERAL (Buscador y Filtros) ---
    st.sidebar.header("🔍 Buscador y Filtros")
    
    # Buscador por nombre o cédula
    busqueda = st.sidebar.text_input("Buscar por Nombre o Cédula:")
    
    # Filtro de Cátedra
    opciones_catedra = sorted(df_raw["Cátedra"].unique().tolist())
    filtro_catedra = st.sidebar.multiselect("Filtrar por Cátedra:", opciones_catedra, default=opciones_catedra)

    # Aplicar Filtros
    df_filtrado = df_raw[df_raw["Cátedra"].isin(filtro_catedra)]
    if busqueda:
        df_filtrado = df_filtrado[
            df_filtrado["Primer_Nombre"].str.contains(busqueda, case=False, na=False) | 
            df_filtrado["Cedula_Identidad"].astype(str).str.contains(busqueda, na=False)
        ]

    # --- SECCIÓN DE ESTADÍSTICAS (KPIs) ---
    st.markdown("---")
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Total Integrantes", len(df_filtrado))
    with kpi2:
        num_catedras = len(df_filtrado["Cátedra"].unique())
        st.metric("Cátedras Activas", num_catedras)
    with kpi3:
        municipio_top = df_filtrado["Municipio"].mode()[0] if not df_filtrado.empty else "N/A"
        st.metric("Municipio Mayoritario", municipio_top)

    # --- MAPA CON CLUSTERING ---
    st.markdown("### Ubicación Geográfica")
    
    # Centro del mapa basado en el primer resultado o Táchira general
    centro = [7.7667, -72.2250]
    m = folium.Map(location=centro, zoom_start=11, tiles="CartoDB positron")
    
    # Crear el cluster (Agrupamiento)
    marker_cluster = MarkerCluster().add_to(m)

    for _, fila in df_filtrado.iterrows():
        ciudad = fila["Ciudad"]
        if ciudad in COORDENADAS_MUNICIPIOS:
            coord = COORDENADAS_MUNICIPIOS[ciudad]
            
            # Popup con diseño
            info = f"""
            <div style='font-family: Arial; font-size: 12px;'>
                <b>{fila['Primer_Nombre']} {fila['Primer_Apellido']}</b><br>
                <hr style='margin: 5px 0;'>
                <b>Cátedra:</b> {fila['Cátedra']}<br>
                <b>Municipio:</b> {fila['Municipio']}<br>
                <b>Celular:</b> {fila['Celular']}
            </div>
            """
            
            folium.Marker(
                location=coord,
                popup=folium.Popup(info, max_width=250),
                tooltip=f"{fila['Primer_Nombre']} ({fila['Cátedra']})",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(marker_cluster)

    # Mostrar Mapa
    st_folium(m, width="100%", height=500)

    # --- TABLA DE DETALLES ---
    with st.expander("Ver tabla detallada de integrantes"):
        st.write(df_filtrado)

else:
    st.info("Esperando datos de la encuesta...")
