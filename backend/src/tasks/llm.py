# src/tasks/llm.py
"""LLM client wrapper for GLM, Gemini, Claude, or OpenAI-compatible providers."""

import os
from abc import ABC, abstractmethod
from typing import Optional


class LLMClient(ABC):
    """Base class for LLM clients."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the prompt."""
        pass


class GLMClient(LLMClient):
    """Z.AI GLM client using official SDK."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GLM client using Z.AI SDK.

        Uses dedicated Coding endpoint for agent polling.
        """
        from dotenv import load_dotenv
        from zai import ZaiClient

        load_dotenv()

        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "ZHIPUAI_API_KEY must be set in environment. "
                "Get it from your Z.AI project settings."
            )

        self.client = ZaiClient(api_key=self.api_key)
        self.coding_endpoint = True
        self.model = os.getenv("GLM_MODEL", "glm-4-flash")

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response using Z.AI SDK."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 500),
            )

            if response and hasattr(response, "choices") and response.choices:
                return response.choices[0].message.content
            raise ValueError(f"Invalid response from Z.AI API: {response}")

        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")


class GeminiClient(LLMClient):
    """Google Gemini client."""

    def __init__(self, api_key: Optional[str] = None):
        import google.generativeai as genai
        from dotenv import load_dotenv

        load_dotenv()

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def generate(self, prompt: str, **kwargs) -> str:
        result = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 500),
                **kwargs,
            },
        )
        return result.text


class ClaudeClient(LLMClient):
    """Anthropic Claude client (backup option)."""

    def __init__(self, api_key: Optional[str] = None):
        import anthropic
        from dotenv import load_dotenv

        load_dotenv()

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-haiku-20241022"

    async def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 500),
            temperature=kwargs.get("temperature", 0.7),
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return response.content[0].text


class OpenAICompatClient(LLMClient):
    """OpenAI-compatible client (Vercel AI Gateway, DeepInfra, local vLLM, etc.)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        from dotenv import load_dotenv
        from openai import AsyncOpenAI

        load_dotenv()

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set in environment. "
                "For Vercel AI Gateway, use your AI Gateway API key."
            )

        self.base_url = base_url or os.getenv(
            "OPENAI_BASE_URL", "https://ai-gateway.vercel.sh/v1"
        )
        self.model = model or os.getenv("OPENAI_MODEL", "alibaba/qwen-3-32b")
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 500),
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            raise ValueError(f"Invalid response from OpenAI-compatible API: {response}")
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")


def get_llm_client(
    provider: Optional[str] = None, api_key: Optional[str] = None
) -> LLMClient:
    """
    Get an LLM client instance.

    Args:
        provider: "glm", "gemini", "claude", "openai_compat", "vercel", or "deepinfra".
                  Defaults to openai_compat (Vercel AI Gateway).
        api_key: Optional API key (otherwise reads from env)
    """
    from dotenv import load_dotenv

    load_dotenv()

    provider = provider or os.getenv("LLM_PROVIDER", "openai_compat")

    if provider == "glm":
        return GLMClient(api_key)
    if provider == "gemini":
        return GeminiClient(api_key)
    if provider == "claude":
        return ClaudeClient(api_key)
    if provider in ("openai_compat", "deepinfra", "openai", "vercel", "ai_gateway"):
        return OpenAICompatClient(api_key)
    raise ValueError(f"Unknown provider: {provider}")
