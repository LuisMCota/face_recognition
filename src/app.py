import streamlit as st
from streamlit_option_menu import option_menu
from src.api_utils import fetch_attendance_data, send_image_for_prediction, register_student
from attendance_utils import apply_filters, display_totals, display_attendance_chart
from style import set_styles
import pandas as pd
import firebase_admin
from firebase_admin import credentials, initialize_app
from dotenv import load_dotenv
import os

load_dotenv()

# Crear el objeto de credenciales a partir de las variables de entorno
cred = credentials.Certificate({
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
})

# Inicializar la app de Firebase si no está ya inicializada
if not firebase_admin._apps:
    initialize_app(cred)
    
set_styles()

# Panel de asistencia
def mostrar_asistencia():
    st.title("Registro de Asistencia")
    df = fetch_attendance_data()
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
        filtered_df = apply_filters(df)
        display_totals(filtered_df)
        display_attendance_chart(filtered_df)
    else:
        st.warning("No hay registros de asistencia disponibles.")

# Toma de asistencia con foto
def tomar_asistencia():
    st.title("Tomar Asistencia")
    foto_asistencia = st.camera_input("Foto de asistencia")
    if foto_asistencia:
        st.image(foto_asistencia, caption="Foto Capturada para Verificación", use_column_width=True)
        nombre_identificado, estado = send_image_for_prediction(foto_asistencia)
        
        if nombre_identificado:
            st.success(f"Asistencia registrada para: {nombre_identificado} - Estado: {estado}")
        else:
            st.error("No se pudo verificar la asistencia. Intente nuevamente.")

# Registro de nuevo alumno
def agregar_alumno():
    st.title("Agregar Nuevo Alumno")
    nombre_alumno = st.text_input("Nombre completo del Alumno")
    tuition_id = st.text_input("Tuition ID del Alumno")
    foto_alumno = st.camera_input("Captura una foto del alumno")
    
    if st.button("Registrar Alumno") and nombre_alumno and tuition_id and foto_alumno:
        exito, mensaje = register_student(nombre_alumno, tuition_id, foto_alumno)
        if exito:
            st.success(mensaje)
        else:
            st.error(mensaje)

# Menú de navegación y lógica de enrutamiento
with st.sidebar:
    selected = option_menu(
        menu_title="Menú Principal",
        options=["Panel General", "Agregar Alumno", "Tomar Asistencia"],
        icons=["house", "person-plus", "camera"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#B0B0B0"},
            "icon": {"color": "#FFA500", "font-size": "20px"},
            "nav-link": {
                "font-size": "18px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#B39DDB",
            },
            "nav-link-selected": {"background-color": "#8A2BE2"},
        }
    )

# Lógica de enrutamiento según la selección del menú
if selected == "Tomar Asistencia":
    tomar_asistencia()
elif selected == "Agregar Alumno":
    agregar_alumno()
elif selected == "Panel General":
    mostrar_asistencia()
