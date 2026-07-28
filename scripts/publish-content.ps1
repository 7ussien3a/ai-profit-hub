$ErrorActionPreference = "Stop"

Write-Host "AI Profit Hub content publish check" -ForegroundColor Cyan
Write-Host "This command validates content, builds generated pages, updates search, sitemap, RSS, and checks generated routes."

python scripts/content_pipeline.py publish-check

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review changes with: git status --short"
Write-Host "2. Commit when ready: git add .gitignore content scripts data sitemap.xml rss.xml articles js README.md docs && git commit -m `"feat(content): add Obsidian content workflow`""
Write-Host "3. Push after review: git push origin main"
