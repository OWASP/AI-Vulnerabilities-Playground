# Quick Start Script for Frontend (Windows PowerShell)
Write-Host "🚀 Starting AIVP Frontend..." -ForegroundColor Cyan

# Check if Node.js is available
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
Set-Location apps\web

# Check if node_modules exists
if (-not (Test-Path node_modules)) {
    Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}

# Create .env if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

# Start the development server
Write-Host "🎯 Starting Vite dev server on http://localhost:5173" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
npm run dev
