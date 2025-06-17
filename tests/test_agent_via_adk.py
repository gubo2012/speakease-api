import pytest
import time
import os
import asyncio
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google import adk
from google.adk.sessions import VertexAiSessionService
# from google.adk import types
from vertexai import agent_engines

LOCATION = "us-central1"
PROJECT_ID = "gcpxmlb25"
# PROJECT_ID = "842207255412"
AGENT_ENGINE_ID = "638851440109944832"
SERVICE_ACCOUNT_FILE = "gcpxmlb25-e063bdf91528.json"

SESSION_ID = "6499499654562971648"


app_name=AGENT_ENGINE_ID
user_id="USER_ID"

def get_google_auth_token():
    """Get OAuth2 token using service account credentials"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        print("\nAuthentication successful!")
        print(f"Service Account Email: {credentials.service_account_email}")
        return credentials.token
    except Exception as e:
        print(f"\nAuthentication Error: {str(e)}")
        raise

async def run_agent_demo():
    """Main function to demonstrate agent functionality"""
    print("Starting agent demo...")
    
    # Create the ADK runner with VertexAiSessionService
    session_service = VertexAiSessionService(PROJECT_ID, LOCATION)

    user_id = "test_user_001"

    try:
        # Create a session
        print("Creating new session...")
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id
        )
        print(f"Session created with ID: {session.id}")

        agent = agent_engines.get(app_name)
       

        print(f"Created session for user ID: {user_id}")
        print("Type 'quit' to exit.")
        while True:
            user_input = input("Input: ")
            if user_input == "quit":
                break

            for event in agent.stream_query(
                user_id=user_id,
                session_id=session.id,
                message=user_input
            ):
                if "content" in event:
                    if "parts" in event["content"]:
                        parts = event["content"]["parts"]
                        for part in parts:
                            if "text" in part:
                                text_part = part["text"]
                                print(f"Response: {text_part}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
    finally:
        # Clean up - delete the session
        print("\nCleaning up - deleting session...")
        await session_service.delete_session(session.id)
        print("Session deleted successfully")

def main():
    """Entry point for running the agent demo"""
    try:
        asyncio.run(run_agent_demo())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {str(e)}")

if __name__ == "__main__":
    main()
