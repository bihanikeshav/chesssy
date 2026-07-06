"""OpenAI-compatible client for Claude API via local wrapper."""
import json
import httpx
from typing import Generator, Optional

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from config import CLAUDE_API_BASE, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TEMPERATURE


class ClaudeClient:
    """HTTP client for OpenAI-compatible Claude endpoint at localhost:8000."""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or CLAUDE_API_BASE).rstrip("/")
        self.model = model or CLAUDE_MODEL
        self.endpoint = f"{self.base_url}/v1/chat/completions"
        self._client = httpx.Client(timeout=httpx.Timeout(15.0, connect=3.0))

    def generate(self, system_prompt: str, user_prompt: str,
                 max_tokens: int = None, temperature: float = None) -> str:
        """
        Blocking call to generate a complete response.

        Returns:
            The assistant's response text.
        """
        payload = self._build_payload(system_prompt, user_prompt,
                                      max_tokens or CLAUDE_MAX_TOKENS,
                                      temperature or CLAUDE_TEMPERATURE,
                                      stream=False)
        try:
            response = self._client.post(self.endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise ConnectionError(f"Claude API error: {e}")

    def stream(self, system_prompt: str, user_prompt: str,
               max_tokens: int = None, temperature: float = None) -> Generator[str, None, None]:
        """
        Streaming call that yields text chunks as they arrive.

        Yields:
            Text chunks (delta content) from the SSE stream.
        """
        payload = self._build_payload(system_prompt, user_prompt,
                                      max_tokens or CLAUDE_MAX_TOKENS,
                                      temperature or CLAUDE_TEMPERATURE,
                                      stream=True)
        try:
            with self._client.stream("POST", self.endpoint, json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise ConnectionError(f"Claude API stream error: {e}")

    def is_available(self) -> bool:
        """Check if the Claude API endpoint is reachable."""
        try:
            response = self._client.get(
                f"{self.base_url}/v1/models",
                timeout=httpx.Timeout(2.0, connect=1.0)
            )
            return response.status_code == 200
        except Exception:
            return False

    def _build_payload(self, system_prompt: str, user_prompt: str,
                       max_tokens: int, temperature: float, stream: bool) -> dict:
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }

    def close(self):
        self._client.close()

    def __del__(self):
        try:
            self._client.close()
        except Exception:
            pass
