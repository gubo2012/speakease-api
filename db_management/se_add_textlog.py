import os
import sys
import psycopg2
import random
from datetime import datetime, timedelta
import logging

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.config.cloud_config import get_psql_connection_string

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample text content for different scenarios
SAMPLE_TEXTS = [
    "Hello, how can I help you today?",
    "I'm looking for some conversation practice.",
    "Can we talk about daily life in English?",
    "What's the weather like in your city?",
    "I enjoy learning new languages.",
    "Let's practice some common phrases.",
    "How was your weekend?",
    "I'm trying to improve my pronunciation.",
    "Do you have any tips for language learning?",
    "What's your favorite way to practice speaking?"
]

def add_text_logs():
    """
    Add sample text logs to the database.
    """
    try:
        # Get database connection string
        conn_string = get_psql_connection_string()
        
        # Connect to the database
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Add 5 sample text logs
                for i in range(5):
                    # Generate a random timestamp within the last 24 hours
                    timestamp = datetime.now() - timedelta(hours=random.randint(0, 24))
                    
                    # Get random text content
                    text_content = random.choice(SAMPLE_TEXTS)
                    
                    # Insert the text log
                    cur.execute("""
                        INSERT INTO textlog (uid, session_id, timestamp, text_type, text_content)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        "DDeNcLqfYySaVL8SUfwnE2PYb4A2",  # uid
                        "sid001",                         # session_id
                        timestamp,                        # timestamp
                        "others",                         # text_type
                        text_content                      # text_content
                    ))
                    
                    logger.info(f"Added text log {i+1}: {text_content}")
                
                # Commit the transaction
                conn.commit()
                logger.info("Successfully added all text logs")
                
    except Exception as e:
        logger.error(f"Error adding text logs: {str(e)}")
        raise

if __name__ == "__main__":
    add_text_logs()
