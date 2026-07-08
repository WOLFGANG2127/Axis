import inspect
import cognee

print("remember signature:", inspect.signature(cognee.remember))
print("recall signature   :", inspect.signature(cognee.recall))
print("search signature   :", inspect.signature(cognee.search))