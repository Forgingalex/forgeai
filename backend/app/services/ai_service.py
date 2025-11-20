"""
AI service - uses Ollama for free, unlimited AI.

This module provides:
- Async AI chat completion
- Streaming chat responses
- Abstraction over Ollama API

Why Ollama?
- Free, unlimited usage
- Privacy-first (local processing)
- No API rate limits
- Works offline
"""
import httpx
import logging
from typing import List, Dict, Optional, AsyncGenerator
from app.core.config import settings
from app.core.logging_config import get_logger
import json

logger = get_logger(__name__)

# Ollama client
OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL
OLLAMA_MODEL = settings.OLLAMA_MODEL


async def ask_brain(prompt: str, model: str = None, provider: str = "ollama") -> str:
    """
    Single-shot chat completion via Ollama.
    
    Args:
        prompt: The prompt to send to the AI model
        model: Optional model name (defaults to configured model)
        provider: AI provider (currently only "ollama")
    
    Returns:
        AI-generated response text
    
    Raises:
        ValueError: If provider is not supported
        httpx.HTTPError: If API request fails
    
    Note:
        Uses async httpx for non-blocking requests.
        Timeout is 60 seconds.
    """
    model = model or OLLAMA_MODEL
    logger.debug(f"AI request: model={model}, prompt_length={len(prompt)}")
    
    if provider == "ollama":
        try:
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
                response_text = result.get("response", "")
                logger.debug(f"AI response received (length: {len(response_text)} chars)")
                return response_text
        except httpx.TimeoutException:
            logger.error("AI request timed out")
            raise
        except httpx.HTTPError as e:
            logger.error(f"AI HTTP error: {e}")
            raise
    else:
        raise ValueError(f"Provider {provider} not available. Use 'ollama'")


async def stream_chat(
    messages: List[Dict[str, str]], 
    model: str = None, 
    provider: str = "ollama"
) -> AsyncGenerator[str, None]:
    """
    Stream chat responses from Ollama using chat API.
    
    Args:
        messages: List of message dicts with "role" and "content"
        model: Optional model name (defaults to configured model)
        provider: AI provider (currently only "ollama")
    
    Yields:
        Response text chunks as they arrive
    
    Raises:
        ValueError: If provider is not supported
        httpx.HTTPError: If API request fails
    
    Note:
        Uses Ollama's streaming chat API for real-time responses.
        Timeout is 120 seconds for long conversations.
    """
    model = model or OLLAMA_MODEL
    logger.debug(f"Streaming chat: model={model}, messages={len(messages)}")
    
    if provider == "ollama":
        # Convert messages format for Ollama chat API
        # Ollama expects: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        ollama_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        try:
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
                    chunk_count = 0
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "message" in chunk and "content" in chunk["message"]:
                                    content = chunk["message"]["content"]
                                    chunk_count += 1
                                    yield content
                            except json.JSONDecodeError:
                                continue
                    logger.debug(f"Streaming completed: {chunk_count} chunks")
        except httpx.TimeoutException:
            logger.error("Streaming chat timed out")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Streaming chat HTTP error: {e}")
            raise
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
