#!/bin/zsh

# Create a distributable package (zip file)
# Users can download, extract, and run without cloning

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_NAME="Menus"
TEMP_DIR="/tmp/Menus_Package_$$"
ZIP_FILE="$HOME/Desktop/$PACKAGE_NAME.zip"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Creating Distributable Menus Package${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -f "$SCRIPT_DIR/manage.py" ]; then
    echo -e "${YELLOW}Error: manage.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

mkdir -p "$TEMP_DIR/$PACKAGE_NAME"

echo "Copying project files..."
cp -r "$SCRIPT_DIR/ajouter-recette.html" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/connexion.html" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/db.sqlite3" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/generer.html" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/index.html" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/manage.py" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/menus_project" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/profile.html" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/recipes" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/repas.html" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/requirements.txt" "$TEMP_DIR/$PACKAGE_NAME/"
cp -r "$SCRIPT_DIR/static" "$TEMP_DIR/$PACKAGE_NAME/"
[ -f "$SCRIPT_DIR/.gitignore" ] && cp "$SCRIPT_DIR/.gitignore" "$TEMP_DIR/$PACKAGE_NAME/"

# Create the launcher using realpath for reliable path resolution
cat > "$TEMP_DIR/$PACKAGE_NAME/Start.command" <<'EOF'
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

chmod +x "$TEMP_DIR/$PACKAGE_NAME/Start.command"

cat > "$TEMP_DIR/$PACKAGE_NAME/README.txt" <<'EOF'
Menus Application
================

INSTALLATION:
------------
To install the Menus application:

1. Extract the zip file (double-click it)
2. Open the "Menus" folder
3. Double-click "Start.command"

That's it! The application will:
  - Run database migrations (if needed)
  - Start the Django development server
  - Automatically open your browser to http://127.0.0.1:8000/

USAGE:
------
To stop the server:
  Press Control+C in the Terminal window

REQUIREMENTS:
------------
- Python 3 (pre-installed on most Macs)
- Django and dependencies (will be installed automatically on first run)

TROUBLESHOOTING:
---------------
If you get an error about Python not being found:
  Install Python from https://www.python.org/downloads/macos/

If you get an error about Django not being found:
  Run: python3 -m pip install -r requirements.txt

If port 8000 is already in use:
  Run: lsof -i :8000 to find the process ID
  Run: kill <PID> to stop it
EOF

echo "Creating zip file..."
cd /tmp
zip -r "$ZIP_FILE" "Menus_Package_$$" > /dev/null 2>&1
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Distributable Package Created!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "File: $ZIP_FILE"
echo ""
echo "To share:"
echo "  - Email the zip file to users"
echo "  - Upload to a file sharing service"
echo "  - Post on your website"
echo ""
echo "Users just need to:"
echo "  1. Download the zip"
echo "  2. Extract it"
echo "  3. Double-click 'Start.command' inside the Menus folder"
echo ""
