"""
AI client configuration and utilities for OpenAI and Replicate APIs.
"""

import os
from openai import OpenAI
from replicate.client import Client as ReplicateClient

# Initialize AI clients (using HAL9 proxy tokens)
OAI_TOKEN = os.getenv("HAL9_TOKEN")
if not OAI_TOKEN:
    raise RuntimeError("HAL9_TOKEN must be set")


def get_openai_client() -> OpenAI:
    """Get configured OpenAI client."""
    return OpenAI(
        base_url="https://api.hal9.com/proxy/server=https://api.openai.com/v1/",
        api_key=OAI_TOKEN,
    )


def get_replicate_client() -> ReplicateClient:
    """Get configured Replicate client.""" 
    return ReplicateClient(
        base_url="https://api.hal9.com/proxy/server=https://api.replicate.com",
        api_token=OAI_TOKEN,
    )


def ask_llm(prompt: str, default: str = "") -> str:
    """
    Send a prompt to the LLM and return the response.
    
    Args:
        prompt: The prompt to send
        default: Default response if request fails
        
    Returns:
        LLM response text or default value
    """
    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return resp.choices[0].message.content
    except Exception:
        return default