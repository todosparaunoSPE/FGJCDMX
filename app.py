# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 09:51:35 2025

@author: jperezr
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------
# Simulación de datos
# -----------------------------
np.random.seed(42)
alcaldias = ['Álvaro Obregón', 'Coyoacán', 'Cuauhtémoc', 'Iztapalapa', 'Miguel Hidalgo', 'Tlalpan']
delitos = ['Robo a transeúnte', 'Homicidio', 'Lesiones', 'Secuestro', 'Extorsión']

n = 500
data = pd.DataFrame({
    'Fecha': [datetime.today() - timedelta(days=np.random.randint(0, 180)) for _ in range(n)],
    'Alcaldía': np.random.choice(alcaldias, n),
    'Tipo de delito': np.random.choice(delitos, n),
    'Latitud': np.random.uniform(19.2, 19.5, n),
    'Longitud': np.random.uniform(-99.25, -99.05, n)
})

# -----------------------------
# Interfaz Streamlit
# -----------------------------
st.set_page_config(page_title="Tablero Geoespacial FGJCDMX", layout="wide")
st.title("📍 Tablero Geoespacial de Incidencia Delictiva - CDMX")

st.sidebar.header("Filtros")
alcaldia_sel = st.sidebar.multiselect("Selecciona alcaldías", options=alcaldias, default=alcaldias)
delito_sel = st.sidebar.multiselect("Selecciona tipo de delito", options=delitos, default=delitos)
fecha_ini = st.sidebar.date_input("Fecha inicio", value=datetime.today() - timedelta(days=60))
fecha_fin = st.sidebar.date_input("Fecha fin", value=datetime.today())

st.sidebar.markdown("---")
st.sidebar.header("ℹ️ Ayuda")
st.sidebar.info("""
Filtra por alcaldía, tipo de delito y rango de fechas. 
Los resultados se mostrarán en el mapa, gráfico de barras y tabla.
""")

st.sidebar.markdown("---")
st.sidebar.caption("Creado por Javier Horacio Pérez Ricárdez")

# -----------------------------
# Filtrado de datos
# -----------------------------
data_filtrada = data[
    (data['Alcaldía'].isin(alcaldia_sel)) &
    (data['Tipo de delito'].isin(delito_sel)) &
    (data['Fecha'] >= pd.to_datetime(fecha_ini)) &
    (data['Fecha'] <= pd.to_datetime(fecha_fin))
]

# Asignar color por tipo de delito
color_map = {
    'Robo a transeúnte': [255, 0, 0, 160],
    'Homicidio': [0, 0, 255, 160],
    'Lesiones': [0, 255, 0, 160],
    'Secuestro': [255, 255, 0, 160],
    'Extorsión': [255, 165, 0, 160]
}
data_filtrada['color'] = data_filtrada['Tipo de delito'].map(color_map)

# -----------------------------
# Mapa interactivo con Pydeck
# -----------------------------
st.subheader("🗺️ Mapa de incidentes")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=19.35,
        longitude=-99.15,
        zoom=10,
        pitch=40,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=data_filtrada,
            get_position='[Longitud, Latitud]',
            get_fill_color='color',
            get_radius=250,
            pickable=True,
        )
    ],
    tooltip={
        "html": "<b>Delito:</b> {Tipo de delito}<br/><b>Alcaldía:</b> {Alcaldía}<br/><b>Fecha:</b> {Fecha}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
))

# -----------------------------
# Gráfico de barras
# -----------------------------
st.subheader("📊 Delitos por alcaldía")
conteo = data_filtrada.groupby(['Alcaldía', 'Tipo de delito']).size().reset_index(name='Total')
fig = px.bar(conteo, x='Alcaldía', y='Total', color='Tipo de delito', barmode='group', height=400)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Mostrar tabla de datos
# -----------------------------
with st.expander("🔍 Ver datos filtrados"):
    st.dataframe(data_filtrada.reset_index(drop=True))

# -----------------------------
# Descarga de datos filtrados
# -----------------------------
@st.cache_data
def convertir_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convertir_csv(data_filtrada)
st.download_button("📥 Descargar datos filtrados", data=csv, file_name="datos_filtrados.csv", mime='text/csv')
