from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

# Paths
ROOT = Path(__file__).resolve().parents[2]
KB_DIR = ROOT / "data" / "knowledge_base"
VECTOR_STORE_DIR = ROOT / "data" / "vector_store"

# Initialize Embeddings
embeddings = OpenAIEmbeddings(
    model = "text-embedding-3-small",
    api_key = os.getenv("OPENAI_API_KEY")
)

def build_vector_store():
    """Load documents, split into chunks, and create vector store."""

    print("Building vector store...")

    # 1. Load documents
    print(f"Loading documents from {KB_DIR}...")
    loader = DirectoryLoader(
        str(KB_DIR),
        glob="**/*.md",
        loader_cls=TextLoader
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    # 2. Split into chunks
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    # 3. Create vector store
    print("Generating embeddings and storing in ChromaDB...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_DIR)
    )
    print(f"Vector store created at {VECTOR_STORE_DIR}")

    return vector_store

def load_vector_store():
    """Load existing vector store."""

    if not VECTOR_STORE_DIR.exists():
        raise FileNotFoundError(
            f"Vector store not found at {VECTOR_STORE_DIR}. "
            "Run build_vector_store() first."
        )

    return Chroma(
        persist_directory=str(VECTOR_STORE_DIR),
        embedding_function=embeddings
    )

def search_vector_store(query: str, top_k: int = 3):
    """Search vector store for relevant documents."""

    vector_store = load_vector_store()
    results = vector_store.similarity_search_with_score(query, k=top_k)

    return results


def load_memory_store(collection_name: str):
    """Load or create a ChromaDB collection for long-term memory.

    Separate from the RAG vector store — this is where agent outputs
    are stored and retrieved across sessions.
    """
    memory_dir = ROOT / "data" / "memory" / collection_name
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    return Chroma(
        persist_directory=str(memory_dir),
        embedding_function=embeddings,
        # hnsw:space = distance formula ChromaDB uses internally to compare vectors
        # "cosine" measures angle between vectors (ignores length, only cares about direction)
        # Best for text — a short and long sentence on the same topic still match correctly
        # Score 0 = perfect match, 1 = unrelated → relevance = 1 - score (clean 0-1 range)
        collection_metadata={"hnsw:space": "cosine"}
    )