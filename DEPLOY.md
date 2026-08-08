# 🌐 Deploy FRIDAY AI Live (Cloud)

This guide shows how to publish the FRIDAY AI **web app** to a cloud host so it
is live on the internet and accessible from any phone/laptop/browser.

> **🚀 Auto-deploy is wired up.** This repo includes `.github/workflows/deploy.yml`
> which triggers a Render deployment automatically on every push to `main`.
> You only need to (1) create the Render service and (2) add its Deploy Hook URL
> as a GitHub secret — then every future push deploys itself.

> **Important:** FRIDAY's _desktop-only_ features (opening apps, controlling the
> screen, dragging files, installing software) only work on your local PC.
> On a cloud server, the **voice + AI + LLM + research + memory** features work
> because the web UI uses the **browser's microphone** (client-side). Everything
> that needs your PC degrades gracefully and is simply not available remotely.

---

## Deployment files included

| File               | Purpose                                                |
| ------------------ | ------------------------------------------------------ |
| `Procfile`         | Gunicorn start command (used by Render/Railway/Heroku) |
| `render.yaml`      | Render.com blueprint (free plan, auto-config)          |
| `runtime.txt`      | Pins Python version to 3.11.9                          |
| `requirements.txt` | All Python dependencies (gunicorn added)               |
| `.gitignore`       | Excludes secrets/user data from being committed to git |

---

## ✅ Enable auto-deploy (2 quick steps)

1. **Create the Render service** (one-time):
   - Go to https://render.com → **New** → **Blueprint** → connect your GitHub **`Friday`** repo.
   - Render reads `render.yaml` and creates the service. Note the public URL it gives you.
   - In Render → your new **Web Service** → **Settings** → **Deploy Hook**, copy the **Deploy Hook URL**.
2. **Add the hook as a GitHub secret** (one-time):
   - On GitHub → your **Friday** repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
   - Name: `RENDER_DEPLOY_HOOK`, Value: paste the Deploy Hook URL.
   - Also add `GEMINI_API_KEY` as a secret (your Gemini key) if you want the AI brain live.

After that, **every push to `main` triggers an automatic deployment** via
`.github/workflows/deploy.yml`. You can also click **Actions → Deploy FRIDAY AI to Render → Run workflow**
to deploy manually anytime.

---

## Option 1 — Deploy on Render.com (recommended, free)

1. Push this project to a **GitHub** repository.
2. Go to https://render.com → **New** → **Blueprint**.
3. Connect your GitHub repo. Render reads `render.yaml` automatically.
4. Click **Apply**. Render builds and deploys for free.
5. When done you get a public URL like `https://friday-ai.onrender.com`.

> Alternatively, use the **Web Service** flow:
>
> - Build Command: `pip install -r requirements.txt`
> - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
> - Instance Type: Free

---

## Option 2 — Deploy on Railway.app

1. Push to GitHub.
2. Go to https://railway.app → **New Project** → **Deploy from GitHub repo**.
3. Railway auto-detects the Python app. Set start command:
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
4. Railway generates a live URL automatically.

---

## Option 3 — Deploy on PythonAnywhere (simple)

1. Upload the project (web tab → "Add a new web app").
2. Choose **Flask** and set the WSGI file to import `app`.
3. In `app.py`, the `if __name__ == "__main__":` block is skipped by the WSGI
   server, so it uses the `app` object directly — no port conflicts.

---

## Using your Gemini API key on the server

The free Render/Railway plan that serves the web UI needs your Gemini key to
power the AI brain. **Do not** commit `config.json` with a real key (it's in
`.gitignore`). Instead, set it as an **environment variable** on the host:

1. In Render/Railway, add an env var `GEMINI_API_KEY` = your key.
2. The app reads `config.json` by default. To read from env, the app needs a
   small change. Run this helper to inject the env var into config at startup:

```python
# at the top of app.py, before creating FridayCortex():
import os
config = "config.json"
if os.environ.get("GEMINI_API_KEY"):
    import json
    try:
        with open(config) as f:
            c = json.load(f)
        c["gemini_api_key"] = os.environ["GEMINI_API_KEY"]
        with open(config, "w") as f:
            json.dump(c, f)
    except Exception:
        pass
```

---

## Verify it's live

Once deployed, open:

- `https://YOUR_APP_URL/` → the FRIDAY voice UI
- `https://YOUR_APP_URL/api/status` → health check returning JSON

> The health check path is already set to `/api/status` in `render.yaml`.

---

## Security note (important)

If you expose FRIDAY publicly:

- Keep `"sensitive_action_permission": true` (it's on by default).
- Prefer PIN/password protection on the host. Desktop-only actions are not
  possible remotely, so the main exposure is the AI conversation + web search,
  which is low-risk but still public.
- Do not commit `config.json`, `.vault_key`, or any `*.json` data files —
  `.gitignore` already excludes them.
