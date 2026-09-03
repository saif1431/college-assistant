"""Embedding model provider.

Cached so the (relatively expensive) HuggingFace model is only ever loaded
once per process, however many retrievers are built from it.
"""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings


@lru_cache
def get_embeddings(model_name: str) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=model_name)
