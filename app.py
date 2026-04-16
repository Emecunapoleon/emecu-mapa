import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(page_title="Mapa EMECU Táchira", layout="wide")

# URL de datos
SHEET_ID = "1r-U_9tbE4Q1OK0QllaM14yseq1T-eppb9cfrXo0lq3c"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def cargar_datos():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return None

df = cargar_datos()

# --- BARRA LATERAL: ESTADÍSTICAS Y FILTROS ---
with st.sidebar:
    st.image("https://i.postimg.cc/NfBWMzGC/Gran14-Napoleon-blanco.png", width=100)
    st.title("Estadísticas Globales")
    
    if df is not None:
        st.metric("Total Integrantes", len(df))
        st.metric("Cátedras", len(df["Cátedra"].unique()))
        
        st.markdown("---")
        st.subheader("Filtrar Mapa")
        busqueda = st.text_input("Buscar por nombre/cédula:")
        catedras = sorted(df["Cátedra"].unique().tolist())
        sel_catedras = st.multiselect("Cátedras:", catedras, default=catedras)
    else:
        st.error("No se detectaron datos.")

# --- CUERPO PRINCIPAL ---
st.markdown("<h2 style='text-align: center;'>🗺️ Mapa Geográfico EMECU</h2>", unsafe_allow_html=True)

if df is not None:
    # Aplicar filtros
    df_f = df[df["Cátedra"].isin(sel_catedras)]
    if busqueda:
        df_f = df_f[df_f["Primer_Nombre"].str.contains(busqueda, case=False, na=False) | 
                    df_f["Cedula_Identidad"].astype(str).str.contains(busqueda, na=False)]

    # Mapa
    COORD_Tachira = [7.7667, -72.2250]
    m = folium.Map(location=COORD_Tachira, zoom_start=11, tiles="CartoDB positron")
    cluster = MarkerCluster().add_to(m)

    # Diccionario de coordenadas básico
    coords = {"San Cristóbal": [7.7667, -72.2250], "Rubio": [7.7000, -72.3500], 
              "Táriba": [7.8200, -72.2200], "Cárdenas": [7.8000, -72.2000], "Junín": [7.6800, -72.3600]}

    for _, fila in df_f.iterrows():
        ciudad = fila["Ciudad"]
        if ciudad in coords:
            folium.Marker(
                location=coords[ciudad],
                popup=f"<b>{fila['Primer_Nombre']}</b><br>{fila['Cátedra']}",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(cluster)

    st_folium(m, width="100%", height=600)
