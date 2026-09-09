import os
import pickle
import numpy as np
from typing import List, Dict, Any
from .embeddings import EmbeddingService
from .knowledge_base import KnowledgeBaseLoader

class RAGRetriever:
    def __init__(self, data_dir: str = "data", kb_dir: str = "knowledge_base"):
        self.data_dir = os.path.abspath(data_dir)
        self.kb_dir = os.path.abspath(kb_dir)
        self.cache_file = os.path.join(self.data_dir, "vector_store.pkl")
        
        self.embedding_service = EmbeddingService()
        self.chunks: List[Dict[str, Any]] = []
        self.vectors: np.ndarray = None

        os.makedirs(self.data_dir, exist_ok=True)
        self._initialize_index()

    def _initialize_index(self):
        """
        Loads cached vector store if available; otherwise parses knowledge base,
        computes embeddings, and caches index to disk.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = data.get("chunks", [])
                    self.vectors = data.get("vectors", None)
                print(f"[RAG Index] Loaded {len(self.chunks)} knowledge chunk(s) from local cache ({self.cache_file}).")
                return
            except Exception as e:
                print(f"[RAG Warning] Failed to load cache file: {e}. Re-building vector index...")

        # Build fresh vector index
        loader = KnowledgeBaseLoader(self.kb_dir)
        self.chunks = loader.load_chunks()

        if not self.chunks:
            print("[RAG Warning] No knowledge base documents found.")
            return

        if self.embedding_service.is_configured():
            print(f"[RAG Index] Generating embeddings for {len(self.chunks)} knowledge chunk(s)...")
            vec_list = []
            embedding_failed = False
            for item in self.chunks:
                try:
                    vec = self.embedding_service.get_embedding(item["full_text"])
                    vec_list.append(vec)
                except Exception as err:
                    if not embedding_failed:
                        print(f" -> Embedding generation notice for '{item['topic']}': {err}")
                        embedding_failed = True
                    vec_list.append([0.0] * 768)

            if not embedding_failed:
                self.vectors = np.array(vec_list, dtype=np.float32)
                try:
                    with open(self.cache_file, "wb") as f:
                        pickle.dump({"chunks": self.chunks, "vectors": self.vectors}, f)
                    print(f"[RAG Index] Vector store cached successfully to {self.cache_file}.")
                except Exception as e:
                    print(f"[RAG Warning] Failed to save vector cache: {e}")
            else:
                print("[RAG Warning] API key not validated yet or embedding generation failed. Using keyword search fallback.")

    def retrieve(self, query: str, top_k: int = 3, threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Performs vector similarity search against cached embeddings.
        Falls back to keyword matching if embeddings are unconfigured.
        """
        if not query.strip() or not self.chunks:
            return []

        results = []

        # Vector search mode
        if self.vectors is not None and self.embedding_service.is_configured():
            try:
                query_vec = np.array(self.embedding_service.get_query_embedding(query), dtype=np.float32)
                
                # Compute Cosine Similarity: (A . B) / (||A|| * ||B||)
                norm_query = np.linalg.norm(query_vec)
                norm_docs = np.linalg.norm(self.vectors, axis=1)

                # Avoid divide-by-zero
                norm_docs[norm_docs == 0] = 1e-9
                if norm_query == 0:
                    norm_query = 1e-9

                similarities = np.dot(self.vectors, query_vec) / (norm_docs * norm_query)

                # Get top K indices sorted descending
                top_indices = np.argsort(similarities)[::-1][:top_k]

                for idx in top_indices:
                    sim = float(similarities[idx])
                    if sim >= threshold:
                        chunk = dict(self.chunks[idx])
                        chunk["similarity"] = round(sim, 3)
                        chunk["score_pct"] = round(sim * 100)
                        results.append(chunk)

                if results:
                    return results
            except Exception as e:
                print(f"[RAG Warning] Vector search error: {e}. Switching to keyword matching...")

        # Keyword matching fallback
        query_words = set(query.lower().split())
        for chunk in self.chunks:
            text = chunk["full_text"].lower()
            matches = sum(1 for w in query_words if len(w) > 2 and w in text)
            if matches > 0:
                sim = min(0.95, 0.4 + matches * 0.1)
                item = dict(chunk)
                item["similarity"] = round(sim, 3)
                item["score_pct"] = round(sim * 100)
                results.append(item)

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
