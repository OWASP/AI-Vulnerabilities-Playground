#!/bin/bash
# Quick Start Script for Frontend (macOS/Linux)

echo "🚀 Starting AIVP Frontend..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install Node.js 18+"
    exit 1
fi

# Navigate to frontend directory
cd apps/web

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Start the development server
echo "🎯 Starting Vite dev server on http://localhost:5173"
echo "Press Ctrl+C to stop"
npm run dev
