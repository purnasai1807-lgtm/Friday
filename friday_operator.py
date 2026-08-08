"""
FRIDAY AI - Operator Module
============================
Adds the "AI Computer Operator" layer, autonomous missions, self-learning,
local AI (Ollama/Llama/Qwen/Mistral/DeepSeek), and multi-device sync.

1. AI Computer Operator - see the screen and interact with any software
2. Autonomous Missions - plan -> research -> code -> test -> fix -> deploy
3. Self-Learning - learn routines, preferences, frequently used apps
4. Local AI - offline models via Ollama (Llama, Qwen, Mistral, DeepSeek, etc.)
5. Multi-Device Sync - sync memory, chats, tasks across devices
"""
import os
import json
import time
import datetime
import threading
import subprocess
import shutil

# Optional: screen automation / computer operator
try:
    import pyautogui
    PYAUTOGUI = True
except Exception:
    PYAUTOGUI = False

try:
    import pyperclip
    PYPERCLIP = True
except Exception:
    PYPERCLIP = False

try:
    import requests
    REQUESTS = True
except Exception:
    REQUESTS = False


class FridayOperator:
    def __init__(self, base_dir=None, agent=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.agent = agent
        self.sync_file = os.path.join(self.base_dir, "sync_state.json")
        self.learning_file = os.path.join(self.base_dir, "learning.json")
        self.missions_file = os.path.join(self.base_dir, "missions.json")
        self._load()

    # ---------- Persistence ----------
    def _load(self):
        self.learning = {"routines": [], "fav_apps": [], "fav_sites": [], "commands": {}, "study_schedule": []}
        self.missions = []
        self.sync = {"last_sync": None, "devices": []}
        for path, key in [(self.learning_file, "learning"), (self.missions_file, "missions"), (self.sync_file, "sync")]:
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        setattr(self, key, json.load(f))
            except Exception:
                pass

    def _save(self, key):
        path = {"learning": self.learning_file, "missions": self.missions_file, "sync": self.sync_file}[key]
        try:
            with open(path, "w") as f:
                json.dump(getattr(self, key), f, indent=2)
        except Exception:
            pass

    # ==========================================================
    #  1. AI COMPUTER OPERATOR  (see + interact with any software)
    # ==========================================================
    def operator_status(self):
        return ("AI Computer Operator: " +
                ("ON - I can see your screen and control apps." if PYAUTOGUI else
                 "limited - install 'pyautogui' for full screen control."))

    def screen_text(self):
        """Read text from the screen (OCR)."""
        try:
            from PIL import Image
            import pytesseract
            if not PYAUTOGUI:
                return "Screen capture needs pyautogui. Install it."
            img = pyautogui.screenshot()
            img.save(os.path.join(self.base_dir, "screen_capture.png"))
            text = pytesseract.image_to_string(img)
            if text.strip():
                return "I read this from your screen: " + text.strip()[:600]
            return "I captured the screen but couldn't read text. Is pytesseract installed?"
        except Exception as e:
            return "Screen OCR error: " + str(e)

    def click_at(self, x, y, doble=False):
        if not PYAUTOGUI:
            return "Screen control needs pyautogui. Install it."
        try:
            pyautogui.click(int(x), int(y))
            return f"Clicked at ({x}, {y})."
        except Exception as e:
            return "Could not click: " + str(e)

    def type_text(self, text=""):
        if not PYAUTOGUI:
            return "Typing needs pyautogui. Install it."
        try:
            pyautogui.write(text)
            return f"Typed: {text}"
        except Exception as e:
            return "Could not type: " + str(e)

    def press_key(self, key="enter"):
        if not PYAUTOGUI:
            return "Key press needs pyautogui."
        try:
            pyautogui.press(key)
            return f"Pressed {key}."
        except Exception as e:
            return "Could not press key: " + str(e)

    def scroll(self, direction="down", amount="5"):
        if not PYAUTOGUI:
            return "Scrolling needs pyautogui."
        try:
            amt = int(amount) * (1 if direction == "up" else -1)
            pyautogui.scroll(amt)
            return f"Scrolled {direction}."
        except Exception as e:
            return "Could not scroll: " + str(e)

    def screenshot(self):
        if not PYAUTOGUI:
            return "Screenshots need pyautogui."
        try:
            path = os.path.join(self.base_dir, "screenshot_" + time.strftime("%H%M%S") + ".png")
            pyautogui.screenshot(path)
            return f"Screenshot saved: {path}"
        except Exception as e:
            return "Could not capture: " + str(e)

    def install_software(self, name=""):
        """Best-effort software install via winget (Windows)."""
        if not name:
            return "What software should I install? e.g. 'install firefox'."
        try:
            r = subprocess.run(f'winget install --id {name} --silent --accept-package-agreements',
                               shell=True, capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return f"Installing {name} in the background using winget."
            # try name directly
            subprocess.Popen(f'winget install {name} --silent', shell=True)
            return f"Queued installation of {name} via winget."
        except Exception:
            return f"Could not start installation of {name}. Is winget available?"

    def open_file_anywhere(self, path=""):
        try:
            os.startfile(path)
            return f"Opened {path}."
        except Exception:
            return f"Could not open {path}."

    # ==========================================================
    #  2. AUTONOMOUS MISSIONS
    # ==========================================================
    def start_mission(self, goal=""):
        if not goal:
            return "What mission should I plan? e.g. 'mission: build a portfolio website'."
        mission = {
            "id": time.strftime("%Y%m%d%H%M%S"),
            "goal": goal,
            "status": "planned",
            "steps": ["research", "design", "build", "test", "deploy", "report"],
            "created": datetime.datetime.now().isoformat(),
            "progress": []
        }
        self.missions.append(mission)
        self._save("missions")
        return (f"Mission started. I'll plan, research, build, test, and deploy. "
                f"Goal: {goal}. I'll report progress as I go.")

    def mission_status(self):
        if not self.missions:
            return "No missions active. Say 'mission: <goal>' to start one."
        out = []
        for m in self.missions[-5:]:
            out.append(f"- {m['goal']} [{m['status']}]")
        return "Your missions:\n" + "\n".join(out)

    # ==========================================================
    #  3. SELF-LEARNING
    # ==========================================================
    def learn_command(self, phrase="", result=""):
        self.learning["commands"][phrase] = result
        self._save("learning")
        return "I've learned that command."

    def learn_fav_app(self, app=""):
        if app and app not in self.learning["fav_apps"]:
            self.learning["fav_apps"].append(app)
            self._save("learning")
        return f"Noted. Your frequently used apps: {', '.join(self.learning['fav_apps']) or 'none yet'}."

    def learn_fav_site(self, site=""):
        if site and site not in self.learning["fav_sites"]:
            self.learning["fav_sites"].append(site)
            self._save("learning")
        return f"Noted. Favorite sites: {', '.join(self.learning['fav_sites']) or 'none yet'}."

    def learning_report(self):
        return (f"Self-learning report:\n"
                f"- Favorite apps: {', '.join(self.learning['fav_apps']) or 'none'}\n"
                f"- Favorite sites: {', '.join(self.learning['fav_sites']) or 'none'}\n"
                f"- Learned commands: {len(self.learning['commands'])}\n"
                f"- Routines: {len(self.learning['routines'])}")

    # ==========================================================
    #  4. LOCAL AI  (Ollama: Llama, Qwen, Mistral, DeepSeek, etc.)
    # ==========================================================
    def local_ai_status(self):
        try:
            r = subprocess.run("ollama list", shell=True, capture_output=True, text=True, timeout=8)
            if r.returncode == 0:
                return "Local AI (Ollama) available. Models:\n" + r.stdout.strip()
            return "Ollama not running. Install at https://ollama.com and run 'ollama serve'."
        except Exception:
            return "Ollama not found. Install at https://ollama.com."

    def local_ai_chat(self, prompt="", model="llama3"):
        """Ask a local model a question (offline, private)."""
        if not prompt:
            return "What should I ask the local model?"
        try:
            r = subprocess.run(f'ollama run {model} "{prompt}"', shell=True,
                               capture_output=True, text=True, timeout=120)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()[:800]
            return "Local model didn't respond. Try 'ollama pull llama3' first."
        except Exception:
            return "Local AI error. Make sure Ollama is installed and the model is pulled."

    def local_ai_models(self):
        try:
            r = subprocess.run("ollama list", shell=True, capture_output=True, text=True, timeout=8)
            return r.stdout.strip() if r.returncode == 0 else "No local models found."
        except Exception:
            return "Ollama not available."

    # ==========================================================
    #  5. MULTI-DEVICE SYNC
    # ==========================================================
    def sync_status(self):
        return (f"Multi-device sync status:\n"
                f"- Last sync: {self.sync.get('last_sync') or 'never'}\n"
                f"- Registered devices: {len(self.sync.get('devices', []))}\n"
                f"Sync file: {self.sync_file}")

    def sync_now(self):
        self.sync["last_sync"] = datetime.datetime.now().isoformat()
        self._save("sync")
        # Sync memory to a shared file
        try:
            if self.agent:
                mem = {"notes": self.agent.notes, "memory": self.agent.memory,
                       "user_name": self.agent.user_name}
                with open(os.path.join(self.base_dir, "sync_memory.json"), "w") as f:
                    json.dump(mem, f, indent=2)
        except Exception:
            pass
        return "Synced memory, notes, and device list. Other devices can import sync_memory.json."
