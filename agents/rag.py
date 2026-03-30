import hashlib
import os
import requests

import chromadb
from chromadb.config import Settings

import config


def _get_collection():
    client = chromadb.PersistentClient(
        path=config.CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def _embed(texts: list[str]) -> list[list[float]]:
    resp = requests.post(
        f"{config.OLLAMA_URL}/api/embed",
        json={"model": config.EMBED_MODEL, "input": texts},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"]


def _chunk_text(text: str) -> list[str]:
    size = config.RAG_CHUNK_SIZE
    overlap = config.RAG_CHUNK_OVERLAP
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if len(chunk) >= 50:
            chunks.append(chunk)
        start += size - overlap
    return chunks


def _extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            return f.read()


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def ingest_files(file_paths: list[str]) -> dict:
    """Ingest documents into ChromaDB. Returns counts of ingested/skipped chunks."""
    try:
        collection = _get_collection()
        total_ingested = 0
        total_skipped = 0

        for file_path in file_paths:
            try:
                text = _extract_text(file_path)
                if not text.strip():
                    continue

                chunks = _chunk_text(text)
                if not chunks:
                    continue

                doc_hash = _content_hash(text)
                source = os.path.basename(file_path)
                candidate_ids = [f"{doc_hash}_{i}" for i in range(len(chunks))]

                # Deduplication: skip already-stored IDs
                existing = collection.get(ids=candidate_ids)
                existing_ids = set(existing["ids"])

                novel_ids = []
                novel_chunks = []
                novel_metas = []
                for i, (chunk_id, chunk) in enumerate(zip(candidate_ids, chunks)):
                    if chunk_id not in existing_ids:
                        novel_ids.append(chunk_id)
                        novel_chunks.append(chunk)
                        novel_metas.append({"source": source, "chunk_index": i})

                total_skipped += len(chunks) - len(novel_chunks)

                if novel_chunks:
                    embeddings = _embed(novel_chunks)
                    collection.add(
                        ids=novel_ids,
                        embeddings=embeddings,
                        documents=novel_chunks,
                        metadatas=novel_metas,
                    )
                    total_ingested += len(novel_chunks)

            except Exception as e:
                # Per-file errors are logged but don't abort the whole batch
                print(f"[rag] Error ingesting {file_path}: {e}")

        return {"ingested": total_ingested, "skipped": total_skipped}

    except Exception as e:
        print(f"[rag] ingest_files error: {e}")
        return {"ingested": 0, "skipped": 0, "error": str(e)}


def retrieve(query: str) -> list[str]:
    """Retrieve top-k relevant chunks for a query string."""
    try:
        collection = _get_collection()
        if collection.count() == 0:
            return []

        embeddings = _embed([query])
        results = collection.query(
            query_embeddings=embeddings,
            n_results=min(config.RAG_TOP_K, collection.count()),
        )
        return results["documents"][0] if results["documents"] else []

    except Exception as e:
        print(f"[rag] retrieve error: {e}")
        return []


def list_documents() -> list[dict]:
    """Return [{source, chunk_count}] for all indexed documents."""
    try:
        collection = _get_collection()
        if collection.count() == 0:
            return []

        all_items = collection.get(include=["metadatas"])
        counts: dict[str, int] = {}
        for meta in all_items["metadatas"]:
            src = meta.get("source", "unknown")
            counts[src] = counts.get(src, 0) + 1

        return [{"source": src, "chunk_count": cnt} for src, cnt in sorted(counts.items())]

    except Exception as e:
        print(f"[rag] list_documents error: {e}")
        return []
