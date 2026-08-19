with open('src/data/dhan_client.py', 'r', encoding='utf-8') as f:
    text = f.read()
    if 'while' in text: print('while loop found in dhan_client.py')
    if 'retry' in text.lower(): print('retry found in dhan_client.py')
