import traceback
import sys
sys.path.insert(0, '.')
import scripts.auto_publisher
try:
    scripts.auto_publisher.main('articles/article56.md')
    print('OK')
except Exception as e:
    with open('error3.log', 'w') as f:
        f.write(traceback.format_exc())
