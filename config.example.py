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
