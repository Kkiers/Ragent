from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class OllamaEmbeddingSettings:
    base_url: str = "http://localhost:11434"
    model: str = "nomic-embed-text:latest"
    timeout_s: int = 120


class OllamaEmbedder:
    def __init__(self, settings: Optional[OllamaEmbeddingSettings] = None):
        self.settings = settings or OllamaEmbeddingSettings()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            vecs = self._embed_batch_via_embed(texts)
            if vecs is not None:
                return vecs
        except Exception:
            pass
        out: List[List[float]] = []
        for t in texts:
            out.append(self._embed_single_via_embeddings(t))
        return out

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self.settings.base_url.rstrip("/") + path
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.settings.timeout_s) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore") if e.fp else ""
            raise RuntimeError(f"Ollama HTTPError {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"无法连接 Ollama: {url} ({e})") from e

    def _embed_batch_via_embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        res = self._post_json("/api/embed", {"model": self.settings.model, "input": texts})
        if isinstance(res.get("embeddings"), list):
            return res["embeddings"]
        data = res.get("data")
        if isinstance(data, list) and data and isinstance(data[0], dict) and "embedding" in data[0]:
            return [row["embedding"] for row in data]
        return None

    def _embed_single_via_embeddings(self, text: str) -> List[float]:
        res = self._post_json("/api/embeddings", {"model": self.settings.model, "prompt": text})
        emb = res.get("embedding")
        if not isinstance(emb, list):
            raise RuntimeError(f"Ollama /api/embeddings 无 embedding: {res}")
        return emb


def create_ollama_embedder(
    *,
    base_url: str = "http://localhost:11434",
    model: str = "nomic-embed-text:latest",
    timeout_s: int = 120,
) -> OllamaEmbedder:
    return OllamaEmbedder(OllamaEmbeddingSettings(base_url=base_url, model=model, timeout_s=timeout_s))
