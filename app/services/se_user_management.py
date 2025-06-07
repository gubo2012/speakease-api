from typing import Optional
import logging
from datetime import datetime
from app.config.cloud_config import get_firestore_client
from app.schemas.se_user import SEUserCreate, SEUserUpdate, SEUserResponse
from google.cloud import firestore

logger = logging.getLogger(__name__)

def get_se_user(uid: str) -> Optional[SEUserResponse]:
    """
    Get se user information by UID from Firestore.
    
    Args:
        uid (str): The unique identifier of the user
        
    Returns:
        Optional[SEUserResponse]: User information if found, None if not found
    """
    try:
        db = get_firestore_client()
        user_ref = db.collection('se_users').document(uid)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            logger.info(f"Successfully retrieved se user data for UID: {uid}")
            return SEUserResponse(**user_data)
        else:
            logger.warning(f"No se user found with UID: {uid}")
            return None
            
    except Exception as e:
        logger.error(f"Error retrieving se user data: {str(e)}")
        raise

def create_se_user(uid: str, user_data: SEUserCreate) -> SEUserResponse:
    """
    Create a new se user in Firestore.
    
    Args:
        uid (str): The unique identifier of the user
        user_data (SEUserCreate): User data to be stored
        
    Returns:
        SEUserResponse: Created user data
    """
    try:
        db = get_firestore_client()
        user_ref = db.collection('se_users').document(uid)
        
        # Convert to dict and add created_at
        user_dict = user_data.model_dump()
        user_dict['created_at'] = datetime.now()
            
        user_ref.set(user_dict)
        logger.info(f"Successfully created se user with UID: {uid}")
        return SEUserResponse(**user_dict)
        
    except Exception as e:
        logger.error(f"Error creating se user: {str(e)}")
        raise

def update_se_user(uid: str, user_data: SEUserUpdate) -> Optional[SEUserResponse]:
    """
    Update an existing se user in Firestore.
    
    Args:
        uid (str): The unique identifier of the user
        user_data (SEUserUpdate): Updated user data
        
    Returns:
        Optional[SEUserResponse]: Updated user data if successful, None if user not found
    """
    try:
        db = get_firestore_client()
        user_ref = db.collection('se_users').document(uid)
        
        # Check if user exists
        if not user_ref.get().exists:
            logger.warning(f"No se user found with UID: {uid} to update")
            return None
            
        # Convert to dict and remove None values
        update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
        user_ref.update(update_data)
        
        # Get updated user data
        updated_user = user_ref.get()
        logger.info(f"Successfully updated se user with UID: {uid}")
        return SEUserResponse(**updated_user.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating se user: {str(e)}")
        raise

def delete_se_user(uid: str) -> bool:
    """
    Delete an se user from Firestore.
    
    Args:
        uid (str): The unique identifier of the user
        
    Returns:
        bool: True if deletion was successful, False if user not found
    """
    try:
        db = get_firestore_client()
        user_ref = db.collection('se_users').document(uid)
        
        # Check if user exists
        if not user_ref.get().exists:
            logger.warning(f"No se user found with UID: {uid} to delete")
            return False
            
        user_ref.delete()
        logger.info(f"Successfully deleted se user with UID: {uid}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting se user: {str(e)}")
        raise 

def log_usage(uid: str, service_type: str, details: dict) -> bool:
    """
    Log the usage of a service by a user in the se_usage_logs collection.
    
    Args:
        uid (str): User ID
        service_type (str): Type of service used
        details (dict): Additional details about the usage
        
    Returns:
        bool: True if usage was successfully logged, False otherwise
    """
    try:
        db = get_firestore_client()
        
        # Get the user's usage log document reference
        usage_log_ref = db.collection('se_usage_logs').document(uid)
        
        # Create a new log entry in the subcollection
        log_entry = {
            'timestamp': datetime.now(),
            'service_type': service_type,
            'grade_level': details.get('grade_level'),
            'essay_type': details.get('essay_type'),
            'word_count': details.get('essay_length', 0)  # Using essay_length as word count
        }
        
        # Add the log entry to the subcollection
        usage_log_ref.collection('entries').add(log_entry)
        
        logger.info(f"Successfully logged usage for user {uid}: {service_type}")
        return True
        
    except Exception as e:
        logger.error(f"Error logging usage for user {uid}: {str(e)}")
        return False 

def fetch_usage_summary(uid: str) -> list:
    """
    Fetch the latest 20 usage entries for a user.
    
    Args:
        uid (str): User ID
        
    Returns:
        list: List of usage entries, each containing timestamp, grade_level, essay_type, and word_count
    """
    try:
        db = get_firestore_client()
        
        # Get the user's usage log document reference
        usage_log_ref = db.collection('se_usage_logs').document(uid)
        
        # Query the entries subcollection, ordered by timestamp descending, limited to 20
        entries = (
            usage_log_ref.collection('entries')
            .order_by('timestamp', direction=firestore.Query.DESCENDING)
            .limit(20)
            .get()
        )
        
        # Format the results
        usage_summary = []
        for entry in entries:
            entry_data = entry.to_dict()
            usage_summary.append({
                'timestamp': entry_data.get('timestamp'),
                'grade_level': entry_data.get('grade_level'),
                'essay_type': entry_data.get('essay_type'),
                'word_count': entry_data.get('word_count')
            })
        
        logger.info(f"Successfully fetched usage summary for user {uid}")
        return usage_summary
        
    except Exception as e:
        logger.error(f"Error fetching usage summary for user {uid}: {str(e)}")
        return [] 