import os
import sys
import psycopg2
import logging

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.config.cloud_config import get_psql_connection_string

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_text_logs():
    """
    Read and display 5 rows from the textlog table.
    """
    try:
        # Get database connection string
        conn_string = get_psql_connection_string()
        
        # Connect to the database
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Query to select 5 rows from textlog table
                cur.execute("""
                    SELECT uid, session_id, timestamp, text_type, text_content
                    FROM textlog
                    ORDER BY timestamp DESC
                    LIMIT 5
                """)
                
                # Fetch all results
                rows = cur.fetchall()
                
                # Print the results
                logger.info("Retrieved 5 text logs:")
                for i, row in enumerate(rows, 1):
                    logger.info(f"\nLog {i}:")
                    logger.info(f"UID: {row[0]}")
                    logger.info(f"Session ID: {row[1]}")
                    logger.info(f"Timestamp: {row[2]}")
                    logger.info(f"Text Type: {row[3]}")
                    logger.info(f"Content: {row[4]}")
                
    except Exception as e:
        logger.error(f"Error reading text logs: {str(e)}")
        raise

if __name__ == "__main__":
    read_text_logs()
