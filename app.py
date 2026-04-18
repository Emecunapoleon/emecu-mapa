import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configuración de la interfaz
st.set_page_config(page_title="Mapa Territorial EMECU - Táchira", layout="wide")

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

# Coordenadas base de los municipios del Táchira
coords_municipios = {
    "San Cristóbal": {"lat": 7.7667, "lon": -72.2250},
    "Rubio": {"lat": 7.7000, "lon": -72.3500},
    "Táriba": {"lat": 7.8200, "lon": -72.2200},
    "Cárdenas": {"lat": 7.8000, "lon": -72.2000},
    "Junín": {"lat": 7.6800, "lon": -72.3600}
}

st.title("🗺️ Mapa de Densidad Territorial EMECU")

if df is not None:
    # 1. Procesar coordenadas
    df['lat'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lat'))
    df['lon'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lon'))
    df = df.dropna(subset=['lat', 'lon'])
    
    # 2. Agrupar por ciudad
    df_counts = df.groupby(['lat', 'lon', 'Ciudad']).size().reset_index(name='cantidad')

    # 3. Crear el Mapa con Plotly (Estilo Libre)
    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lat=df_counts['lat'],
        lon=df_counts['lon'],
        mode='markers+text',
        marker=go.scattermapbox.Marker(
            size=df_counts['cantidad'] * 15 + 10, # Tamaño base + crecimiento por cantidad
            color='#1E88E5', # Azul vibrante
            opacity=0.8,
            # Efecto de borde para que resalte
        ),
        text=df_counts['Ciudad'],
        textposition="top right",
        hoverinfo='text',
        hovertext=[f"<b>{c}</b><br>Integrantes: {q}" for c, q in zip(df_counts['Ciudad'], df_counts['cantidad'])]
    ))

    # Configuración del diseño
    fig.update_layout(
        mapbox_style="open-street-map", # <--- El mapa con colores, ríos y calles (Gratis)
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            center=go.layout.mapbox.Center(lat=7.7667, lon=-72.2250),
            zoom=10,
            pitch=40 # Mantenemos algo de inclinación para que no sea totalmente plano
        ),
        height=700,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"Visualizando {len(df)} registro(s) en el Estado Táchira.")

else:
    st.error("No se pudo cargar la base de datos de Google Sheets.")
