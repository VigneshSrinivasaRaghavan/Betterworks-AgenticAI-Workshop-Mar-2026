"""
Quick test to verify PersistentMemory (LTM) is working correctly.
Run: python test_persistent_memory.py
"""
from src.core.memory import PersistentMemory


def test_persistent_memory():
    print("=" * 50)
    print("Testing PersistentMemory (Long-term Memory)")
    print("=" * 50)

    memory = PersistentMemory(collection_name="test_memory")

    print("\n--- Storing interactions ---")
    memory.store_interaction(
        "Generated 5 login API tests covering 2FA, rate limiting, and session expiry",
        metadata={"type": "test_case", "requirement": "login API"}
    )
    memory.store_interaction(
        "Generated 4 payment API tests covering checkout, refund, and failed transactions",
        metadata={"type": "test_case", "requirement": "payment API"}
    )
    memory.store_interaction(
        "Analyzed database connection pool error - root cause: Microservice-B not closing connections",
        metadata={"type": "log_analysis", "severity": "high"}
    )

    print("\n--- Retrieving similar to: 'login authentication tests' ---")
    context = memory.get_context("authentication tests", top_k=2)
    print(context)

    print("\n--- Retrieving similar to: 'database error analysis' ---")
    context = memory.get_context("database error analysis", top_k=2)
    print(context)

    print("\n" + "=" * 50)
    print("PersistentMemory test complete!")
    print("=" * 50)


if __name__ == "__main__":
    test_persistent_memory()
