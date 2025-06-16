import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Test configuration
TEST_ENV = os.getenv('TEST_ENV', 'dev').lower()  # dev, local_docker, or gcp

# Server URLs
DEV_SERVER_URL = "http://127.0.0.1:8000"
LOCAL_DOCKER_URL = "http://localhost:8010"
GCP_SERVER_URL = os.getenv('GCP_SERVER_URL', '')

# Base URL for tests based on environment
if TEST_ENV == 'dev':
    BASE_URL = DEV_SERVER_URL
elif TEST_ENV == 'local_docker':
    BASE_URL = LOCAL_DOCKER_URL
else:  # gcp
    BASE_URL = GCP_SERVER_URL

# Test user credentials
# TEST_USER_UID = "Nqdwyt3DWffVqGsai7JWXBjqcHh1" 
TEST_USER_UID = "haDFSFQZTESPGIcad6kWkbAj7GE3"