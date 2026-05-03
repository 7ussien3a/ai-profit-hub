$sitePath = Join-Path $PSScriptRoot ""
$files = Get-ChildItem -Path $sitePath -Filter "*.html" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $content = $content -replace 'TechMind AI', 'AI Profit Hub'
    $content = $content -replace 'techmindai\.com', 'ai-profit-hub.com'
    $content = $content -replace 'techmindai', 'ai-profit-hub'
    $content = $content -replace 'contact@ai-profit-hub.com', 'contact@ai-profit-hub.com'
    Set-Content $file.FullName -Value $content -Encoding UTF8 -NoNewline
    Write-Host "Updated: $($file.Name)"
}
Write-Host "All files updated!"
