"""AI service - uses Ollama for free, unlimited AI."""
import httpx
from typing import List, Dict, Optional, AsyncGenerator
from app.core.config import settings
import json

# Ollama client
OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL
OLLAMA_MODEL = settings.OLLAMA_MODEL


async def ask_brain(prompt: str, model: str = None, provider: str = "ollama") -> str:
    """Single-shot chat completion via Ollama."""
    model = model or OLLAMA_MODEL
    
    if provider == "ollama":
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    else:
        raise ValueError(f"Provider {provider} not available. Use 'ollama'")


async def stream_chat(
    messages: List[Dict[str, str]], 
    model: str = None, 
    provider: str = "ollama"
) -> AsyncGenerator[str, None]:
    """Stream chat responses from Ollama using chat API."""
    model = model or OLLAMA_MODEL
    
    if provider == "ollama":
        # Convert messages format for Ollama chat API
        # Ollama expects: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        ollama_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model,
                    "messages": ollama_messages,
                    "stream": True,
                }
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                yield chunk["message"]["content"]
                        except json.JSONDecodeError:
                            continue
    else:
        raise ValueError(f"Provider {provider} not available. Use 'ollama'")


# Import brain functions from core module
from app.core.brain import (
    summarize_pdf,
    index_pdf_bytes_to_kb,
    ask_with_context,
    extract_text_from_pdf_bytes,
    split_text_to_chunks,
)
