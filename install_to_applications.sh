#!/bin/zsh

# Install Menus to Applications directory
# Creates the app in /Applications/Menus and adds a desktop alias

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_NAME="Menus"
APPS_DIR="/Applications/$PACKAGE_NAME"
DESKTOP_ALIAS="$HOME/Desktop/menus.command"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Installing Menus to Applications${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if project exists
if [ ! -f "$SCRIPT_DIR/manage.py" ]; then
    echo -e "${YELLOW}Error: manage.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Remove old versions
if [ -d "$APPS_DIR" ]; then
    echo "Removing old installation from Applications..."
    rm -rf "$APPS_DIR"
fi

if [ -e "$DESKTOP_ALIAS" ]; then
    echo "Removing old desktop alias..."
    rm "$DESKTOP_ALIAS"
fi

# Create Applications directory
mkdir -p "$APPS_DIR"

# Copy all project files
echo "Copying project files to Applications..."
cp -r "$SCRIPT_DIR/ajouter-recette.html" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/connexion.html" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/db.sqlite3" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/generer.html" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/index.html" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/manage.py" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/menus_project" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/menus-sauvegardes.html" "$APP_DIR/"
cp -r "$SCRIPT_DIR/profile.html" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/recipes" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/repas.html" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/requirements.txt" "$APPS_DIR/"
cp -r "$SCRIPT_DIR/static" "$APPS_DIR/"
[ -f "$SCRIPT_DIR/.gitignore" ] && cp "$SCRIPT_DIR/.gitignore" "$APPS_DIR/"

# Create the launcher script
cat > "$APPS_DIR/Start.command" <<'EOF'
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
sleep 2

# Open browser
open "http://127.0.0.1:8000/"

# Bring server back to foreground
fg %1 2>/dev/null || wait $SERVER_PID
EOF

chmod +x "$APPS_DIR/Start.command"

# Create README
cat > "$APPS_DIR/README.txt" <<EOF
Menus Application
================

To start the application:
  Double-click "Start.command" in the Menus folder

To start from Desktop:
  Double-click "menus.command" on your Desktop

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

# Create desktop alias (symlink)
echo "Creating desktop alias..."
ln -s "$APPS_DIR/Start.command" "$DESKTOP_ALIAS"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Application installed to: $APPS_DIR"
echo "Desktop alias created at: $DESKTOP_ALIAS"
echo ""
echo "To use:"
echo "  1. Double-click 'menus.command' on your Desktop"
echo "  2. Or double-click 'Start.command' in /Applications/Menus"
echo ""
echo "The alias on your Desktop points to the application in Applications."
echo "You can move or delete the Desktop alias without affecting the application."
echo ""
