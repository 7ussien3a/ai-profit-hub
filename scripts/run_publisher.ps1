$ErrorActionPreference = "SilentlyContinue"
Set-Location "C:\Users\Admin\Desktop\X\مشروع قوقل ادسنس\site"
C:\Users\Admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\auto_publisher.py
git add .
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "Auto-publish cycle: $timestamp"
git push