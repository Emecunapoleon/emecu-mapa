import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Configuración de la interfaz
st.set_page_config(page_title="Mapa Territorial EMECU (3D)", layout="wide")

# URL de datos (Tu Google Sheet)
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

# --- COORDENADAS DE LOS MUNICIPIOS ---
coords_municipios = {
    "San Cristóbal": {"lat": 7.7667, "lon": -72.2250},
    "Rubio": {"lat": 7.7000, "lon": -72.3500},
    "Táriba": {"lat": 7.8200, "lon": -72.2200},
    "Cárdenas": {"lat": 7.8000, "lon": -72.2000},
    "Junín": {"lat": 7.6800, "lon": -72.3600}
}

st.title("📊 Análisis de Densidad Territorial EMECU (3D)")

if df is not None:
    # 1. Asignar coordenadas
    df['lat'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lat'))
    df['lon'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lon'))
    df = df.dropna(subset=['lat', 'lon'])

    # 2. Agrupar por ubicación
    df_counts = df.groupby(['lat', 'lon', 'Ciudad']).size().reset_index(name='cantidad')

    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.subheader("Estado Actual")
        st.metric("Hermanos Registrados", len(df))
        st.write("Visualización 3D del Estado Táchira.")
        st.markdown("---")
        st.caption("Nota: Se utiliza cartografía abierta (CartoDB) para evitar bloqueos de API.")

    with col2:
        # Configuración de la cámara
        view_state = pdk.ViewState(
            latitude=7.7667,
            longitude=-72.2250,
            zoom=10,
            pitch=50,
            bearing=0
        )

        # Capa de columnas 3D
        layer = pdk.Layer(
            "ColumnLayer",
            data=df_counts,
            get_position='[lon, lat]',
            get_elevation='cantidad',
            elevation_scale=800, # Ajusta esto para que las barras se vean más altas
            radius=400,
            get_fill_color=[49, 130, 206, 200], # Azul EMECU
            pickable=True,
            auto_highlight=True,
        )

        # RENDERIZADO CON MAPA BASE LIBRE
        # Usamos un estilo de mapa que no requiere Token de Mapbox
        st.pydeck_chart(pdk.Deck(
            map_style=None, # IMPORTANTE: Al ser None, usa el predeterminado de Deck.gl o CartoDB
            initial_view_state=view_state,
            layers=[layer],
            tooltip={
                "html": "<b>Ciudad:</b> {Ciudad}<br><b>Integrantes:</b> {cantidad}",
                "style": {"color": "white", "backgroundColor": "#2e5077"}
            }
        ))
else:
    st.warning("Cargando datos del censo...")
