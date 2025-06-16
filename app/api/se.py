from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse
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
import httpx


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
async def add_text_log_endpoint(request: Request, uid: str, session_id: str):
    """
    Proxy text log creation to another server.
    """
    try:
        body = await request.body()
        headers = dict(request.headers)
        headers["X-Internal-Token"] = "my-shared-secret"  # optional security

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://35.192.165.158:8020/apps/se/text_logs/{uid}/{session_id}",
                content=body,
                headers=headers
            )

        return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        logger.error(f"Error in add_text_log endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/text_logs/{uid}/{session_id}")
async def get_session_text_logs_endpoint(request: Request, uid: str, session_id: str, text_type: Optional[str] = None):
    """
    Proxy text log retrieval to another server.
    """
    try:
        headers = dict(request.headers)
        headers["X-Internal-Token"] = "my-shared-secret"  # optional security

        async with httpx.AsyncClient() as client:
            url = f"http://35.192.165.158:8020/apps/se/text_logs/{uid}/{session_id}"
            if text_type:
                url += f"?text_type={text_type}"
            response = await client.get(url, headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        logger.error(f"Error in get_session_text_logs endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest_text_logs/{uid}")
async def get_latest_text_logs_endpoint(request: Request, uid: str, limit: int = 10):
    """
    Proxy latest text log retrieval to another server.
    """
    try:
        headers = dict(request.headers)
        headers["X-Internal-Token"] = "my-shared-secret"  # optional security

        async with httpx.AsyncClient() as client:
            url = f"http://35.192.165.158:8020/apps/se/latest_text_logs/{uid}?limit={limit}"
            response = await client.get(url, headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())
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