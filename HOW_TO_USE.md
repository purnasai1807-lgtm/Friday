# 🗣️ How to Use FRIDAY

FRIDAY is **always-on, 100% VOICE-ONLY, and has NO CHAT BOT** — no text input,
no buttons, no chat log. It wakes up when you **say "friday"**, and it works on
your **desktop, laptop, and phone**. Every command is spoken, and every response
is spoken back to you.

---

## 1️⃣ First-Time Setup (only once)

### Step A — Install FRIDAY (pick ONE of these)

| What you want | What to do
| **FRIDAY runs in background always** (recommended) | Double-click **`install_autostart.bat`** — this makes FRIDAY start automatically with Windows and always listen, even with VS Code / app closed |
| FRIDAY runs in background just for now | Double-click **`start_friday_listener.bat`** |
| FRIDAY as a desktop window | Double-click **`start_friday_desktop.bat`** |
| FRIDAY in your browser (phone + laptop) | Double-click **`start_friday.bat`**, then open `http://127.0.0.1:5000` |

> The first time, these scripts automatically install everything FRIDAY needs.
> Make sure your **microphone is connected and working**.

### Step B — (Optional but recommended) Enable the AI brain

1. Get a **free** Gemini API key: https://aistudio.google.com/app/apikey
2. Open **`config.json`** (in the FRIDAY folder)
3. Replace `YOUR_GEMINI_API_KEY_HERE` with your real key
4. Restart FRIDAY

Now FRIDAY understands natural language and can talk about anything, all by voice.

---

## 2️⃣ Talking to FRIDAY (voice)

1. **Wait** until FRIDAY says it's online / the mic indicator shows it's listening.
2. **Wake it up** — say:

   > **"FRIDAY"** or **"wake up friday"**

   It answers: _"Yes sir, FRIDAY at your service. How can I help?"_

3. **Give a command** — say something like:

| Say                                      | FRIDAY does          |
| ---------------------------------------- | -------------------- |
| "What time is it?"                       | Tells the time       |
| "What's the weather in London?"          | Fetches live weather |
| "What is 15 times 4?"                    | Calculates           |
| "Open YouTube"                           | Opens YouTube        |
| "Open notepad"                           | Opens Notepad        |
| "Remember to buy milk"                   | Saves a note         |
| "Show my notes"                          | Reads your notes     |
| "Remind me to drink water in 30 seconds" | Sets a timer         |
| "Tell me a joke"                         | Tells a joke         |
| "Search for AI news"                     | Opens a web search   |
| "What is AI?"                            | Explains a topic     |

**🖥️ Computer Control Agent (use any software like a person):**

| Say                                | FRIDAY does                          |
| ---------------------------------- | ------------------------------------ |
| "Take a screenshot"                | Captures the screen                  |
| "Read the screen"                  | Reads text visible on screen (OCR)   |
| "Click at 100, 200"                | Clicks at those pixel coordinates    |
| "Click on <button/text>"           | Finds & clicks a button by text      |
| "Type hello world"                 | Types text into the focused field    |
| "Press enter" / "Press tab"        | Presses a key                        |
| "Scroll down"                      | Scrolls the page/window              |
| "Drag from 300,200 to 500,400"     | Drags the mouse (e.g. drag files)    |
| "Fill form name=John, email=x@y.z" | Auto-fills a form                    |
| "Install firefox"                  | Installs software (winget/choco/pip) |
| "Switch to chrome"                 | Switches to another app              |

**👁️ Vision-Based Desktop AI (see the screen like a human):**

| Say                           | FRIDAY does                            |
| ----------------------------- | -------------------------------------- |
| "Analyze the screen"          | Describes the whole screen in detail   |
| "Explain this error"          | Detects & explains errors on screen    |
| "Explain this chart"          | Analyzes a chart/graph on screen       |
| "Read document C:\report.pdf" | Reads & summarizes a file (no opening) |
| "Review the code on screen"   | Reviews visible code for bugs          |

**🧠 Self-Learning Memory (learns your habits & predicts needs):**

| Say                                     | FRIDAY does                             |
| --------------------------------------- | --------------------------------------- |
| "Learning report"                       | Shows what FRIDAY has learned about you |
| "Show my learned routines"              | Lists routines learned from your usage  |
| "What do I need right now"              | Predicts what you likely need now       |
| "Favorite apps"                         | Lists your most-used apps               |
| "Remember that John works at Microsoft" | Adds a fact to your knowledge graph     |
| "What do you know about John"           | Recalls everything connected to John    |

4. **Put it to sleep** when done — say:

   > **"go to sleep friday"**

---

## 3️⃣ Permission (safety) control

For **sensitive actions** (shutdown, restart, opening programs/websites, web
search), FRIDAY will ask for your permission first:

> _"To do that, I need your permission. Please confirm by saying 'yes friday' or
> 'no friday'."_

- Say **"yes friday"** / **"go ahead"** → it does it
- Say **"no friday"** / **"cancel"** → it cancels

On the web app you can also click **Allow / Deny**.

---

## 4️⃣ Using it on your PHONE

1. Run the web server: double-click **`start_friday.bat`** on your computer.
2. Find your computer's IP: open Command Prompt and run `ipconfig`, note the
   IPv4 address (e.g. `192.168.1.5`).
3. On your phone (same Wi-Fi), open a browser and go to:

   ```
   http://YOUR_COMPUTER_IP:5000
   ```

4. Tap the page so the browser asks for microphone permission → **Allow**.
5. Now say **"FRIDAY"** and talk to it from your phone.

---

## 5️⃣ Stopping FRIDAY

- **Background listener**: the console window shows it — close it (or press `Ctrl+C`).
- **If you used install_autostart.bat**: delete
  `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\FRIDAY_Listener.vbs`
  to stop it from starting with Windows.

---

## 💡 Good to know

- Wake word: **"friday"**, "wake up friday", "hey friday"
- Sleep word: **"go to sleep friday"**, "sleep friday"
- Voice responses come from your computer/phone speakers.
- For the background listener, the wake word is recognized **locally** (no
  internet needed for wake-up).
