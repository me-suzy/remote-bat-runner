"""Remote .bat runner — trigger a Windows batch file from your phone via ngrok."""
import os
import secrets
import subprocess
import sys
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request
from pyngrok import conf, ngrok

import config

BASE_DIR = Path(__file__).resolve().parent
BAT_PATH = Path(config.BAT_PATH)
SECRET_FILE = BASE_DIR / "secret.txt"
TOKEN_FILE = BASE_DIR / "ngrok_token.txt"
URL_FILE = BASE_DIR / "current_url.txt"


def load_or_create_secret() -> str:
    if SECRET_FILE.exists():
        return SECRET_FILE.read_text(encoding="utf-8").strip()
    value = secrets.token_urlsafe(24)
    SECRET_FILE.write_text(value, encoding="utf-8")
    return value


def load_ngrok_token() -> str:
    token = os.environ.get("NGROK_AUTHTOKEN")
    if token:
        return token.strip()
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    sys.exit(
        "Missing ngrok authtoken. Create ngrok_token.txt in this folder "
        "or set the NGROK_AUTHTOKEN environment variable. "
        "Get a free token at https://dashboard.ngrok.com/get-started/your-authtoken"
    )


SECRET = load_or_create_secret()
app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    if request.args.get("k") != SECRET:
        abort(404)
    return render_template("index.html", secret=SECRET, title=config.APP_TITLE)


@app.route("/run", methods=["POST"])
def run_bat():
    if request.args.get("k") != SECRET and request.headers.get("X-Key") != SECRET:
        abort(403)
    if not BAT_PATH.exists():
        return jsonify(ok=False, error=f"Missing file: {BAT_PATH}"), 500
    try:
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "", str(BAT_PATH)],
            cwd=str(BAT_PATH.parent),
            shell=False,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return jsonify(ok=True, message="Started")
    except Exception as e:  # noqa: BLE001
        return jsonify(ok=False, error=str(e)), 500


@app.route("/manifest.webmanifest")
def manifest():
    return app.send_static_file("manifest.webmanifest")


def start_tunnel() -> str:
    conf.get_default().auth_token = load_ngrok_token()
    kwargs = {"proto": "http"}
    if config.NGROK_DOMAIN:
        kwargs["domain"] = config.NGROK_DOMAIN
    tunnel = ngrok.connect(config.PORT, **kwargs)
    url = tunnel.public_url.replace("http://", "https://")
    full = f"{url}/?k={SECRET}"
    URL_FILE.write_text(full, encoding="utf-8")
    print("=" * 60)
    print("PUBLIC URL (open on phone, then Add to Home Screen):")
    print(full)
    print("=" * 60, flush=True)
    return full


if __name__ == "__main__":
    start_tunnel()
    app.run(host="127.0.0.1", port=config.PORT, debug=False, use_reloader=False)
