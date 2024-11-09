# face_app

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Face recognition app for assistance list

# Classroom Attendance with Face Recognition

## Project Overview
This project is a classroom attendance system that utilizes facial recognition for tracking student attendance. The system is designed to streamline the attendance process by automatically identifying students through their facial features. The project is built with several integrated technologies for both backend and frontend functionality.

## Key Components

- **Flask API**: Used as the backend framework to handle API requests.
- **DeepFace FaceNet Model**: The face recognition model is based on the DeepFace FaceNet architecture.
- **Google Cloud Run**: Hosts the Flask API and manages scalable deployment.
- **Google Cloud Storage**: Stores the trained face recognition model, allowing it to be accessed and updated by the Cloud Run instance.
- **DynamoDB**: Serves as the database for storing attendance records and user information.
- **Streamlit Frontend**: Provides a user interface for accessing attendance data and interacting with the system.

## Features and Endpoints

The system exposes three main endpoints for interacting with the facial recognition and attendance tracking functionalities:

### 1. **Recognition Endpoint**
   - **Purpose**: Recognizes a user by their face and marks attendance.
   - **Description**: This endpoint receives an image of the user, processes it through the DeepFace FaceNet model, and, if the user is recognized, logs their attendance in DynamoDB.

### 2. **New User Endpoint**
   - **Purpose**: Adds a new user to the system.
   - **Description**: This endpoint allows the addition of a new user's face data by retraining the model with the new data, updating the saved model in the Google Cloud Storage bucket. The updated model is then deployed to the Cloud Run instance.

### 3. **Attendance Data Endpoint**
   - **Purpose**: Retrieves attendance records.
   - **Description**: This endpoint fetches attendance data from DynamoDB, making it available for review or analytics.

## System Architecture

- **API (Flask)**: Handles all incoming requests and routes them to the appropriate endpoints.
- **Face Recognition Model (DeepFace)**: The DeepFace FaceNet model, hosted in a Google Cloud Storage bucket, provides the facial recognition capabilities.
- **Google Cloud Run**: The Flask API, connected to the stored model in Google Cloud Storage, is hosted on Google Cloud Run for efficient scaling and management.
- **DynamoDB**: Manages the storage of attendance records and user data, supporting real-time retrieval and updates.
- **Streamlit (Frontend)**: Presents an intuitive user interface where users can view attendance data and interact with the recognition system.

## Getting Started

### Prerequisites
- Google Cloud Platform (GCP) account
- AWS DynamoDB setup
- Python 3.12
- Streamlit, Flask, DeepFace libraries

### Running the Project

#### Option 1: Deploy on GCP and AWS
1. **Prepare the Docker Image**:
   - Add your API code and `requirements.txt` to a Dockerfile.
   - Build and push the Docker image to Google Container Registry.

2. **Deploy to Google Cloud Run**:
   - Use the built Docker image to deploy the API on Google Cloud Run.
   - Set environment variables and connect the API to Google Cloud Storage for the model.

3. **DynamoDB Connection**:
   - Use `boto3` to connect the API to DynamoDB for attendance and user data.

4. **Streamlit Frontend**:
   - Deploy the Streamlit application, ensuring it connects to the Cloud Run API URL for endpoint access.

#### Option 2: Run Locally
1. **Set Up API**:
   - Download the API code and remove any GCP dependencies if they aren’t required for local execution.
   - Keep the DynamoDB connection via `boto3` if you need database access.
   - Run the API locally with:
     ```bash
     python3 api.py
     ```

2. **Run Streamlit Frontend**:
   - Adjust the API URL in the Streamlit code to point to `http://localhost:5000` (or the appropriate port on your local machine).
   - Start the frontend with:
     ```bash
     streamlit run app.py
     ```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any feature requests, improvements, or bug fixes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This project provides an automated, scalable solution for classroom attendance management through facial recognition.

Reference Images of the frontend working all-together

![image](https://github.com/user-attachments/assets/3ec0ff49-fd5e-4e92-b25b-a32725e40145)

![image](https://github.com/user-attachments/assets/37019c54-059c-4018-8d30-5858ca1e8f8a)

![image](https://github.com/user-attachments/assets/7f76adb4-b467-41c5-9344-31f39427d02d)
