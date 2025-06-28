import os
import requests
from dotenv import load_dotenv

def load_api_key():
    """Load API key from .env file"""
    load_dotenv()
    return os.getenv("LLM_API_KEY")

def get_embedding(text, model="BAAI/bge-large-zh-v1.5", api_key=None):
    """
    Generate embedding for the given text using the specified model.
    
    Args:
        text (str or list): Text to embed. Can be a single string or a list of strings.
        model (str): The embedding model to use.
        api_key (str, optional): API key for the provider. If None, loads from .env.
        
    Returns:
        dict: The raw response from the API containing embeddings
    """
    if api_key is None:
        api_key = load_api_key()

    if not api_key:
        raise ValueError("LLM_API_KEY not found. Please ensure it is set in a .env file.")
    
    url = "https://api.siliconflow.cn/v1/embeddings"
    
    payload = {
        "model": model,
        "input": text,
        "encoding_format": "float"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception("Error: The request to the embedding API timed out after 60 seconds.")
    except requests.exceptions.RequestException as e:
        # This will catch other requests-related errors, e.g., connection errors
        raise Exception(f"Error calling embedding API: {e}")