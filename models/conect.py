from google.cloud import storage
import joblib  # Usa joblib en lugar de pickle
from google.oauth2 import service_account

# Ruta al archivo JSON de credenciales
credentials_path = "credentials.json"

# Cargar las credenciales directamente desde el archivo JSON
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Nombre del bucket y archivo dentro del bucket
BUCKET_NAME = "gcf-v2-uploads-77024392592-us-central1"
MODEL_FILE = "svm_model.pkl"  # Nombre del archivo en el bucket

# Función para descargar el archivo desde Google Cloud Storage usando las credenciales
def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} from bucket {bucket_name} to {destination_file_name}.")

# Ruta local temporal para el archivo descargado
destination_file_path = "svm_model.pkl"

# Llama a la función para descargar el archivo
download_blob(BUCKET_NAME, MODEL_FILE, destination_file_path)

# Cargar el archivo del modelo usando joblib para verificar que se descargó correctamente
try:
    model = joblib.load(destination_file_path)
    print("Modelo cargado exitosamente:", model)
except Exception as e:
    print("Error al cargar el modelo:", e)
