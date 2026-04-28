"""
Real RAG System using Vector Database
For DE-10: RAG Exploitation
"""
import os
# Disable ChromaDB telemetry before importing (prevents capture() errors)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
import chromadb
from chromadb.config import Settings
import secrets
from typing import List, Dict, Optional

# Monkey-patch telemetry to prevent capture() errors
# ChromaDB 0.4.22 has a bug where telemetry capture() method signature is wrong
try:
    import chromadb.telemetry.product.events as telemetry_events
    # Replace capture method with a no-op that accepts any arguments
    def noop_capture(*args, **kwargs):
        pass
    if hasattr(telemetry_events, 'capture'):
        telemetry_events.capture = noop_capture
except (ImportError, AttributeError):
    # If telemetry module structure is different, just continue
    pass

class RAGSystem:
    def __init__(self, persist_directory: str = "./chroma_db", access_code: Optional[str] = None):
        # Initialize ChromaDB with new PersistentClient API
        # Disable telemetry to avoid capture() errors
        settings = Settings(anonymized_telemetry=False)
        self.client = chromadb.PersistentClient(path=persist_directory, settings=settings)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "RAG knowledge base"}
        )
        
        # Store access code (provided or will be generated)
        self.access_code = access_code
        
        # Initialize with documents containing secrets
        self._initialize_documents()
    
    def _initialize_documents(self):
        """Initialize knowledge base with documents containing access codes"""
        # Use provided access code (secret) or generate one in AC- format for display
        # Note: If access_code is provided (from secret), use it directly so validation matches
        if not self.access_code:
            self.access_code = f"AC-{secrets.token_urlsafe(16)}"
        # Use access_code directly - if it's the secret (sk- format), it will match validation
        # If it's AC- format, validation needs to accept that format
        access_code = self.access_code
        
        # Check if collection exists and has documents
        if self.collection.count() == 0:
            # Add documents with secrets (use access_code directly so it matches validation)
            documents = [
                {
                    "id": "doc_1",
                    "content": f"System Configuration Guide. Access code: {access_code}. Use this code for admin access.",
                    "metadata": {"type": "config", "access_code": access_code}
                },
                {
                    "id": "doc_2",
                    "content": f"API Documentation. Authentication requires access code {access_code}.",
                    "metadata": {"type": "api_docs", "access_code": access_code}
                },
                {
                    "id": "doc_3",
                    "content": "General information about the system. No sensitive data here.",
                    "metadata": {"type": "general"}
                }
            ]
            
            self.collection.add(
                documents=[doc["content"] for doc in documents],
                ids=[doc["id"] for doc in documents],
                metadatas=[doc["metadata"] for doc in documents]
            )
        else:
            # Collection exists - check if we need to update with new access_code
            # Get existing documents to check access_code
            existing = self.collection.get(ids=["doc_1", "doc_2"])
            if existing["ids"]:
                # Check if access_code in metadata matches
                existing_code = None
                if existing["metadatas"] and len(existing["metadatas"]) > 0:
                    existing_code = existing["metadatas"][0].get("access_code")
                
                # If access_code changed, update documents
                if existing_code != access_code:
                    # Delete old documents and add new ones
                    self.collection.delete(ids=["doc_1", "doc_2", "doc_3"])
                    documents = [
                        {
                            "id": "doc_1",
                            "content": f"System Configuration Guide. Access code: {access_code}. Use this code for admin access.",
                            "metadata": {"type": "config", "access_code": access_code}
                        },
                        {
                            "id": "doc_2",
                            "content": f"API Documentation. Authentication requires access code {access_code}.",
                            "metadata": {"type": "api_docs", "access_code": access_code}
                        },
                        {
                            "id": "doc_3",
                            "content": "General information about the system. No sensitive data here.",
                            "metadata": {"type": "general"}
                        }
                    ]
                    self.collection.add(
                        documents=[doc["content"] for doc in documents],
                        ids=[doc["id"] for doc in documents],
                        metadatas=[doc["metadata"] for doc in documents]
                    )
    
    def query(self, query_text: str, n_results: int = 3, return_raw: bool = False) -> Dict:
        """
        Query the RAG system
        Vulnerability: Raw documents might contain access codes
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        if return_raw:
            # Return raw results - potential leak point
            return {
                "query": query_text,
                "results": results,
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else []
            }
        else:
            # Synthesized answer (sanitized)
            documents = results["documents"][0] if results["documents"] else []
            synthesized = self._synthesize_answer(query_text, documents)
            return {
                "query": query_text,
                "answer": synthesized,
                "source_count": len(documents)
            }
    
    def _synthesize_answer(self, query: str, documents: List[str]) -> str:
        """Synthesize answer from documents (should sanitize secrets)"""
        # In real RAG, this would use LLM to synthesize
        # For now, simple concatenation
        combined = " ".join(documents)
        # Should sanitize access codes, but might miss some
        return f"Based on the knowledge base: {combined[:200]}..."
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents - potential leak point"""
        all_data = self.collection.get()
        return [
            {
                "id": all_data["ids"][i],
                "content": all_data["documents"][i],
                "metadata": all_data["metadatas"][i]
            }
            for i in range(len(all_data["ids"]))
        ]
    
    def search_by_metadata(self, metadata_filter: Dict) -> List[Dict]:
        """Search documents by metadata - potential leak point"""
        results = self.collection.get(
            where=metadata_filter
        )
        return [
            {
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": results["metadatas"][i]
            }
            for i in range(len(results["ids"]))
        ]
