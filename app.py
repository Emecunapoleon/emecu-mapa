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
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

df = cargar_datos()

# --- COORDENADAS DE LOS MUNICIPIOS (Táchira) ---
coords_municipios = {
    "San Cristóbal": {"lat": 7.7667, "lon": -72.2250},
    "Rubio": {"lat": 7.7000, "lon": -72.3500},
    "Táriba": {"lat": 7.8200, "lon": -72.2200},
    "Cárdenas": {"lat": 7.8000, "lon": -72.2000},
    "Junín": {"lat": 7.6800, "lon": -72.3600},
    "Otro": {"lat": 7.7667, "lon": -72.2250} # Coordenada de respaldo
}

# --- TÍTULO Y LEYENDA CENTRALIZADA ---
st.title("📊 Análisis de Densidad Territorial EMECU (3D)")
st.info("Visualización 3D del Estado Táchira. El fondo claro y los colores de alta visibilidad facilitan la lectura.")

if df is not None:
    # 1. Asignar coordenadas al DataFrame
    # Usamos .get() con un valor predeterminado para evitar errores de KeyError
    df['lat'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, coords_municipios["Otro"])['lat'])
    df['lon'] = df['Ciudad'].map(lambda x: coords_municipios.get(x, coords_municipios["Otro"])['lon'])
    
    # Limpiar datos que puedan tener coordenadas nulas por algún error
    df = df.dropna(subset=['lat', 'lon'])

    # 2. Agrupar por ubicación para calcular la altura de las barras (3D)
    df_counts = df.groupby(['lat', 'lon', 'Ciudad']).size().reset_index(name='cantidad')

    # --- CUERPO PRINCIPAL ---
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.subheader("Estado Actual")
        st.metric("Total Hermanos Registrados", len(df))
        st.write("La altura de las barras azules representa la concentración de integrantes en el punto geográfico.")
        st.caption("Nota: Para que las barras se dispersen, cada registro debe tener latitud/longitud única. Por ahora se agrupan por Ciudad.")

    with col2:
        # --- CONFIGURACIÓN DE LA VISTA (Cámara 3D) ---
        view_state = pdk.ViewState(
            latitude=7.7667,
            longitude=-72.2250,
            zoom=10,
            pitch=50,  # Inclinación para el efecto 3D
            bearing=0   # Rotación de la brújula
        )

        # --- CAPA 1: EL MAPA BASE (CartoDB Positron - Libre de API) ---
        # Este es el truco para ver ríos, carreteras y montañas con colores vivos
        base_layer = pdk.Layer(
            "TileLayer",
            "https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
            pickable=False,
        )

        # --- CAPA 2: LAS BARRAS 3D (ColumnLayer) ---
        column_layer = pdk.Layer(
            "ColumnLayer",
            data=df_counts,
            get_position='[lon, lat]',
            get_elevation='cantidad',  # Altura basada en la cantidad
            elevation_scale=800,       # Escala alta para que la barrita de 1 persona sea visible
            radius=400,                # Ancho de la barra
            get_fill_color=[49, 130, 206, 220], # Azul intenso con transparencia
            pickable=True,
            auto_highlight=True,
        )

        # --- RENDERIZADO DEL MAPA ---
        # Combinamos ambas capas: la base y las barras
        st.pydeck_chart(pdk.Deck(
            map_style=None, # IMPORTANTE: Al ser None, no pide API de Mapbox
            initial_view_state=view_state,
            layers=[base_layer, column_layer], # <--- AQUÍ ESTÁ LA SOLUCIÓN
            tooltip={
                "html": "<b>Ciudad:</b> {Ciudad}<br><b>Integrantes:</b> {cantidad}",
                "style": {"color": "white", "backgroundColor": "#2e5077"}
            }
        ))

else:
    st.error("No se pudieron cargar los datos del censo...")
