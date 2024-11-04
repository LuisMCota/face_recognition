FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias de sistema necesarias para OpenCV y DeepFace
RUN apt-get update && apt-get install -y \
    apt-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requisitos e instalar dependencias de Python
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el resto de los archivos de la aplicación
COPY . .

EXPOSE 8080

# Ejecutar la aplicación
CMD ["python", "server.py"]
