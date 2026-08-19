import os
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            with open(os.path.join(root, file), 'r') as f:
                content = f.read()
                if 'DhanRateLimitError' in content:
                    print(f"Found in {file}")
