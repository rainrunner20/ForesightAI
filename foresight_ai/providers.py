"""Local inference adapter; the mock adapter is for plumbing tests only."""
import json
from typing import Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen

from .dataset import VERDICTS


class ModelProvider(Protocol):
    def predict(self, system: str, prompt: str) -> dict: ...


class MockProvider:
    """Returns an intentionally fixed output; never use for reported research scores."""
    def predict(self, system: str, prompt: str) -> dict:
        return {"verdict": "Not Enough Evidence", "evidence_ids": [],
                "rationale": "Mock provider response; no model was called."}


class OllamaProvider:
    def __init__(self, model: str = "qwen3:4b", url: str = "http://localhost:11434/api/chat",
                 timeout: int = 120):
        if not url.startswith(("http://localhost:", "http://127.0.0.1:")):
            raise ValueError("For safety, Ollama endpoint must be on localhost")
        self.model, self.url, self.timeout = model, url, timeout

    def predict(self, system: str, prompt: str) -> dict:
        body = json.dumps({"model": self.model, "stream": False, "format": "json",
                           "messages": [{"role": "system", "content": system},
                                        {"role": "user", "content": prompt}],
                           "options": {"temperature": 0.1}}).encode("utf-8")
        request = Request(self.url, body, {"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_json = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError) as exc:
            raise RuntimeError("Local Ollama is unavailable. Start Ollama and download the model.") from exc
        content = response_json.get("message", {}).get("content", "")
        try:
            result = json.loads(content)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Model response is not JSON: {str(content)[:120]!r}") from exc
        if not isinstance(result, dict):
            raise ValueError("Model response must be a JSON object")
        return result


def parse_prediction(raw: dict) -> dict:
    verdict = str(raw.get("verdict", "")).strip()
    if verdict not in VERDICTS:
        # Invalid formats count as an error, not an answer we silently normalize.
        verdict = "INVALID"
    evidence_ids = raw.get("evidence_ids", [])
    if not isinstance(evidence_ids, list):
        evidence_ids = []
    return {"verdict": verdict, "evidence_ids": [x for x in evidence_ids if isinstance(x, str)],
            "rationale": str(raw.get("rationale", ""))[:2000]}
