import sys
import io
import traceback
import runpy

with open("stdout.txt", "wb") as f_out, open("stderr.txt", "wb") as f_err:
    sys.stdout = io.TextIOWrapper(f_out, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(f_err, encoding="utf-8")

    try:
        sys.argv = ['scripts/auto_publisher.py', 'articles/article62.md']
        runpy.run_path('scripts/auto_publisher.py', run_name='__main__')
    except SystemExit as e:
        print(f"Exited with {e.code}")
    except Exception as e:
        traceback.print_exc()

    sys.stdout.flush()
    sys.stderr.flush()
