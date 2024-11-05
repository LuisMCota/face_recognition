import streamlit as st
from streamlit_option_menu import option_menu
from api_utils import fetch_attendance_data, send_image_for_prediction, register_student
from attendance_utils import apply_filters, display_totals, display_attendance_chart
from style import set_styles
import pandas as pd

set_styles()

# Función para mostrar el panel de asistencia
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

# Inicializa el estado de la sesión para controlar la captura de la foto
if "photo_taken" not in st.session_state:
    st.session_state["photo_taken"] = False
if "retry_photo" not in st.session_state:
    st.session_state["retry_photo"] = False

# Función para tomar asistencia con foto
def tomar_asistencia():
    st.title("Tomar Asistencia")

    # Captura de foto
    foto_asistencia = st.camera_input("Foto de asistencia")
    
    if foto_asistencia:
        # Mostrar la imagen capturada para confirmación visual
        st.image(foto_asistencia, caption="Foto Capturada para Verificación", use_column_width=True)
        st.session_state["photo_taken"] = True  # Activar el estado de foto capturada

    # Botón "Volver a tomar foto" siempre disponible
    if st.button("Volver a tomar foto"):
        st.session_state["photo_taken"] = False
        st.experimental_rerun()  # Recargar para limpiar la foto capturada

    # Botón "Pasar Asistencia" solo activo si se ha capturado una foto
    if st.session_state["photo_taken"]:
        if st.button("Pasar Asistencia"):
            # Llamar a la función de predicción para identificar al usuario
            nombre_identificado, estado = send_image_for_prediction(foto_asistencia)
            
            # Verificar si el nombre fue identificado correctamente
            if nombre_identificado and nombre_identificado.lower() not in ["unknown", "desconocido"]:
                st.success(f"Asistencia registrada para: {nombre_identificado} - Estado: {estado}")
                st.session_state["photo_taken"] = False  # Resetear el estado de captura
            else:
                # Mostrar mensaje de error si el usuario no fue identificado o si hubo un error
                st.error("⚠️ Usuario no identificado o asistencia no verificada.")
                st.session_state["photo_taken"] = False  # Permitir nuevo intento de captura
                st.experimental_rerun()

# Función para registrar un nuevo alumno
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
