"""Hybrid AI provider service with tiered reasoning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import AsyncGenerator, Dict, Iterable, List, Optional

import httpx

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

try:
    import google.generativeai as genai

    GOOGLE_AI_AVAILABLE = True
except ImportError:
    genai = None
    GOOGLE_AI_AVAILABLE = False


class AIProvider(str, Enum):
    """Supported AI providers."""

    AUTO = "auto"
    GOOGLE = "google"
    OLLAMA = "ollama"


class ReasoningMode(str, Enum):
    """Reasoning modes exposed by the chat UI."""

    CHAT = "chat"
    SEARCH = "search"
    THINK = "think"
    CANVAS = "canvas"


@dataclass(frozen=True)
class AICompletion:
    """Completed AI response."""

    content: str
    provider: AIProvider
    model: str


class RateLimitError(Exception):
    """Raised when a provider rate limit is exceeded."""


class QuotaExceededError(Exception):
    """Raised when a provider quota is exceeded."""


class NetworkError(Exception):
    """Raised when a provider cannot be reached."""


class AIService:
    """Tiered AI service using Gemini first and Ollama as local fallback."""

    def __init__(self) -> None:
        self.ollama_base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.ollama_model = settings.OLLAMA_MODEL
        self.google_model = settings.GOOGLE_AI_MODEL
        if GOOGLE_AI_AVAILABLE and settings.GOOGLE_AI_API_KEY and genai is not None:
            genai.configure(api_key=settings.GOOGLE_AI_API_KEY)

    async def complete(
        self,
        prompt: str,
        mode: ReasoningMode = ReasoningMode.CHAT,
        provider: AIProvider = AIProvider.AUTO,
        model: Optional[str] = None,
    ) -> AICompletion:
        """Run a single-shot completion.

        Args:
            prompt: User or system prompt.
            mode: UI reasoning mode.
            provider: Requested provider. AUTO uses Gemini then Ollama.
            model: Optional explicit model name.

        Returns:
            AI completion metadata and text.
        """
        routed_prompt = self._prompt_for_mode(prompt, mode)
        provider_order = self._provider_order(provider)
        errors: List[str] = []

        for candidate in provider_order:
            try:
                if candidate is AIProvider.GOOGLE:
                    google_model = model or self.google_model
                    content = await self._complete_google(routed_prompt, google_model)
                    return AICompletion(content=content, provider=candidate, model=google_model)

                ollama_model = model or self.ollama_model
                content = await self._complete_ollama(routed_prompt, ollama_model)
                return AICompletion(content=content, provider=candidate, model=ollama_model)
            except (RateLimitError, QuotaExceededError, NetworkError, httpx.HTTPError, ValueError) as exc:
                errors.append(f"{candidate.value}: {exc}")
                logger.warning(
                    "ai_provider_failed",
                    extra={"provider": candidate.value, "mode": mode.value, "error": str(exc)},
                )

        raise NetworkError("All AI providers failed: " + "; ".join(errors))

    async def stream(
        self,
        messages: List[Dict[str, str]],
        mode: ReasoningMode = ReasoningMode.CHAT,
        provider: AIProvider = AIProvider.AUTO,
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response with provider fallback.

        Args:
            messages: Chat messages with ``role`` and ``content`` keys.
            mode: UI reasoning mode.
            provider: Requested provider.
            model: Optional explicit model.

        Yields:
            Text chunks as they arrive.
        """
        routed_messages = self._messages_for_mode(messages, mode)
        provider_order = self._provider_order(provider)
        errors: List[str] = []

        for candidate in provider_order:
            try:
                if candidate is AIProvider.GOOGLE:
                    google_model = model or self.google_model
                    async for chunk in self._stream_google(routed_messages, google_model):
                        yield chunk
                    return

                ollama_model = model or self.ollama_model
                async for chunk in self._stream_ollama(routed_messages, ollama_model):
                    yield chunk
                return
            except (RateLimitError, QuotaExceededError, NetworkError, httpx.HTTPError, ValueError) as exc:
                errors.append(f"{candidate.value}: {exc}")
                logger.warning(
                    "ai_stream_provider_failed",
                    extra={"provider": candidate.value, "mode": mode.value, "error": str(exc)},
                )

        raise NetworkError("All AI providers failed: " + "; ".join(errors))

    def _provider_order(self, provider: AIProvider) -> List[AIProvider]:
        if provider is AIProvider.AUTO:
            return [AIProvider.GOOGLE, AIProvider.OLLAMA]
        return [provider]

    def _prompt_for_mode(self, prompt: str, mode: ReasoningMode) -> str:
        if mode is ReasoningMode.THINK:
            return (
                "You are ForgeAI in Deep Reasoning mode. Analyze the task carefully, "
                "surface assumptions, solve step by step internally, and provide a concise, "
                "well-structured final answer.\n\n"
                f"Task:\n{prompt}"
            )
        if mode is ReasoningMode.CANVAS:
            return (
                "You are ForgeAI in Canvas mode. Produce an answer that can sit beside a "
                "Markdown/code editor. Prefer clear sections, runnable snippets where useful, "
                "and concrete next edits.\n\n"
                f"Task:\n{prompt}"
            )
        return prompt

    def _messages_for_mode(
        self,
        messages: Iterable[Dict[str, str]],
        mode: ReasoningMode,
    ) -> List[Dict[str, str]]:
        routed = [{"role": item["role"], "content": item["content"]} for item in messages]
        if not routed:
            return routed

        if mode in {ReasoningMode.THINK, ReasoningMode.CANVAS}:
            routed[-1] = {
                **routed[-1],
                "content": self._prompt_for_mode(routed[-1]["content"], mode),
            }
        return routed

    async def _complete_google(self, prompt: str, model: str) -> str:
        if not GOOGLE_AI_AVAILABLE or genai is None:
            raise ValueError("google-generativeai is not installed")
        if not settings.GOOGLE_AI_API_KEY:
            raise ValueError("GOOGLE_AI_API_KEY is not configured")

        try:
            ai_model = genai.GenerativeModel(model)
            response = await ai_model.generate_content_async(prompt)
            return response.text or ""
        except Exception as exc:
            self._raise_google_error(exc)
            raise

    async def _complete_ollama(self, prompt: str, model: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
                return str(response.json().get("response", ""))
        except httpx.ConnectError as exc:
            raise NetworkError("Cannot connect to Ollama. Confirm the local service is running.") from exc
        except httpx.TimeoutException as exc:
            raise NetworkError("Ollama request timed out.") from exc

    async def _stream_google(
        self,
        messages: List[Dict[str, str]],
        model: str,
    ) -> AsyncGenerator[str, None]:
        if not GOOGLE_AI_AVAILABLE or genai is None:
            raise ValueError("google-generativeai is not installed")
        if not settings.GOOGLE_AI_API_KEY:
            raise ValueError("GOOGLE_AI_API_KEY is not configured")

        prompt = self._flatten_messages(messages)
        try:
            ai_model = genai.GenerativeModel(model)
            response = await ai_model.generate_content_async(prompt, stream=True)
            async for chunk in response:
                text = getattr(chunk, "text", "")
                if text:
                    yield text
        except Exception as exc:
            self._raise_google_error(exc)
            raise

    async def _stream_ollama(
        self,
        messages: List[Dict[str, str]],
        model: str,
    ) -> AsyncGenerator[str, None]:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.ollama_base_url}/api/chat",
                    json={"model": model, "messages": messages, "stream": True},
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        content = payload.get("message", {}).get("content")
                        if content:
                            yield str(content)
        except httpx.ConnectError as exc:
            raise NetworkError("Cannot connect to Ollama. Confirm the local service is running.") from exc
        except httpx.TimeoutException as exc:
            raise NetworkError("Ollama streaming request timed out.") from exc

    def _flatten_messages(self, messages: List[Dict[str, str]]) -> str:
        return "\n\n".join(f"{message['role'].upper()}: {message['content']}" for message in messages)

    def _raise_google_error(self, exc: Exception) -> None:
        error_text = str(exc)
        error_lower = error_text.lower()
        if "429" in error_text or "rate limit" in error_lower:
            raise RateLimitError(error_text) from exc
        if "quota" in error_lower:
            raise QuotaExceededError(error_text) from exc
        if any(marker in error_lower for marker in ("network", "connection", "timeout")):
            raise NetworkError(error_text) from exc


async def ask_brain(
    prompt: str,
    model: Optional[str] = None,
    provider: str = "auto",
) -> str:
    """Compatibility wrapper for legacy imports."""
    completion = await AIService().complete(
        prompt=prompt,
        provider=AIProvider(provider),
        model=model,
    )
    return completion.content


async def stream_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    provider: str = "auto",
) -> AsyncGenerator[str, None]:
    """Compatibility wrapper for legacy imports."""
    async for chunk in AIService().stream(
        messages=messages,
        provider=AIProvider(provider),
        model=model,
    ):
        yield chunk

