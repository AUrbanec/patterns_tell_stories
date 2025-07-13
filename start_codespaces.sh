#!/bin/bash

# 🎙️ Podcast Relationship Mapper - Codespaces Quick Start
echo "🎙️ Welcome to Podcast Relationship Mapper!"
echo "=========================================="

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "⚠️  GEMINI_API_KEY not set!"
    echo ""
    echo "📋 To get started:"
    echo "1. Get your API key from: https://aistudio.google.com/app/apikey"
    echo "2. Run: export GEMINI_API_KEY=\"your_api_key_here\""
    echo "3. Run: ./start_codespaces.sh"
    echo ""
    exit 1
fi

echo "✅ API key detected"

# Install dependencies if not already installed
if [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Initialize database if it doesn't exist
if [ ! -f "podcast_mapper.db" ]; then
    echo "🗄️  Initializing database..."
    python -c "from database import create_tables; create_tables()"
fi

echo ""
echo "🚀 Starting servers..."
echo ""

# Start backend in background
echo "Starting backend server on port 8000..."
python run_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "Starting frontend server on port 3000..."
cd frontend
python -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Both servers are running!"
echo ""
echo "📱 Access your application:"
echo "   • Backend API: http://localhost:8000"
echo "   • Frontend UI: http://localhost:3000"
echo ""
echo "💡 In Codespaces:"
echo "   • Look for port forwarding notifications"
echo "   • Click the 'Ports' tab to access URLs"
echo "   • Click the globe icon next to each port"
echo ""
echo "🛑 To stop servers: Ctrl+C"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Keep script running
wait