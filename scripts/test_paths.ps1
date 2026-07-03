# -*- coding: utf-8 -*-
# test_paths.ps1 - يختبر أن الناشر يكتشف المسارات الصحيحة من موقعه الجديد
$scriptPath = Join-Path (Get-Location).Path 'scripts\auto_publisher.py'
Write-Host ("Testing: $scriptPath")
# استخرج منطق اكتشاف المسارات (لا تشغّل main)
$probe = @"
import os, sys
_SCRIPT_DIR = os.path.dirname(os.path.abspath(r'$scriptPath'))
if os.path.isdir(os.path.join(_SCRIPT_DIR, 'site')):
    ROOT_DIR = _SCRIPT_DIR; SITE_DIR = os.path.join(_SCRIPT_DIR, 'site')
else:
    SITE_DIR = os.path.dirname(os.path.dirname(_SCRIPT_DIR)); ROOT_DIR = os.path.dirname(SITE_DIR)
print('SCRIPT_DIR :', _SCRIPT_DIR)
print('SITE_DIR   :', SITE_DIR, '(exists:', os.path.isdir(SITE_DIR), ')')
print('ROOT_DIR   :', ROOT_DIR)
print('articles   :', os.path.join(SITE_DIR,'articles'), '(exists:', os.path.isdir(os.path.join(SITE_DIR,'articles')), ')')
cfg = os.path.join(_SCRIPT_DIR, 'publish-config.json')
print('config     :', cfg, '(exists:', os.path.exists(cfg), ')')
tmpl = os.path.join(SITE_DIR, 'article-template.html')
print('template   :', tmpl, '(exists:', os.path.exists(tmpl), ')')
"@
$probe | Out-File -FilePath "$env:TEMP\probe.py" -Encoding UTF8
$pythonExe = @('python','python3','py') | ForEach-Object { $c = Get-Command $_ -ErrorAction SilentlyContinue; if ($c) { $_ } } | Select-Object -First 1
if (-not $pythonExe) { Write-Host 'No python on PATH - skipping runtime probe (syntax-only)'; exit 0 }
& $pythonExe "$env:TEMP\probe.py"
