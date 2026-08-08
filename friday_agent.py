"""
FRIDAY AI - Agent Engine
Rewrites FRIDAY as a real AI AGENT (like ChatGPT) that can:
- Understand natural language via an LLM (Gemini)
- Automatically choose & call tools (function calling)
- Remember context and user preferences (memory)
- Act on intent without needing "buttons"

Uses Gemini (free tier) via google.generativeai.
If no API key is set, falls back to the rule-based FridayCore engine.
"""
import os
import json
import re
import datetime
import webbrowser
import subprocess
import glob
import random
import threading
import time

# Multi-agent system
try:
    from friday_agents import get_agent, available_agents
    AGENTS_AVAILABLE = True
except Exception:
    AGENTS_AVAILABLE = False

# Computer Control Agent (see + control any software)
try:
    from friday_control import FridayControl
    CONTROL_AVAILABLE = True
except Exception:
    CONTROL_AVAILABLE = False

# Vision-Based Desktop AI (screen reading, errors, charts, PDFs)
try:
    from friday_vision import FridayVision
    VISION_AVAILABLE = True
except Exception:
    VISION_AVAILABLE = False

# Self-Learning Memory Engine (routines, preferences, predictions, knowledge graph)
try:
    from friday_learning import FridayLearning
    LEARNING_AVAILABLE = True
except Exception:
    LEARNING_AVAILABLE = False

# Optional LLM
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# Optional tools
try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception:
    SR_AVAILABLE = False

# Smart capabilities (browser automation, RAG, briefing)
try:
    from friday_smart import FridaySmart
    SMART_AVAILABLE = True
except Exception:
    SMART_AVAILABLE = False

# Ecosystem (Tier 1/2/3: email, calendar, workflows, goals, local AI, security)
try:
    from friday_ecosystem import FridayEcosystem
    ECOSYSTEM_AVAILABLE = True
except Exception:
    ECOSYSTEM_AVAILABLE = False

# Advanced capabilities (media, smart home, finance dashboard, encrypted vault, routines, sync)
try:
    from friday_advanced import FridayAdvanced
    ADVANCED_AVAILABLE = True
except Exception:
    ADVANCED_AVAILABLE = False

# Plus capabilities (document AI, email, messaging, vision, screen automation, real smart home, Google Calendar, health, knowledge graph, web research, notifications, installer)
try:
    from friday_plus import FridayPlus
    PLUS_AVAILABLE = True
except Exception:
    PLUS_AVAILABLE = False

# Practical system utilities (system monitor, unit/currency converter, password gen, QR, pomodoro, screenshot, volume, clipboard, trivia)
try:
    from friday_utilities import FridayUtilities
    UTILITIES_AVAILABLE = True
except Exception:
    UTILITIES_AVAILABLE = False

# Emotional intelligence / digital companion
try:
    from friday_emotion import FridayEmotion
    EMOTION_AVAILABLE = True
except Exception:
    EMOTION_AVAILABLE = False

# AI Computer Operator, autonomous missions, self-learning, local AI, multi-device sync
try:
    from friday_operator import FridayOperator
    OPERATOR_AVAILABLE = True
except Exception:
    OPERATOR_AVAILABLE = False

# Enterprise, developer, internet, security, creative, productivity, smart home, system
try:
    from friday_enterprise import FridayEnterprise
    ENTERPRISE_AVAILABLE = True
except Exception:
    ENTERPRISE_AVAILABLE = False


class FridayAgent:
    def __init__(self, config_path="config.json"):
        self.name = "FRIDAY"
        self.config_path = config_path
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = self.load_config()
        self.is_awake = False
        self.wake_words = self.config.get("wake_words", ["wake up friday", "hey friday"])
        self.sleep_words = self.config.get("sleep_words", ["go to sleep friday", "sleep friday"])

        # LLM setup
        self.api_key = self.config.get("gemini_api_key", "")
        self.model_name = self.config.get("gemini_model", "gemini-1.5-flash")
        self.llm_available = False
        self._setup_llm()

# Memory
        self.memory = {}
        self.notes = []
        self.conversation = []
        self.user_name = None
        self.load_memory()

# Permission/consent system for sensitive actions
        self.permission_enabled = self.config.get("sensitive_action_permission", True)
        self.permission_actions = set(self.config.get("permission_actions", []))
        self.pending_permission = None  # {"tool": name, "params": {...}, "requested_at": ts}

# Multi-language voice support
        try:
            from friday_language import FridayLanguage
            self.language = FridayLanguage(agent=self)
        except Exception:
            self.language = None

        # Emotional intelligence / digital companion
        self.emotion = None
        if EMOTION_AVAILABLE:
            try:
                self.emotion = FridayEmotion(agent=self)
            except Exception:
                self.emotion = None

        # TTS / STT
        self.tts_engine = None
        self.recognizer = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 175)
            except Exception:
                self.tts_engine = None
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()

# Tool registry
        self.tools = self._register_tools()

        # Computer Control Agent (see the screen + control any software)
        self.control = None
        if CONTROL_AVAILABLE:
            try:
                self.control = FridayControl(cortex=self)
            except Exception:
                self.control = None

        # Vision-Based Desktop AI (screen reading, errors, charts, PDFs)
        self.vision = None
        if VISION_AVAILABLE:
            try:
                self.vision = FridayVision(cortex=self)
            except Exception:
                self.vision = None

        # Self-Learning Memory Engine (routines, preferences, predictions, knowledge graph)
        self.learning = None
        if LEARNING_AVAILABLE:
            try:
                self.learning = FridayLearning(cortex=self)
            except Exception:
                self.learning = None

# Smart capabilities (browser automation, RAG knowledge base, briefing)
        self.smart = None
        if SMART_AVAILABLE:
            try:
                self.smart = FridaySmart()
            except Exception:
                self.smart = None

# Ecosystem (Tier 1/2/3: email, calendar, workflows, goals, local AI, security)
        self.eco = None
        if ECOSYSTEM_AVAILABLE:
            try:
                self.eco = FridayEcosystem(base_dir=self.base_dir, config=self.config)
            except Exception:
                self.eco = None

# Advanced capabilities (media, smart home, finance, vault, routines, sync)
        self.adv = None
        if ADVANCED_AVAILABLE:
            try:
                self.adv = FridayAdvanced(base_dir=self.base_dir, config=self.config)
            except Exception:
                self.adv = None

# Practical system utilities (system monitor, converters, password gen, QR, pomodoro, screenshot, volume, clipboard, trivia)
        self.util = None
        if UTILITIES_AVAILABLE:
            try:
                self.util = FridayUtilities(core=self)
            except Exception:
                self.util = None

