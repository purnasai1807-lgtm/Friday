# FRIDAY AI - Always-On Personal JARVIS

FRIDAY is a JARVIS-like personal AI assistant that **automatically wakes up when you say "friday"** — on your **phone, laptop, or desktop**. It is **100% VOICE-ONLY: there is NO chat bot, NO text input, and NO buttons**. Every interaction happens by speaking to FRIDAY, and every response is spoken back to you. It runs continuously, even when the app or VS Code is closed.

> 🧠 **AI AGENT MODE**: FRIDAY is built as a real AI agent. With a free Gemini API key it uses an LLM brain to understand natural language and automatically calls tools (like ChatGPT + function calling). Without a key it runs in rule-based mode (still fully functional).

## 🎯 Key Features

- 🗣️ **Always-On Wake Word** - Say **"FRIDAY"** to wake it up, any time, anywhere (phone, laptop, desktop)
- 🔘 **NO BUTTONS** - Pure voice control. FRIDAY listens continuously and wakes automatically
- 🖥️ **Runs Without VS Code / App** - Background listener auto-starts with Windows
- 📱 **Phone + Laptop + Desktop** - Web app works on your phone (same Wi-Fi), desktop app is native
- 🔐 **User Permission Control** - Sensitive actions (shutdown, restart, open programs, web search) require your verbal or on-screen confirmation before executing
- 🤖 **AI Agent** - Natural language understanding + automatic tool calling (with Gemini key)
- 🎨 **GIF Themes** - Iron Man, Matrix, DNA, Brain, NFT and more animated backgrounds

## 🧠 Capabilities

| Category                  | What FRIDAY Can Do                                                                                                                       |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 🗣️ Voice                  | Wake word "friday", speech recognition, text-to-speech                                                                                   |
| 🌤️ Weather                | Live weather via wttr.in                                                                                                                 |
| 🧮 Calculator             | "What is 15 times 4?"                                                                                                                    |
| 🔍 Web Search             | "Search for AI news"                                                                                                                     |
| 🌐 Open Anything          | Programs, websites, apps                                                                                                                 |
| 📝 Notes & Memory         | "Remember to buy milk", remembers you                                                                                                    |
| ⏰ Timers                 | "Remind me to drink water in 30 seconds"                                                                                                 |
| 💻 Computer Control       | "Open notepad", "Shutdown", "Restart" (with permission)                                                                                  |
| 🖥️ Computer Control Agent | "Click at 100, 200", "Type hello", "Scroll down", "Install firefox", "Drag file ... to ...", "Fill form name=John"                       |
| 👁️ Vision-Based AI        | "Read the screen", "Analyze the screen", "Explain this error", "Explain this chart", "Read document <path>", "Review the code on screen" |
| 🧠 Self-Learning Memory   | "Learning report", "Show my learned routines", "What do I need right now", "Favorite apps", "What do you know about <X>"                 |
| 🧬 Knowledge Graph        | "Remember that John works at Microsoft", "What do you know about John"                                                                   |
| 👨‍💻 Coding                 | "Write a python function to sort a list"                                                                                                 |
| 📖 Explain                | "What is AI?", "Define gravity"                                                                                                          |
| ✍️ Translation            | "Translate hello to French"                                                                                                              |
| 📰 News & Wikipedia       | Latest headlines, topic summaries                                                                                                        |
| 📋 Planner Agent          | Break big tasks into steps                                                                                                               |
| 🔍 Research Agent         | Gather & summarize info                                                                                                                  |
| 💻 Coding Agent           | Generate code                                                                                                                            |
| 🌐 Browser Agent          | Open & browse sites                                                                                                                      |
| 👁️ Vision Agent           | Screenshots & OCR                                                                                                                        |
| 🧠 Memory Agent           | Long-term memory                                                                                                                         |
| 💰 Finance Agent          | Expenses & budgets                                                                                                                       |
| 🎯 Goal Tracking          | Set & track goals                                                                                                                        |
| 🧬 Digital Twin           | Learns your preferences                                                                                                                  |
| 🔐 Permission Control     | Approve sensitive actions                                                                                                                |

