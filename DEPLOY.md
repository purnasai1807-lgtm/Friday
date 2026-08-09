# 🌐 Deploy FRIDAY AI Live (Cloud)

This guide shows how to publish the FRIDAY AI **web app** to a cloud host so it
is live on the internet and accessible from any phone/laptop/browser.

---

## 🚀 Quick start: put FRIDAY live on the internet (no app store, no same Wi-Fi)

This is the **recommended** way to make FRIDAY public. It runs on a free cloud
server, so it is online **24/7** — even when your PC and VS Code are **closed**,
and anyone anywhere can open it in their browser (any Wi-Fi / mobile data).

> **What works online:** the AI brain, voice (via the browser's microphone),
> web search, weather, memory, notes, multi-agent features, and the LLM.
> **What stays local/desktop-only:** opening apps _on your PC_, controlling your
> screen, typing/clicking on your PC. These gracefully stay unavailable online.

### Step 1 — Put the code on GitHub (one-time)

1. Create a free account at https://github.com if you don't have one.
2. Click **New repository** → name it `friday-ai` → make it **Public** (or Private, either works) → **Create**.
3. Upload these files to it (drag & drop the whole project folder, or use Git):
   ```bash
   cd c:/Users/HP/Desktop/FRIDAY_AN_AI
   git init
   git add .
   git commit -m "FRIDAY AI public deploy"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/friday-ai.git
   git push -u origin main
   ```

### Step 2 — Create a free Render.com service (one-time)

1. Go to https://render.com → **Sign up** for free (GitHub sign-in is easiest).
2. Click **New** → **Blueprint** → connect your GitHub account → choose the `friday-ai` repo.
3. Render reads `render.yaml` automatically and creates the web service.
4. Click **Apply**. Render builds and deploys (~2–4 minutes).
5. When done, you get a public URL like `https://friday-ai.onrender.com`.

### Step 3 — Add your Gemini API key (recommended, free)

1. Get a free key at https://aistudio.google.com/app/apikey
2. In Render → your service → **Environment** → **Add Environment Variable**:
   - Key: `GEMINI_API_KEY`
   - Value: your key
3. Save — Render redeploys automatically.

### Step 4 — Share it!

Open `https://friday-ai.onrender.com` on any phone/laptop and talk to FRIDAY.
Share that link with anyone — they don't need your Wi-Fi, and your PC can stay off.

---

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
