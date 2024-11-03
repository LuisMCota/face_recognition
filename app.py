import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import numpy as np
import requests
from PIL import Image
import uuid

st.set_page_config(page_title="Facial Recognition & Attendance", page_icon="👤", layout="wide")
st.markdown(
    """
    <style>
        .main {
            background-color: #F5EEF8;
            color: #4A148C;
        }
        .css-18e3th9 {
            padding: 1rem;
            background-color: #FF7043 !important;
        }
        .css-1d391kg {
            color: #4A148C !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Define the base URL of your API server (update this to ngrok link when needed)
api_base_url = "https://a2a2-2806-10b7-3-c248-285f-e846-87cf-3e85.ngrok-free.app"

# Function to display attendance records
def mostrar_asistencia():
    st.title("Registro de Asistencia")
    
    api_url = f"{api_base_url}/get_attendance_records"
    try:
        response = requests.get(api_url)
        data = response.json()

        if response.status_code == 200:
            attendance_records = data.get('records', [])
            if attendance_records:
                # Convert records to a DataFrame and display it
                df = pd.DataFrame(attendance_records)
                st.write("Historial de Asistencia")
                st.dataframe(df)

                # Display attendance statistics
                if 'Status' in df.columns:
                    status_counts = df['Status'].value_counts()
                    st.write("Estadísticas de Asistencia")
                    st.bar_chart(status_counts)
            else:
                st.warning("No hay registros de asistencia disponibles.")
        else:
            st.error("No se pudo obtener los registros de asistencia.")
    except Exception as e:
        st.error(f"Error en la conexión con el servidor: {e}")

# Attendance-taking function
def tomar_asistencia():
    st.title("Tomar Asistencia")
    st.write("Captura una foto para verificar la asistencia:")
    foto_asistencia = st.camera_input("Foto de asistencia")

    if foto_asistencia:
        st.image(foto_asistencia, caption="Foto Capturada para Verificación", use_column_width=True)
        img_byte_arr = io.BytesIO()
        image = Image.open(foto_asistencia)
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        api_url = f"{api_base_url}/predict_image"
        
        try:
            response = requests.post(api_url, files={"file": img_byte_arr})
            response_data = response.json()
            
            if response.status_code == 200:
                student_name = response_data['prediction']
                st.success(f"Asistencia registrada para: {student_name}")
            else:
                st.error("No se pudo verificar la asistencia. Intente nuevamente.")
        except Exception as e:
            st.error(f"Error en la conexión con el servidor: {e}")
    else:
        st.info("Por favor, capture una foto para verificar la asistencia.")

# Student registration function
def agregar_alumno():
    st.title("Agregar Nuevo Alumno")
    
    # Input fields for name and tuition ID
    nombre_alumno = st.text_input("Nombre del Alumno")
    tuition_id = st.text_input("Tuition ID del Alumno")
    foto_alumno = st.camera_input("Captura una foto del alumno")

    if st.button("Registrar Alumno"):
        if nombre_alumno and tuition_id and foto_alumno:
            # Convert the captured image to bytes for the API request
            img_byte_arr = io.BytesIO()
            image = Image.open(foto_alumno)
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Define the API endpoint for retraining
            api_url = f"{api_base_url}/retrain"
            
            # Send POST request with the image, name, and tuition ID
            try:
                response = requests.post(
                    api_url,
                    files={"image": ("image.jpg", img_byte_arr, "image/jpeg")},
                    data={"label": nombre_alumno, "tuition_id": tuition_id}
                )
                
                # Check for successful retraining response
                if response.status_code == 200:
                    st.success(f"Alumno '{nombre_alumno}' registrado y modelo actualizado con TuitionID: {tuition_id}.")
                else:
                    st.error("Error al registrar el alumno. Intente nuevamente.")
            except Exception as e:
                st.error(f"Error en la conexión con el servidor: {e}")
        else:
            st.warning("Por favor, ingrese el nombre del alumno, su Tuition ID y capture una foto.")

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Menú Principal",
        options=["Panel General", "Información del Alumno", "Agregar Alumno", "Tomar Asistencia", "Mostrar Asistencia"],
        icons=["house", "person-circle", "person-plus", "camera", "clipboard-data"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#E6E6FA"},
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

# Route based on selected option
if selected == "Tomar Asistencia":
    tomar_asistencia()
elif selected == "Agregar Alumno":
    agregar_alumno()
elif selected == "Mostrar Asistencia":
    mostrar_asistencia()
