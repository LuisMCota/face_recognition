import streamlit as st
from streamlit_option_menu import option_menu
from api_utils import fetch_attendance_data, send_image_for_prediction, register_student
from attendance_utils import apply_filters, display_totals, display_attendance_chart
from style import set_styles
import pandas as pd

set_styles()

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

def tomar_asistencia():
    st.title("Tomar Asistencia")
    foto_asistencia = st.camera_input("Foto de asistencia")
    if foto_asistencia:
        st.image(foto_asistencia, caption="Foto Capturada para Verificación", use_column_width=True)
        
        # Llamar a la función de predicción y recibir el nombre y el estado
        nombre_identificado, estado = send_image_for_prediction(foto_asistencia)
        
        if nombre_identificado:
            st.success(f"Asistencia registrada para: {nombre_identificado} - Estado: {estado}")
        else:
            st.error("No se pudo verificar la asistencia. Intente nuevamente.")

def agregar_alumno():
    st.title("Agregar Nuevo Alumno")
    nombre_alumno = st.text_input("Nombre completo del Alumno")
    tuition_id = st.text_input("Tuition ID del Alumno")
    foto_alumno = st.camera_input("Captura una foto del alumno")
    
    if st.button("Registrar Alumno") and nombre_alumno and tuition_id and foto_alumno:
        # Llamar a la función de registro y recibir éxito o error junto con el mensaje
        exito, mensaje = register_student(nombre_alumno, tuition_id, foto_alumno)
        
        # Mostrar mensaje de éxito o error
        if exito:
            st.success(mensaje)
        else:
            st.error(mensaje)
            
# Menú de la barra lateral
with st.sidebar:
        selected = option_menu(
            menu_title="Menú Principal",
            options=["Panel General", "Agregar Alumno", "Tomar Asistencia"],
            icons=["house", "person-plus", "camera"],
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
# Routing de las opciones del menú
if selected == "Tomar Asistencia":
    tomar_asistencia()
elif selected == "Agregar Alumno":
    agregar_alumno()
elif selected == "Panel General":
    mostrar_asistencia()
