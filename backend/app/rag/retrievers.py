"""Retriever registry: builds/loads one retriever per knowledge domain.

`Rule-Book-2023.pdf` and `UET_Taxila_Sample_Department_Descriptions.pdf` are
merged into a single 'academic' index (the legacy prototype indexed them
separately, but its classifier never actually produced a category that
reached the rule-book retriever — see legacy/chatbot.py and
CHATBOT_DOCUMENTATION.md). 'fee' stays its own domain. 'general' queries
skip retrieval entirely and are handled directly by the graph.
"""

from langchain_core.vectorstores import VectorStoreRetriever

from app.core.config import Settings
from app.models.domain import QueryType
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import build_or_load_vector_store

DOMAIN_SOURCES: dict[QueryType, list[str]] = {
    QueryType.ACADEMIC: [
        "Rule-Book-2023.pdf",
        "UET_Taxila_Sample_Department_Descriptions.pdf",
    ],
    QueryType.FEE: [
        "UET_Taxila_Sample_Fee_Structure.pdf",
    ],
}


def build_retrievers(settings: Settings) -> dict[QueryType, VectorStoreRetriever]:
    embeddings = get_embeddings(settings.embedding_model)
    documents_dir = settings.documents_path
    persist_dir = settings.vector_store_path

    retrievers: dict[QueryType, VectorStoreRetriever] = {}
    for domain, filenames in DOMAIN_SOURCES.items():
        pdf_paths = [documents_dir / name for name in filenames]
        missing = [str(p) for p in pdf_paths if not p.exists()]
        if missing:
            raise FileNotFoundError(
                f"Missing source PDF(s) for domain '{domain.value}': {missing}"
            )

        vector_store = build_or_load_vector_store(
            domain=domain.value,
            pdf_paths=pdf_paths,
            persist_dir=persist_dir,
            embeddings=embeddings,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        retrievers[domain] = vector_store.as_retriever(
            search_kwargs={"k": settings.retrieval_k}
        )

    return retrievers
