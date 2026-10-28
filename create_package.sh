#!/bin/zsh

# Create a self-contained Menus package
# This creates a folder that can be placed anywhere (Desktop, Applications, etc.)
# and will work without needing to clone the repository

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_NAME="Menus"
INSTALL_DIR="$HOME/Desktop/$PACKAGE_NAME"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Creating Self-Contained Menus Package${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -f "$SCRIPT_DIR/manage.py" ]; then
    echo -e "${YELLOW}Error: manage.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "Removing old package..."
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"

echo "Copying project files..."
cp -r "$SCRIPT_DIR/ajouter-recette.html" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/connexion.html" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/db.sqlite3" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/generer.html" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/index.html" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/manage.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/menus_project" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/profile.html" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/recipes" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/repas.html" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/static" "$INSTALL_DIR/"
[ -f "$SCRIPT_DIR/.gitignore" ] && cp "$SCRIPT_DIR/.gitignore" "$INSTALL_DIR/"

# Create a self-contained launcher script using realpath for reliable path resolution
cat > "$INSTALL_DIR/Start.command" <<'EOF'
#!/usr/bin/env zsh

# Self-contained Menus Launcher
# Uses realpath for reliable absolute path resolution

SCRIPT_DIR="$(dirname "$(realpath "$0" 2>/dev/null || echo "$0")")"
PROJECT_DIR="$SCRIPT_DIR"

if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    echo "Error: Cannot find manage.py in $PROJECT_DIR"
    echo "This script must be in the same folder as manage.py"
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

# Start the server in background, wait, then open browser
$PYTHON manage.py runserver &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Open browser
open "http://127.0.0.1:8000/"

# Bring server back to foreground
fg %1 2>/dev/null || wait $SERVER_PID
EOF

chmod +x "$INSTALL_DIR/Start.command"

cat > "$INSTALL_DIR/README.txt" <<EOF
Menus Application
================

To start the application:
  Double-click "Start.command"

The application will:
  - Run database migrations (if needed)
  - Start the Django development server
  - Open your browser to http://127.0.0.1:8000/

To stop:
  Press Control+C in the Terminal window

Requirements:
  - Python 3 (pre-installed on most Macs)
  - Django and dependencies (will be installed automatically on first run if missing)
EOF

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Package Created!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Location: $INSTALL_DIR"
echo ""
echo "To use:"
echo "  1. Open Finder"
echo "  2. Go to your Desktop"
echo "  3. Double-click 'Start.command' inside the Menus folder"
echo ""
echo "The package is self-contained and can be:"
echo "  - Moved to any location"
echo "  - Copied to another Mac"
echo "  - Shared with others"
echo ""
