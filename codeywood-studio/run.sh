#!/bin/bash
# Launch Codeywood Studio (dev mode — Flask + Vite)
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$DIR")"

# Start Flask backend
source "$ROOT/scripts/venv/bin/activate"
echo "Starting Flask API on :5555..."
cd "$DIR/backend" && python3 app.py &
FLASK_PID=$!

# Start Vite dev server
echo "Starting Vite dev server on :5173..."
cd "$DIR/frontend" && npm run dev &
VITE_PID=$!

# Open browser
sleep 2
open http://localhost:5173

echo ""
echo "Codeywood Studio running:"
echo "  Frontend: http://localhost:5173"
echo "  API:      http://localhost:5555"
echo "  Press Ctrl+C to stop"

trap "kill $FLASK_PID $VITE_PID 2>/dev/null; exit" INT TERM
wait
