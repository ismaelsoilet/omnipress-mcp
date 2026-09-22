# ==============================================================================
# OmniPress MCP — GitHub Publication Helper Script
# ==============================================================================

Write-Host "🚀 Preparing to publish OmniPress MCP to GitHub..." -ForegroundColor Cyan

# 1. Check for Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️ Git is not installed or not in PATH." -ForegroundColor Yellow
    $install = Read-Host "Would you like to install Git via winget now? (Y/N)"
    if ($install -eq 'Y' -or $install -eq 'y') {
        Write-Host "📦 Installing Git via winget..." -ForegroundColor Green
        winget install --id Git.Git -e --source winget
        Write-Host "✅ Git installation requested. Please restart PowerShell and re-run this script." -ForegroundColor Green
        Exit
    } else {
        Write-Host "Please install Git from https://git-scm.com/ and re-run this script." -ForegroundColor Red
        Exit
    }
}

# 2. Initialize Git repository
if (-not (Test-Path ".git")) {
    Write-Host "🌱 Initializing Git repository..." -ForegroundColor Green
    git init -b main
}

# 3. Add and commit files
Write-Host "📝 Staging project files..." -ForegroundColor Green
git add .
git commit -m "feat: initial release of OmniPress MCP (Agentic Publishing Engine with LinkedIn, X, Threads, and Reddit support)"

# 4. Connect to remote repository
$repoUrl = Read-Host "Enter your GitHub repository URL (e.g. https://github.com/username/omnipress-mcp.git)"
if ($repoUrl) {
    git remote remove origin -ErrorAction SilentlyContinue
    git remote add origin $repoUrl
    Write-Host "🚀 Pushing to $repoUrl..." -ForegroundColor Green
    git push -u origin main
    Write-Host "🎉 Successfully published to GitHub!" -ForegroundColor Cyan
} else {
    Write-Host "Repository initialized and committed locally. Add your remote with: git remote add origin <url> and git push -u origin main" -ForegroundColor Yellow
}
