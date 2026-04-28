#!/bin/bash
# Quick Start Script for Backend (macOS/Linux)

echo "🚀 Starting AIVP Backend..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found! Please install Python 3.10+"
    exit 1
fi

# Navigate to backend directory
cd apps/api

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Check if Ollama is running
echo "🔍 Checking Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Warning: Ollama might not be running. Start it with: ollama serve"
fi

# Start the server
echo "🎯 Starting FastAPI server on http://localhost:8000"
echo "Press Ctrl+C to stop"
uvicorn main:app --reload --port 8000
