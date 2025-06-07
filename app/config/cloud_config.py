import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import secretmanager
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# GCP Project Configuration
GCP_PROJECT_ID = "gcpxmlb25"

# Step 1: Initialize service account credentials
def initialize_service_account():
    """
    Initialize service account credentials.
    In Cloud Run, credentials are automatically provided.
    In local environment, use the service account file.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Check if we're running in Cloud Run
    if os.getenv("K_SERVICE"):
        logger.info("Running in Cloud Run - using default credentials")
        return None  # Cloud Run will use default credentials
    
    # Local environment - use service account file
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set for local environment")
    
    try:
        # Read and log the service account info
        with open(credentials_path, 'r') as f:
            sa_info = json.load(f)
            logger.debug(f"Service Account Project ID: {sa_info.get('project_id')}")
            logger.debug(f"Service Account Client Email: {sa_info.get('client_email')}")
        
        return service_account.Credentials.from_service_account_file(credentials_path)
    except Exception as e:
        logger.error(f"Failed to initialize service account: {str(e)}")
        raise RuntimeError(f"Failed to initialize service account: {str(e)}")

# Initialize service account credentials
service_account_creds = initialize_service_account()

# Step 2: Set up Secret Manager client
def get_secret_manager_client():
    """
    Get a Secret Manager client using the service account credentials.
    """
    if service_account_creds:
        return secretmanager.SecretManagerServiceClient(credentials=service_account_creds)
    return secretmanager.SecretManagerServiceClient()  # Use default credentials in Cloud Run

secret_client = get_secret_manager_client()

def get_secret(secret_id):
    """
    Get a secret from GCP Secret Manager using the service account.
    
    Args:
        secret_id (str): The ID of the secret to retrieve
        
    Returns:
        str: The secret value
    """
    name = f"projects/{GCP_PROJECT_ID}/secrets/{secret_id}/versions/latest"
    try:
        response = secret_client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to access secret {secret_id} in project {GCP_PROJECT_ID}: {str(e)}")
        raise RuntimeError(f"Failed to access secret {secret_id}: {str(e)}")

# Step 3: Set up Firebase and other services
# Firebase Configuration
FIRESTORE_DATABASE_NAME = "lingoforge"

def initialize_firebase_apps():
    """
    Initialize Firebase Auth and Firestore using credentials from Secret Manager.
    """
    try:
        # Initialize Firebase Auth
        if not firebase_admin._apps:
            auth_cred_json = get_secret("firebase-auth-credentials")
            auth_cred = credentials.Certificate(json.loads(auth_cred_json))
            firebase_admin.initialize_app(auth_cred, name='auth')
        
        # Initialize Firestore
        firestore_cred_json = get_secret("firestore-credentials")
        db_cred = credentials.Certificate(json.loads(firestore_cred_json))
        return firebase_admin.initialize_app(db_cred, name='db')
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Firebase apps: {str(e)}")

# Initialize Firebase apps
db_app = initialize_firebase_apps()

def get_firestore_client():
    """
    Get a Firestore client with the configured database name.
    
    Returns:
        firestore.Client: A Firestore client instance
    """
    db = firestore.client(app=db_app)
    db._database = FIRESTORE_DATABASE_NAME
    return db

# API Keys and other secrets
def get_gemini_api_key():
    """Get the Gemini API key from Secret Manager."""
    return get_secret("gemini-api-key")


def get_psql_password():
    """Get the PostgreSQL password from Secret Manager."""
    return get_secret("psql_password")

# PostgreSQL connection settings
PSQL_HOST = "35.192.165.158"
PSQL_PORT = 5432
PSQL_USER = "lingoforge"
PSQL_DB = "speakease"

def get_psql_connection_string():
    """
    Get the PostgreSQL connection string with credentials.
    
    Returns:
        str: PostgreSQL connection string
    """
    password = get_psql_password()
    return f"postgresql://{PSQL_USER}:{password}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}" 