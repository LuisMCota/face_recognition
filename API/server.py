import joblib
from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from deepface import DeepFace
import io
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import os
import cv2
import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Acceder a las variables de entorno para AWS
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_default_region = os.getenv("AWS_DEFAULT_REGION")
bucket_name = "modelsfaceapp"  # Reemplaza con el nombre de tu bucket S3

# Inicializar el cliente S3
s3_client = boto3.client(
    's3',
    region_name=aws_default_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Función para descargar y cargar los archivos desde S3 en memoria
def load_file_from_s3(s3_key):
    file_stream = io.BytesIO()
    try:
        s3_client.download_fileobj(bucket_name, s3_key, file_stream)
        file_stream.seek(0)  # Reiniciar el puntero del archivo
        return joblib.load(file_stream)
    except ClientError as e:
        print(f"Error al descargar {s3_key} desde S3: {e}")
        return None

# Función para subir archivos a S3
def upload_file_to_s3(obj, s3_key):
    file_stream = io.BytesIO()
    joblib.dump(obj, file_stream)  # Guarda el objeto en el buffer de memoria
    file_stream.seek(0)  # Reinicia el puntero del archivo
    try:
        s3_client.upload_fileobj(file_stream, bucket_name, s3_key)
        print(f"Archivo {s3_key} subido exitosamente a S3.")
    except ClientError as e:
        print(f"Error al subir {s3_key} a S3: {e}")

# Nombres de los archivos en S3
model_s3_key = "svm_model.pkl"
encoder_s3_key = "label_encoder.pkl"
embeddings_s3_key = "X_embeddings.pkl"
labels_s3_key = "y_labels.pkl"

# Cargar el modelo, el codificador, los embeddings y las etiquetas directamente desde S3 en memoria
svm_model = load_file_from_s3(model_s3_key) or SVC(kernel='linear', probability=True)
label_encoder = load_file_from_s3(encoder_s3_key) or LabelEncoder()
X_embeddings = load_file_from_s3(embeddings_s3_key)
y_labels = load_file_from_s3(labels_s3_key)

# Verificar si todos los archivos se cargaron correctamente
if any([svm_model is None, label_encoder is None, X_embeddings is None, y_labels is None]):
    print("Error al cargar uno o más archivos desde S3. Verifique los archivos en el bucket y las credenciales.")
else:
    print("Archivos cargados exitosamente desde S3.")

    # Verificar si el modelo está entrenado
    if not hasattr(svm_model, "support_"):  # Comprueba si el modelo SVC ha sido entrenado
        print("El modelo SVC no está entrenado. Procediendo a entrenar el modelo.")
        label_encoder.fit(y_labels)
        y_encoded = label_encoder.transform(y_labels)
        svm_model.fit(X_embeddings, y_encoded)
        print("El modelo SVC ha sido entrenado.")

# Inicializar DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name=aws_default_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
students_table = dynamodb.Table('Students')
attendance_table = dynamodb.Table('Attendance')

# Cargar mapeo de PredictedIdentifier a TuitionID
predicted_to_tuition = {}

def load_predicted_to_tuition_mapping():
    response = students_table.scan()
    for item in response.get('Items', []):
        predicted_identifier = item.get('PredictedIdentifier')
        tuition_id = item.get('TuitionID')
        if predicted_identifier and tuition_id:
            predicted_to_tuition[predicted_identifier] = tuition_id

load_predicted_to_tuition_mapping()

# Función para generar embeddings
def generate_embedding(image):
    img_np = np.array(image)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    embedding = DeepFace.represent(img_path=img_rgb, model_name="Facenet", detector_backend="mtcnn", enforce_detection=False)[0]['embedding']
    return np.array(embedding)

# Función para determinar el estado de asistencia
def get_class_status():
    current_time = datetime.now().time()
    class_start = datetime.strptime("14:00", "%H:%M").time()
    class_end = datetime.strptime("20:45", "%H:%M").time()
    
    if current_time < class_start:
        return "missed"
    elif current_time > class_end:
        return "missed"
    elif current_time < datetime.strptime("14:15", "%H:%M").time():
        return "attended"
    else:
        return "tardy"

@app.route('/predict_image', methods=['POST'])
def predict_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    image = Image.open(file.stream)
    embedding = generate_embedding(image)
    
    try:
        # Predicción
        prediction = svm_model.predict([embedding])[0]
        print(f"Prediction result: {prediction}")

        if prediction in label_encoder.classes_:
            predicted_identifier = prediction
        else:
            predicted_identifier = label_encoder.inverse_transform([int(prediction)])[0]

        # Buscar el TuitionID en función del PredictedIdentifier
        tuition_id = predicted_to_tuition.get(predicted_identifier, None)
        correct_name = 'Unknown'
        if tuition_id:
            response = students_table.get_item(Key={'TuitionID': tuition_id})
            correct_name = response['Item'].get('CorrectName', 'Unknown') if 'Item' in response else 'Unknown'

        status = get_class_status()
        
        # Generar y registrar la asistencia en DynamoDB
        record_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        attendance_item = {
            'RecordID': record_id,
            'StudentID': str(predicted_identifier),
            'Timestamp': timestamp,
            'Status': status,
            'CorrectName': correct_name
        }
        attendance_table.put_item(Item=attendance_item)
        print(f"Attendance recorded for {correct_name} with status {status}.")

        return jsonify({'prediction': correct_name, 'status': status, 'timestamp': timestamp})

    except Exception as e:
        print(f"Error in prediction flow: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    if 'image' not in request.files or 'label' not in request.form:
        return jsonify({'error': 'Image and label data are required'}), 400

    # Extrae imagen y etiqueta
    image_file = request.files['image']
    label = request.form['label']
    tuition_id = request.form.get('tuition_id', f"temp_{str(uuid.uuid4())[:8]}")
    image = Image.open(image_file.stream)
    new_embedding = generate_embedding(image)

    try:
        # Cargar embeddings y etiquetas existentes
        X_existing = X_embeddings if X_embeddings is not None else np.empty((0, len(new_embedding)))
        y_existing = y_labels if y_labels is not None else np.array([])

        # Añadir datos nuevos y reentrenar
        X = np.vstack([X_existing, [new_embedding]])
        y = np.hstack([y_existing, [label]])
        label_encoder.fit(y)
        y_encoded = label_encoder.transform(y)
        
        svm_model.fit(X, y_encoded)

        # Subir archivos a S3
        upload_file_to_s3(svm_model, model_s3_key)
        upload_file_to_s3(label_encoder, encoder_s3_key)
        upload_file_to_s3(X, embeddings_s3_key)
        upload_file_to_s3(y, labels_s3_key)

        # Registrar estudiante en DynamoDB
        if label not in predicted_to_tuition:
            students_table.put_item(
                Item={
                    "TuitionID": tuition_id,
                    "CorrectName": label,
                    "PredictedIdentifier": label
                }
            )
            predicted_to_tuition[label] = tuition_id
            print(f"Estudiante {label} agregado a DynamoDB con TuitionID: {tuition_id}.")

        return jsonify({'status': f"Estudiante '{label}' registrado y modelo actualizado."})

    except Exception as e:
        print(f"Error durante el reentrenamiento: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint para obtener registros de asistencia
@app.route('/get_attendance_records', methods=['GET'])
def get_attendance_records():
    try:
        response = attendance_table.scan()
        records = response.get('Items', [])
        return jsonify({'records': records})
    except ClientError as e:
        print(f"Error fetching attendance records: {e}")
        return jsonify({'error': 'Failed to fetch attendance records.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
