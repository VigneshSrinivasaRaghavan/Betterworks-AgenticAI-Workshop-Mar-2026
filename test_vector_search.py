from src.core import search_vector_store

queries = [
    "How to test login API?",
    "Database connection issues",
    "API rate limiting"
]

print("Testing Vector Search...")
for query in queries:
    results = search_vector_store(query)
    print(f"Query: {query}")
    print("Results:", results, "\n")
    print("=============")

