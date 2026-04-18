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

# --- COORDENADAS ---
coords_municipios = {
    "San Cristóbal": {"lat": 7.7667, "lon": -72.2250},
    "Rubio": {"lat": 7.7000, "lon": -72.3500},
    "Táriba": {"lat": 7.8200, "lon": -72.2200},
    "Cárdenas": {"lat": 7.8000, "lon": -72.2000},
    "Junín": {"lat": 7.6800, "lon": -72.3600}
}

st.title("📊 Mapa 3D de Alta Visibilidad - EMECU")

if df is not None:
    df['lat'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lat'))
    df['lon'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lon'))
    df = df.dropna(subset=['lat', 'lon'])
    df_counts = df.groupby(['lat', 'lon', 'Ciudad']).size().reset_index(name='cantidad')

    # --- EL TRUCO PARA EL COLOR ---
    # Definimos el mapa base como una constante de Deck.gl que NO usa Mapbox
    COPIER_PLATE = {
        "version": 8,
        "sources": {
            "osm": {
                "type": "raster",
                "tiles": ["https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"],
                "tileSize": 256,
                "attribution": "&copy; OpenStreetMap contributors"
            }
        },
        "layers": [
            {
                "id": "osm",
                "type": "raster",
                "source": "osm",
                "minzoom": 0,
                "maxzoom": 19
            }
        ]
    }

    view_state = pdk.ViewState(
        latitude=7.7667, longitude=-72.2250, zoom=10, pitch=55, bearing=0
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=df_counts,
        get_position='[lon, lat]',
        get_elevation='cantidad',
        elevation_scale=1000, # Barra bien alta para que se note
        radius=400,
        get_fill_color=[0, 102, 204, 230], # Azul Rey llamativo
        pickable=True,
        auto_highlight=True,
    )

    # Renderizado forzando el estilo manual
    st.pydeck_chart(pdk.Deck(
        map_style=COPIER_PLATE, # <--- Esto fuerza los colores de OpenStreetMap
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Ciudad: {Ciudad}\nHermanos: {cantidad}"}
    ))
else:
    st.write("Cargando...")
