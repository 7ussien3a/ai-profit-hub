import sys
import traceback
try:
    import runpy
    sys.argv = ['scripts/auto_publisher.py', 'articles/article62.md']
    runpy.run_path('scripts/auto_publisher.py', run_name='__main__')
except Exception as e:
    with open("err2.txt", "w") as f:
        traceback.print_exc(file=f)
