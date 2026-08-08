"""
FRIDAY AI - Core Assistant Engine
JARVIS-like voice assistant that responds to "wake up friday" wake word.
"""
import re
import datetime
import webbrowser
import os
import subprocess
import json
import random
import glob

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


class FridayCore:
    def __init__(self):
        self.name = "FRIDAY"
        self.is_awake = False
        self.wake_words = ["wake up friday", "hey friday", "ok friday", "hello friday", "friday"]
        self.sleep_words = ["go to sleep friday", "sleep friday", "shut down friday", "goodbye friday"]
        self.engine = None
        self.recognizer = None
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 170)
                self.engine.setProperty('volume', 1.0)
            except Exception:
                self.engine = None
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
        self.memory = {}
        self.notes = []
        self.load_memory()

    # ---------- Memory ----------
    def load_memory(self):
        try:
            if os.path.exists("memory.json"):
                with open("memory.json", "r") as f:
                    data = json.load(f)
                    self.notes = data.get("notes", [])
                    self.memory = data.get("memory", {})
        except Exception:
            pass

    def save_memory(self):
        try:
            with open("memory.json", "w") as f:
                json.dump({"notes": self.notes, "memory": self.memory}, f)
        except Exception:
            pass

    # ---------- Text to Speech ----------
    def speak(self, text):
        """Convert text to speech."""
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass
        return text

    # ---------- Speech Recognition ----------
    def listen(self, timeout=8, phrase_limit=8):
        """Listen and convert speech to text."""
        if not SR_AVAILABLE or not self.recognizer:
            return None
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            try:
                text = self.recognizer.recognize_google(audio)
                return text.lower()
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                return None
        except Exception:
            return None

    # ---------- Wake Word Detection ----------
    def check_wake_word(self, text):
        """Returns True if the text contains a wake word."""
        if not text:
            return False
        for w in self.wake_words:
            if w in text:
                return True
        return False

    def check_sleep_word(self, text):
        """Returns True if the text contains a sleep word."""
        if not text:
            return False
        for w in self.sleep_words:
            if w in text:
                return True
        return False

    # ---------- Command Processing ----------
    def process(self, text):
        """Process a user command and return a response string."""
        text = text.lower().strip()
        if not text:
            return "I didn't catch that. Please try again."

        # Check for sleep words
        if self.check_sleep_word(text):
            self.is_awake = False
            return "Going to sleep. Say 'wake up friday' to wake me."

        # Greetings
        if re.search(r"\b(hi|hello|hey|good (morning|afternoon|evening))\b", text):
            return self.greet()

        if "how are you" in text:
            return "I'm functioning optimally. All systems are running smoothly. How can I assist you?"

        if "what is your name" in text or "who are you" in text:
            return "I am FRIDAY, your personal AI assistant, inspired by Tony Stark's JARVIS."

        # Calculator (check before time/date to avoid "what is" conflicts)
        if any(c in text for c in ["+", "-", "*", "/", "x", "plus", "minus", "times", "divided", "calculate", "what is"]):
            calc = self.calculate(text)
            if calc is not None:
                return f"The answer is {calc}."

        # Time and date
        if "time" in text and any(w in text for w in ["what", "tell", "current", "now"]):
            return self.get_time()
        if "date" in text and any(w in text for w in ["what", "today", "tell", "current"]):
            return self.get_date()
        if "day" in text and any(w in text for w in ["what", "today", "which"]):
            return self.get_day()

        # Weather
        if "weather" in text or "temperature" in text:
            return self.weather(text)

        # Web search
        if re.search(r"\b(search|google|look up|find)\b", text):
            return self.web_search(text)

        # Open website
        if "open" in text and any(w in text for w in ["youtube", "google", "facebook", "instagram", "twitter", "website", "site"]):
            return self.open_website(text)

        # Notes
        if "note" in text and ("take" in text or "remember" in text or "save" in text):
            return self.take_note(text)
        if "notes" in text and any(w in text for w in ["show", "my", "list", "read"]):
            return self.show_notes()

        # Computer control
        if "open" in text and any(w in text for w in ["notepad", "calculator", "camera", "paint", "browser", "explorer", "file"]):
            return self.open_app(text)
        if "shutdown" in text or "shut down" in text:
            return self.shutdown_computer(text)
        if "restart" in text or "reboot" in text:
            return self.restart_computer(text)

        # Explain anything
        if re.search(r"\b(explain|what is|what are|tell me about|describe)\b", text):
            return self.explain(text)

        # Open anything (generic - catches any remaining "open X")
        if re.search(r"\b(open|launch|start|run)\b", text):
            return self.open_anything(text)

        # Coding assistant
        if any(w in text for w in ["code", "python script", "write a program", "program", "function", "snippet"]):
            return self.coding_assistant(text)

        # Data analysis
        if any(w in text for w in ["analyze", "data analysis", "statistics", "analysis"]):
            return self.data_analysis(text)

        # Joke
        if "joke" in text:
            return self.tell_joke()

        # Motivation
        if any(w in text for w in ["motivate", "motivation", "inspire", "quote"]):
            return self.motivate()

        # Help
        if "help" in text or "what can you do" in text or "commands" in text:
            return self.help()

        # Default
        return self.default_response()

    # ---------- Feature Implementations ----------
    def greet(self):
        hour = datetime.datetime.now().hour
        period = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
        return f"{period}! I am FRIDAY, your personal AI assistant. How can I help you today?"

    def get_time(self):
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}."

    def get_date(self):
        now = datetime.datetime.now().strftime("%B %d, %Y")
        return f"Today's date is {now}."

    def get_day(self):
        now = datetime.datetime.now().strftime("%A")
        return f"Today is {now}."

    def weather(self, text):
        city = None
        m = re.search(r"(?:weather|temperature) (?:in|at|for) ([a-zA-Z ]+)", text)
        if m:
            city = m.group(1).strip()
        if not city:
            city = "your location"
        try:
            import requests
            if city == "your location":
                city_name = "London"
            else:
                city_name = city
            resp = requests.get(
                f"https://wttr.in/{city_name}?format=%C+%t+%h+%w",
                timeout=5
            )
            if resp.status_code == 200:
                return f"The weather in {city_name} is {resp.text.strip()}."
            return "I couldn't fetch the weather right now."
        except Exception:
            return "I couldn't fetch the weather right now. Please check your internet connection."

    def calculate(self, text):
        text = text.lower()
        text = text.replace("plus", "+").replace("minus", "-")
        text = text.replace("times", "*").replace("multiplied by", "*")
        text = text.replace("divided by", "/").replace("x", "*")
        text = text.replace("what is", "").replace("calculate", "").replace("?", "").strip()
        expr = re.sub(r"[^0-9+\-*/(). ]", "", text).strip()
        if not expr:
            return None
        try:
            result = eval(expr)
            return result
        except Exception:
            return None

    def web_search(self, text):
        query = re.sub(r"\b(search|google|look up|find|for)\b", "", text).strip()
        if not query:
            query = "FRIDAY AI"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"I've opened a web search for {query} in your browser."

    def open_website(self, text):
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "github": "https://www.github.com",
            "wikipedia": "https://www.wikipedia.org",
        }
        for name, url in sites.items():
            if name in text:
                webbrowser.open(url)
                return f"Opening {name.title()}."
        m = re.search(r"open (.+)", text)
        if m:
            site = m.group(1).strip()
            webbrowser.open(f"https://{site}")
            return f"Opening {site}."
        return "Which website would you like me to open?"

    def take_note(self, text):
        note = re.sub(r"\b(note that|take a note|remember|save|note|that)\b", "", text).strip()
        if not note:
            note = text
        self.notes.append(note)
        self.save_memory()
        return f"Noted: {note}"

    def show_notes(self):
        if not self.notes:
            return "You have no saved notes."
        return "Your notes: " + "; ".join(self.notes[-10:])

    def open_app(self, text):
        apps = {
            "notepad": "notepad",
            "calculator": "calc",
            "camera": "start microsoft.windows.camera:",
            "paint": "mspaint",
            "browser": "start chrome",
            "explorer": "explorer",
            "file": "explorer",
        }
        for name, cmd in apps.items():
            if name in text:
                try:
                    subprocess.Popen(cmd, shell=True)
                    return f"Opening {name}."
                except Exception:
                    return f"Could not open {name}."
        return "I can open notepad, calculator, camera, paint, browser, or file explorer."

    def shutdown_computer(self, text):
        if "cancel" in text:
            subprocess.Popen("shutdown /a", shell=True)
            return "Shutdown cancelled."
        subprocess.Popen("shutdown /s /t 10", shell=True)
        return "Shutting down in 10 seconds. Say 'cancel shutdown' to cancel."

    def restart_computer(self, text):
        subprocess.Popen("shutdown /r /t 10", shell=True)
        return "Restarting in 10 seconds."

    def explain(self, text):
        """Explain any topic the user asks about."""
        topic = text
        topic = re.sub(r"\b(explain|what is|what are|tell me about|describe|please|me|the|a|an|about)\b", "", topic).strip()
        topic = topic.strip(" ?")
        if not topic:
            topic = "this topic"
        try:
            import requests
            resp = requests.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic.replace(" ", "_"),
                timeout=5,
                headers={"User-Agent": "FRIDAY-AI/1.0"}
            )
            if resp.status_code == 200:
                data = resp.json()
                summary = data.get("extract", "")
                if summary:
                    return f"{topic.title()}: {summary}"
        except Exception:
            pass
        knowledge = {
            "python": "Python is a high-level, interpreted programming language known for its readability and versatile libraries. It is widely used for web development, data science, AI, and automation.",
            "ai": "Artificial Intelligence (AI) is the simulation of human intelligence in machines that are programmed to think, learn, and perform tasks that typically require human intelligence.",
            "machine learning": "Machine Learning is a subset of AI that enables systems to automatically learn and improve from experience without being explicitly programmed, using data and algorithms.",
            "weather": "Weather is the state of the atmosphere at a particular place and time, including temperature, humidity, precipitation, wind, and cloud cover.",
            "computer": "A computer is an electronic device that processes data according to a set of instructions (programs) to perform calculations, store information, and run applications.",
            "space": "Space, or outer space, is the vast region beyond Earth's atmosphere where stars, planets, galaxies, and other celestial bodies exist.",
            "earth": "Earth is the third planet from the Sun and the only known planet to harbor life. It has liquid water, a protective atmosphere, and a magnetic field.",
            "moon": "The Moon is Earth's only natural satellite, influencing tides and providing light at night.",
            "sun": "The Sun is the star at the center of our solar system, providing light and heat that sustains life on Earth through nuclear fusion.",
            "physics": "Physics is the natural science that studies matter, energy, motion, and the fundamental forces of the universe.",
            "gravity": "Gravity is a fundamental force that attracts objects with mass toward one another. It keeps planets in orbit and objects grounded on Earth.",
            "atom": "An atom is the smallest unit of ordinary matter, consisting of protons, neutrons, and electrons.",
        }
        for key, val in knowledge.items():
            if key in text:
                return val
        return (f"I searched for information about {topic}, but couldn't find a detailed explanation offline. "
                f"Try asking 'search for {topic}' to find it on the web, or ask about common topics like Python, AI, weather, space, or physics.")

    def open_anything(self, text):
        """Open any app, file, folder, website, or program the user names."""
        m = re.search(r"(?:open|launch|start|run)\s+(.+)", text)
        target = m.group(1).strip().lower() if m else text.strip().lower()
        target = re.sub(r"\b(please|the|a|an|now)\b", "", target).strip()

        common_apps = {
            "notepad": ["notepad", "notepad.exe"],
            "calculator": ["calc", "calculator"],
            "paint": ["mspaint", "paint"],
            "camera": ["start microsoft.windows.camera:"],
            "browser": ["start chrome", "start msedge"],
            "chrome": ["start chrome"],
            "edge": ["start msedge"],
            "firefox": ["start firefox"],
            "file explorer": ["explorer"],
            "explorer": ["explorer"],
            "this pc": ["explorer"],
            "word": ["start winword"],
            "excel": ["start excel"],
            "powerpoint": ["start powerpnt"],
            "spotify": ["start spotify:"],
            "vscode": ["code"],
            "visual studio code": ["code"],
            "cmd": ["start cmd"],
            "command prompt": ["start cmd"],
            "terminal": ["start cmd"],
            "task manager": ["taskmgr"],
            "control panel": ["control"],
            "settings": ["start ms-settings:"],
            "photos": ["start ms-photos:"],
            "store": ["start ms-windows-store:"],
            "mail": ["start outlook:"],
            "whatsapp": ["start whatsapp:"],
            "telegram": ["start telegram:"],
            "discord": ["start discord:"],
            "youtube": ["start https://www.youtube.com"],
            "google": ["start https://www.google.com"],
            "github": ["start https://www.github.com"],
            "gmail": ["start https://mail.google.com"],
            "linkedin": ["start https://www.linkedin.com"],
            "instagram": ["start https://www.instagram.com"],
            "twitter": ["start https://www.x.com"],
            "facebook": ["start https://www.facebook.com"],
            "wikipedia": ["start https://www.wikipedia.org"],
            "netflix": ["start https://www.netflix.com"],
            "amazon": ["start https://www.amazon.com"],
        }

        for name, cmds in common_apps.items():
            if name in target:
                for c in cmds:
                    try:
                        subprocess.Popen(c, shell=True)
                        return f"Opening {name.title()}."
                    except Exception:
                        continue
                return f"Could not open {name}."

        if re.search(r"\.(com|org|net|io|ai|gov|edu|co|in)\b", target):
            if not target.startswith("http"):
                target = "https://" + target
            webbrowser.open(target)
            return f"Opening website {target}."

        try:
            result = subprocess.run(
                f'where {target}.exe 2>nul || where {target} 2>nul',
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                exe = result.stdout.strip().split("\n")[0]
                subprocess.Popen(exe, shell=True)
                return f"Opening {target}."
        except Exception:
            pass

        common_paths = [
            os.path.expandvars(r"%ProgramFiles%\WindowsApps"),
            os.path.expandvars(r"%ProgramFiles%"),
            os.path.expandvars(r"%ProgramFiles(x86)%"),
            os.path.expandvars(r"%LocalAppData%\Programs"),
        ]
        for base in common_paths:
            if os.path.isdir(base):
                for f in glob.glob(os.path.join(base, "**", f"{target}.exe"), recursive=True):
                    subprocess.Popen(f, shell=True)
                    return f"Opening {target}."
                for d in glob.glob(os.path.join(base, "**", target), recursive=True):
                    if os.path.isdir(d):
                        os.startfile(d)
                        return f"Opening {target}."

        try:
            if os.path.exists(target):
                os.startfile(target)
                return f"Opening {target}."
        except Exception:
            pass

        return (f"I couldn't find an app called '{target}'. I can open common apps like notepad, calculator, "
                f"browser, word, excel, spotify, vscode, or websites. Try 'open whatsapp' or 'open youtube'.")

    def coding_assistant(self, text):
        if "sort" in text:
            return "Here's a Python bubble sort:\n\n"
        return ("I can help with coding. Try asking things like 'write a python script to print hello world' "
                "or 'how do I sort a list in python'.")

    def data_analysis(self, text):
        return ("I can perform data analysis. Provide a CSV file or describe the data "
                "and I'll generate statistics, charts, and insights using Python.")

    def tell_joke(self):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer I needed a break, and now it won't stop sending me KitKat ads.",
            "Why was the computer cold? It left its Windows open!",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
        ]
        return random.choice(jokes)

    def motivate(self):
        quotes = [
            "The best way to predict the future is to invent it. - Alan Kay",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
            "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
            "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
            "It always seems impossible until it's done. - Nelson Mandela",
        ]
        return random.choice(quotes)

    def default_response(self):
        responses = [
            "I understand you said that, but I'm still learning that skill. Try asking about the weather, time, web search, or 'help' to see what I can do.",
            "I'm not sure I understand. Say 'help' to see what I can do, or ask me to search the web.",
            "I'm continuously learning new capabilities. For now, try 'help' to explore what I can do.",
        ]
        return random.choice(responses)

    def help(self):
        return ("Here's what I can do:\n"
                "- Time & date: 'What time is it?'\n"
                "- Weather: 'What's the weather in London?'\n"
                "- Calculator: 'What is 15 times 4?'\n"
                "- Web search: 'Search for AI news'\n"
                "- Open websites: 'Open YouTube'\n"
                "- Open apps: 'Open notepad' or 'Open WhatsApp'\n"
                "- Explain: 'Explain what is AI' or 'What is Python?'\n"
                "- Notes: 'Remember to buy milk' / 'Show my notes'\n"
                "- Computer: 'Shutdown' / 'Restart'\n"
                "- Coding: 'Help me write python code'\n"
                "- Jokes: 'Tell me a joke'\n"
                "- Motivation: 'Motivate me'\n"
                "Say 'wake up friday' to activate me, and 'go to sleep friday' to deactivate.")

    # ---------- Continuous Listening Loop ----------
    def run_voice_loop(self):
        """Run the assistant in a loop, listening for wake word, then commands."""
        if not SR_AVAILABLE:
            return "Speech recognition not available. Please install speechrecognition and pyaudio."
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
    friday = FridayCore()
    friday.run_voice_loop()
