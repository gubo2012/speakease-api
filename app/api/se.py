from fastapi import APIRouter, HTTPException, Body
from app.services.se_user_management import (
    get_se_user,
    create_se_user,
    update_se_user,
    delete_se_user,
    log_usage,
    fetch_usage_summary
)
from app.services.se_prompt import get_outgoing_paraphrase, get_incoming_paraphrase
from app.services.se_psql_management import add_text_log, get_session_text_logs, get_latest_text_logs
from app.schemas.se_user import SEUserCreate, SEUserUpdate, SEUserResponse
from pydantic import BaseModel
import logging
from typing import List, Optional, Dict, Any
import requests


router = APIRouter()
logger = logging.getLogger('app.main')  # Use the main app's logger

multi_agent_url = "http://localhost:8010"

class ParaphraseRequest(BaseModel):
    text_content: str

class TextLogRequest(BaseModel):
    text_content: str
    text_type: Optional[str] = "others"

class RunAgentRequest(BaseModel):
    question: str

@router.get("/users/{uid}", response_model=SEUserResponse)
async def get_se_user_endpoint(uid: str):
    try:
        user_data = get_se_user(uid)
        if user_data is None:
            raise HTTPException(status_code=404, detail="SE User not found")
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_se_user endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{uid}", response_model=SEUserResponse)
async def create_se_user_endpoint(uid: str, user_data: SEUserCreate):
    try:
        # Check if user already exists
        existing_user = get_se_user(uid)
        if existing_user is not None:
            raise HTTPException(status_code=409, detail="SE User already exists")
            
        created_user = create_se_user(uid, user_data)
        return created_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_se_user endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{uid}", response_model=SEUserResponse)
async def update_se_user_endpoint(uid: str, user_data: SEUserUpdate):
    try:
        updated_user = update_se_user(uid, user_data)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="SE User not found")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_se_user endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{uid}")
async def delete_se_user_endpoint(uid: str):
    try:
        success = delete_se_user(uid)
        if not success:
            raise HTTPException(status_code=404, detail="SE User not found")
        return {"message": f"SE User {uid} successfully deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_se_user endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fetch_usage_summary/{uid}")
async def fetch_usage_summary_endpoint(uid: str):
    try:
        usage_summary = fetch_usage_summary(uid)
        return {
            "status": "success",
            "usage_summary": usage_summary
        }
    except Exception as e:
        logger.error(f"Error in fetch_usage_summary endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch usage summary: {str(e)}"
        )

@router.post("/outgoing_paraphrase")
async def outgoing_paraphrase_endpoint(request: ParaphraseRequest):
    """
    Generate a more conversational paraphrase for the given text.
    
    Args:
        request (ParaphraseRequest): Request containing the text to be paraphrased
        
    Returns:
        dict: Response containing the paraphrased text or error message
    """
    try:
        result = get_outgoing_paraphrase(request.text_content)
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate paraphrase"
            )
        return {
            "status": "success",
            "paraphrase": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in outgoing_paraphrase endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/incoming_paraphrase")
async def incoming_paraphrase_endpoint(request: ParaphraseRequest):
    """
    Generate a simplified, literal paraphrase for the given text.
    
    Args:
        request (ParaphraseRequest): Request containing the text to be paraphrased
        
    Returns:
        dict: Response containing the paraphrased text or error message
    """
    try:
        result = get_incoming_paraphrase(request.text_content)
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate paraphrase"
            )
        return {
            "status": "success",
            "paraphrase": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in incoming_paraphrase endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text_logs/{uid}/{session_id}")
async def add_text_log_endpoint(uid: str, session_id: str, request: TextLogRequest):
    """
    Add a new text log entry.
    
    Args:
        uid (str): User ID
        session_id (str): Session ID
        request (TextLogRequest): Request containing text content and optional text type
        
    Returns:
        dict: Response indicating success or failure
    """
    try:
        success = add_text_log(uid, session_id, request.text_content, request.text_type)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add text log")
        return {"status": "success", "message": "Text log added successfully"}
    except Exception as e:
        logger.error(f"Error in add_text_log endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/text_logs/{uid}/{session_id}")
async def get_session_text_logs_endpoint(uid: str, session_id: str, text_type: Optional[str] = None):
    """
    Get all text logs for a specific user and session.
    
    Args:
        uid (str): User ID
        session_id (str): Session ID
        text_type (str, optional): Filter by text type
        
    Returns:
        dict: Response containing the text logs
    """
    try:
        logger.info(f"Received request for session text logs - uid: {uid}, session_id: {session_id}, text_type: {text_type}")
        logs = get_session_text_logs(uid, session_id, text_type)
        logger.info(f"Retrieved {len(logs)} logs for session {session_id}")
        if len(logs) > 0:
            logger.info(f"First log entry: {logs[0]}")
        return {
            "status": "success",
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error in get_session_text_logs endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest_text_logs/{uid}")
async def get_latest_text_logs_endpoint(uid: str, limit: int = 10):
    """
    Get the latest text logs for a specific user.
    
    Args:
        uid (str): User ID
        limit (int, optional): Number of latest logs to return. Defaults to 10
        
    Returns:
        dict: Response containing the latest text logs
    """
    try:
        logger.info(f"Received request for latest text logs - uid: {uid}, limit: {limit}")
        logs = get_latest_text_logs(uid, limit)
        logger.info(f"Retrieved {len(logs)} logs for user {uid}")
        if len(logs) > 0:
            logger.info(f"First log entry: {logs[0]}")
        return {
            "status": "success",
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error in get_latest_text_logs endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize_session/{uid}/{session_id}")
async def initialize_session_endpoint(uid: str, session_id: str):
    try:
        result = initialize_session(uid, session_id)
        return {"status": "success", "message": result or "Session initialized successfully"}
    except Exception as e:
        logger.error(f"Error initializing session: {e}")
        raise HTTPException(status_code=500, detail=f"Error initializing session: {e}")

@router.post("/run_agent/{uid}/{session_id}")
async def run_agent_endpoint(uid: str, session_id: str, request: RunAgentRequest):
    try:
        result = run_agent(request.question, uid, session_id)
        return {"status": "success", "agent_response": result}
    except Exception as e:
        logger.error(f"Error communicating with the agent server: {e}")
        raise HTTPException(status_code=500, detail=f"Error communicating with the agent server: {e}") 