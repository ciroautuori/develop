import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseTool

logger = logging.getLogger(__name__)

class RAGTool(BaseTool):
    """Tool for retrieving knowledge from local RAG files."""
    
    def __init__(self, name: str, description: str, data_paths: List[str]):
        self._name = name
        self._description = description
        self.data_paths = data_paths
        self.knowledge_base = []
        self._load_data()
        
    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def _load_data(self):
        """Load data from files into memory."""
        count = 0
        for path_str in self.data_paths:
            path = Path(path_str)
            if not path.exists():
                logger.warning(f"RAG file not found: {path}")
                continue
                
            try:
                if path.suffix == '.json':
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Handle different JSON structures
                        if isinstance(data, list):
                            self.knowledge_base.extend([str(item) for item in data])
                            count += len(data)
                        elif isinstance(data, dict):
                            self.knowledge_base.append(str(data))
                            count += 1
                            
                elif path.suffix == '.md':
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Split by headers for better retrieval chunks
                        sections = content.split('\n## ')
                        self.knowledge_base.extend(sections)
                        count += len(sections)
                        
            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
                
        logger.info(f"Loaded {count} items for tool {self.name}")

    async def execute(self, query: str) -> Dict[str, Any]:
        """Simple keyword search (Phase 1)."""
        query = query.lower()
        results = []
        
        # Simple keyword matching scoring
        for item in self.knowledge_base:
            item_lower = item.lower()
            score = 0
            
            # Exact phrase match
            if query in item_lower:
                score += 10
            
            # Individual word match
            words = query.split()
            matches = sum(1 for w in words if w in item_lower and len(w) > 3)
            score += matches
            
            if score > 0:
                results.append((score, item))
        
        # Sort by score
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Take top 3
        top_results = [item[:1000] + "..." for score, item in results[:3]]
        
        if not top_results:
            return {"result": f"No specific information found in {self.name} knowledge base."}
            
        return {
            "source": self.name,
            "relevant_info": "\n---\n".join(top_results)
        }

# Factory functions for specific RAG domains

def get_medical_rag_tool():
    base_path = "/app/data/rag/medical"  # Docker path
    # Fallback for local dev
    if not Path(base_path).exists():
        base_path = "apps/ironRep/apps/backend/data/rag/medical"
        
    return RAGTool(
        name="medical_knowledge",
        description="Useful for retrieving medical protocols, rehab exercises, and sports medicine info. Use this for injury-related questions.",
        data_paths=[
            f"{base_path}/rehab_protocols.json",
            f"{base_path}/sports_medicine_knowledge_base.md",
            f"{base_path}/movement_standards_complete.md"
        ]
    )

def get_training_rag_tool():
    base_path = "/app/data/rag"  # Docker path
    # Fallback for local dev
    if not Path(base_path).exists():
        base_path = "apps/ironRep/apps/backend/data/rag"

    return RAGTool(
        name="training_knowledge",
        description="Useful for CrossFit WODs, exercise standards, and training techniques.",
        data_paths=[
            f"{base_path}/training/crossfit_knowledge_base.md",
            f"{base_path}/exercises/exercises_complete.json"
        ]
    )
