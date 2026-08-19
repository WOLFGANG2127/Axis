import os
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            try:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    if 'while' in f.read():
                        print(f"Loop found in {file}")
            except: pass
