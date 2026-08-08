"""
FRIDAY AI - Central Brain (Cortex)
=====================================
Unified orchestrator that connects every module into one intelligent system.

Responsibilities:
- Wake/sleep state machine
- Voice input/output coordination
- Command routing to the right specialist module
- Memory + Knowledge Graph management
- Autonomous mission planning and execution
- Multi-agent coordination
- Self-learning and adaptation
- Permission/consent enforcement
"""
import os
import re
import json
import time
import datetime
import threading
import subprocess
import webbrowser
import random
import queue

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

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False


class FridayCortex:
    def __init__(self, config_path="config.json"):
        self.name = "FRIDAY"
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = self._load_config(config_path)
        self.is_awake = False
        self.listening = False
        self.processing = False
        self.wake_words = self.config.get("wake_words", ["wake up friday", "hey friday", "friday"])
        self.sleep_words = self.config.get("sleep_words", ["go to sleep friday", "sleep friday"])

        # LLM
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

        # Permission system
        self.permission_enabled = self.config.get("sensitive_action_permission", True)
        self.permission_actions = set(self.config.get("permission_actions", []))
        self.pending_permission = None

        # Voice
        self.tts_engine = None
        self.recognizer = None
        self.voice_queue = queue.Queue()
        self.voice_thread = None
        self._setup_voice()

        # Module references (lazy loaded)
        self._modules = {}
        self._init_modules()

        # Mission tracker
        self.active_missions = {}
        self.mission_counter = 0

    # ==================== CONFIG ====================
    def _load_config(self, path):
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _setup_llm(self):
        if GEMINI_AVAILABLE and self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE":
            try:
                genai.configure(api_key=self.api_key)
                self.llm_available = True
            except Exception:
                self.llm_available = False

    # ==================== VOICE ====================
    def _setup_voice(self):
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 175)
                self.tts_engine.setProperty('volume', 1.0)
            except Exception:
                self.tts_engine = None
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()

    def speak(self, text):
        """Queue text for TTS output. Non-blocking."""
        if not text:
            return
        self.voice_queue.put(text)
        if self.voice_thread is None or not self.voice_thread.is_alive():
            self.voice_thread = threading.Thread(target=self._voice_worker, daemon=True)
            self.voice_thread.start()

    def _voice_worker(self):
        """Background worker that speaks queued messages."""
        while True:
            try:
                text = self.voice_queue.get(timeout=0.5)
                if text and self.tts_engine:
                    try:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    except Exception:
                        pass
            except queue.Empty:
                break
            except Exception:
                break

    def listen(self, timeout=8, phrase_limit=8):
        """Listen and convert speech to text."""
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

    # ==================== MODULES ====================
    def _init_modules(self):
        """Lazy-load all capability modules."""
        self._load_control()
        self._load_learning()
        self._load_vision()
        self._load_agents()
        self._load_intelligence()
        self._load_plus()
        self._load_advanced()
        self._load_ecosystem()
        self._load_enterprise()
        self._load_utilities()
        self._load_emotion()
        self._load_language()

    def _load_control(self):
        try:
            from friday_control import FridayControl
            self._modules['control'] = FridayControl(cortex=self)
        except Exception:
            pass

    def _load_learning(self):
        try:
            from friday_learning import FridayLearning
            self._modules['learning'] = FridayLearning(cortex=self)
        except Exception:
            pass

    def _load_vision(self):
        try:
            from friday_vision import FridayVision
            self._modules['vision'] = FridayVision(cortex=self)
        except Exception:
            pass

    def _load_agents(self):
        try:
            from friday_agents import available_agents, get_agent
            self._modules['agents'] = {'available': available_agents, 'get': get_agent}
        except Exception:
            pass

    def _load_intelligence(self):
        try:
            from friday_intelligence import FridayIntelligence
            self._modules['intelligence'] = FridayIntelligence(base_dir=self.base_dir, agent=self)
        except Exception:
            pass

    def _load_plus(self):
        try:
            from friday_plus import FridayPlus
            self._modules['plus'] = FridayPlus(base_dir=self.base_dir, agent=self)
        except Exception:
            pass

    def _load_advanced(self):
        try:
            from friday_advanced import FridayAdvanced
            self._modules['advanced'] = FridayAdvanced(base_dir=self.base_dir, config=self.config)
        except Exception:
            pass

    def _load_ecosystem(self):
        try:
            from friday_ecosystem import FridayEcosystem
            self._modules['ecosystem'] = FridayEcosystem(base_dir=self.base_dir, config=self.config)
        except Exception:
            pass

    def _load_enterprise(self):
        try:
            from friday_enterprise import FridayEnterprise
            self._modules['enterprise'] = FridayEnterprise(base_dir=self.base_dir, agent=self)
        except Exception:
            pass

    def _load_utilities(self):
        try:
            from friday_utilities import FridayUtilities
            self._modules['utilities'] = FridayUtilities(core=self)
        except Exception:
            pass

    def _load_emotion(self):
        try:
            from friday_emotion import FridayEmotion
            self._modules['emotion'] = FridayEmotion(agent=self)
        except Exception:
            pass

    def _load_language(self):
        try:
            from friday_language import FridayLanguage
            self._modules['language'] = FridayLanguage(agent=self)
        except Exception:
            pass

    def get_module(self, name):
        return self._modules.get(name)

    # ==================== MEMORY ====================
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

    # ==================== WAKE / SLEEP ====================
    def check_wake_word(self, text):
        if not text:
            return False
        return any(w in text for w in self.wake_words)

    def check_sleep_word(self, text):
        if not text:
            return False
        return any(w in text for w in self.sleep_words)

    # ==================== PERMISSIONS ====================
    def is_sensitive(self, tool_name):
        return self.permission_enabled and tool_name in self.permission_actions

    def request_permission(self, tool_name, params):
        self.pending_permission = {
            "tool": tool_name,
            "params": params,
            "requested_at": time.time()
        }
        return (f"To do that, I need your permission. "
                f"Please confirm by saying 'yes friday' or 'go ahead', "
                f"or say 'no friday' to cancel.")

    def confirm_permission(self, allow=True):
        if not self.pending_permission:
            return "There's no pending action to confirm."
        req = self.pending_permission
        self.pending_permission = None
        if not allow:
            return "Understood. I've cancelled that action."
        tool_name = req["tool"]
        params = req["params"]
        result = self._execute_tool_direct(tool_name, params)
        return result if result else "Action completed."

    def _execute_tool_direct(self, tool_name, params):
        """Execute a tool directly (for confirmed sensitive actions)."""
        control = self.get_module('control')
        if control:
            result = control.execute(tool_name, params)
            if result is not None:
                return result
        return f"Executed {tool_name}."

    # ==================== LLM ====================
    def _llm_response(self, prompt):
        if not self.llm_available:
            return None
        try:
            model = genai.GenerativeModel(self.model_name)
            resp = model.generate_content(prompt)
            return resp.text.strip()
        except Exception:
            return None

    # ==================== CORE PROCESSING ====================
    def process(self, text):
        """Main processing pipeline. Routes to the best module."""
        text = text.strip()
        if not text:
            return "I didn't catch that. Please try again."

        if self.check_sleep_word(text):
            self.is_awake = False
            return "Going to sleep. Say 'wake up friday' to wake me."

        if self.pending_permission:
            t = text.lower()
            if any(w in t for w in ["yes", "go ahead", "confirm", "ok friday", "proceed", "yeah", "approve"]):
                return self.confirm_permission(allow=True)
            if any(w in t for w in ["no", "cancel", "stop", "don't", "do not", "deny"]):
                return self.confirm_permission(allow=False)

        # Emotional response
        emotion = self.get_module('emotion')
        if emotion:
            try:
                emo = emotion.process_emotion(text)
                if emo.get("is_emotional") and emo.get("empathetic"):
                    return emo["empathetic"]
            except Exception:
                pass

        # Remember name
        m = re.search(r"my name is (\w+)", text.lower())
        if m:
            self.user_name = m.group(1)
            self.save_memory()
            return f"Nice to meet you, {self.user_name}! I'll remember that."

        # Conversation history
        self.conversation.append({"role": "user", "content": text})
        if len(self.conversation) > 50:
            self.conversation = self.conversation[-50:]

        response = None

        # 1. Computer Control (highest priority for action commands)
        response = self._route_control(text)
        if response:
            self._log_and_speak(response)
            return response

        # 2. Multi-Agent Dispatch
        response = self._route_agents(text)
        if response:
            self._log_and_speak(response)
            return response

        # 3. LLM-powered reasoning
        if self.llm_available:
            response = self._llm_process(text)
            if response:
                self._log_and_speak(response)
                return response

        # 4. Rule-based fallback
        response = self._rule_process(text)
        self._log_and_speak(response)
        return response

    def _log_and_speak(self, response):
        self.conversation.append({"role": "assistant", "content": response})
        if self.config.get("voice_enabled", True):
            self.speak(response)

    def _route_control(self, text):
        """Route to the Computer Control Agent."""
        control = self.get_module('control')
        if not control:
            return None
        return control.handle_voice_command(text)

    def _route_agents(self, text):
        """Route to the multi-agent system."""
        agents_mod = self.get_module('agents')
        if not agents_mod:
            return None
        t = text.lower()
        available = agents_mod['available']()
        get_agent = agents_mod['get']

        if re.search(r"(set a goal|new goal|add goal|goal to|show my goals)", t):
            return get_agent("goal", core=self).run(text)
        if re.search(r"(i prefer|i like |i love|i enjoy|my favorite|show my profile|digital twin|about me)", t):
            return get_agent("digital_twin", core=self).run(text)
        if re.search(r"(expense|financ|spent|budget)", t):
            return get_agent("finance", core=self).run(text)
        if re.search(r"(create a presentation|plan this|make a plan|organize|mission|project|autonomous)", t):
            return get_agent("planner", core=self).run(text)
        if re.search(r"(research|gather info|find information|look into|investigate)", t):
            return get_agent("research", core=self).run(text)
        if re.search(r"(write code|code for|program|script that|build an app|make a function)", t):
            return get_agent("coding", core=self).run(text)
        if re.search(r"(open (chrome|edge|browser)|browse|visit site|go to website)", t):
            return get_agent("browser", core=self).run(text)
        if re.search(r"(screenshot|ocr|analyze (this )?image|read text from|screen)", t):
            return get_agent("vision", core=self).run(text)
        if re.search(r"(remember that|show what you remember|recall|list my notes|what do you remember)", t):
            return get_agent("memory", core=self).run(text)
        if re.search(r"(create a workflow|automate|workflow)", t):
            return get_agent("automation", core=self).run(text)
        if re.search(r"(is this safe|security check|check this action|dangerous)", t):
            return get_agent("security", core=self).run(text)
        if re.search(r"(review this|check my|validate|proofread)", t):
            return get_agent("reviewer", core=self).run(text)
        if re.search(r"(what agents|list agents|your agents|show agents)", t):
            return f"I have {len(available)} specialized agents: {', '.join(available)}."
        return None

    def _llm_process(self, text):
        """Use LLM to decide and execute tools. Falls back to None on timeout/error."""
        try:
            system = self._build_system_prompt()
            prompt = (
                f"{system}\n\n"
                f"User: {text}\n\n"
                f"If the user asked for an action, respond with exactly:\n"
                f"TOOL:tool_name(key=value, key2=value2)\n"
                f"If the user asked a question or is chatting, respond normally as FRIDAY.\n"
                f"Response:"
            )
            model = genai.GenerativeModel(self.model_name)

            result_holder = {}
            def _call():
                try:
                    resp = model.generate_content(prompt)
                    result_holder['raw'] = resp.text.strip()
                except Exception as e:
                    result_holder['error'] = str(e)

            t = threading.Thread(target=_call, daemon=True)
            t.start()
            t.join(timeout=8)

            if not result_holder.get('raw'):
                return None

            raw = result_holder['raw']
            tool_name, params = self._extract_tool_call(raw)
            if tool_name:
                if self.is_sensitive(tool_name):
                    return self.request_permission(tool_name, params)
                result = self._execute_tool_direct(tool_name, params)
                return result if result else raw
            return raw
        except Exception:
            return None

    def _build_system_prompt(self):
        tool_desc = (
            "Available tools:\n"
            "- get_time, get_date, get_day, get_weather\n"
            "- calculate(expression), web_search(query)\n"
            "- open_website(site), open_program(app)\n"
            "- take_note(note), show_notes\n"
            "- shutdown, restart, joke, motivate\n"
            "- write_code(request), translate(text, target_language)\n"
            "- remind_me(message, seconds), remember_info(key, value)\n"
            "- screen_read, click_at(x,y), type_text(text), press_key(key)\n"
            "- install_software(name), open_file(path)\n"
            "- research(query), summarize(query)\n"
            "- mission(goal)\n"
        )
        memory_str = json.dumps(self.memory) if self.memory else "None"
        notes_str = "; ".join(self.notes[-5:]) if self.notes else "None"
        return (
            f"You are FRIDAY, a friendly, capable personal AI assistant inspired by JARVIS.\n"
            f"{tool_desc}\n"
            f"User name: {self.user_name or 'unknown'}\n"
            f"Remembered info: {memory_str}\n"
            f"Notes: {notes_str}\n"
            f"Current time: {datetime.datetime.now().strftime('%I:%M %p on %B %d, %Y')}\n"
            f"Be concise but helpful, like JARVIS."
        )

    def _extract_tool_call(self, text):
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

    def _rule_process(self, text):
        """Fallback rule-based processing."""
        text_l = text.lower().strip()

        # Greetings
        if re.search(r"\b(hi|hello|hey|good (morning|afternoon|evening))\b", text_l):
            hour = datetime.datetime.now().hour
            period = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
            return f"{period}! I am FRIDAY. How can I help?"

        if "how are you" in text_l:
            return "I'm functioning optimally. All systems running smoothly."

        # Calculator
        if any(c in text_l for c in ["+", "-", "*", "/", "x", "plus", "minus", "times", "divided", "calculate"]):
            calc = self._simple_calc(text_l)
            if calc:
                return calc

        # Time
        if "time" in text_l and any(w in text_l for w in ["what", "tell", "current", "now"]):
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
        # Date
        if "date" in text_l and any(w in text_l for w in ["what", "today", "tell", "current"]):
            return f"Today's date is {datetime.datetime.now().strftime('%B %d, %Y')}."
        # Day
        if "day" in text_l and any(w in text_l for w in ["what", "today", "which"]):
            return f"Today is {datetime.datetime.now().strftime('%A')}."

        # Weather
        if "weather" in text_l or "temperature" in text_l:
            m = re.search(r"(?:weather|temperature) (?:in|at|for) ([a-zA-Z ]+)", text_l)
            city = m.group(1).strip() if m else ""
            control = self.get_module('control')
            if control:
                res = control.execute('get_weather', {'city': city})
                if res:
                    return res

        # Web search
        if re.search(r"\b(search|google|look up|find)\b", text_l):
            query = re.sub(r"\b(search|google|look up|find|for)\b", "", text_l).strip()
            control = self.get_module('control')
            if control:
                res = control.execute('web_search', {'query': query})
                if res:
                    return res

        # Open website
        if "open" in text_l and any(w in text_l for w in ["youtube", "google", "facebook", "instagram", "twitter", "github", "website", "site"]):
            control = self.get_module('control')
            if control:
                res = control.execute('open_website', {'site': text_l})
                if res:
                    return res

        # Open program
        if "open" in text_l:
            m = re.search(r"open\s+(.+)", text_l)
            if m:
                app = m.group(1).strip()
                control = self.get_module('control')
                if control:
                    res = control.execute('open_program', {'app': app})
                    if res:
                        return res

        # Notes
        if "note" in text_l and any(w in text_l for w in ["take", "remember", "save"]):
            note = re.sub(r"\b(note that|take a note|remember|save|note|that)\b", "", text_l).strip()
            self.notes.append(note)
            self.save_memory()
            return f"Noted: {note}"
        if "notes" in text_l and any(w in text_l for w in ["show", "my", "list", "read"]):
            return "Your notes: " + "; ".join(self.notes[-15:]) if self.notes else "You have no saved notes."

        # Remind
        if "remind" in text_l:
            m = re.search(r"remind (?:me )?(?:to )?(.+)", text_l)
            msg = m.group(1).strip() if m else text_l
            m2 = re.search(r"in (\d+) (seconds?|minutes?|hours?)", text_l)
            seconds = 30
            if m2:
                num = int(m2.group(1))
                unit = m2.group(2)
                if "minute" in unit:
                    seconds = num * 60
                elif "hour" in unit:
                    seconds = num * 3600
            def _remind():
                time.sleep(seconds)
                self.speak(f"Reminder: {msg}")
                print(f"\n[REMINDER] {msg}")
            threading.Thread(target=_remind, daemon=True).start()
            return f"I'll remind you about '{msg}' in {seconds} seconds."

        # Remember info
        if "remember that" in text_l:
            parts = text_l.replace("remember that ", "").split(" is ")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                self.remember(key, val)
                return f"Got it. I'll remember that {key} is {val}."

        # Shutdown / restart
        if "shutdown" in text_l or "shut down" in text_l:
            if self.is_sensitive("shutdown"):
                return self.request_permission("shutdown", {})
            subprocess.Popen("shutdown /s /t 10", shell=True)
            return "Shutting down in 10 seconds. Say 'cancel shutdown' to cancel."
        if "restart" in text_l or "reboot" in text_l:
            if self.is_sensitive("restart"):
                return self.request_permission("restart", {})
            subprocess.Popen("shutdown /r /t 10", shell=True)
            return "Restarting in 10 seconds."

        # Joke
        if "joke" in text_l:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "Why don't scientists trust atoms? Because they make up everything!",
                "I told my computer I needed a break, and now it won't stop sending me KitKat ads.",
                "Why was the computer cold? It left its Windows open!",
                "There are only 10 types of people in the world: those who understand binary and those who don't.",
            ]
            return random.choice(jokes)

        # Motivation
        if any(w in text_l for w in ["motivate", "motivation", "inspire", "quote"]):
            quotes = [
                "The best way to predict the future is to invent it. - Alan Kay",
                "Success is not final, failure is not fatal: it is the courage to continue that counts. - Churchill",
                "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
                "It always seems impossible until it's done. - Nelson Mandela",
            ]
            return random.choice(quotes)

        # Computer Control - screen read
        if re.search(r"\b(read screen|screen text|what is on screen)\b", text_l):
            vision = self.get_module('vision')
            if vision:
                return vision.read_screen()

        # Computer Control - click
        if re.search(r"\b(click|tap) at\b", text_l):
            m = re.search(r"(?:click|tap) at\s+(\d+)\s*,\s*(\d+)", text_l)
            if m:
                control = self.get_module('control')
                if control:
                    return control.execute('click_at', {'x': m.group(1), 'y': m.group(2)})

        # Computer Control - type
        if re.search(r"\btype\s+", text_l):
            m = re.search(r"type\s+(.+)", text_l)
            if m:
                control = self.get_module('control')
                if control:
                    return control.execute('type_text', {'text': m.group(1).strip()})

        # Computer Control - press key
        if re.search(r"\bpress\s+(enter|esc|tab|space|backspace|up|down)\b", text_l):
            m = re.search(r"press\s+(\w+)", text_l)
            if m:
                control = self.get_module('control')
                if control:
                    return control.execute('press_key', {'key': m.group(1)})

        # Install software
        if "install" in text_l and "software" in text_l:
            m = re.search(r"install (?:software )?(.+)", text_l)
            if m:
                control = self.get_module('control')
                if control:
                    return control.execute('install_software', {'name': m.group(1).strip()})

        # Learning report
        if re.search(r"\b(learning report|self learning|improvement report|learning stats)\b", text_l):
            learning = self.get_module('learning')
            if learning:
                return learning.report()

        # Mission
        if "mission:" in text_l:
            goal = text.split("mission:", 1)[1].strip()
            intel = self.get_module('intelligence')
            if intel:
                return intel.run_full_mission(goal)
            return f"Mission received: {goal}. Planning phase initiated."

        # Help
        if "help" in text_l or "what can you do" in text_l or "commands" in text_l:
            return self.help_text()

        # Default
        return ("I understand, but I'm still learning that skill. "
                "Try asking about time, weather, open apps, search the web, "
                "or say 'help' to see more.")

    def _simple_calc(self, text):
        text = text.lower()
        text = text.replace("plus", "+").replace("minus", "-")
        text = text.replace("times", "*").replace("multiplied by", "*")
        text = text.replace("divided by", "/").replace("x", "*")
        text = text.replace("what is", "").replace("calculate", "").replace("?", "").strip()
        expr = re.sub(r"[^0-9+\-*/(). ]", "", text).strip()
        if not expr:
            return None
        try:
            return f"The answer is {eval(expr)}."
        except Exception:
            return None

    def help_text(self):
        return (
            "I'm FRIDAY, your AI assistant. I can understand voice commands and control your computer.\n"
            "Try:\n"
            "- 'What time is it?' / 'What's the weather in London?'\n"
            "- 'Calculate 15 times 4'\n"
            "- 'Search for AI news'\n"
            "- 'Open YouTube' / 'Open notepad'\n"
            "- 'Click at 100, 200' / 'Type hello world'\n"
            "- 'Read the screen' / 'Take a screenshot'\n"
            "- 'Install Firefox'\n"
            "- 'Remember that my favorite color is blue'\n"
            "- 'Mission: build a restaurant website'\n"
            "- 'Tell me a joke' / 'Motivate me'\n"
            "- 'Write a python script to sort a list'\n"
            "Say 'go to sleep friday' to deactivate me."
        )

    # ==================== VOICE LOOP ====================
    def run_voice_loop(self, callback=None):
        """Continuous listening loop. Runs forever."""
        if not SR_AVAILABLE:
            print("Speech recognition not available.")
            return
        self.speak("FRIDAY is online. Say 'wake up friday' to activate me.")
        while True:
            try:
                text = self.listen(timeout=8, phrase_limit=8)
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
                    if callback:
                        callback(text, response)
            except KeyboardInterrupt:
                break
            except Exception:
                continue
