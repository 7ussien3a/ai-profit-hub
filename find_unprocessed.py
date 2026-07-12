import json
import os

topics = json.load(open('topics.json', encoding='utf-8'))
for i, t in enumerate(topics):
    basename = t['basename']
    filepath = os.path.join('articles', basename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        if size > 1000 and not basename.startswith('article'):
            print(f'{i}: {basename}')
