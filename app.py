import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configuración de la interfaz
st.set_page_config(page_title="Mapa 3D EMECU - Táchira", layout="wide")

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

# Coordenadas base
coords_municipios = {
    "San Cristóbal": {"lat": 7.7667, "lon": -72.2250},
    "Rubio": {"lat": 7.7000, "lon": -72.3500},
    "Táriba": {"lat": 7.8200, "lon": -72.2200},
    "Cárdenas": {"lat": 7.8000, "lon": -72.2000},
    "Junín": {"lat": 7.6800, "lon": -72.3600}
}

st.title("📊 Análisis Territorial EMECU (3D)")

if df is not None:
    # Preparar datos
    df['lat'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lat'))
    df['lon'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lon'))
    df = df.dropna(subset=['lat', 'lon'])
    df_counts = df.groupby(['lat', 'lon', 'Ciudad']).size().reset_index(name='cantidad')

    # --- CREACIÓN DEL MAPA CON PLOTLY ---
    # Usamos Scattermapbox pero con un estilo que resalte
    fig = go.Figure()

    # Añadimos los puntos como burbujas 3D (el tamaño depende de la cantidad)
    fig.add_trace(go.Scattermapbox(
        lat=df_counts['lat'],
        lon=df_counts['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=df_counts['cantidad'] * 20, # Tamaño de la burbuja
            color='#0077b6',                # Azul llamativo
            opacity=0.7
        ),
        text=df_counts['Ciudad'] + ": " + df_counts['cantidad'].astype(str) + " hermanos",
        hoverinfo='text'
    ))

    # Configuramos el diseño del mapa para que sea "OpenStreetMap" (GRATIS)
    fig.update_layout(
        mapbox_style="open-street-map", # <--- ESTO ES GRATIS Y TIENE COLORES
        hovermode='closest',
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=7.7667,
                lon=-72.2250
            ),
            pitch=60, # Inclinación para el efecto visual
            zoom=10
        ),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.info("Nota: Debido a restricciones de seguridad de las librerías de mapas, hemos migrado a un motor de visualización abierto. Los círculos representan la densidad de hermanos por ciudad.")

else:
    st.error("No se pudieron cargar los datos.")