## ⚙️ Quick Start

### One-time setup (recommended)

Double-click **`install_autostart.bat`** — this adds FRIDAY to Windows startup so it runs silently in the background and **always listens for "friday"**, even when the app or VS Code is closed.

### Option A: Always-On Background (no window)

Double-click **`start_friday_listener.bat`** — FRIDAY runs in the background, auto-waking on "friday". No window needed.

### Option B: Desktop App (native window)

Double-click **`start_friday_desktop.bat`** — opens a FRIDAY window that's always listening.

### Option C: Web App (phone + laptop + desktop)

Double-click **`start_friday.bat`** to start the web server. Then open:

- This computer: `http://127.0.0.1:5000`
- Your phone (same Wi-Fi): `http://YOUR_COMPUTER_IP:5000`

The web app uses the browser's microphone to listen continuously for **"FRIDAY"**.

### Manual

```bash
cd C:\Users\HP\Desktop\FRIDAY_AN_AI
pip install -r requirements.txt
python friday_listener.py   # Always-on background listener
python friday_app.py        # Desktop app
python app.py               # Web server
```

## 🔑 Enable Full AI Agent Mode (Recommended)

1. Get a **free** Gemini API key from https://aistudio.google.com/app/apikey
2. Open **`config.json`** and replace `YOUR_GEMINI_API_KEY_HERE`
3. Restart FRIDAY

Now FRIDAY uses a real AI brain to understand anything you say and automatically choose the right tool.

## 🔐 Permission Control

By default, FRIDAY asks for permission before sensitive actions:

- **Shutdown / Restart**
- **Opening programs**
- **Opening websites**
- **Web searches**

When a sensitive action is requested, FRIDAY will ask for confirmation. You can:

- Say **"yes friday"** or **"go ahead"** to allow
- Say **"no friday"** or **"cancel"** to deny

To disable permission prompts, set `"sensitive_action_permission": false` in `config.json`.

## 🎨 Themes

The desktop app uses an animated GIF background (Iron Man, Matrix, DNA, Brain, NFT, Earth, etc.) automatically. The pure-voice interface is voice-controlled only — no menus or buttons.

## 📁 Project Structure

- `friday_agent.py` — Main AI agent engine (tools, memory, permission system)
- `friday_control.py` — Computer Control Agent (screen OCR, click, type, drag, fill forms, install)
- `friday_vision.py` — Vision-Based Desktop AI (screen reading, errors, charts, PDFs)
- `friday_learning.py` — Self-Learning Memory (routines, preferences, knowledge graph, predictions)
- `friday_advanced.py` — Advanced capabilities (vault, finance, smart home, routines)
- `friday_ecosystem.py` — Ecosystem (email, calendar, workflows, goals, security)
- `friday_smart.py` — Smart capabilities (browser automation, RAG, briefing)
- `friday_agents.py` — Multi-agent system
- `friday_listener.py` / `.pyw` — Always-on background wake-word listener
- `friday_app.py` — Native desktop app (pure voice, no chat/buttons)
- `app.py` — Flask web server (voice-only, phone/laptop/desktop)
- `templates/index.html` + `static/` — Futuristic web UI
- `static/gifs/` — Animated GIF themes
- `config.json` — Configuration (API key, permission, always-on)
- `install_autostart.bat` — Adds FRIDAY to Windows startup
- `start_friday_listener.bat` — Runs background listener
- `start_friday.bat` — Web server
- `start_friday_desktop.bat` — Desktop app

## 📝 Note

- Voice recognition requires a working microphone
- For best accuracy, install `pyaudio` (included in batch files)
- The background listener uses local speech recognition (no internet needed for wake word)
- The web app uses browser speech recognition + speech synthesis
