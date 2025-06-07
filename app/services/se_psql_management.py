import os
import sys
import psycopg2
from datetime import datetime
import logging
from typing import List, Optional, Dict, Any

from app.config.cloud_config import get_psql_connection_string

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

psql_log_file = os.path.join(log_dir, 'se_psql.log')

# Create a separate logger for PostgreSQL operations
logger = logging.getLogger('se_psql')
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler(psql_log_file)
file_handler.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def add_text_log(uid: str, session_id: str, text_content: str, text_type: str = "others") -> bool:
    """
    Add a single text log to the database.
    
    Args:
        uid (str): User ID
        session_id (str): Session ID
        text_content (str): The text content to log
        text_type (str, optional): Type of text. Defaults to "others"
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn_string = get_psql_connection_string()
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO textlog (uid, session_id, timestamp, text_type, text_content)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    uid,
                    session_id,
                    datetime.now(),
                    text_type,
                    text_content
                ))
                conn.commit()
                return True
    except Exception as e:
        logger.error(f"Error adding text log: {str(e)}")
        return False

def get_session_text_logs(uid: str, session_id: str, text_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all text logs for a specific user and session.
    
    Args:
        uid (str): User ID
        session_id (str): Session ID
        text_type (str, optional): Filter by text type
        
    Returns:
        List[Dict[str, Any]]: List of text log entries
    """
    try:
        conn_string = get_psql_connection_string()
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT uid, session_id, timestamp, text_type, text_content
                    FROM textlog
                    WHERE uid = %s AND session_id = %s
                """
                params = [uid, session_id]
                
                if text_type:
                    query += " AND text_type = %s"
                    params.append(text_type)
                
                query += " ORDER BY timestamp ASC"
                
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                results = []
                for row in cur.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
    except Exception as e:
        logger.error(f"Error fetching session text logs: {str(e)}")
        return []

def get_latest_text_logs(uid: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the latest text logs for a specific user.
    
    Args:
        uid (str): User ID
        limit (int, optional): Number of latest logs to return. Defaults to 10
        
    Returns:
        List[Dict[str, Any]]: List of text log entries
    """
    try:
        conn_string = get_psql_connection_string()
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT uid, session_id, timestamp, text_type, text_content
                    FROM textlog
                    WHERE uid = %s
                """
                params = [uid]
                
                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                results = []
                for row in cur.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
    except Exception as e:
        logger.error(f"Error fetching latest text logs: {str(e)}")
        return []
