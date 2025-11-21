"""
AI service - hybrid approach with automatic fallback.

This module provides:
- Async AI chat completion
- Streaming chat responses
- Multi-provider support (Google AI Studio/Gemini, Ollama)
- Automatic fallback when limits are hit or offline

Default: Google AI Studio (fast, cloud-based)
Fallback: Ollama (slower, local, unlimited)
"""
import httpx
import logging
from typing import List, Dict, Optional, AsyncGenerator
from app.core.config import settings
from app.core.logging_config import get_logger
import json

logger = get_logger(__name__)

# Try importing Google AI
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Google AI features unavailable.")

# Ollama client
OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL
OLLAMA_MODEL = settings.OLLAMA_MODEL

# Google AI setup
if GOOGLE_AI_AVAILABLE and settings.GOOGLE_AI_API_KEY:
    try:
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        GOOGLE_AI_MODEL = settings.GOOGLE_AI_MODEL or "gemini-1.5-flash"
        logger.info(f"Google AI configured with model: {GOOGLE_AI_MODEL}")
    except Exception as e:
        logger.error(f"Failed to configure Google AI: {e}")
        GOOGLE_AI_MODEL = None
else:
    GOOGLE_AI_MODEL = None
    if not settings.GOOGLE_AI_API_KEY:
        logger.info("Google AI API key not set, will use Ollama only")


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class QuotaExceededError(Exception):
    """Raised when daily quota is exceeded."""
    pass


class NetworkError(Exception):
    """Raised when network connection fails."""
    pass


async def ask_brain(prompt: str, model: str = None, provider: str = "auto") -> str:
    """
    Single-shot chat completion with automatic provider selection and fallback.
    
    Args:
        prompt: The prompt to send to the AI model
        model: Optional model name (ignored if provider="auto")
        provider: AI provider ("auto", "google", or "ollama")
                 "auto" tries Google first, falls back to Ollama
    
    Returns:
        AI-generated response text
    
    Raises:
        ValueError: If provider is not supported
        httpx.HTTPError: If API request fails
    """
    logger.debug(f"AI request: provider={provider}, prompt_length={len(prompt)}")
    
    # Auto mode: try Google first, fallback to Ollama
    if provider == "auto":
        # Try Google AI first if available
        if GOOGLE_AI_AVAILABLE and settings.GOOGLE_AI_API_KEY and GOOGLE_AI_MODEL:
            try:
                return await _ask_google_ai(prompt, GOOGLE_AI_MODEL)
            except RateLimitError:
                logger.warning("Google AI rate limit hit, falling back to Ollama")
                # Fall through to Ollama
            except QuotaExceededError:
                logger.warning("Google AI quota exceeded, falling back to Ollama")
                # Fall through to Ollama
            except NetworkError:
                logger.warning("Google AI network error, falling back to Ollama")
                # Fall through to Ollama
            except Exception as e:
                logger.warning(f"Google AI error: {e}, falling back to Ollama")
        
        # Fallback to Ollama
        logger.info("Using Ollama as fallback")
        return await _ask_ollama(prompt, model or OLLAMA_MODEL)
    
    elif provider == "google":
        if not GOOGLE_AI_AVAILABLE:
            raise ValueError("Google AI not available. Install google-generativeai package.")
        if not settings.GOOGLE_AI_API_KEY:
            raise ValueError("GOOGLE_AI_API_KEY not set in environment variables.")
        return await _ask_google_ai(prompt, model or GOOGLE_AI_MODEL or "gemini-2.5-flash")
    
    elif provider == "ollama":
        return await _ask_ollama(prompt, model or OLLAMA_MODEL)
    
    else:
        raise ValueError(f"Provider {provider} not available. Use 'auto', 'google', or 'ollama'")


async def _ask_google_ai(prompt: str, model: str) -> str:
    """Internal function to call Google AI."""
    try:
        ai_model = genai.GenerativeModel(model)
        response = await ai_model.generate_content_async(prompt)
        response_text = response.text
        logger.debug(f"Google AI response received (length: {len(response_text)} chars)")
        return response_text
    except Exception as e:
        error_str = str(e).lower()
        error_msg = str(e)
        
        # Check for rate limit errors
        if "429" in error_msg or "rate limit" in error_str or "quota" in error_str:
            if "daily" in error_str or "quota exceeded" in error_str:
                raise QuotaExceededError(f"Daily quota exceeded: {e}")
            raise RateLimitError(f"Rate limit exceeded: {e}")
        
        # Check for network errors
        if "network" in error_str or "connection" in error_str or "timeout" in error_str:
            raise NetworkError(f"Network error: {e}")
        
        raise


async def _ask_ollama(prompt: str, model: str) -> str:
    """Internal function to call Ollama."""
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
            logger.debug(f"Ollama response received (length: {len(response_text)} chars)")
            return response_text
    except httpx.TimeoutException:
        logger.error("Ollama request timed out")
        raise
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama service")
        raise NetworkError("Cannot connect to Ollama. Make sure Ollama is running.")
    except httpx.HTTPError as e:
        logger.error(f"Ollama HTTP error: {e}")
        raise


