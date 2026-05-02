"""Remote .bat runner + recent-files browser, exposed via ngrok."""
import os
import secrets
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request
from pyngrok import conf, ngrok

import config

BASE_DIR = Path(__file__).resolve().parent
BAT_PATH = Path(config.BAT_PATH)
SCAN_ROOT = Path(config.SCAN_ROOT) if getattr(config, "SCAN_ROOT", None) else None
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


# -- Routes ----------------------------------------------------------------

@app.route("/")
def index():
    if request.args.get("k") != SECRET:
        abort(404)
    return render_template(
        "index.html",
        secret=SECRET,
        title=config.APP_TITLE,
        files_enabled=SCAN_ROOT is not None,
    )


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


@app.route("/files")
def files_page():
    if request.args.get("k") != SECRET:
        abort(404)
    if SCAN_ROOT is None:
        return "SCAN_ROOT is not configured in config.py", 500
    return render_template(
        "files.html",
        secret=SECRET,
        root=str(SCAN_ROOT),
        pdfs=_latest_pdfs(SCAN_ROOT, config.SCAN_FILE_LIMIT, config.SCAN_FILE_EXTS),
        folders=_latest_folders(SCAN_ROOT, config.SCAN_FOLDER_LIMIT),
        scanned_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        exts=", ".join(config.SCAN_FILE_EXTS),
    )


@app.route("/manifest.webmanifest")
def manifest():
    return app.send_static_file("manifest.webmanifest")


# -- Helpers ---------------------------------------------------------------

def _human_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{int(n)} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _fmt_date(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def _latest_pdfs(root: Path, limit: int, exts):
    """Top-level files in root with one of the given extensions, newest first."""
    exts_lower = tuple(e.lower() for e in exts)
    items = []
    try:
        with os.scandir(root) as it:
            for entry in it:
                if not entry.is_file(follow_symlinks=False):
                    continue
                if not entry.name.lower().endswith(exts_lower):
                    continue
                try:
                    st = entry.stat()
                except OSError:
                    continue
                items.append((st.st_mtime, st.st_size, Path(entry.path)))
    except OSError:
        pass
    items.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "name": p.name,
            "path": str(p),
            "size": _human_size(int(size)),
            "date": _fmt_date(mtime),
        }
        for mtime, size, p in items[:limit]
    ]


def _latest_folders(root: Path, limit: int):
    """Top-level folders in root, newest first."""
    items = []
    try:
        with os.scandir(root) as it:
            for entry in it:
                if not entry.is_dir(follow_symlinks=False):
                    continue
                if entry.name.startswith("$") or entry.name.lower() == "system volume information":
                    continue
                try:
                    st = entry.stat()
                except OSError:
                    continue
                items.append((st.st_mtime, Path(entry.path)))
    except OSError:
        pass
    items.sort(key=lambda x: x[0], reverse=True)
    return [
        {"name": p.name, "path": str(p), "date": _fmt_date(mtime)}
        for mtime, p in items[:limit]
    ]


# -- Tunnel ----------------------------------------------------------------

def start_tunnel() -> str:
    conf.get_default().auth_token = load_ngrok_token()
    kwargs = {"proto": "http"}
    if config.NGROK_DOMAIN:
        kwargs["domain"] = config.NGROK_DOMAIN
    tunnel = ngrok.connect(config.PORT, **kwargs)
    url = tunnel.public_url.replace("http://", "https://")
    home = f"{url}/?k={SECRET}"
    files = f"{url}/files?k={SECRET}"
    URL_FILE.write_text(home + "\n" + files + "\n", encoding="utf-8")
    print("=" * 60)
    print("PUBLIC URLs (open on phone, then Add to Home Screen):")
    print("  RUN button page :", home)
    if SCAN_ROOT is not None:
        print("  Recent files    :", files)
    print("=" * 60, flush=True)
    return home


if __name__ == "__main__":
    start_tunnel()
    app.run(host="127.0.0.1", port=config.PORT, debug=False, use_reloader=False)
