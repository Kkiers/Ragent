from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from app.infra.embedding.ollama_embedder import OllamaEmbedder, OllamaEmbeddingSettings


@dataclass
class ChromaSettings:
    persist_directory: str = "knowledge/chroma"
    collection_name: str = "huawei_voicecall_faq"


class OllamaLangChainEmbeddings:
    """仅用于 Chroma 打开已有集合（入库时写入的向量）；query 路径用自算向量 + by_vector 检索。"""

    def __init__(self, embedder: OllamaEmbedder):
        self.embedder = embedder

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedder.embed_texts(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embedder.embed_texts([text])[0]


def create_chroma_vectorstore(
    *,
    settings: Optional[ChromaSettings] = None,
    ollama_base_url: str = "http://localhost:11434",
    ollama_embedding_model: str = "nomic-embed-text:latest",
):
    from langchain_community.vectorstores import Chroma  # type: ignore

    s = settings or ChromaSettings()
    embedder = OllamaEmbedder(
        OllamaEmbeddingSettings(base_url=ollama_base_url, model=ollama_embedding_model)
    )
    embeddings = OllamaLangChainEmbeddings(embedder)
    return Chroma(
        collection_name=s.collection_name,
        persist_directory=s.persist_directory,
        embedding_function=embeddings,
    )
