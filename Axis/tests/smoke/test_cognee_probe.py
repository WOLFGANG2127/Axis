import cognee

print("Cognee imported successfully")
public_names = [name for name in dir(cognee) if not name.startswith("_")]
print("Public names:")
for name in public_names[:100]:
    print(name)

print("\nHas remember():", hasattr(cognee, "remember"))
print("Has cognify():", hasattr(cognee, "cognify"))
print("Has search():", hasattr(cognee, "search"))