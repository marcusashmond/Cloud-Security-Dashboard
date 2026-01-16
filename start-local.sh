#!/bin/bash

echo "🚀 Starting Cloud Security Dashboard (Local Development)"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Installing..."
    echo "Please install Node.js from: https://nodejs.org/"
    echo "Or run: brew install node"
    exit 1
fi

echo "✓ Node.js found: $(node --version)"
echo "✓ npm found: $(npm --version)"
echo ""

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo ""
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip3 install -r backend/requirements.txt
echo ""

# Set environment variable for SQLite
export USE_SQLITE=true

echo "🗄️  Using SQLite database (no Docker required)"
echo ""

# Start backend in background
echo "🚀 Starting backend server (http://localhost:8000)..."
cd backend
python3 -m uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend server (http://localhost:3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application started!"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '✅ Servers stopped'; exit" INT
wait
