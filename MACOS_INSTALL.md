# macOS Installation Guide

This guide explains how to install the Menus application on any Mac with a double-clickable desktop icon.

---

## ✅ Preferred Installation: Applications Directory (Recommended)

The cleanest way to install is to place the application in your `/Applications/` folder and create a desktop symlink.

### Steps:

1. **Open Terminal** (press `Command + Space`, type `Terminal`, press Enter)

2. **Navigate to your project directory** (where `manage.py` is located):
   ```bash
   cd /path/to/your/menus/project
   ```

3. **Run the Applications installer:**
   ```bash
   ./install_to_applications.sh
   ```

4. **Double-click `menus.command` on your Desktop**

5. **Terminal opens** → Server starts → Your browser automatically opens to http://127.0.0.1:8000/

**Result:** Application installed in `/Applications/Menus/` with a Desktop symlink for easy access.

---

## Alternative: Self-Contained Folder on Desktop

If you prefer to have a self-contained folder directly on your Desktop:

1. **Open Terminal**

2. **Navigate to your project directory:**
   ```bash
   cd /path/to/your/menus/project
   ```

3. **Run the package creator:**
   ```bash
   ./create_package.sh
   ```

4. **Double-click `Start.command` inside the `Menus` folder on your Desktop**

**Result:** Self-contained `Menus` folder on Desktop with all files inside.

---

## For Sharing: Create a Zip File

To share the application with others, create a distributable zip file:

1. **Open Terminal**

2. **Navigate to your project directory:**
   ```bash
   cd /path/to/your/menus/project
   ```

3. **Run:**
   ```bash
   ./create_distributable.sh
   ```

4. **Share `~/Desktop/Menus.zip`** with users

**Users just need to:** Extract the zip and double-click `Start.command` inside the Menus folder.

---

## How It Works

All installation methods use reliable path resolution to ensure the application finds its files, regardless of where it's launched from. The scripts use universal binaries (`zsh`, `python3`) that work natively on both Intel and Apple Silicon Macs without requiring Rosetta.

The application will:
- Run database migrations (if needed)
- Start the Django development server
- Open your browser automatically to http://127.0.0.1:8000/

---

## Stopping the Server

To stop the application:
- Go to the Terminal window that's running the server
- Press `Control + C`
- Close the Terminal window

---

## Troubleshooting

### "Cannot find manage.py" error

This usually means the script path resolution failed. Try:
- Make sure you're running the installer from the directory containing `manage.py`
- Ensure you have the latest version of the installer scripts
- The script `Start.command` must be in the same folder as `manage.py`

### "Python not found" error

Install Python from https://www.python.org/downloads/macos/ or use Homebrew:
```bash
brew install python
```

### "No module named django"

Install the requirements from your project directory:
```bash
python3 -m pip install -r requirements.txt
```

### Port already in use

Try a different port:
```bash
python3 manage.py runserver 8080
```
Then access http://127.0.0.1:8080/

### Django compatibility errors

If you see `TypeError: __init__() got an unexpected keyword argument 'condition'`, your Django version expects `check=` instead of `condition=` in `CheckConstraint` calls. Make sure your code uses `check=` parameter which works with both Django 4.x and 5.x.

---

## Installation Scripts Summary

| Script | Creates | Use Case | Preferred? |
|--------|---------|----------|------------|
| `install_to_applications.sh` | `/Applications/Menus/` + Desktop symlink | Personal installation | ✅ **Yes** |
| `create_package.sh` | Self-contained folder on Desktop | Portable version | ❌ Alternative |
| `create_distributable.sh` | Zip file for sharing | Distribution | ❌ For sharing |

---

## Notes

- The development server is for local use only
- The application uses SQLite by default
- All data is stored in `db.sqlite3` in the application directory
- All solutions work on both Intel and Apple Silicon Macs without Rosetta
- The Applications installation method is most similar to how native macOS apps are organized
