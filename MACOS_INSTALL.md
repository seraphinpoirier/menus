# macOS Installation Guide

The simplest way to have a desktop icon that launches your Menus application with a double-click.

---

## ✅ Quick Install (Recommended - No Rosetta)

This creates a `.command` file on your Desktop that launches the application using Terminal.

**Why this works without Rosetta:**
- Uses `zsh` (universal binary on Apple Silicon)
- Uses `python3` (universal binary on Apple Silicon)
- Opens in Terminal (universal app)

### Steps:

1. **Open Terminal** (press `Command + Space`, type `Terminal`, press Enter)

2. **Run the installer:**
   ```bash
   cd /Users/stephane/Documents/workarea/menus_test/menus
   ./copy_to_desktop.sh
   ```

3. **Double-click `Menus.command` on your Desktop**

4. **Terminal opens** → Server starts → Open your browser to http://127.0.0.1:8000/

---

## How It Works

The installer (`copy_to_desktop.sh`) creates a custom `Menus.command` file on your Desktop with the **absolute path** to your project hardcoded. This ensures it always finds your `manage.py` file, even if you move the .command file.

---

## Stopping the Server

To stop the application:
- Go to the Terminal window that's running the server
- Press `Control + C`
- Close the Terminal window

---

## Troubleshooting

### "Cannot find manage.py" error

The .command file is looking for the project at `/Users/stephane/Documents/workarea/menus_test/menus`.

If you moved your project, either:
- Move it back to the original location, OR
- Run `./copy_to_desktop.sh` again from the new location

### "Python not found" error

Install Python from https://www.python.org/downloads/macos/ or use Homebrew:
```bash
brew install python
```

### "No module named django"

Install the requirements:
```bash
cd /Users/stephane/Documents/workarea/menus_test/menus
python3 -m pip install -r requirements.txt
```

### Port already in use

Try a different port:
```bash
python3 manage.py runserver 8080
```
Then access http://127.0.0.1:8080/

---

## Files Created

| File | Location | Purpose |
|------|----------|---------|
| `copy_to_desktop.sh` | Project directory | Creates the desktop launcher |
| `Menus.command` | Desktop | The launcher (created by the installer) |

---

## Notes

- The development server is for local use only
- The application uses SQLite by default
- All data is stored in `db.sqlite3` in your project directory
- This solution works on both Intel and Apple Silicon Macs without Rosetta
