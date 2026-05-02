# Remote .bat Runner

Trigger a Windows `.bat` file on your laptop from your phone with a single tap,
and peek at the most recently downloaded files — even when you're away from
home. No port forwarding, no VPN.

A tiny Flask web app on the laptop exposes:

- **`/`** — a big green **RUN** button that starts your `.bat`.
- **`/files`** — a list of the most recently modified files (e.g. PDFs) and
  folders at the top level of a chosen directory (e.g. `G:\` or your Downloads
  folder). Optional — disabled by default.

Both routes run in the same Python process and share the same
[ngrok](https://ngrok.com) tunnel. Add each URL to your phone's home screen
as a PWA and you'll have two 1-tap icons.

## How it works

```
 Phone (browser/PWA)  ──HTTPS──▶  ngrok  ──▶  Flask (localhost:5000)  ──▶  your .bat
```

- The URL contains a secret token; without it the page returns 404.
- All traffic is end-to-end over ngrok's HTTPS tunnel.
- The laptop only exposes the port to ngrok, not to the open internet.

## Requirements

- Windows 10/11 laptop that stays powered on (screen can be locked — sleep must be disabled).
- [Python 3.10+](https://www.python.org/downloads/)
- Free [ngrok account](https://dashboard.ngrok.com/signup) (for the authtoken and
  one free static "dev domain").

## Setup

```cmd
git clone https://github.com/YOUR_USERNAME/remote-bat-runner.git
cd remote-bat-runner
pip install -r requirements.txt
```

1. **Copy the config template and edit it:**

   ```cmd
   copy config.example.py config.py
   ```

   Edit `config.py`:
   - `BAT_PATH` — absolute path to the `.bat` file you want to run.
   - `NGROK_DOMAIN` — optional. Paste your free static domain from
     [dashboard.ngrok.com/domains](https://dashboard.ngrok.com/domains)
     (e.g. `"your-name.ngrok-free.dev"`) so the URL stays the same across restarts.
     Leave as `None` to get a random URL each launch.
   - `SCAN_ROOT` — optional. Set to a folder path (e.g. `r"G:\\"` or your
     Downloads folder) to enable the `/files` page. Leave as `None` to disable.
     Tweak `SCAN_FILE_EXTS`, `SCAN_FILE_LIMIT`, `SCAN_FOLDER_LIMIT` to taste.

2. **Add your ngrok authtoken.** Grab it from
   [dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)
   and save it to `ngrok_token.txt` (one line, no quotes). Alternatively set
   the `NGROK_AUTHTOKEN` environment variable.

3. **Generate the PWA icons** (one-time):

   ```cmd
   python make_icons.py
   ```

4. **Run it:**

   ```cmd
   start.bat
   ```

   The console prints both URLs:

   ```
   PUBLIC URLs (open on phone, then Add to Home Screen):
     RUN button page : https://your-name.ngrok-free.dev/?k=<secret>
     Recent files    : https://your-name.ngrok-free.dev/files?k=<secret>
   ```

5. **On your phone:** open each URL in Chrome/Safari → accept the ngrok warning
   on first visit → browser menu → **Add to Home Screen**. You now have one
   icon for the RUN button and (optionally) a second icon for the recent-files
   list.

## Keeping the laptop awake

Screen locked is fine — the server keeps running. Sleep/hibernate is not. Run
once, as admin if needed:

```cmd
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0
```

To also ignore the lid-close action on a laptop:

```cmd
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setactive SCHEME_CURRENT
```

## Security notes

- The URL-embedded `?k=<secret>` is the only thing protecting your endpoint.
  Don't share the full URL publicly — treat it like a password.
- `secret.txt` is auto-generated on first run. Delete it to rotate the secret.
- `config.py`, `ngrok_token.txt`, `secret.txt`, and `current_url.txt` are in
  `.gitignore` — never commit them.
- The `/run` endpoint only starts the `.bat` configured in `config.py`. It does
  not accept arbitrary commands from the client.

## Extending

- **Multiple scripts.** Turn `BAT_PATH` into a dict like
  `{"pdf": r"D:\...\a.bat", "backup": r"D:\...\b.bat"}`, map routes
  `/run/<name>`, and add more buttons to `templates/index.html`.
- **Recursive scan.** `_latest_pdfs` / `_latest_folders` in `app.py` use
  `os.scandir` (top-level only) for speed. Swap to `os.walk` if you want to
  recurse — but cap the depth and add a time budget; scanning a full drive
  can be very slow.

## License

MIT
