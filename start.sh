#!/bin/bash
# =========================================================================
# 🚨 iReport - Single Command Project Setup & Launcher
# =========================================================================

echo "🚀 Starting iReport - Cybercrime Assistant Portal..."

# 1. Virtual environment setup
if [ ! -d "venv" ]; then
    echo "📦 Creating Python Virtual Environment..."
    python3 -m venv venv
fi

echo "⚡ Activating Virtual Environment & Installing Dependencies..."
source venv/bin/activate
pip install -r backend/requirements.txt --quiet

# 2. Database initialization and seeding
echo "🗄️ Initializing SQLite Database & Seeding Demo Accounts..."
cd backend
python3 init_db.py
python3 seed_data.py
python3 seed_roles.py

# 3. Launch Flask Backend Server
echo "🌐 Launching Backend API Server on http://localhost:5000..."
python3 app.py &
BACKEND_PID=$!

cd ..

# 4. Launch Node.js Frontend Server
if [ -d "frontend" ]; then
    echo "🎨 Launching Frontend Server on http://localhost:3000..."
    cd frontend
    npm install --quiet
    npm start &
    FRONTEND_PID=$!
    cd ..
fi

echo "============================================================="
echo "🎉 iReport is running!"
echo "👉 Web Portal / Flask Server: http://localhost:5000"
echo "👉 Express Frontend Server:  http://localhost:3000"
echo "============================================================="
echo "Press Ctrl+C to terminate servers."

wait $BACKEND_PID $FRONTEND_PID
