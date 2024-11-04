# Usa una imagen base de Python
FROM python:3.8-slim

# Instala dependencias de sistema necesarias para OpenCV, DeepFace y otras dependencias de imagen
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia requirements.txt y luego instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación al contenedor
COPY . .

# Exponer el puerto (ajusta según sea necesario: 5000 para Flask, 8501 para Streamlit)
EXPOSE 8501

# Iniciar la aplicación (ajusta según tu framework)
CMD ["streamlit", "run", "API/server.py"]
