from __future__ import annotations

import os
from typing import Dict, List
import requests


class LLMClient:
    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://127.0.0.1:11434",
        )
        self.model = os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5:1.5b",
        )

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=180,
        )

        if not response.ok:
            raise RuntimeError(
                f"Ollama request failed: {response.status_code} {response.text}"
            )

        data = response.json()
        return data["message"]["content"].strip()