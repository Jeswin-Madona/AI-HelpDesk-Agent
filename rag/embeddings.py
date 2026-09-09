import os
import warnings
warnings.filterwarnings("ignore")
from typing import List, Optional

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    import google.generativeai as legacy_genai

class EmbeddingService:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        raw_model = model_name or os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
        self.model_name = raw_model.replace("models/", "") if raw_model else "gemini-embedding-001"
        
        self.client = None
        if self.api_key and HAS_GENAI:
            self.client = genai.Client(api_key=self.api_key)
        elif self.api_key and not HAS_GENAI:
            legacy_genai.configure(api_key=self.api_key)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates vector embedding for input text.
        """
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")

        try:
            if HAS_GENAI and self.client:
                res = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text
                )
                return list(res.embeddings[0].values)
            else:
                result = legacy_genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                return result["embedding"]
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding via Gemini API: {str(e)}")

    def get_query_embedding(self, text: str) -> List[float]:
        """
        Generates vector embedding optimized for user retrieval query.
        """
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")

        try:
            if HAS_GENAI and self.client:
                res = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text
                )
                return list(res.embeddings[0].values)
            else:
                result = legacy_genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_query"
                )
                return result["embedding"]
        except Exception as e:
            raise RuntimeError(f"Failed to generate query embedding via Gemini API: {str(e)}")

