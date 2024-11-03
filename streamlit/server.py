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

app = Flask(__name__)

# Paths to model, encoder, and embeddings
MODEL_PATH = "./models/svm_model.pkl"
ENCODER_PATH = "./models/label_encoder.pkl"
EMBEDDINGS_PATH = "./models/X_embeddings.pkl"
LABELS_PATH = "./models/y_labels.pkl"

# Initialize DynamoDB resources
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
students_table = dynamodb.Table('Students')
attendance_table = dynamodb.Table('Attendance')

# Load or initialize the model and encoder
try:
    svm_model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    print("Model and label encoder loaded successfully.")
except Exception as e:
    print(f"Error loading model or encoder: {str(e)}")
    svm_model = SVC(kernel='linear', probability=True)
    label_encoder = LabelEncoder()

# Load PredictedIdentifier to TuitionID mapping
predicted_to_tuition = {}

def load_predicted_to_tuition_mapping():
    response = students_table.scan()
    for item in response.get('Items', []):
        predicted_identifier = item.get('PredictedIdentifier')
        tuition_id = item.get('TuitionID')
        if predicted_identifier and tuition_id:
            predicted_to_tuition[predicted_identifier] = tuition_id

# Load mapping at startup
load_predicted_to_tuition_mapping()

# Function to generate embeddings
def generate_embedding(image):
    img_np = np.array(image)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    embedding = DeepFace.represent(img_path=img_rgb, model_name="Facenet", detector_backend="mtcnn", enforce_detection=False)[0]['embedding']
    return np.array(embedding)

# Function to determine class status based on current time
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
        # Predict label based on the embedding
        prediction = svm_model.predict([embedding])[0]
        print(f"Prediction result: {prediction}")

        # Decode label or handle integer prediction
        if prediction in label_encoder.classes_:
            predicted_identifier = prediction
        else:
            predicted_identifier = label_encoder.inverse_transform([int(prediction)])[0]

        print(f"Using PredictedIdentifier: {predicted_identifier}")

        # Find TuitionID based on PredictedIdentifier
        tuition_id = predicted_to_tuition.get(predicted_identifier, None)
        if tuition_id:
            # Fetch CorrectName from DynamoDB using TuitionID
            response = students_table.get_item(Key={'TuitionID': tuition_id})
            if 'Item' in response:
                correct_name = response['Item'].get('CorrectName', 'Unknown')
                print(f"Fetched CorrectName: {correct_name}")
            else:
                correct_name = 'Unknown'
                print(f"Student with TuitionID '{tuition_id}' not found in DynamoDB.")
        else:
            correct_name = 'Unknown'
            print(f"PredictedIdentifier '{predicted_identifier}' not found in mapping.")

        # Determine class status
        status = get_class_status()
        
        # Generate a unique RecordID
        record_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Log attendance in DynamoDB
        attendance_item = {
            'RecordID': record_id,   # Primary key for Attendance table
            'StudentID': str(predicted_identifier),
            'Timestamp': timestamp,
            'Status': status,
            'CorrectName': correct_name
        }
        try:
            attendance_table.put_item(Item=attendance_item)
            print(f"Attendance recorded for {correct_name} with status {status}.")
        except ClientError as e:
            print(f"Error logging attendance to DynamoDB: {e}")
            return jsonify({'error': 'Failed to log attendance.'}), 500

        return jsonify({'prediction': correct_name, 'status': status, 'timestamp': timestamp})

    except Exception as e:
        print(f"Error in prediction flow: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    if 'image' not in request.files or 'label' not in request.form:
        return jsonify({'error': 'Image and label data are required'}), 400

    # Extract image and label
    image_file = request.files['image']
    label = request.form['label']
    tuition_id = request.form.get('tuition_id', f"temp_{str(uuid.uuid4())[:8]}")  # Generate TuitionID if not provided
    image = Image.open(image_file.stream)
    new_embedding = generate_embedding(image)

    try:
        # Load existing embeddings and labels
        if os.path.exists(EMBEDDINGS_PATH) and os.path.exists(LABELS_PATH):
            X_existing = joblib.load(EMBEDDINGS_PATH)
            y_existing = joblib.load(LABELS_PATH)
        else:
            X_existing, y_existing = np.empty((0, len(new_embedding))), np.array([])

        # Append new data and retrain
        X = np.vstack([X_existing, [new_embedding]])
        y = np.hstack([y_existing, [label]])
        label_encoder.fit(y)
        y_encoded = label_encoder.transform(y)
        
        svm_model.fit(X, y_encoded)
        joblib.dump(svm_model, MODEL_PATH)
        joblib.dump(label_encoder, ENCODER_PATH)
        joblib.dump(X, EMBEDDINGS_PATH)
        joblib.dump(y, LABELS_PATH)

        # Add the new student to DynamoDB
        if label not in predicted_to_tuition:
            try:
                students_table.put_item(
                    Item={
                        "TuitionID": tuition_id,
                        "CorrectName": label,
                        "PredictedIdentifier": label
                    }
                )
                predicted_to_tuition[label] = tuition_id  # Update the local mapping
                print(f"Added {label} to DynamoDB with TuitionID: {tuition_id}.")
            except ClientError as e:
                print(f"Error adding student to DynamoDB: {e}")
                return jsonify({'error': 'Failed to add student to DynamoDB'}), 500

        return jsonify({'status': f"Student '{label}' registered and model updated."})

    except Exception as e:
        print(f"Error during retraining: {e}")
        return jsonify({'error': str(e)}), 500

    load_predicted_to_tuition_mapping()  # Refresh mapping after retrain

# New endpoint to fetch attendance records
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
