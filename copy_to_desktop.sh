#!/bin/zsh

# Copy the Menus launcher to Desktop
# Creates a self-contained .command file with the correct project path

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$HOME/Desktop/Menus.command"
PROJECT_DIR="$SCRIPT_DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Installing Menus Desktop Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if project exists
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    echo -e "${YELLOW}Error: manage.py not found in $PROJECT_DIR${NC}"
    exit 1
fi

# Remove old versions
for f in "$HOME/Desktop/Menus.app" "$HOME/Desktop/MenusServer.command" "$DESKTOP_FILE"; do
    if [ -e "$f" ]; then
        echo "Removing old file: $f"
        rm -rf "$f"
    fi
done

# Create a custom .command file with the correct path embedded
cat > "$DESKTOP_FILE" <<'EOF'
#!/usr/bin/env zsh

# Menus Application Launcher
# Created by copy_to_desktop.sh
PROJECT_DIR="/Users/stephane/Documents/workarea/menus_test/menus"

if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    echo "Error: Cannot find manage.py at $PROJECT_DIR/manage.py"
    echo "The project may have been moved."
    exit 1
fi

cd "$PROJECT_DIR"

# Check for virtual environment
if [ -d ".venv/bin" ]; then
    PYTHON=".venv/bin/python3"
else
    PYTHON="python3"
fi

# Run migrations
echo "Running database migrations..."
$PYTHON manage.py migrate --noinput 2>&1 | grep -v "^$" || true

echo ""
echo "========================================"
echo "Starting Menus Server"
echo "========================================"
echo ""
echo "Server will be available at: http://127.0.0.1:8000/"
echo "Press Control+C to stop"
echo ""
echo ""

# Start the server in background, wait, then open browser, then bring to foreground
$PYTHON manage.py runserver &
SERVER_PID=$!

# Wait for server to start (5 seconds should be enough)
sleep 5

# Open browser
open "http://127.0.0.1:8000/"

# Bring server back to foreground and wait for it
fg %1 2>/dev/null || wait $SERVER_PID
EOF

# Make executable
chmod +x "$DESKTOP_FILE"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "A 'Menus.command' file has been placed on your Desktop."
echo "It is configured to use the project at: $PROJECT_DIR"
echo ""
echo "To use:"
echo "  1. Double-click 'Menus.command' on your Desktop"
echo "  2. A Terminal window will open"
echo "  3. The server will start and your browser will open automatically to http://127.0.0.1:8000/"
echo "  4. Press Control+C to stop"
echo ""
echo "To stop:"
echo "  - Press Control+C in the Terminal window"
echo "  - Close the Terminal window"
echo ""
echo "If port 8000 is already in use:"
echo "  - Run: lsof -i :8000 to find the process"
echo "  - Run: kill <PID> to stop it"
echo ""