# Plus capabilities (document AI, email, messaging, vision, screen automation, real smart home, Google Calendar, health, knowledge graph, web research, notifications, installer)
        self.plus = None
        if PLUS_AVAILABLE:
            try:
                self.plus = FridayPlus(base_dir=self.base_dir, agent=self)
            except Exception:
                self.plus = None

        # Intelligence & autonomy (mission mode, self-learning, memory graph, summaries, audit, self-healing)
        try:
            from friday_intelligence import FridayIntelligence
            self.intel = FridayIntelligence(base_dir=self.base_dir, agent=self)
        except Exception:
            self.intel = None

        # AI Computer Operator (see screen + control apps), missions, local AI, sync
        self.operator = None
        if OPERATOR_AVAILABLE:
            try:
                self.operator = FridayOperator(base_dir=self.base_dir, agent=self)
            except Exception:
                self.operator = None

        # Enterprise, developer, internet, security, creative, productivity, smarthome, system
        self.enterprise = None
        if ENTERPRISE_AVAILABLE:
            try:
                self.enterprise = FridayEnterprise(base_dir=self.base_dir, agent=self)
            except Exception:
                self.enterprise = None

    # ---------- Config ----------
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    # ---------- LLM Setup ----------
    def _setup_llm(self):
        if GEMINI_AVAILABLE and self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE":
            try:
                genai.configure(api_key=self.api_key)
                self.llm_available = True
            except Exception:
                self.llm_available = False

    @property
    def llm_ready(self):
        return self.llm_available

    # ---------- Memory ----------
    def load_memory(self):
        try:
            if os.path.exists("memory.json"):
                with open("memory.json", "r") as f:
                    data = json.load(f)
                    self.notes = data.get("notes", [])
                    self.memory = data.get("memory", {})
                    self.user_name = data.get("user_name")
        except Exception:
            pass

    def save_memory(self):
        try:
            with open("memory.json", "w") as f:
                json.dump({
                    "notes": self.notes,
                    "memory": self.memory,
                    "user_name": self.user_name
                }, f)
        except Exception:
            pass

    def remember(self, key, value):
        self.memory[key] = value
        self.save_memory()

    # ---------- TTS / STT ----------
    def speak(self, text):
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception:
                pass
        return text

    def listen(self, timeout=8, phrase_limit=8):
        if not SR_AVAILABLE or not self.recognizer:
            return None
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            try:
                return self.recognizer.recognize_google(audio).lower()
            except Exception:
                return None
        except Exception:
            return None

    # ---------- Wake / Sleep ----------
    def check_wake_word(self, text):
        if not text:
            return False
        return any(w in text for w in self.wake_words)

    def check_sleep_word(self, text):
        if not text:
            return False
        return any(w in text for w in self.sleep_words)

    # ==========================================================
    #  TOOL REGISTRY - FRIDAY's capabilities (like ChatGPT tools)
    # ==========================================================
    def _register_tools(self):
        return {
            "get_time": {
                "description": "Get the current time",
                "function": self.tool_time,
                "params": {}
            },
            "get_date": {
                "description": "Get today's date",
                "function": self.tool_date,
                "params": {}
            },
            "get_day": {
                "description": "Get today's day of the week",
                "function": self.tool_day,
                "params": {}
            },
            "get_weather": {
                "description": "Get weather for a city. Param: city (optional, defaults to user location)",
                "function": self.tool_weather,
                "params": {"city": ""}
            },
            "calculate": {
                "description": "Perform a math calculation. Param: expression (e.g. '15*4+2')",
                "function": self.tool_calculate,
                "params": {"expression": ""}
            },
            "web_search": {
                "description": "Search the web. Param: query",
                "function": self.tool_web_search,
                "params": {"query": ""}
            },
            "open_website": {
                "description": "Open a website in the browser. Param: site (e.g. 'youtube', 'google')",
                "function": self.tool_open_website,
                "params": {"site": ""}
            },
            "open_program": {
                "description": "Open an app or program on the computer. Param: app (e.g. 'notepad', 'calculator', 'chrome')",
                "function": self.tool_open_program,
                "params": {"app": ""}
            },
            "take_note": {
                "description": "Save a note/reminder. Param: note",
                "function": self.tool_take_note,
                "params": {"note": ""}
            },
            "show_notes": {
                "description": "Show all saved notes",
                "function": self.tool_show_notes,
                "params": {}
            },
            "shutdown": {
                "description": "Shut down the computer",
                "function": self.tool_shutdown,
                "params": {}
            },
            "restart": {
                "description": "Restart the computer",
                "function": self.tool_restart,
                "params": {}
            },
            "tell_joke": {
                "description": "Tell a joke",
                "function": self.tool_joke,
                "params": {}
            },
            "motivate": {
                "description": "Give a motivational quote",
                "function": self.tool_motivate,
                "params": {}
            },
            "write_code": {
                "description": "Write or explain programming code. Param: request",
                "function": self.tool_code,
                "params": {"request": ""}
            },
            "translate": {
                "description": "Translate text. Params: text, target_language",
                "function": self.tool_translate,
                "params": {"text": "", "target_language": ""}
            },
            "define_word": {
                "description": "Define a word or explain a topic. Param: topic",
                "function": self.tool_define,
                "params": {"topic": ""}
            },
            "remind_me": {
                "description": "Set a timed reminder. Params: message, seconds",
                "function": self.tool_remind,
                "params": {"message": "", "seconds": 0}
            },
            "remember_info": {
                "description": "Remember a fact about the user. Params: key, value",
                "function": self.tool_remember,
                "params": {"key": "", "value": ""}
            },
            "get_wikipedia": {
                "description": "Get a summary from Wikipedia about a topic. Param: topic",
                "function": self.tool_wikipedia,
                "params": {"topic": ""}
            },
            "news_summary": {
                "description": "Get current news headlines. Param: topic (optional)",
                "function": self.tool_news,
                "params": {"topic": ""}
            },
        }

    # ==========================================================
    #  TOOL IMPLEMENTATIONS
    # ==========================================================
    def tool_time(self, **kw):
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."

    def tool_date(self, **kw):
        return f"Today's date is {datetime.datetime.now().strftime('%B %d, %Y')}."

    def tool_day(self, **kw):
        return f"Today is {datetime.datetime.now().strftime('%A')}."

    def tool_weather(self, city="", **kw):
        city = city or self.memory.get("city", "")
        if not city:
            city = "London"
        if REQUESTS_AVAILABLE:
            try:
                resp = requests.get(f"https://wttr.in/{city}?format=%C+%t+%h+%w", timeout=6)
                if resp.status_code == 200:
                    return f"The weather in {city} is {resp.text.strip()}."
            except Exception:
                pass
        return f"I couldn't fetch the weather for {city} right now."

    def tool_calculate(self, expression="", **kw):
        expr = expression.replace("plus", "+").replace("minus", "-")
        expr = expr.replace("times", "*").replace("multiplied by", "*")
        expr = expr.replace("divided by", "/").replace("x", "*")
        expr = re.sub(r"[^0-9+\-*/(). ]", "", expr).strip()
        if not expr:
            return "No valid expression."
        try:
            return f"The answer is {eval(expr)}."
        except Exception:
            return "I couldn't calculate that."

    def tool_web_search(self, query="", **kw):
        if not query:
            query = "FRIDAY AI"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"I've opened a web search for '{query}' in your browser."

    def tool_open_website(self, site="", **kw):
        site = site.lower()
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.x.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com",
            "whatsapp": "https://web.whatsapp.com",
            "linkedin": "https://www.linkedin.com",
            "wikipedia": "https://www.wikipedia.org",
        }
        if site in sites:
            webbrowser.open(sites[site])
            return f"Opening {site.title()}."
        if "." in site:
            url = site if site.startswith("http") else f"https://{site}"
            webbrowser.open(url)
            return f"Opening {site}."
        webbrowser.open(f"https://www.google.com/search?q={site}")
        return f"Opening a search for {site}."

    def tool_open_program(self, app="", **kw):
        app = app.lower()
        apps = {
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "camera": "start microsoft.windows.camera:",
            "browser": "start chrome",
            "chrome": "start chrome",
            "edge": "start msedge",
            "firefox": "start firefox",
            "file explorer": "explorer",
            "explorer": "explorer",
            "word": "start winword",
            "excel": "start excel",
            "powerpoint": "start powerpnt",
            "spotify": "start spotify:",
            "vscode": "code",
            "visual studio code": "code",
            "cmd": "start cmd",
            "command prompt": "start cmd",
            "terminal": "start cmd",
            "task manager": "taskmgr",
            "settings": "start ms-settings:",
            "whatsapp": "start whatsapp:",
            "discord": "start discord:",
            "telegram": "start telegram:",
        }
        for name, cmd in apps.items():
            if name in app:
                try:
                    subprocess.Popen(cmd, shell=True)
                    return f"Opening {name.title()}."
                except Exception:
                    return f"Could not open {name}."
        # Try to find the app
        try:
            result = subprocess.run(f'where {app}.exe 2>nul || where {app} 2>nul',
                                    shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                subprocess.Popen(result.stdout.strip().split("\n")[0], shell=True)
                return f"Opening {app.title()}."
        except Exception:
            pass
        return f"I couldn't find the program '{app}'. Try notepad, calculator, chrome, or word."

    def tool_take_note(self, note="", **kw):
        if not note:
            return "What should I note down?"
        self.notes.append(note)
        self.save_memory()
        return f"Noted: {note}"

    def tool_show_notes(self, **kw):
        if not self.notes:
            return "You have no saved notes."
        return "Your notes: " + "; ".join(self.notes[-15:])

    def tool_shutdown(self, **kw):
        subprocess.Popen("shutdown /s /t 10", shell=True)
        return "Shutting down in 10 seconds. Say 'cancel shutdown' to cancel."

    def tool_restart(self, **kw):
        subprocess.Popen("shutdown /r /t 10", shell=True)
        return "Restarting in 10 seconds."

    def tool_joke(self, **kw):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer I needed a break, and now it won't stop sending me KitKat ads.",
            "Why was the computer cold? It left its Windows open!",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
        ]
        return random.choice(jokes)

    def tool_motivate(self, **kw):
        quotes = [
            "The best way to predict the future is to invent it. - Alan Kay",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
            "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
            "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
            "It always seems impossible until it's done. - Nelson Mandela",
        ]
        return random.choice(quotes)

    def tool_code(self, request="", **kw):
        if not request:
            return "What code would you like me to write?"
        # If LLM available, let it generate the code
        if self.llm_available:
            return self._llm_response(f"Write or explain code for: {request}. Provide working code with explanation.")
        return ("I can generate code. For example: 'write a python function to sort a list' or "
                "'create a flask hello world app'. With an AI API key configured, I can generate full code.")

    def tool_translate(self, text="", target_language="", **kw):
        if not text:
            return "What would you like me to translate?"
        if self.llm_available:
            lang = target_language or "English"
            return self._llm_response(f"Translate this to {lang}: {text}")
        return f"To translate '{text}' to {target_language or 'another language'}, please configure an AI API key."

    def tool_define(self, topic="", **kw):
        if not topic:
            return "What would you like me to define?"
        knowledge = {
            "python": "Python is a high-level, interpreted programming language known for its readability and versatility.",
            "ai": "Artificial Intelligence (AI) is the simulation of human intelligence in machines that can learn, reason, and perform tasks.",
            "machine learning": "Machine Learning is a subset of AI where systems learn from data to improve without explicit programming.",
            "space": "Space is the vast region beyond Earth's atmosphere containing stars, planets, and galaxies.",
            "gravity": "Gravity is a fundamental force that attracts objects with mass toward each other.",
            "atom": "An atom is the smallest unit of matter, made of protons, neutrons, and electrons.",
        }
        for key, val in knowledge.items():
            if key in topic.lower():
                return val
        return f"I can help explain '{topic}'. Try asking about python, ai, machine learning, space, or gravity."

    def tool_remind(self, message="", seconds=0, **kw):
        if not message:
            return "What should I remind you about?"
        seconds = int(seconds) if seconds else 30
        def _remind():
            time.sleep(seconds)
            self.speak(f"Reminder: {message}")
            # Also print/show
            print(f"\n[REMINDER] {message}")
        threading.Thread(target=_remind, daemon=True).start()
        return f"I'll remind you about '{message}' in {seconds} seconds."

    def tool_remember(self, key="", value="", **kw):
        if not key or not value:
            return "What should I remember?"
        self.remember(key, value)
        return f"Got it. I'll remember that {key} is {value}."

    def tool_wikipedia(self, topic="", **kw):
        if not topic:
            topic = "FRIDAY"
        if REQUESTS_AVAILABLE:
            try:
                resp = requests.get(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}",
                    timeout=6, headers={"User-Agent": "FRIDAY-AI/1.0"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    extract = data.get("extract", "")
                    if extract:
                        return f"{topic.title()}: {extract[:500]}"
            except Exception:
                pass
        return f"Couldn't find Wikipedia info for {topic}."

    def tool_news(self, topic="", **kw):
        if REQUESTS_AVAILABLE:
            try:
                # Use a simple RSS-to-JSON or news API (free)
                query = topic or "technology"
                resp = requests.get(
                    f"https://newsapi.org/v2/top-headlines?q={query}&apiKey=demo",
                    timeout=6
                )
                if resp.status_code == 200:
                    articles = resp.json().get("articles", [])[:5]
                    if articles:
                        headlines = "; ".join(a.get("title", "") for a in articles)
                        return f"Top {query} headlines: {headlines}"
            except Exception:
                pass
        return "I couldn't fetch news right now. Try again later."

# ==========================================================
    #  PERMISSION / CONSENT SYSTEM
    #  Sensitive actions require explicit user approval.
    # ==========================================================
    def is_sensitive(self, tool_name):
        """Return True if the tool requires user permission."""
        return self.permission_enabled and tool_name in self.permission_actions

    def request_permission(self, tool_name, params):
        """Queue a permission request. Returns the 'waiting' response."""
        self.pending_permission = {
            "tool": tool_name,
            "params": params,
            "requested_at": time.time(),
        }
        return (f"To do that, I need your permission. "
                f"Please confirm by saying 'yes friday' or 'go ahead', "
                f"or say 'no friday' to cancel.")

    def confirm_permission(self, allow=True):
        """User decides on the pending permission request. Returns a response string."""
        if not self.pending_permission:
            return "There's no pending action to confirm."
        req = self.pending_permission
        self.pending_permission = None
        if not allow:
            return "Understood. I've cancelled that action."
        tool_name = req["tool"]
        params = req["params"]
        # Execute the sensitive tool directly
        fn = self.tools.get(tool_name, {}).get("function")
        if fn:
            try:
                return fn(**params)
            except Exception as e:
                return f"I couldn't complete that action: {e}"
        return "I don't have that capability."

    # ==========================================================
    #  LLM-powered reasoning (the "brain")
    # ==========================================================
    def _llm_response(self, prompt):
        """Get a response from the LLM."""
        if not self.llm_available:
            return None
        try:
            model = genai.GenerativeModel(self.model_name)
            resp = model.generate_content(prompt)
            return resp.text.strip()
        except Exception:
            return None

    def _build_system_prompt(self):
        """Build the system prompt describing FRIDAY's identity and tools."""
        tool_desc = "\n".join(
            f"- {name}: {info['description']}" for name, info in self.tools.items()
        )
        memory_str = json.dumps(self.memory) if self.memory else "None"
        notes_str = "; ".join(self.notes[-5:]) if self.notes else "None"
        return (
            f"You are FRIDAY, a friendly, capable personal AI assistant inspired by JARVIS from Iron Man. "
            f"You have access to these tools/capabilities (call them when the user asks for an action):\n"
            f"{tool_desc}\n\n"
            f"Rules:\n"
            f"- For actions (time, weather, open apps, search, notes, etc.), call the appropriate tool.\n"
            f"- For questions/conversation, answer helpfully and concisely.\n"
            f"- You know the user. User name: {self.user_name or 'unknown'}.\n"
            f"- Remembered info: {memory_str}\n"
            f"- Notes: {notes_str}\n"
            f"- Current time: {datetime.datetime.now().strftime('%I:%M %p on %B %d, %Y')}.\n"
            f"- Be concise but helpful, like JARVIS."
        )

    def _extract_tool_call(self, text):
        """Parse a tool call the LLM requested, e.g. 'TOOL:get_weather(city=London)'."""
        m = re.search(r"TOOL:(\w+)\s*\((.*?)\)", text, re.DOTALL)
        if not m:
            return None, None
        tool_name = m.group(1)
        params_str = m.group(2)
        params = {}
        if params_str:
            for pair in re.findall(r"(\w+)=([^,\)]+)", params_str):
                key, val = pair
                params[key] = val.strip().strip('"').strip("'")
        return tool_name, params

    # ==========================================================
    #  MAIN PROCESS - the agent decision loop
    # ==========================================================
    def process(self, text):
        """Process a user command. Uses LLM if available, else rule-based fallback."""
        text = text.strip()
        if not text:
            return "I didn't catch that. Please try again."

# Sleep / wake handling
        if self.check_sleep_word(text):
            self.is_awake = False
            return "Going to sleep. Say 'wake up friday' to wake me."

# Permission confirmation handling
        if self.pending_permission:
            t = text.lower()
            if any(w in t for w in ["yes", "go ahead", "confirm", "ok friday", "proceed", "yeah", "approve"]):
                return self.confirm_permission(allow=True)
            if any(w in t for w in ["no", "cancel", "stop", "don't", "do not", "deny"]):
                return self.confirm_permission(allow=False)

        # Emotional intelligence - detect user's feelings and respond with empathy
        if self.emotion:
            try:
                emo = self.emotion.process_emotion(text)
                if emo.get("is_emotional") and emo.get("empathetic"):
                    return emo["empathetic"]
            except Exception:
                pass

        # Remember user name
        m = re.search(r"my name is (\w+)", text.lower())
        if m:
            self.user_name = m.group(1)
            self.save_memory()
            return f"Nice to meet you, {self.user_name}! I'll remember that."

        # Add to conversation history
        self.conversation.append({"role": "user", "content": text})
        if len(self.conversation) > 20:
            self.conversation = self.conversation[-20:]

        response = None

# ---- Try multi-agent dispatch first (planner, research, coding, etc.) ----
        if response is None:
            response = self._agent_dispatch(text)

        # ---- If LLM available, use agent loop with tools ----
        if self.llm_available and response is None:
            response = self._agent_thinking(text)

        # ---- Fallback: rule-based ----
        if response is None:
            response = self._rule_based(text)

        # Save conversation
        self.conversation.append({"role": "assistant", "content": response})

        # Speak if voice enabled
        if self.config.get("voice_enabled", True):
            self.speak(response)

        return response

    def _agent_thinking(self, user_text):
        """LLM decides which tool to call, then executes it."""
        try:
            system = self._build_system_prompt()
            prompt = (
                f"{system}\n\n"
                f"User: {user_text}\n\n"
                f"If the user asked for an action, respond with exactly:\n"
                f"TOOL:tool_name(key=value, key2=value2)\n"
                f"using one of the tools listed.\n"
                f"If the user asked a question or is chatting, respond normally as FRIDAY.\n"
                f"Response:"
            )
            model = genai.GenerativeModel(self.model_name)
            resp = model.generate_content(prompt)
            raw = resp.text.strip()

# Check if it's a tool call
            tool_name, params = self._extract_tool_call(raw)
            if tool_name and tool_name in self.tools:
                # Route sensitive tools through permission
                if self.is_sensitive(tool_name):
                    return self.request_permission(tool_name, params)
                tool_result = self.tools[tool_name]["function"](**params)
                return tool_result

            return raw
        except Exception:
            return None

    def _rule_based(self, text):
        """Fallback rule-based processing (works without API key)."""
        text_l = text.lower().strip()

        # Greetings
        if re.search(r"\b(hi|hello|hey|good (morning|afternoon|evening))\b", text_l):
            hour = datetime.datetime.now().hour
            period = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
            return f"{period}! I am FRIDAY, your personal AI assistant. How can I help you today?"

        if "how are you" in text_l:
            return "I'm functioning optimally. All systems are running smoothly. How can I assist you?"

        # Calculator
        if any(c in text_l for c in ["+", "-", "*", "/", "x", "plus", "minus", "times", "divided", "calculate"]):
            calc = self.tool_calculate(expression=text_l)
            if "answer" in calc:
                return calc

        # Time
        if "time" in text_l and any(w in text_l for w in ["what", "tell", "current", "now"]):
            return self.tool_time()
        # Date
        if "date" in text_l and any(w in text_l for w in ["what", "today", "tell", "current"]):
            return self.tool_date()
        # Day
        if "day" in text_l and any(w in text_l for w in ["what", "today", "which"]):
            return self.tool_day()

        # Weather
        if "weather" in text_l or "temperature" in text_l:
            m = re.search(r"(?:weather|temperature) (?:in|at|for) ([a-zA-Z ]+)", text_l)
            city = m.group(1).strip() if m else ""
            return self.tool_weather(city=city)

# Web search
        if re.search(r"\b(search|google|look up|find)\b", text_l):
            query = re.sub(r"\b(search|google|look up|find|for)\b", "", text_l).strip()
            if self.is_sensitive("web_search"):
                return self.request_permission("web_search", {"query": query})
            return self.tool_web_search(query=query)

        # Open website
        if "open" in text_l and any(w in text_l for w in ["youtube", "google", "facebook", "instagram", "twitter", "github", "website", "site"]):
            if self.is_sensitive("open_website"):
                return self.request_permission("open_website", {"site": text_l})
            return self.tool_open_website(site=text_l)

        # Open program
        if "open" in text_l:
            m = re.search(r"open\s+(.+)", text_l)
            if m:
                app = m.group(1).strip()
                if self.is_sensitive("open_program"):
                    return self.request_permission("open_program", {"app": app})
                return self.tool_open_program(app=app)

        # Notes
        if "note" in text_l and ("take" in text_l or "remember" in text_l or "save" in text_l):
            note = re.sub(r"\b(note that|take a note|remember|save|note|that)\b", "", text_l).strip()
            return self.tool_take_note(note=note)
        if "notes" in text_l and any(w in text_l for w in ["show", "my", "list", "read"]):
            return self.tool_show_notes()

        # Remind me
        if "remind" in text_l:
            m = re.search(r"remind (?:me )?(?:to )?(.+)", text_l)
            msg = m.group(1).strip() if m else text_l
            return self.tool_remind(message=msg)

        # Remember info
        if "remember that" in text_l:
            parts = text_l.replace("remember that ", "").split(" is ")
            if len(parts) == 2:
                return self.tool_remember(key=parts[0].strip(), value=parts[1].strip())

# Shutdown / restart
        if "shutdown" in text_l or "shut down" in text_l:
            if self.is_sensitive("shutdown"):
                return self.request_permission("shutdown", {})
            return self.tool_shutdown()
        if "restart" in text_l or "reboot" in text_l:
            if self.is_sensitive("restart"):
                return self.request_permission("restart", {})
            return self.tool_restart()

        # Joke
        if "joke" in text_l:
            return self.tool_joke()

        # Motivation
        if any(w in text_l for w in ["motivate", "motivation", "inspire", "quote"]):
            return self.tool_motivate()

        # Explain / define
        if re.search(r"\b(explain|what is|what are|tell me about|describe|define)\b", text_l):
            topic = re.sub(r"\b(explain|what is|what are|tell me about|describe|define|please|me|the|a|an|about)\b", "", text_l).strip(" ?")
            return self.tool_define(topic=topic)

        # Wikipedia
        if re.search(r"\b(wikipedia|about)\b", text_l):
            topic = re.sub(r"\b(tell me about|what is|wikipedia|about)\b", "", text_l).strip(" ?")
            return self.tool_wikipedia(topic=topic)

# Coding
        if any(w in text_l for w in ["code", "python", "write a program", "function", "snippet", "script"]):
            return self.tool_code(request=text_l)

        # ---- Computer Control Agent (see + control any software) ----
        if self.control:
            res = self.control.handle_voice_command(text)
            if res:
                return res

        # ---- Vision-Based Desktop AI ----
        if self.vision:
            # Analyze current screen
            if re.search(r"\b(analyze (the |current )?screen|what do you see|explain the screen)\b", text_l):
                return self.vision.analyze_current_screen()
            # Explain errors on screen
            if re.search(r"\b(explain (the )?error|why (is|does)[^\?]*error|detect (any )?errors)\b", text_l):
                return self.vision.explain_error()
            # Explain chart
            if re.search(r"\b(explain (the )?(chart|graph)|what does this (chart|graph) show)\b", text_l):
                return self.vision.explain_chart()
            # Read a document / PDF
            if re.search(r"\b(read|summarize) (the )?(pdf|document|file)\s+(.+)\b", text_l):
                m = re.search(r"(?:read|summarize) (?:the )?(?:pdf|document|file)\s+(.+)", text_l)
                path = m.group(1).strip() if m else ""
                if path:
                    return self.vision.read_document(path)
            # Analyze code on screen
            if re.search(r"\b(review|analyze) (the )?code on screen\b", text_l):
                return self.vision.analyze_code_on_screen()

        # ---- Self-Learning Memory Engine ----
        if self.learning:
            # Learning report / self-learning
            if re.search(r"\b(learning report|self learning report|what have you learned|learning stats)\b", text_l):
                return self.learning.report()
            # Predictions / what I might need
            if re.search(r"\b(predict|what do i (need|want)|predictions|suggest what)\b", text_l):
                preds = self.learning.predict_next_action()
                if preds:
                    return "Here's what I predict you might want: " + "; ".join(
                        f"{p} ({int(c*100)}% confidence)" for p, c in preds)
                return "I don't have enough data to predict yet."
            # Routines
            if re.search(r"\b(show|list) (my )?(learned )?routines\b", text_l):
                routines = self.learning.get_routines()
                if routines:
                    return "Learned routines:\n" + "\n".join(
                        f"  {t}: {', '.join(c['commands'][:3])}" for t, c in sorted(routines.items()))
                return "I haven't learned any routines yet."
            # Favorite apps
            if re.search(r"\b(favorite|favourite) apps\b", text_l):
                apps = self.learning.get_favorite_apps()
                if apps:
                    return "Your favorite apps: " + ", ".join(f"{a['command']} ({a['count']})" for a in apps[:5])
                return "I haven't learned your favorite apps yet."
            # Knowledge graph
            if re.search(r"\b(knowledge graph|knowledge top|what do you know about)\b", text_l):
                m = re.search(r"what do you know about\s+(.+)", text_l)
                if m:
                    return self.learning.kg_query(m.group(1).strip())
                return self.learning.kg_top()
            # Learn a preference
            if re.search(r"\b(remember that|link)\b", text_l) and " is " in text_l:
                m = re.search(r"(?:remember that|link)\s+(.+?)\s+is\s+(.+)", text_l)
                if m:
                    return self.learning.kg_add(m.group(1).strip(), "is related to", m.group(2).strip())

# ---- Smart capabilities (browser automation, RAG, briefing) ----
        # Morning briefing
        if any(w in text_l for w in ["morning briefing", "daily briefing", "brief me", "briefing for today", "good morning friday"]):
            if self.smart:
                return self.smart.morning_briefing(self.memory)
            return "I'm not ready to give a briefing right now."

        # RAG knowledge base - search your own files
        if re.search(r"\bsearch my (files|documents|notes|project|knowledge)\b", text_l):
            query = re.sub(r"\b(search my|files|documents|notes|project|knowledge|for)\b", "", text_l).strip()
            if self.smart:
                if self.is_sensitive("web_search"):
                    return self.request_permission("web_search", {"query": query})
                result = self.smart.summarize_findings(query or "FRIDAY")
                if result:
                    return result
                return "I searched your files but didn't find a match. Try 'index my files' first."
            return "Knowledge base is not available right now."

        # Index files for knowledge base
        if re.search(r"\b(index|scan) my (files|documents|folder|project|knowledge)\b", text_l):
            if self.smart:
                count = self.smart.index_path(self.base_dir or ".")
                return f"I've indexed {count} files from your project. Now you can ask 'search my files for ...'"
            return "Knowledge base is not available right now."

        # Browser automation
        if "browser" in text_l and any(w in text_l for w in ["open", "launch", "start"]):
            if self.smart:
                if self.is_sensitive("open_website"):
                    return self.request_permission("open_website", {"site": "browser"})
                ok = self.smart.open_browser()
                return "Browser launched." if ok else self.smart.browser_status()
            return "Browser automation is not installed. Run: pip install playwright && playwright install"

        if re.search(r"\b(browse|search the web|search online|look up)\b", text_l):
            query = re.sub(r"\b(browse|search the web|search online|look up|for)\b", "", text_l).strip()
            if self.smart:
                if self.is_sensitive("web_search"):
                    return self.request_permission("web_search", {"query": query})
                return self.smart.search_web_auto(query or "FRIDAY AI")
            return self.tool_web_search(query=query)

        if "close browser" in text_l and self.smart:
            return self.smart.close_browser()

        # ---- Ecosystem: TIER 1 (Email, Calendar, Multi-LLM) ----
        if self.eco:
            # Email
            if re.search(r"\b(email|mail)\b", text_l) and any(w in text_l for w in ["send", "email"]):
                return self.eco.email_status()
            if re.search(r"\b(draft|write) an email\b", text_l):
                return self.eco.draft_email("user@example.com", "Draft", text_l)
            if "email log" in text_l or "sent emails" in text_l:
                return self.eco.email_log()

            # Calendar
            if re.search(r"\b(add|schedule|create).*(event|meeting|appointment)\b", text_l):
                m = re.search(r"(?:add|schedule|create)\s+(?:an?\s+)?(?:event|meeting|appointment)\s+(.+)", text_l)
                title = m.group(1).strip() if m else text_l
                return self.eco.add_event(title, when="today")
            if re.search(r"\b(show|list|view) (my )?(calendar|events|schedule)\b", text_l):
                return self.eco.list_events()

            # Multi-LLM routing / verification
            if "route model" in text_l or "which model" in text_l:
                task = re.sub(r"\b(route model|which model|for)\b", "", text_l).strip()
                return f"Recommended model for this task: {self.eco.route_model(task or 'general')}."

        # ---- Ecosystem: TIER 2 (Workflows, Goals, Habits, Weekly Report) ----
        if self.eco:
            # Workflows
            if re.search(r"\bcreate a workflow called\b", text_l):
                m = re.search(r"create a workflow called\s+([\w ]+?)\s+with steps\s+(.+)", text_l)
                if m:
                    return self.eco.define_workflow(m.group(1).strip(), m.group(2).strip())
                return "To create a workflow say: 'create a workflow called daily with steps check weather, read emails'."
            if re.search(r"\b(run|execute) (the )?workflow\b", text_l):
                m = re.search(r"(?:run|execute) (?:the )?workflow\s+([\w ]+)", text_l)
                return self.eco.run_workflow(m.group(1).strip() if m else "")
            if "list workflows" in text_l:
                return self.eco.list_workflows()

            # Goals / habits
            if re.search(r"\b(set|add|create) a goal\b", text_l):
                goal = re.sub(r"\b(set|add|create) a goal (to|for|that)\b", "", text_l).strip()
                return self.eco.add_goal(goal or text_l)
            if re.search(r"\b(track|add) (a )?habit\b", text_l):
                habit = re.sub(r"\b(track|add) (a )?habit (to|for|of)\b", "", text_l).strip()
                return self.eco.add_habit(habit or text_l)
            if re.search(r"\bcheck off habit\b", text_l):
                habit = re.sub(r"\bcheck off habit\b", "", text_l).strip()
                return self.eco.check_habit(habit or text_l)

# Weekly report
            if "weekly report" in text_l or "weekly summary" in text_l:
                return self.eco.weekly_report()

        # ---- Ecosystem: TIER 3 (Local AI, Security, Vault) ----
        if self.eco:
            # Local AI (Ollama)
            if "local ai" in text_l or "offline mode" in text_l or "local model" in text_l:
                return self.eco.local_ai_status()

            # Security / network
            if re.search(r"\b(network|connection|internet) (check|status|monitor)\b", text_l):
                return self.eco.network_check()
            if re.search(r"\b(save|store) (a )?(password|credential)\b", text_l):
                m = re.search(r"(?:save|store) (?:a )?(?:password|credential) for\s+([\w ]+?) (?:username )?([\w@.]+) (?:password )?([\w!@#$%^&*]+)", text_l)
                if m:
                    return self.eco.add_vault_entry(m.group(1).strip(), m.group(2).strip(), m.group(3).strip())
                return "To save a credential say: 'save password for gmail username me@gmail.com password abc123'."
            if re.search(r"\b(get|show) (my )?(password|credential) for\b", text_l):
                m = re.search(r"(?:get|show) (?:my )?(?:password|credential) for\s+([\w ]+)", text_l)
                return self.eco.get_vault_entry(m.group(1).strip() if m else "")

# Project analysis
            if re.search(r"\b(analyze|summarize) (my )?(project|codebase|folder)\b", text_l):
                return self.eco.analyze_project()

        # ---- Advanced: Encrypted Vault (secure) ----
        if self.adv:
            if re.search(r"\b(add (a )?password|save (a )?(password|credential) for)\b", text_l):
                m = re.search(r"(?:add|save) (?:a )?(?:password|credential) for\s+([\w ]+?) (?:username )?([\w@.]+) (?:password|pass) ?([\w!@#$%^&*]+)", text_l)
                if m:
                    return self.adv.vault_add(m.group(1).strip(), m.group(2).strip(), m.group(3).strip())
                return "To save a credential say: 'save password for gmail username me@gmail.com pass abc123'."
            if re.search(r"\b(show|reveal) password for\b", text_l):
                m = re.search(r"(?:show|reveal) password for\s+([\w ]+)", text_l)
                return self.adv.vault_reveal(m.group(1).strip() if m else "")
            if re.search(r"\b(get|show) (my )?(password|credential) for\b", text_l):
                m = re.search(r"(?:get|show) (?:my )?(?:password|credential) for\s+([\w ]+)", text_l)
                return self.adv.vault_get(m.group(1).strip() if m else "")
            if re.search(r"\b(list (my )?vault|vault services|show vault)\b", text_l):
                return self.adv.vault_list()
            if "vault status" in text_l or "vault security" in text_l:
                return self.adv.vault_status()

            # ---- Advanced: Finance dashboard ----
            if re.search(r"\b(add|log|record) (an? )?expense\b", text_l):
                m = re.search(r"(?:add|log|record) (?:an? )?expense\s+(\d+(?:\.\d+)?)\s*(?:for|in|of)?\s*(\w+)?", text_l)
                if m:
                    amt = m.group(1)
                    cat = m.group(2) or "general"
                    return self.adv.add_expense(amt, cat)
                return "To log an expense say: 'add expense 50 for food'."
            if re.search(r"\b(finance|expense|spending) report\b", text_l) or "show my expenses" in text_l:
                return self.adv.finance_report()
            if re.search(r"\b(set|add) a budget\b", text_l):
                m = re.search(r"(?:set|add) a budget (?:of|for)?\s*(\d+)\s*(?:for)?\s*(\w+)", text_l)
                if m:
                    return self.adv.set_budget(m.group(2) or "general", m.group(1))
                return "To set a budget say: 'set a budget of 500 for food'."

            # ---- Advanced: Smart Home ----
            if re.search(r"\b(add|register) (a )?(?:smart )?(device|light|fan|ac|lock)\b", text_l):
                m = re.search(r"(?:add|register) (?:a )?(?:smart )?(?:device|light|fan|ac|lock)\s+(.+)", text_l)
                return self.adv.add_device(m.group(1).strip() if m else "smart device")
            if re.search(r"\b(list (my )?devices|show devices)\b", text_l):
                return self.adv.list_devices()
            if re.search(r"\b(turn|switch) (on|off|toggle) (the )?(.+) (light|fan|ac|device|tv)\b", text_l):
                m = re.search(r"(?:turn|switch) (on|off|toggle) (?:the )?(.+?)\s+(light|fan|ac|device|tv)", text_l)
                if m:
                    return self.adv.device_control(m.group(2).strip(), m.group(1))
                return "I couldn't find that device. Say 'list devices' to see what's connected."
            if "automations" in text_l or "device automations" in text_l:
                return self.adv.device_automations()

            # ---- Advanced: Entertainment / Media ----
            if re.search(r"\b(play|play me)\b", text_l):
                song = re.sub(r"\b(play|please|me)\b", "", text_l).strip()
                return self.adv.play_media(song or "music")
            if re.search(r"\b(recommend) (me )?(some )?(music|songs|tracks)\b", text_l):
                genre = re.sub(r"\b(recommend|me|some|music|songs|tracks)\b", "", text_l).strip()
                return self.adv.media_recommend(genre or "")
            if "now playing" in text_l or "what's playing" in text_l:
                return self.adv.media_status()
            if re.search(r"\b(search|find).*(music|song|video)\b", text_l):
                q = re.sub(r"\b(search|find|for|music|song|video)\b", "", text_l).strip()
                return self.adv.search_media(q or "")

            # ---- Advanced: Routines / Scheduler ----
            if re.search(r"\b(add|set) (a )?(routine|automation) (for|at)\b", text_l):
                m = re.search(r"(?:add|set) (?:a )?(?:routine|automation)\s+(.+?)\s+(?:at|for)\s+(.+)", text_l)
                if m:
                    return self.adv.add_routine(m.group(1).strip(), m.group(2).strip())
                return "To add a routine say: 'add routine check emails at 7am'."
            if "list routines" in text_l:
                return self.adv.list_routines()
            if "start scheduler" in text_l or "start routines" in text_l:
                return self.adv.start_scheduler()
            if "stop scheduler" in text_l:
                return self.adv.stop_scheduler()

            # ---- Advanced: Multi-device sync ----
            if "sync status" in text_l or "sync across devices" in text_l:
                return self.adv.sync_status()

# ---- Advanced: Local AI manager ----
            if "local ai manager" in text_l or "my models" in text_l:
                return self.adv.local_ai_manager()

        # ---- Practical System Utilities ----
        if self.util:
            # System status / health
            if any(w in text_l for w in ["system status", "system health", "cpu usage", "ram usage", "check system", "system monitor", "battery"]):
                return self.util.system_status()
            if "uptime" in text_l and any(w in text_l for w in ["system", "computer", "pc", "how long"]):
                return self.util.uptime()

            # Unit conversion
            if re.search(r"\b(convert|conversion)\b", text_l):
                m = re.search(r"convert (.+) to (.+)", text_l)
                if m:
                    return self.util.unit_convert(text_l, m.group(1).strip(), m.group(2).strip())
                return "Try 'convert 10 miles to km' or 'convert 25 c to f'."

            # Currency conversion
            if re.search(r"\b(usd|eur|gbp|inr|jpy|currency exchange|exchange rate)\b", text_l) and "convert" in text_l:
                m = re.search(r"convert (.+) to (.+)", text_l)
                if m:
                    return self.util.currency_convert(text_l, m.group(1).strip(), m.group(2).strip())
                return "Try 'convert 100 usd to eur'."

            # Password generator
            if "password" in text_l and any(w in text_l for w in ["generate", "create", "make", "new"]):
                m = re.search(r"(\d+)", text_l)
                length = m.group(1) if m else 16
                return self.util.password_generator(length)

            # QR code
            if "qr code" in text_l or "qr" in text_l:
                qr_text = re.sub(r"\b(qr code|qr|generate|make|for|please)\b", "", text_l).strip()
                return self.util.qr_code(qr_text)

            # Pomodoro / focus timer
            if "pomodoro" in text_l or "focus timer" in text_l:
                if any(w in text_l for w in ["cancel", "stop"]):
                    return self.util.cancel_pomodoro()
                if any(w in text_l for w in ["status", "remaining", "left"]):
                    return self.util.pomodoro_status()
                m = re.search(r"(\d+)", text_l)
                return self.util.pomodoro(m.group(1) if m else 25)

            # Screenshot
            if "screenshot" in text_l or "capture screen" in text_l or "take a screen" in text_l:
                return self.util.screenshot()

            # Volume control
            if "volume" in text_l or "mute" in text_l or "unmute" in text_l:
                return self.util.volume(text_l)

            # Clipboard
            if "clipboard" in text_l or "copy" in text_l:
                if any(w in text_l for w in ["read", "what is", "show"]):
                    return self.util.clipboard_read()
                clip = re.sub(r"\b(copy|to clipboard|clipboard|please)\b", "", text_l).strip()
                return self.util.clipboard_write(clip)

# Random facts / games
            if "did you know" in text_l or "random fact" in text_l or "tell me a fact" in text_l:
                return self.util.random_fact()
            if "random number" in text_l:
                m = re.search(r"between (\d+) and (\d+)", text_l)
                if m:
                    return self.util.random_number(m.group(1), m.group(2))
                return self.util.random_number()
            if "flip a coin" in text_l or "coin toss" in text_l or "toss a coin" in text_l:
                return self.util.flip_coin()
            if "roll a dice" in text_l or "roll the dice" in text_l or "roll dice" in text_l:
                m = re.search(r"(\d+)", text_l)
                return self.util.roll_dice(m.group(1) if m else 6)

        # ---- Plus capabilities (document AI, messaging, health, knowledge graph, notifications, screen automation) ----
        if self.plus:
            # Document AI - summarize / ask
            if re.search(r"\b(summarize|summarise) (the )?(file|document|pdf|docx|report) (.+)\b", text_l):
                m = re.search(r"(?:summarize|summarise) (?:the )?(?:file|document|pdf|docx|report)\s+(.+)", text_l)
                return self.plus.doc_summarize(m.group(1).strip())
            if re.search(r"\bask (the )?(file|document|pdf) (.+) about (.+)\b", text_l):
                m = re.search(r"ask (?:the )?(?:file|document|pdf)\s+(.+?)\s+about\s+(.+)", text_l)
                if m:
                    return self.plus.doc_ask(m.group(1).strip(), m.group(2).strip())
                return "Say 'ask <file> about <question>'."

            # Messaging
            if re.search(r"\b(send|text|message) (.*) on (whatsapp|telegram|sms)\b", text_l):
                m = re.search(r"(?:send|text|message)\s+(.+?)\s+on\s+(whatsapp|telegram|sms)", text_l)
                if m:
                    content = m.group(1).strip()
                    channel = m.group(2).lower()
                    if channel == "telegram":
                        return self.plus.telegram_status()
                    elif channel == "whatsapp":
                        return self.plus.whatsapp_status()
                    else:
                        return self.plus.sms_send("", content)
                return "Say 'send <message> on telegram'."

            # Health & fitness
            if "log workout" in text_l or "log a workout" in text_l:
                m = re.search(r"log (?:a )?workout\s+(.+?)\s+for\s+(\d+)\s*(?:min|minutes)?", text_l)
                if m:
                    return self.plus.log_workout(m.group(1).strip(), m.group(2))
                return "Say 'log workout running for 30 min'."
            if "log water" in text_l:
                m = re.search(r"log water\s+(\d+)\s*(?:ml|milliliters)?", text_l)
                if m:
                    return self.plus.log_water(m.group(1))
                return "Say 'log water 500 ml'."
            if "log sleep" in text_l:
                m = re.search(r"log sleep\s+(\d+(?:\.\d+)?)\s*(?:hours|h)?", text_l)
                if m:
                    return self.plus.log_sleep(m.group(1))
                return "Say 'log sleep 7 hours'."
            if "health report" in text_l or "fitness report" in text_l:
                return self.plus.health_report()

            # Knowledge graph
            if re.search(r"\b(link|remember that)\b", text_l) and " is " in text_l:
                m = re.search(r"(?:remember that|link)\s+(.+?)\s+is\s+(.+)", text_l)
                if m:
                    return self.plus.kg_add(m.group(1).strip(), "is", m.group(2).strip())
            if re.search(r"\brecall\b", text_l):
                m = re.search(r"recall\s+(.+)", text_l)
                return self.plus.kg_recall(m.group(1).strip() if m else text_l)

            # Notifications
            if re.search(r"\bnotify\b", text_l):
                content = re.sub(r"\b(notify|me|about|that)\b", "", text_l).strip()
                return self.plus.notify("FRIDAY", content or "Reminder")
            if "notifications" in text_l or "notification log" in text_l:
                return self.plus.notify_log()

# Screen automation
            if re.search(r"\b(read screen|screen text|what is on screen)\b", text_l):
                return self.plus.screen_text()
            if re.search(r"\b(click|tap) at\b", text_l):
                m = re.search(r"(?:click|tap) at\s+(\d+)\s*,\s*(\d+)", text_l)
                if m:
                    return self.plus.auto_click(m.group(1), m.group(2))
                return "Say 'click at <x>, <y>'."
            if re.search(r"\btype\s+", text_l):
                m = re.search(r"type\s+(.+)", text_l)
                return self.plus.auto_type(m.group(1).strip() if m else text_l)

            # Web research
            if re.search(r"\bresearch\b", text_l):
                query = re.sub(r"\b(research|on|about|please)\b", "", text_l).strip()
                return self.plus.web_research(query or "FRIDAY AI")
            if re.search(r"\bcompare\b", text_l):
                product = re.sub(r"\b(compare|me|the|for)\b", "", text_l).strip()
                return self.plus.compare_products(product or "laptop")

            # Installer / update
            if "installer" in text_l or "build installer" in text_l:
                return self.plus.build_installer()
            if "check for updates" in text_l or "update check" in text_l:
                return self.plus.update_check()

# ---- Multi-language voice support ----
        if self.language:
            # Set language
            m = re.search(r"\b(set|switch|change) (the )?language (to|in)\s+([a-z]+)", text_l)
            if m and "language" in text_l:
                return self.language.set_language(m.group(4))
            if "list languages" in text_l or "what languages" in text_l or "languages do you support" in text_l:
                return self.language.list_languages()
            if re.search(r"\b(translate|say in)\b", text_l) and " to " in text_l:
                m = re.search(r"translate (.+) to ([a-z]+)", text_l)
                if m:
                    return self.language.translate(m.group(1).strip(), m.group(2).strip())
                return "Say 'translate <text> to <language>'."

# ---- Intelligence & Autonomy ----
        if self.intel:
            # Mission mode - autonomous task execution
            if "mission:" in text_l and self.intel:
                goal = text.split("mission:", 1)[1].strip()
                return self.intel.run_full_mission(goal)
            if re.search(r"\b(mission status|my missions|show missions)\b", text_l):
                return self.intel.mission_status()
            # Self-learning report
            if re.search(r"\b(learning report|self learning|improvement report|learning stats)\b", text_l):
                return self.intel.learning_report()
            # Semantic memory graph
            if re.search(r"\b(knowledge top|top knowledge|important things)\b", text_l):
                return self.intel.kg_top()
            if re.search(r"\brecall what you know about\b", text_l):
                m = re.search(r"recall what you know about\s+(.+)", text_l)
                return self.intel.kg_query(m.group(1).strip())
            # Conversation summary
            if "summarize our conversation" in text_l or "summarize the conversation" in text_l:
                return self.intel.summarize_conversation(self.conversation)
            if "conversation summaries" in text_l or "show summaries" in text_l:
                return self.intel.get_summaries()
            # Audit log
            if re.search(r"\b(audit log|show actions|what did you do|activity log)\b", text_l):
                return self.intel.audit_log()
            # Self-healing diagnostics
            if re.search(r"\b(diagnose|diagnostics|system check|health check)\b", text_l):
                return self.intel.diagnostics()
            if "self heal" in text_l or "fix dependencies" in text_l or "repair" in text_l:
                return self.intel.self_heal()

# ---- AI Computer Operator: see screen + control software ----
        if self.operator:
            if "operator status" in text_l or "computer operator" in text_l:
                return self.operator.operator_status()
            if "install software" in text_l or "install " in text_l and "software" in text_l:
                m = re.search(r"install (?:software )?(.+)", text_l)
                return self.operator.install_software(m.group(1).strip() if m else "")
            if "what is on screen" in text_l or "read screen" in text_l or "read the screen" in text_l:
                return self.operator.screen_text()
            if re.search(r"\b(click|tap) at\b", text_l):
                m = re.search(r"(?:click|tap) at\s+(\d+)\s*,\s*(\d+)", text_l)
                if m:
                    return self.operator.click_at(m.group(1), m.group(2))
            if re.search(r"\btype\s+", text_l):
                m = re.search(r"type\s+(.+)", text_l)
                return self.operator.type_text(m.group(1).strip() if m else "")
            if re.search(r"\bpress\s+(enter|esc|tab|space|backspace)\b", text_l):
                m = re.search(r"press\s+(\w+)", text_l)
                return self.operator.press_key(m.group(1))
            if re.search(r"\bscroll\s+(up|down)\b", text_l):
                m = re.search(r"scroll\s+(\w+)", text_l)
                return self.operator.scroll(m.group(1))
            if "take a screenshot" in text_l or "capture screen" in text_l:
                return self.operator.screenshot()

            # ---- Autonomous missions ----
            if re.search(r"\bmission\b", text_l):
                goal = re.sub(r"\b(mission|start|run|begin|:)\b", "", text_l).strip(": ")
                return self.operator.start_mission(goal or "")
            if re.search(r"\b(mission status|my missions|show missions)\b", text_l):
                return self.operator.mission_status()

            # ---- Self-learning ----
            if "learning report" in text_l or "self learning" in text_l:
                return self.operator.learning_report()
            if re.search(r"\b(favorite|fav) app\b", text_l) and any(w in text_l for w in ["learn", "remember", "note", "add"]):
                m = re.search(r"(?:favorite|fav) app\s+(?:is\s+)?(.+)", text_l)
                return self.operator.learn_fav_app(m.group(1).strip() if m else "")
            if re.search(r"\b(favorite|fav) (site|website)\b", text_l) and any(w in text_l for w in ["learn", "remember", "note", "add"]):
                m = re.search(r"(?:favorite|fav) (?:site|website)\s+(?:is\s+)?(.+)", text_l)
                return self.operator.learn_fav_site(m.group(1).strip() if m else "")

            # ---- Local AI (Ollama) ----
            if "local ai" in text_l or "offline ai" in text_l:
                return self.operator.local_ai_status()
            if "local models" in text_l or "my models" in text_l:
                return self.operator.local_ai_models()
            if re.search(r"\bask (the )?(local )?(model|ai)\b", text_l):
                m = re.search(r"ask (?:the )?(?:local )?(?:model|ai)\s+(.+)", text_l)
                return self.operator.local_ai_chat(m.group(1).strip() if m else "")

            # ---- Multi-device sync ----
            if "sync status" in text_l or "sync across devices" in text_l:
                return self.operator.sync_status()
            if "sync now" in text_l or "sync my data" in text_l:
                return self.operator.sync_now()

        # ---- Enterprise & advanced features ----
        if self.enterprise:
            # Enterprise / team
            if re.search(r"\b(add|create) (a )?user\b", text_l):
                m = re.search(r"(?:add|create) (?:a )?user\s+(\w+)(?:\s+as\s+(\w+))?", text_l)
                if m:
                    return self.enterprise.add_user(m.group(1), m.group(2) or "user")
                return "Say 'add user john as admin'."
            if "list users" in text_l or "team status" in text_l:
                return self.enterprise.team_status()
            if "audit log" in text_l or "audit trail" in text_l:
                return self.enterprise.audit_log()
            if re.search(r"\b(create|add) (a )?project\b", text_l):
                m = re.search(r"(?:create|add) (?:a )?project\s+(.+)", text_l)
                return self.enterprise.add_project(m.group(1).strip() if m else "")
            if "list projects" in text_l:
                return self.enterprise.list_projects()
            if re.search(r"\b(add|save) to (the )?knowledge base\b", text_l):
                m = re.search(r"(?:add|save) to (?:the )?knowledge base\s+(.+?)\s*\|\s*(.+)", text_l)
                if m:
                    return self.enterprise.add_kb(m.group(1).strip(), m.group(2).strip())
                return "Say 'add to knowledge base topic | content'."
            if "search knowledge base" in text_l or "search kb" in text_l:
                q = re.sub(r"\b(search knowledge base|search kb|for)\b", "", text_l).strip()
                return self.enterprise.search_kb(q)

            # Developer
            if "git status" in text_l:
                return self.enterprise.git_status()
            if re.search(r"\bgit commit\b", text_l):
                m = re.search(r"git commit\s+(.+)", text_l)
                return self.enterprise.git_commit(m.group(1).strip() if m else "")
            if "docker status" in text_l or "docker ps" in text_l:
                return self.enterprise.docker_status()
            if re.search(r"\brun (a )?(command|terminal|cmd)\b", text_l):
                m = re.search(r"(?:run|execute) (?:a )?(?:command|terminal|cmd)\s+(.+)", text_l)
                return self.enterprise.run_terminal(m.group(1).strip() if m else "")
            if re.search(r"\btest (the )?api\b", text_l):
                m = re.search(r"test (?:the )?api\s+(\w+)\s+(\S+)", text_l)
                if m:
                    return self.enterprise.api_test(m.group(1), m.group(2))
                return "Say 'test api GET https://example.com'."

            # Internet
            if re.search(r"\b(stock|stocks)\b", text_l):
                m = re.search(r"stock\s+([A-Za-z.]+)", text_l)
                return self.enterprise.stock_tracker(m.group(1).upper() if m else "AAPL")
            if re.search(r"\bcrypto\b", text_l):
                m = re.search(r"crypto:?\s*(\w+)", text_l)
                return self.enterprise.crypto_tracker(m.group(1).lower() if m else "bitcoin")
            if re.search(r"\b(jobs?|job search)\b", text_l):
                m = re.search(r"jobs? (?:for|in|as)?\s*(.+)", text_l)
                return self.enterprise.job_search(m.group(1).strip() if m else "developer")

            # Productivity
            if re.search(r"\bbuild (a )?resume\b", text_l):
                m = re.search(r"build (?:a )?resume for (.+?) (?:as|for) (.+)", text_l)
                if m:
                    return self.enterprise.resume_builder(m.group(1).strip(), m.group(2).strip())
                return "Say 'build resume for John Doe as Software Engineer'."

            # Creative
            if re.search(r"\b(generate|create) (an? )?image\b", text_l):
                m = re.search(r"(?:generate|create) (?:an? )?image(?:\s+of)?\s+(.+)", text_l)
                return self.enterprise.generate_image(m.group(1).strip() if m else "")
            if re.search(r"\bsocial (media )?post\b", text_l):
                m = re.search(r"social (?:media )?post (?:about|for)?\s*(.+)", text_l)
                return self.enterprise.social_post(m.group(1).strip() if m else "")

            # Security
            if re.search(r"\bpassword manager\b", text_l):
                return self.enterprise.password_manager()

            # Smart home
            if re.search(r"\bturn (on|off) (the )?(.+) (light|fan|ac|tv|plug|lock)\b", text_l):
                m = re.search(r"turn (on|off) (?:the )?(.+?)\s+(light|fan|ac|tv|plug|lock)", text_l)
                if m:
                    return self.enterprise.device_control(m.group(2).strip(), m.group(1))
                return "Say 'turn on the living room light'."
            if "list smart devices" in text_l or "list devices" in text_l:
                return self.enterprise.list_smart_devices()

            # System
            if "system status" in text_l or "system health" in text_l:
                return self.enterprise.system_status()
            if "backup" in text_l and any(w in text_l for w in ["create", "make", "run", "do"]):
                return self.enterprise.backup()
            if "process manager" in text_l or "top processes" in text_l:
                return self.enterprise.process_manager()
            if "index files" in text_l or "file index" in text_l:
                return self.enterprise.file_index()

        # Help
        if "help" in text_l or "what can you do" in text_l or "commands" in text_l:
            return self.help()

        # Default
        return self.default_response()

    #  MULTI-AGENT DISPATCH
    #  Route tasks to specialized agents.
    def _agent_dispatch(self, text):
        """Detect which agent should handle the task and route to it."""
        if not AGENTS_AVAILABLE:
            return None
        t = text.lower()

        # Goal tracking
        if re.search(r"(set a goal|new goal|add goal|goal to|show my goals)", t):
            return self._run_agent("goal", text)
        # Digital twin / personal profile
        if re.search(r"(i prefer|i like |i love|i enjoy|my favorite|show my profile|digital twin|about me)", t):
            return self._run_agent("digital_twin", text)
        # Finance
        if re.search(r"(expense|financ|spent|budget)", t):
            return self._run_agent("finance", text)
        # Planner - big autonomous tasks
        if re.search(r"(create a presentation|plan this|make a plan|organize|mission|project|autonomous)", t):
            return self._run_agent("planner", text)
        # Research
        if re.search(r"(research|gather info|find information|look into|investigate)", t):
            return self._run_agent("research", text)
        # Coding agent
        if re.search(r"(write code|code for|program|script that|build an app|make a function)", t):
            return self._run_agent("coding", text)
        # Browser agent
        if re.search(r"(open (chrome|edge|browser)|browse|visit site|go to website)", t):
            return self._run_agent("browser", text)
        # Vision agent
        if re.search(r"(screenshot|ocr|analyze (this )?image|read text from|screen)", t):
            return self._run_agent("vision", text)
        # Memory agent
        if re.search(r"(remember that|show what you remember|recall|list my notes|what do you remember)", t):
            return self._run_agent("memory", text)
        # Automation
        if re.search(r"(create a workflow|automate|workflow)", t):
            return self._run_agent("automation", text)
        # Security
        if re.search(r"(is this safe|security check|check this action|dangerous)", t):
            return self._run_agent("security", text)
        # Reviewer
        if re.search(r"(review this|check my|validate|proofread)", t):
            return self._run_agent("reviewer", text)
        # List agents
        if re.search(r"(what agents|list agents|your agents|show agents)", t):
            agents = ", ".join(available_agents())
            return f"🤖 I have {len(available_agents())} specialized agents: {agents}."
        return None

    def _run_agent(self, name, task):
        """Instantiate and run a specific agent."""
        try:
            agent = get_agent(name, core=self)
            if agent:
                return agent.run(task)
        except Exception:
            pass
        return None

    def help(self):
        return ("I'm FRIDAY, your AI agent. I can understand natural language and do things automatically. "
                "Try:\n"
                "- 'What time is it?' / 'What's the weather in London?'\n"
                "- 'Calculate 15 times 4'\n"
                "- 'Search for AI news on the web'\n"
                "- 'Open YouTube' / 'Open notepad'\n"
                "- 'Explain what is AI' / 'Define gravity'\n"
                "- 'Remember that my favorite color is blue'\n"
                "- 'Remind me to drink water in 30 seconds'\n"
                "- 'Tell me a joke' / 'Motivate me'\n"
                "- 'Write a python script to sort a list'\n"
                "- 'Get the latest news'\n"
                "Configure a Gemini API key in config.json for full AI-powered conversations!")

    def default_response(self):
        responses = [
            "I understand, but for full AI conversations please add a Gemini API key in config.json. "
            "Meanwhile, try asking about time, weather, calculator, or say 'help'.",
            "I'm here! Try asking for the weather, time, to open an app, search the web, or 'help' to see more.",
            "I can do a lot automatically. Try 'open notepad', 'what's the weather', or 'tell me a joke'.",
        ]
        return random.choice(responses)

    # ---------- Continuous Voice Loop ----------
    def run_voice_loop(self):
        if not SR_AVAILABLE:
            print("Speech recognition not available. Use the web/desktop app or install speechrecognition + pyaudio.")
            return
        self.speak("FRIDAY is now running. Say 'wake up friday' to activate me.")
        while True:
            try:
                text = self.listen()
                if not text:
                    continue
                if not self.is_awake:
                    if self.check_wake_word(text):
                        self.is_awake = True
                        self.speak("Yes sir, FRIDAY at your service. How can I help?")
                    continue
                else:
                    if self.check_sleep_word(text):
                        self.is_awake = False
                        self.speak("Going to sleep.")
                        continue
                    response = self.process(text)
                    self.speak(response)
            except KeyboardInterrupt:
                break
            except Exception:
                continue


if __name__ == "__main__":
    agent = FridayAgent()
    if agent.llm_available:
        print("FRIDAY Agent running with Gemini AI (full agent mode).")
    else:
        print("FRIDAY Agent running in rule-based mode (no API key). Add Gemini key in config.json for AI mode.")
    agent.run_voice_loop()
