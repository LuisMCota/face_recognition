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


