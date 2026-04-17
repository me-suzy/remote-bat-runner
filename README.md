# Remote .bat Runner

Trigger a Windows `.bat` file on your laptop from your phone with a single tap,
even when you're away from home. No port forwarding, no VPN.

A tiny Flask web app on the laptop exposes a green **RUN** button via an
[ngrok](https://ngrok.com) tunnel. Open the URL on your phone, add it to the
home screen as a PWA, and you have a 1-tap "start this program on my laptop"
icon.

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

   The console prints a line like:

   ```
   PUBLIC URL (open on phone, then Add to Home Screen):
   https://your-name.ngrok-free.dev/?k=<random-secret>
   ```

5. **On your phone:** open the URL in Chrome/Safari → accept the ngrok warning
   on first visit → browser menu → **Add to Home Screen**. You now have an app
   icon. One tap opens the page, one tap on **RUN** launches the `.bat`.

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

Want to run multiple scripts? Turn `BAT_PATH` into a dict like
`{"pdf": r"D:\...\a.bat", "backup": r"D:\...\b.bat"}`, map routes
`/run/<name>`, and add more buttons to `templates/index.html`.

## License

MIT
