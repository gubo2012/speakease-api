import os
import google.generativeai as genai
from typing import Optional
import logging
from app.config.cloud_config import get_gemini_api_key

logger = logging.getLogger(__name__)

def get_outgoing_paraphrase_prompt(text_content: str) -> str:
    """
    Generate the prompt template for outgoing paraphrase.
    
    Args:
        text_content (str): The text to be paraphrased
        
    Returns:
        str: The constructed prompt template
    """
    return f"""You are a friendly and supportive language coach helping a young student with autism communicate more clearly and naturally. The student will give you a sentence or short paragraph. Your job is to gently rephrase it to sound more conversational and socially appropriate, while keeping the original meaning.

Respond with only the improved version, without commentary.

Keep the tone simple, age-appropriate, and encouraging.

Examples:

User input:
"I like trains. Trains are fun. I like trains."
Say it better:
"I really enjoy trains! They're so much fun to learn about."

User input:
"My favorite thing is dinosaurs because they are big and scary and I like them."
Say it better:
"I love dinosaurs—they're so big and exciting!"

Now, please improve this text:
---
{text_content}
---

Say it better:"""

def get_incoming_paraphrase_prompt(text_content: str) -> str:
    """
    Generate the prompt template for incoming paraphrase.
    
    Args:
        text_content (str): The text to be paraphrased
        
    Returns:
        str: The constructed prompt template
    """
    return f"""You are a helpful and patient communication assistant for a young student with autism. The student may not understand figurative language, sarcasm, or complex expressions. Your job is to rephrase their input into simple, literal, and clear language that makes it easier to understand.

Avoid figurative language, idioms, or metaphors in your output. Use plain English.

Respond with only the simplified version, without commentary or definitions.

Examples:

User input:
"It's raining cats and dogs!"
Explain it to me:
"It's raining very heavily."

User input:
"Don't spill the beans about the surprise party."
Explain it to me:
"Don't tell anyone about the surprise party."

Now, please explain this text:
---
{text_content}
---

Explain it to me:"""

def get_prompt_results(prompt: str) -> Optional[str]:
    """
    Send the prompt to Gemini API and get the results.
    
    Args:
        prompt (str): The prompt to send to the API
        
    Returns:
        Optional[str]: Generated response on success, None on error
    """
    try:
        # Get API key from Secret Manager
        api_key = get_gemini_api_key()
        if not api_key:
            logger.error('Failed to retrieve Gemini API key from Secret Manager')
            return None
            
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Choose the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        # model = genai.GenerativeModel('gemini-pro')  # Alternative model
        
        # Generate response
        response = model.generate_content(prompt)
        
        if not response.text:
            logger.error('No response text received from Gemini API')
            return None
            
        return response.text
        
    except Exception as e:
        logger.error(f'Error generating paraphrase: {str(e)}')
        return None

def get_outgoing_paraphrase(text_content: str) -> Optional[str]:
    """
    Generate a more conversational paraphrase for the given text using the Gemini API.
    This is a convenience function that combines get_outgoing_paraphrase_prompt and get_prompt_results.
    
    Args:
        text_content (str): The text to be paraphrased (1-1000 characters)
        
    Returns:
        Optional[str]: Generated paraphrase on success, None on error
        
    Raises:
        ValueError: If text content length is invalid
    """
    # Validate text content length
    content_length = len(text_content.strip())
    if content_length < 1:
        raise ValueError("Text content is too short. Minimum length is 1 character.")
    if content_length > 1000:
        raise ValueError("Text content is too long. Maximum length is 1,000 characters.")
    
    prompt = get_outgoing_paraphrase_prompt(text_content)
    return get_prompt_results(prompt)

def get_incoming_paraphrase(text_content: str) -> Optional[str]:
    """
    Generate a simplified, literal paraphrase for the given text using the Gemini API.
    This is a convenience function that combines get_incoming_paraphrase_prompt and get_prompt_results.
    
    Args:
        text_content (str): The text to be paraphrased (1-1000 characters)
        
    Returns:
        Optional[str]: Generated paraphrase on success, None on error
        
    Raises:
        ValueError: If text content length is invalid
    """
    # Validate text content length
    content_length = len(text_content.strip())
    if content_length < 1:
        raise ValueError("Text content is too short. Minimum length is 1 character.")
    if content_length > 1000:
        raise ValueError("Text content is too long. Maximum length is 1,000 characters.")
    
    prompt = get_incoming_paraphrase_prompt(text_content)
    return get_prompt_results(prompt) 