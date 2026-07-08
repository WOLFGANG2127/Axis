import inspect
import cognee

print("LLM Provider Setter:")
print(inspect.signature(cognee.config.set_llm_provider))

print()

print("Embedding Provider Setter:")
print(inspect.signature(cognee.config.set_embedding_provider))