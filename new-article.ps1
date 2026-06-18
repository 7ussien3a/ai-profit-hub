##############################################################
# new-article.ps1 — AI Profit Hub
# Creates a new article from the template automatically.
# Usage:
#   .\new-article.ps1 -slug "my-article-name" -title "My Article Title"
##############################################################

param(
    [Parameter(Mandatory=$true)]
    [string]$slug,

    [Parameter(Mandatory=$false)]
    [string]$title = "New Article"
)

$templatePath = ".\article-template.html"
$outputPath   = ".\articles\$slug.html"

# Check template exists
if (-not (Test-Path $templatePath)) {
    Write-Host "[ERROR] article-template.html not found!" -ForegroundColor Red
    exit 1
}

# Check output doesn't already exist
if (Test-Path $outputPath) {
    Write-Host "[WARNING] $outputPath already exists! Choose a different slug." -ForegroundColor Yellow
    exit 1
}

# Copy template to new article
Copy-Item $templatePath $outputPath

# Replace the slug placeholder in the new file
$content = Get-Content $outputPath -Raw -Encoding UTF8
$content = $content -replace 'ARTICLE_URL_SLUG', $slug
$today   = Get-Date -Format "yyyy-MM-dd"
$content = $content -replace '"datePublished": "2026-06-18"', "`"datePublished`": `"$today`""
$content = $content -replace '"dateModified": "2026-06-18"',  "`"dateModified`": `"$today`""
Set-Content $outputPath -Value $content -Encoding UTF8

Write-Host ""
Write-Host "✅ Article created: $outputPath" -ForegroundColor Green
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open: site\articles\$slug.html" -ForegroundColor White
Write-Host "  2. Replace ARTICLE_TITLE with your title" -ForegroundColor White
Write-Host "  3. Replace ARTICLE_DESCRIPTION with 150-160 chars" -ForegroundColor White
Write-Host "  4. Replace ARTICLE_IMAGE_URL with Unsplash URL" -ForegroundColor White
Write-Host "  5. Replace ARTICLE_TAG (e.g. '🤖 AI Tools')" -ForegroundColor White
Write-Host "  6. Replace SOURCE_NAME (e.g. 'TechCrunch')" -ForegroundColor White
Write-Host "  7. Write your article content between the h2/p tags" -ForegroundColor White
Write-Host "  8. Run: git add . ; git commit -m 'New: $title' ; git push" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "The sidebar, TOC, related articles, and high-res images" -ForegroundColor DarkGray
Write-Host "are ALL automatic — no extra work needed!" -ForegroundColor DarkGray
Write-Host ""