async def stream_chat(
    messages: List[Dict[str, str]], 
    model: str = None, 
    provider: str = "auto"
) -> AsyncGenerator[str, None]:
    """
    Stream chat responses with automatic provider selection and fallback.
    
    Args:
        messages: List of message dicts with "role" and "content"
        model: Optional model name (ignored if provider="auto")
        provider: AI provider ("auto", "google", or "ollama")
                 "auto" tries Google first, falls back to Ollama
    
    Yields:
        Response text chunks as they arrive
    
    Raises:
        ValueError: If provider is not supported
        httpx.HTTPError: If API request fails
    """
    logger.debug(f"Streaming chat: provider={provider}, messages={len(messages)}")
    
    # Auto mode: try Google first, fallback to Ollama
    if provider == "auto":
        # Try Google AI first if available
        if GOOGLE_AI_AVAILABLE and settings.GOOGLE_AI_API_KEY and GOOGLE_AI_MODEL:
            try:
                async for chunk in _stream_google_ai(messages, GOOGLE_AI_MODEL):
                    yield chunk
                return
            except RateLimitError:
                logger.warning("Google AI rate limit hit, falling back to Ollama")
            except QuotaExceededError:
                logger.warning("Google AI quota exceeded, falling back to Ollama")
            except NetworkError:
                logger.warning("Google AI network error, falling back to Ollama")
            except Exception as e:
                logger.warning(f"Google AI error: {e}, falling back to Ollama")
        
        # Fallback to Ollama
        logger.info("Using Ollama as fallback for streaming")
        async for chunk in _stream_ollama(messages, model or OLLAMA_MODEL):
            yield chunk
        return
    
    elif provider == "google":
        if not GOOGLE_AI_AVAILABLE:
            raise ValueError("Google AI not available. Install google-generativeai package.")
        if not settings.GOOGLE_AI_API_KEY:
            raise ValueError("GOOGLE_AI_API_KEY not set in environment variables.")
        async for chunk in _stream_google_ai(messages, model or GOOGLE_AI_MODEL or "gemini-2.5-flash"):
            yield chunk
    
    elif provider == "ollama":
        async for chunk in _stream_ollama(messages, model or OLLAMA_MODEL):
            yield chunk
    
    else:
        raise ValueError(f"Provider {provider} not available. Use 'auto', 'google', or 'ollama'")


async def _stream_google_ai(messages: List[Dict[str, str]], model: str) -> AsyncGenerator[str, None]:
    """Internal function to stream from Google AI."""
    try:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        import queue
        
        ai_model = genai.GenerativeModel(model)
        
        # Build chat history from previous messages
        # Only process messages up to the last user message
        history = []
        last_user_message = None
        
        for i, msg in enumerate(messages):
            if msg["role"] == "user":
                if i < len(messages) - 1:
                    # This is not the last message, add to history
                    history.append({"role": "user", "parts": [msg["content"]]})
                else:
                    # This is the last message, we'll stream it
                    last_user_message = msg["content"]
            elif msg["role"] == "assistant" and i < len(messages) - 1:
                # Add assistant response to history
                history.append({"role": "model", "parts": [msg["content"]]})
        
        # Start chat with history
        chat = ai_model.start_chat(history=history)
        
        # Stream the last message using synchronous API wrapped in executor
        # Google AI SDK's async streaming has issues, so we use sync + executor
        if last_user_message:
            # Use queue to pass chunks from sync thread to async generator
            chunk_queue = queue.Queue()
            exception_holder = [None]
            
            def _stream_sync():
                """Synchronous streaming wrapper that puts chunks in queue."""
                try:
                    response = chat.send_message(last_user_message, stream=True)
                    for chunk in response:
                        if chunk.text:
                            chunk_queue.put(chunk.text)
                    chunk_queue.put(None)  # Signal end
                except Exception as e:
                    exception_holder[0] = e
                    chunk_queue.put(None)  # Signal end
            
            # Run sync streaming in executor
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            future = loop.run_in_executor(executor, _stream_sync)
            
            try:
                # Yield chunks from queue as they arrive
                while True:
                    # Check for exceptions
                    if exception_holder[0]:
                        raise exception_holder[0]
                    
                    # Get chunk from queue (non-blocking check)
                    try:
                        chunk = chunk_queue.get_nowait()
                    except queue.Empty:
                        # Queue empty, check if streaming is done
                        if future.done():
                            # Check for exceptions
                            if exception_holder[0]:
                                raise exception_holder[0]
                            # No more chunks
                            break
                        # Wait a bit for more chunks
                        await asyncio.sleep(0.01)
                        continue
                    
                    if chunk is None:
                        break
                    yield chunk
            finally:
                executor.shutdown(wait=False)
        else:
            # No last message, return empty
            return
                
    except Exception as e:
        error_str = str(e).lower()
        error_msg = str(e)
        
        if "429" in error_msg or "rate limit" in error_str or "quota" in error_str:
            if "daily" in error_str or "quota exceeded" in error_str:
                raise QuotaExceededError(f"Daily quota exceeded: {e}")
            raise RateLimitError(f"Rate limit exceeded: {e}")
        
        if "network" in error_str or "connection" in error_str or "timeout" in error_str:
            raise NetworkError(f"Network error: {e}")
        
        raise


async def _stream_ollama(messages: List[Dict[str, str]], model: str) -> AsyncGenerator[str, None]:
    """Internal function to stream from Ollama."""
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
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama service")
        raise NetworkError("Cannot connect to Ollama. Make sure Ollama is running.")
    except httpx.HTTPError as e:
        logger.error(f"Streaming chat HTTP error: {e}")
        raise


# Import brain functions from core module
from app.core.brain import (
    summarize_pdf,
    index_pdf_bytes_to_kb,
    ask_with_context,
    extract_text_from_pdf_bytes,
    split_text_to_chunks,
)
