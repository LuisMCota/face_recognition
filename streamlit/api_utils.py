import requests
import io
from PIL import Image
import pandas as pd

api_base_url = "http://192.168.1.83:10000"

def fetch_attendance_data():
    try:
        response = requests.get(f"{api_base_url}/get_attendance_records")
        response.raise_for_status()
        return pd.DataFrame(response.json().get('records', []))
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame()

def send_image_for_prediction(image_file):
    img_byte_arr = io.BytesIO()
    Image.open(image_file).save(img_byte_arr, format='JPEG')
    try:
        response = requests.post(f"{api_base_url}/predict_image", files={"file": img_byte_arr.getvalue()})
        response.raise_for_status()
        # Obtener tanto el nombre identificado como el estado
        data = response.json()
        return data.get('prediction', 'Desconocido'), data.get('status', 'Sin estado')
    except Exception as e:
        print(f"Error en la conexión con el servidor: {e}")
        return None, None

def register_student(nombre_alumno, tuition_id, image_file):
    img_byte_arr = io.BytesIO()
    Image.open(image_file).save(img_byte_arr, format='JPEG')
    try:
        response = requests.post(
            f"{api_base_url}/retrain",
            files={"image": ("image.jpg", img_byte_arr.getvalue(), "image/jpeg")},
            data={"label": nombre_alumno, "tuition_id": tuition_id}
        )
        response.raise_for_status()
        return True, f"Alumno '{nombre_alumno}' registrado con éxito."
    except Exception as e:
        print(f"Error al registrar alumno: {e}")
        return False, f"Error al registrar alumno '{nombre_alumno}': {e}"
