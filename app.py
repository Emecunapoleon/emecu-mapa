import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. Configuración y Estética
st.set_page_config(page_title="Mapa de Integrantes EMECU", layout="wide")

col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 1, 1])
with col_logo_2:
    st.image("https://i.postimg.cc/NfBWMzGC/Gran14-Napoleon-blanco.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>🗺️ Mapa Geográfico EMECU Táchira</h1>", unsafe_allow_html=True)

# 2. Coordenadas de Referencia (Táchira)
# Esto asigna un punto en el mapa según la ciudad registrada
COORDENADAS_MUNICIPIOS = {
    "San Cristóbal": [7.7667, -72.2250],
    "Rubio": [7.7000, -72.3500],
    "Táriba": [7.8200, -72.2200],
    "Cárdenas": [7.8000, -72.2000],
    "Junín": [7.6800, -72.3600]
}

# 3. Carga de Datos desde Google Sheets (CSV público)
# Usamos el ID de tu hoja que ya conocemos
SHEET_ID = "1r-U_9tbE4Q1OK0QllaM14yseq1T-eppb9cfrXo0lq3c"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def cargar_datos():
    try:
        df = pd.read_csv(URL_CSV)
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

df_integrantes = cargar_datos()

if df_integrantes is not None:
    # 4. Filtros en la barra lateral
    st.sidebar.header("Filtros de Visualización")
    filtro_catedra = st.sidebar.multiselect(
        "Filtrar por Cátedra:",
        options=df_integrantes["Cátedra"].unique(),
        default=df_integrantes["Cátedra"].unique()
    )

    df_filtrado = df_integrantes[df_integrantes["Cátedra"].isin(filtro_catedra)]

    # 5. Creación del Mapa
    # Centrado en el Táchira
    m = folium.Map(location=[7.7667, -72.2250], zoom_start=10, tiles="CartoDB positron")

    # Agregar marcadores
    for index, fila in df_filtrado.iterrows():
        ciudad = fila["Ciudad"]
        if ciudad in COORDENADAS_MUNICIPIOS:
            punto = COORDENADAS_MUNICIPIOS[ciudad]
            
            # Contenido del globo al hacer clic
            popup_text = f"""
            <b>Integrante:</b> {fila['Primer_Nombre']} {fila['Primer_Apellido']}<br>
            <b>Cátedra:</b> {fila['Cátedra']}<br>
            <b>Municipio:</b> {fila['Municipio']}
            """
            
            folium.Marker(
                location=punto,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{fila['Primer_Nombre']} - {fila['Cátedra']}",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

    # Mostrar el mapa en Streamlit
    st_folium(m, width=1200, height=600)

    # 6. Tabla de datos debajo del mapa
    st.markdown("### Listado de Integrantes Seleccionados")
    st.dataframe(df_filtrado[["Primer_Nombre", "Primer_Apellido", "Cátedra", "Ciudad", "Municipio"]], use_container_width=True)

else:
    st.warning("Aún no hay datos registrados para mostrar en el mapa.")
