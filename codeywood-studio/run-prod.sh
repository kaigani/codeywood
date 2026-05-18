#!/bin/bash
# Launch Codeywood Studio (production mode — Flask serves built React)
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$DIR")"

# Build frontend
echo "Building frontend..."
cd "$DIR/frontend" && npm run build
if [ $? -ne 0 ]; then
  echo "Build failed!"
  exit 1
fi

# Start Flask (serves frontend/dist/)
source "$ROOT/scripts/venv/bin/activate"
echo "Starting Codeywood Studio at http://localhost:5555"
open http://localhost:5555 &
cd "$DIR/backend" && python3 app.py
