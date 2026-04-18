import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configuración de la interfaz
st.set_page_config(page_title="Mapa Territorial EMECU - Táchira", layout="wide")

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

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* Filtro para que el logo sea visible en modo claro de móviles */
    @media (prefers-color-scheme: light) {
        .logo-img { filter: invert(1) brightness(0.2); }
    }
    .nombre-escuela {
        color: #1E88E5;
        text-align: center;
        font-size: 1.8rem !important;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .titulo-mapa {
        color: #5d6d7e;
        text-align: center;
        font-size: 1.4rem !important;
        font-weight: 500;
        margin-top: 0px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA INSTITUCIONAL ---
col_a, col_b, col_c = st.columns([1, 0.8, 1])
with col_b:
    # Logo centrado y tamaño moderado
    st.markdown(f'<div style="text-align: center;"><img src="https://i.postimg.cc/NfBWMzGC/Gran14-Napoleon-blanco.png" class="logo-img" style="width: 100px;"></div>', unsafe_allow_html=True)

st.markdown("<p class='nombre-escuela'>Escuela Magnético Espiritual de la Comuna Universal (EMECU)</p>", unsafe_allow_html=True)
st.markdown("<p class='titulo-mapa'>Mapa de Densidad Territorial EMECU del Estado Táchira</p>", unsafe_allow_html=True)

df = cargar_datos()

# Coordenadas base de los municipios
coords_municipios = {
    "San Cristóbal": {"lat": 7.7667, "lon": -72.2250},
    "Rubio": {"lat": 7.7000, "lon": -72.3500},
    "Táriba": {"lat": 7.8200, "lon": -72.2200},
    "Cárdenas": {"lat": 7.8000, "lon": -72.2000},
    "Junín": {"lat": 7.6800, "lon": -72.3600}
}

if df is not None:
    # 1. Procesar coordenadas
    df['lat'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lat'))
    df['lon'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, {}).get('lon'))
    df = df.dropna(subset=['lat', 'lon'])
    
    # 2. Agrupar por ciudad
    df_counts = df.groupby(['lat', 'lon', 'Ciudad']).size().reset_index(name='cantidad')

    # 3. Crear el Mapa con Plotly
    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lat=df_counts['lat'],
        lon=df_counts['lon'],
        mode='markers+text',
        marker=go.scattermapbox.Marker(
            size=df_counts['cantidad'] * 15 + 15, # Tamaño escalable
            color='#1E88E5',
            opacity=0.7,
        ),
        text=df_counts['Ciudad'],
        textposition="top right",
        hoverinfo='text',
        hovertext=[f"<b>{c}</b><br>Integrantes: {q}" for c, q in zip(df_counts['Ciudad'], df_counts['cantidad'])]
    ))

    # Configuración de diseño con OpenStreetMap
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            center=go.layout.mapbox.Center(lat=7.7667, lon=-72.2250),
            zoom=10,
            pitch=45
        ),
        height=650,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
    st.success(f"Visualización activa: {len(df)} registro(s) detectado(s).")
else:
    st.error("Error al conectar con la base de datos de Google Sheets.")
