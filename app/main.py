from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from typing import Dict, List
from datetime import datetime
# from app.config.cloud_config import get_firestore_client

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "app.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Log file location: {log_file}")

app = FastAPI(title="SpeakEase", description="A language translation API using FastAPI and Gemini")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    duration = datetime.now() - start_time
    
    # Log the request details
    logger.info(
        f"API Call - Method: {request.method}, "
        f"Path: {request.url.path}, "
        f"Status: {response.status_code}, "
        f"Duration: {duration.total_seconds():.3f}s"
    )
    
    return response

# Import and include routers
# from app.api import auth
from app.api import se

# app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(se.router, prefix="/apps/se", tags=["se-services"])


@app.get("/")
async def root():
    return {"message": "Welcome to SpeakEase API"}

