"""Copy this file to config.py and edit the values."""

# Absolute path to the .bat file you want to trigger from your phone.
BAT_PATH = r"C:\path\to\your\script.bat"

# ngrok static domain (optional). Leave as None for a random URL each run.
# Free ngrok accounts get one free static "dev domain" at
# https://dashboard.ngrok.com/domains — paste it here, e.g.:
# NGROK_DOMAIN = "your-dev-domain.ngrok-free.dev"
NGROK_DOMAIN = None

# Local Flask port (any free port is fine).
PORT = 5000

# Title shown on the phone page.
APP_TITLE = "Remote Runner"

# --------------------------------------------------------------------------
# Recent-files browser (the /files page).
# Shows the most recently modified files (matching SCAN_FILE_EXTS) and the
# most recently modified subfolders, at the top level of SCAN_ROOT.
# Set SCAN_ROOT to None to disable the page.
# --------------------------------------------------------------------------

SCAN_ROOT = None  # e.g. r"G:\\" or r"C:\Users\me\Downloads"
SCAN_FILE_EXTS = (".pdf",)  # extensions to list (lowercase, with dot)
SCAN_FILE_LIMIT = 2         # how many recent files to show
SCAN_FOLDER_LIMIT = 2       # how many recent folders to show
