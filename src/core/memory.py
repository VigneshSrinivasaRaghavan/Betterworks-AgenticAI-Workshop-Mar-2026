from datetime import datetime
from typing import List, Dict, Optional
from src.core.vector_store import load_memory_store


class PersistentMemory:
    """Long-term memory using ChromaDB for cross-session persistence.

    Stores agent outputs as vector embeddings.
    Retrieved via semantic similarity search at the start of each session.
    Uses a dedicated ChromaDB collection — separate from the RAG collection.
    """

    def __init__(self, collection_name: str = "agent_memory"):
        self.collection_name = collection_name
        self.vector_store = load_memory_store(collection_name)
        print(f"PersistentMemory initialized — collection: {collection_name}")

    def store_interaction(self, text: str, metadata: Optional[Dict] = None) -> None:
        """Store an interaction in long-term memory."""
        if metadata is None:
            metadata = {}

        metadata["timestamp"] = datetime.now().isoformat()
        metadata["collection"] = self.collection_name

        self.vector_store.add_texts(
            texts=[text],
            metadatas=[metadata]
        )
        print(f"Stored in LTM [{self.collection_name}]: {text[:60]}...")

    def retrieve_similar(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve past interactions similar to the query."""
        results = self.vector_store.similarity_search_with_score(query, k=top_k)

        interactions = []
        for doc, score in results:
            interactions.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance": round(1 - score, 3)
            })

        return interactions

    def get_context(self, query: str, top_k: int = 3) -> str:
        """Return formatted LTM context string for injection into LLM prompt."""
        interactions = self.retrieve_similar(query, top_k)

        if not interactions:
            print(f"No past interactions found in LTM for: {query[:50]}")
            return ""

        context_blocks = []
        for i, interaction in enumerate(interactions, 1):
            timestamp = interaction["metadata"].get("timestamp", "unknown")
            block = f"[Past Interaction {i} - {timestamp}]\\n{interaction['content']}"
            context_blocks.append(block)

        print(f"Retrieved {len(interactions)} past interaction(s) from LTM")
        return "\n---\n".join(context_blocks)