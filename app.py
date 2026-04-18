import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Mapa 3D EMECU Táchira", layout="wide")

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

# --- COORDENADAS PRECISAS PARA EL TÁCHIRA ---
# Para que las barras se vean separadas, lo ideal es que cada registro tenga 
# latitud y longitud propia. Si solo tienes "Ciudad", las barras se encimarán.
coords_municipios = {
    "San Cristóbal": {"lat": 7.7667, "lon": -72.2250},
    "Rubio": {"lat": 7.7000, "lon": -72.3500},
    "Táriba": {"lat": 7.8200, "lon": -72.2200},
    "Cárdenas": {"lat": 7.8000, "lon": -72.2000},
    "Junín": {"lat": 7.6800, "lon": -72.3600}
}

if df is not None:
    # 1. Asignar coordenadas al DataFrame
    df['lat'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lat'))
    df['lon'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lon'))
    
    # Limpiar datos sin coordenadas
    df = df.dropna(subset=['lat', 'lon'])

    # 2. Agrupar por ciudad para calcular la altura de las barras
    # Contamos cuántos estudiantes hay por cada punto geográfico
    df_counts = df.groupby(['lat', 'lon', 'Ciudad']).size().reset_index(name='cantidad')

    # --- DISEÑO DE LA PÁGINA ---
    st.title("📊 Análisis de Densidad Territorial EMECU (3D)")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.subheader("Estadísticas")
        st.metric("Total Integrantes", len(df))
        st.write("La altura de las barras representa la concentración de hermanos en la zona.")

    with col2:
        # 3. CONFIGURACIÓN DE PYDECK (EL MAPA 3D)
        view_state = pdk.ViewState(
            latitude=7.7667,
            longitude=-72.2250,
            zoom=10,
            pitch=45, # Ángulo de inclinación para el efecto 3D
            bearing=0
        )

        layer = pdk.Layer(
            "ColumnLayer",
            data=df_counts,
            get_position='[lon, lat]',
            get_elevation='cantidad', # Altura basada en la cantidad de personas
            elevation_scale=100,      # Multiplicador de altura (ajusta según necesites)
            radius=200,               # Ancho de la barrita
            get_fill_color=[49, 130, 206, 200], # Color azul EMECU (RGBA)
            pickable=True,
            auto_highlight=True,
        )

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10", # Fondo oscuro tecnológico
            initial_view_state=view_state,
            layers=[layer],
            tooltip={
                "html": "<b>Ciudad:</b> {Ciudad}<br><b>Integrantes:</b> {cantidad}",
                "style": {"color": "white"}
            }
        ))

else:
    st.error("No se pudieron cargar los datos para el renderizado 3D.")
