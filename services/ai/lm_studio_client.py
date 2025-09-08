"""
LM Studio Client - Embeddings and Reranking Only
NO MOCKS ALLOWED - Real LM Studio integration required
"""

import os
import requests
from typing import List, Dict, Any

# NO-MOCKS GUARD: Hard-fail if any mock toggle is detected
if os.getenv("DISABLE_MOCKS", "0") == "1":
    if os.getenv("MOCK_LMS", "0") != "0":
        raise RuntimeError("NO-MOCKS: LM Studio mock mode is forbidden (MOCK_LMS must be 0).")

class LMStudioClient:
    """LM Studio client for embeddings and reranking (NOT creative generation)"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1"):
        self.base_url = base_url
        self.api_key = os.getenv("OPENAI_API_KEY", "lm-studio")
        
        # Verify LM Studio is reachable
        if not self._health_check():
            raise RuntimeError("NO-MOCKS: LM Studio is not reachable. Start LM Studio on port 1234.")
    
    def _health_check(self) -> bool:
        """Check if LM Studio is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/models", 
                                  headers={"Authorization": f"Bearer {self.api_key}"}, 
                                  timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate Qwen 1024-dim embeddings for content"""
        # Implementation for embedding generation
        pass
    
    async def rerank_content(self, query: str, candidates: List[str]) -> List[Dict[str, Any]]:
        """Chat-based reranking for content quality"""
        # Implementation for content reranking
        pass
    
    async def health_check(self) -> bool:
        """Check if LM Studio is running and healthy"""
        return self._health_check()