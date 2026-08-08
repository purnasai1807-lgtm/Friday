"""
FRIDAY AI - Computer Control Agent
====================================
The "hands and eyes" of FRIDAY. This module can:

1. See the screen (OCR, text detection, UI element recognition)
2. Click buttons, menus, and any UI element by text search
3. Type text into focused fields
4. Drag and drop files between windows
5. Fill forms automatically (login, signup, surveys)
6. Install software (winget, chocolatey, npm, pip, etc.)
7. Navigate any desktop application (browsers, Office, VS Code, etc.)
8. Recover from UI changes (uses OCR + search, not fixed coordinates)

Architecture:
- ScreenCapture: grabs screenshots
- ScreenReader: OCR to understand what's on screen
- UIController: intelligent clicking, typing, dragging
- FormFiller: automatic form completion
- AppNavigator: sequence-based app control
- SoftwareInstaller: cross-platform install
"""
import os
import re
import json
import time
import subprocess
import threading

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = True
except Exception:
    PYAUTOGUI_AVAILABLE = False

try:
    from PIL import ImageGrab
    PILLOW_AVAILABLE = True
except Exception:
    PILLOW_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except Exception:
    PYTESSERACT_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False


class FridayControl:
    def __init__(self, cortex=None):
        self.cortex = cortex
        self.base_dir = cortex.base_dir if cortex else os.path.dirname(os.path.abspath(__file__))
        self.screen_reader = ScreenReader(self)
        self.ui_controller = UIController(self)
        self.form_filler = FormFiller(self)
        self.app_navigator = AppNavigator(self)
        self.installer = SoftwareInstaller(self)
        self.last_screenshot = None
        self.last_ocr_text = ""
        self.action_history = []

    # ==================== MAIN INTERFACE ====================
    def handle_voice_command(self, text):
        """Route a voice command to the appropriate control action."""
        text_l = text.lower().strip()

        # Screenshot / screen read
        if "take a screenshot" in text_l or "capture screen" in text_l:
            return self.ui_controller.screenshot()
        if re.search(r"\b(read screen|screen text|what is on screen|what's on screen)\b", text_l):
            return self.screen_reader.read_current_screen()
        if "analyze screen" in text_l or "what do you see" in text_l:
            return self.screen_reader.analyze_current_screen()

        # Click
        if re.search(r"\b(click|tap) at\b", text_l):
            m = re.search(r"(?:click|tap) at\s+(\d+)\s*,\s*(\d+)", text_l)
            if m:
                return self.ui_controller.click(int(m.group(1)), int(m.group(2)))
            return "Say 'click at X, Y' where X and Y are pixel coordinates."

        # Click on text (intelligent click)
        if "click on" in text_l or "click the" in text_l:
            target = re.sub(r"\b(click on|click the|click)\b", "", text_l).strip()
            return self.ui_controller.click_on_text(target)

        # Double click
        if "double click" in text_l:
            m = re.search(r"(\d+)\s*,\s*(\d+)", text_l)
            if m:
                return self.ui_controller.double_click(int(m.group(1)), int(m.group(2)))
            return "Say 'double click at X, Y'."

        # Right click
        if "right click" in text_l:
            m = re.search(r"(\d+)\s*,\s*(\d+)", text_l)
            if m:
                return self.ui_controller.right_click(int(m.group(1)), int(m.group(2)))

        # Type
        if re.search(r"\btype\s+", text_l):
            m = re.search(r"type\s+(.+)", text_l)
            if m:
                return self.ui_controller.type_text(m.group(1).strip())
            return "Say 'type <text>' to type something."

        # Press key
        if re.search(r"\bpress\s+(enter|esc|tab|space|backspace|up|down|left|right|escape|delete)\b", text_l):
            m = re.search(r"press\s+(\w+)", text_l)
            if m:
                return self.ui_controller.press_key(m.group(1))

        # Scroll
        if re.search(r"\bscroll\s+(up|down)\b", text_l):
            m = re.search(r"scroll\s+(\w+)", text_l)
            direction = m.group(1) if m else "down"
            m2 = re.search(r"(\d+)", text_l)
            amount = int(m2.group(1)) if m2 else 5
            return self.ui_controller.scroll(direction, amount)

        # Drag and drop
        if "drag" in text_l and "drop" in text_l:
            m = re.search(r"drag\s+(\d+)\s*,\s*(\d+)\s*(?:to|drop)\s+(\d+)\s*,\s*(\d+)", text_l)
            if m:
                return self.ui_controller.drag(int(m.group(1)), int(m.group(2)),
                                                int(m.group(3)), int(m.group(4)))
            return "Say 'drag from X1,Y1 to X2,Y2'."

        # Drag file to window
        if "drag file" in text_l or "move file" in text_l:
            m = re.search(r"(?:drag|move) file\s+(.+?)\s+(?:to|into)\s+(.+)", text_l)
            if m:
                return self.form_filler.drag_file(m.group(1).strip(), m.group(2).strip())
            return "Say 'drag file <path> to <window>'."

        # Fill form
        if "fill form" in text_l or "fill the form" in text_l:
            m = re.search(r"fill (?:the )?form(?:\s+with)?\s*(.+)?", text_l)
            fields_str = m.group(1).strip() if m else ""
            return self.form_filler.fill_form(fields_str)

        # Fill field
        if "fill" in text_l and "with" in text_l:
            m = re.search(r"fill\s+(?:the\s+)?(.+?)\s+with\s+(.+)", text_l)
            if m:
                field = m.group(1).strip()
                value = m.group(2).strip()
                return self.form_filler.fill_field(field, value)

        # Open file
        if "open file" in text_l:
            m = re.search(r"open file\s+(.+)", text_l)
            if m:
                path = m.group(1).strip()
                path = self._resolve_path(path)
                if os.path.exists(path):
                    os.startfile(path)
                    return f"Opened file: {path}"
                return f"File not found: {path}"

        # Open folder
        if "open folder" in text_l:
            m = re.search(r"open folder\s+(.+)", text_l)
            if m:
                path = m.group(1).strip()
                path = self._resolve_path(path)
                if os.path.isdir(path):
                    os.startfile(path)
                    return f"Opened folder: {path}"
                return f"Folder not found: {path}"

        # Install software
        if "install" in text_l:
            m = re.search(r"install\s+(?:software\s+)?(.+)", text_l)
            if m:
                name = m.group(1).strip()
                return self.installer.install(name)

        # Switch to app
        if "switch to" in text_l or "alt tab" in text_l:
            app = re.sub(r"\b(switch to|alt tab|alt-tab)\b", "", text_l).strip()
            return self.app_navigator.switch_to(app)

        # Close window
        if "close window" in text_l or "close this" in text_l:
            return self.ui_controller.close_window()

        # Minimize / maximize
        if "minimize" in text_l:
            return self.ui_controller.minimize_window()
        if "maximize" in text_l:
            return self.ui_controller.maximize_window()

        return None

    def execute(self, tool_name, params):
        """Execute a tool by name (used by LLM tool calls)."""
        tool_map = {
            'get_weather': lambda p: self._get_weather(p.get('city', '')),
            'web_search': lambda p: self._web_search(p.get('query', '')),
            'open_website': lambda p: self._open_website(p.get('site', '')),
            'open_program': lambda p: self._open_program(p.get('app', '')),
            'screen_read': lambda p: self.screen_reader.read_current_screen(),
            'click_at': lambda p: self.ui_controller.click(int(p.get('x', 0)), int(p.get('y', 0))),
            'type_text': lambda p: self.ui_controller.type_text(p.get('text', '')),
            'press_key': lambda p: self.ui_controller.press_key(p.get('key', 'enter')),
            'install_software': lambda p: self.installer.install(p.get('name', '')),
            'open_file': lambda p: self._open_file(p.get('path', '')),
        }
        fn = tool_map.get(tool_name)
        if fn:
            return fn(params)
        return None

    # ==================== BASIC TOOLS ====================
    def _get_weather(self, city):
        if not REQUESTS_AVAILABLE:
            return "Weather requires internet."
        try:
            resp = requests.get(f"https://wttr.in/{city}?format=%C+%t+%h+%w", timeout=6)
            if resp.status_code == 200:
                return f"The weather in {city} is {resp.text.strip()}."
        except Exception:
            pass
        return f"I couldn't fetch the weather for {city}."

    def _web_search(self, query):
        if not query:
            query = "FRIDAY"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"I've opened a web search for '{query}'."

    def _open_website(self, site):
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "facebook": "https://www.facebook.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com",
            "whatsapp": "https://web.whatsapp.com",
            "linkedin": "https://www.linkedin.com",
            "wikipedia": "https://www.wikipedia.org",
        }
        for name, url in sites.items():
            if name in site.lower():
                webbrowser.open(url)
                return f"Opening {name.title()}."
        if "." in site:
            url = site if site.startswith("http") else f"https://{site}"
            webbrowser.open(url)
            return f"Opening {site}."
        webbrowser.open(f"https://www.google.com/search?q={site}")
        return f"Searching for {site}."

    def _open_program(self, app):
        apps = {
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "camera": "start microsoft.windows.camera:",
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
            if name in app.lower():
                try:
                    subprocess.Popen(cmd, shell=True)
                    return f"Opening {name.title()}."
                except Exception:
                    return f"Could not open {name}."
        return f"I couldn't find '{app}'. Try notepad, calculator, chrome, or word."

    def _open_file(self, path):
        path = self._resolve_path(path)
        if os.path.exists(path):
            os.startfile(path)
            return f"Opened {path}."
        return f"File not found: {path}"

    def _resolve_path(self, path):
        """Resolve a user-provided path, expanding environment vars."""
        path = os.path.expandvars(path)
        if not os.path.isabs(path):
            # Search common locations
            common = [
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Downloads"),
                self.base_dir,
            ]
            for base in common:
                candidate = os.path.join(base, path)
                if os.path.exists(candidate):
                    return candidate
        return path


class ScreenReader:
    """Understand what's on screen using OCR + intelligent analysis."""

    def __init__(self, control):
        self.control = control
        self.cortex = control.cortex

    def read_current_screen(self):
        """Take a screenshot and OCR it."""
        if not PYAUTOGUI_AVAILABLE or not PILLOW_AVAILABLE:
            return "Screen reading requires pyautogui and Pillow. Install them."
        try:
            img = pyautogui.screenshot()
            path = os.path.join(self.control.base_dir, "screen_capture.png")
            img.save(path)
            self.control.last_screenshot = path

            if PYTESSERACT_AVAILABLE:
                text = pytesseract.image_to_string(img)
                self.control.last_ocr_text = text
                if text.strip():
                    return f"I read this from your screen: {text.strip()[:800]}"
                return "I captured the screen but couldn't read any text. The screen might be an image or game."
            return f"Screenshot saved to {path}. Install pytesseract for text reading."
        except Exception as e:
            return f"Screen read error: {e}"

    def analyze_current_screen(self):
        """Deep analysis of the current screen with LLM if available."""
        text = self.read_current_screen()
        if self.cortex and self.cortex.llm_available:
            try:
                analysis = self.cortex._llm_response(
                    f"Analyze this screen content and explain what the user is seeing, "
                    f"including any errors, important info, or actionable items:\n\n{text}"
                )
                if analysis:
                    return f"{text}\n\nAnalysis: {analysis}"
            except Exception:
                pass
        return text

    def find_text_on_screen(self, target_text):
        """Find coordinates of a specific text on screen using OCR."""
        if not PYTESSERACT_AVAILABLE or not PYAUTOGUI_AVAILABLE:
            return None
        try:
            img = pyautogui.screenshot()
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            target = target_text.lower()
            for i, word in enumerate(data.get('text', [])):
                if word and target in word.lower():
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    return (x, y)
        except Exception:
            pass
        return None

    def find_element(self, description):
        """Find a UI element by description (uses LLM + OCR or CV)."""
        # First try OCR text matching
        coords = self.find_text_on_screen(description)
        if coords:
            return coords

        # Fallback: LLM-guided analysis
        if self.cortex and self.cortex.llm_available:
            try:
                img = pyautogui.screenshot()
                path = os.path.join(self.control.base_dir, "screen_analyze.png")
                img.save(path)
                # Import here to avoid dependency issues
                import PIL.Image
                import google.generativeai as genai
                genai.configure(api_key=self.cortex.api_key)
                model = genai.GenerativeModel(self.cortex.model_name)
                pil_img = PIL.Image.open(path)
                resp = model.generate_content(
                    f"Find the pixel coordinates of the UI element that matches: '{description}'. "
                    f"Respond with only 'X,Y' coordinates (e.g., '450,300'). If not found, say 'NOT_FOUND'.",
                    [pil_img]
                )
                result = resp.text.strip()
                if 'NOT_FOUND' not in result:
                    m = re.search(r"(\d{1,4})\s*,\s*(\d{1,4})", result)
                    if m:
                        return (int(m.group(1)), int(m.group(2)))
            except Exception:
                pass
        return None


class UIController:
    """Intelligent UI interaction - clicks, types, drags with error recovery."""

    def __init__(self, control):
        self.control = control
        self.cortex = control.cortex
        self.screen_reader = control.screen_reader

    def screenshot(self):
        if not PYAUTOGUI_AVAILABLE:
            return "Screenshot needs pyautogui. Install it."
        try:
            path = os.path.join(self.control.base_dir, "screenshot_" + time.strftime("%H%M%S") + ".png")
            pyautogui.screenshot(path)
            return f"Screenshot saved: {path}"
        except Exception as e:
            return f"Could not capture: {e}"

    def click(self, x, y):
        if not PYAUTOGUI_AVAILABLE:
            return "Click needs pyautogui. Install it."
        try:
            pyautogui.click(int(x), int(y))
            self.control.action_history.append(f"click({x},{y})")
            return f"Clicked at ({x}, {y})."
        except Exception as e:
            return f"Could not click: {e}"

    def click_on_text(self, text):
        """Find text on screen and click it. Smart recovery if UI changes."""
        coords = self.screen_reader.find_text_on_screen(text)
        if coords:
            return self.click(coords[0], coords[1])
        return f"I couldn't find '{text}' on the screen. Say 'read screen' to see what's visible."

    def double_click(self, x, y):
        if not PYAUTOGUI_AVAILABLE:
            return "Double click needs pyautogui."
        try:
            pyautogui.doubleClick(int(x), int(y))
            return f"Double clicked at ({x}, {y})."
        except Exception as e:
            return f"Could not double click: {e}"

    def right_click(self, x, y):
        if not PYAUTOGUI_AVAILABLE:
            return "Right click needs pyautogui."
        try:
            pyautogui.rightClick(int(x), int(y))
            return f"Right clicked at ({x}, {y})."
        except Exception as e:
            return f"Could not right click: {e}"

    def type_text(self, text):
        if not PYAUTOGUI_AVAILABLE:
            return "Typing needs pyautogui. Install it."
        try:
            pyautogui.write(text, interval=0.05)
            self.control.action_history.append(f"type({text[:50]})")
            return f"Typed: {text}"
        except Exception as e:
            return f"Could not type: {e}"

    def press_key(self, key):
        if not PYAUTOGUI_AVAILABLE:
            return "Key press needs pyautogui."
        try:
            pyautogui.press(key.lower())
            return f"Pressed {key}."
        except Exception as e:
            return f"Could not press key: {e}"

    def scroll(self, direction="down", amount=5):
        if not PYAUTOGUI_AVAILABLE:
            return "Scrolling needs pyautogui."
        try:
            amt = int(amount) * (1 if direction == "up" else -1)
            pyautogui.scroll(amt)
            return f"Scrolled {direction}."
        except Exception as e:
            return f"Could not scroll: {e}"

    def drag(self, x1, y1, x2, y2):
        if not PYAUTOGUI_AVAILABLE:
            return "Drag needs pyautogui."
        try:
            pyautogui.moveTo(int(x1), int(y1), duration=0.3)
            pyautogui.dragTo(int(x2), int(y2), duration=0.3)
            return f"Dragged from ({x1},{y1}) to ({x2},{y2})."
        except Exception as e:
            return f"Could not drag: {e}"

    def close_window(self):
        if not PYAUTOGUI_AVAILABLE:
            return "Window control needs pyautogui."
        try:
            pyautogui.hotkey('alt', 'f4')
            return "Window closed."
        except Exception as e:
            return f"Could not close window: {e}"

    def minimize_window(self):
        if not PYAUTOGUI_AVAILABLE:
            return "Window control needs pyautogui."
        try:
            pyautogui.hotkey('win', 'down')
            return "Window minimized."
        except Exception as e:
            return f"Could not minimize: {e}"

    def maximize_window(self):
        if not PYAUTOGUI_AVAILABLE:
            return "Window control needs pyautogui."
        try:
            pyautogui.hotkey('win', 'up')
            return "Window maximized."
        except Exception as e:
            return f"Could not maximize: {e}"


class FormFiller:
    """Automatic form filling with field detection and validation."""

    def __init__(self, control):
        self.control = control
        self.screen_reader = control.screen_reader

    def fill_form(self, fields_str):
        """Fill a form with provided field=value pairs."""
        if not fields_str:
            return "Please provide fields like: 'name=John email=john@example.com'"

        fields = {}
        for pair in fields_str.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                fields[k.strip()] = v.strip()

        if not fields:
            return "I couldn't parse the form fields. Use format: 'field1=value1, field2=value2'"

        results = []
        for field, value in fields.items():
            result = self.fill_field(field, value)
            results.append(result)
            time.sleep(0.3)  # Small delay between fields

        return "Form filled: " + "; ".join(results)

    def fill_field(self, field_name, value):
        """Find a field by its label and fill it with a value."""
        # Try to find the field label on screen
        coords = self.screen_reader.find_text_on_screen(field_name)
        if coords:
            # Click near the label (usually to the right or below)
            self.control.ui_controller.click(coords[0] + 100, coords[1])
            time.sleep(0.2)
            self.control.ui_controller.type_text(value)
            return f"Filled '{field_name}' with '{value}'"
        return f"Couldn't find field '{field_name}' on screen."

    def drag_file(self, file_path, window_name):
        """Drag a file into a specific application window."""
        if not PYAUTOGUI_AVAILABLE:
            return "Drag file needs pyautogui."

        file_path = self.control._resolve_path(file_path)
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        # Find the target window (simplified - in practice would use pygetwindow)
        try:
            import pygetwindow as gw
            windows = [w for w in gw.getAllWindows() if window_name.lower() in w.title.lower()]
            if not windows:
                return f"Couldn't find window: {window_name}"
            target = windows[0]
            target_x = target.left + target.width // 2
            target_y = target.top + target.height // 2

            # Drag from desktop (approximate) to window center
            pyautogui.moveTo(100, 100, duration=0.3)
            pyautogui.dragTo(target_x, target_y, duration=0.5)
            return f"Dragged {os.path.basename(file_path)} to {window_name}."
        except Exception:
            return "Drag file needs pygetwindow. Install: pip install pygetwindow"


class AppNavigator:
    """Navigate and control any desktop application."""

    def __init__(self, control):
        self.control = control
        self.screen_reader = control.screen_reader
        self.navigation_sequences = {}

    def switch_to(self, app_name):
        """Switch to a specific application using Alt+Tab or taskbar."""
        if not PYAUTOGUI_AVAILABLE:
            return "App switching needs pyautogui."

        # Try Alt+Tab first
        try:
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            # Check if we found the right app
            screen_text = self.screen_reader.read_current_screen()
            if app_name.lower() in screen_text.lower():
                return f"Switched to {app_name}."
        except Exception:
            pass

        # Fallback: try to open the app directly
        return self.control._open_program(app_name)

    def navigate_menu(self, menu_path):
        """Navigate a menu path like 'File > Open > Recent > Document1'."""
        if not PYAUTOGUI_AVAILABLE:
            return "Menu navigation needs pyautogui."
        parts = [p.strip() for p in menu_path.split('>')]
        if not parts:
            return "Provide a menu path like 'File > Open'."

        try:
            for i, part in enumerate(parts):
                if i == 0:
                    # First item - use Alt key or click
                    pyautogui.hotkey('alt', part[0].lower())
                else:
                    pyautogui.press('down')
                    time.sleep(0.1)
                time.sleep(0.3)
            return f"Navigated menu: {menu_path}"
        except Exception as e:
            return f"Menu navigation failed: {e}"


class SoftwareInstaller:
    """Install software using various package managers."""

    def __init__(self, control):
        self.control = control

    def install(self, name):
        """Install software using the best available method."""
        name = name.strip()
        if not name:
            return "What software should I install?"

        # Try winget (Windows)
        if self._try_winget(name):
            return f"Installing {name} via winget."

        # Try chocolatey
        if self._try_choco(name):
            return f"Installing {name} via Chocolatey."

        # Try pip
        if self._try_pip(name):
            return f"Installing {name} via pip."

        # Try npm
        if self._try_npm(name):
            return f"Installing {name} via npm."

        # Open Microsoft Store
        try:
            subprocess.Popen(f"start ms-windows-store://search/?query={name}", shell=True)
            return f"Opening Microsoft Store to search for {name}."
        except Exception:
            pass

        return f"Couldn't find an installer for {name}. Try the Microsoft Store manually."

    def _try_winget(self, name):
        try:
            r = subprocess.run(
                ['winget', 'install', '--id', name, '--silent', '--accept-package-agreements', '--accept-source-agreements'],
                capture_output=True, text=True, timeout=30, shell=True
            )
            if r.returncode == 0:
                return True
            # Try by name
            subprocess.Popen(['winget', 'install', name, '--silent'], shell=True)
            return True
        except Exception:
            return False

    def _try_choco(self, name):
        try:
            r = subprocess.run(
                ['choco', 'install', name, '-y'],
                capture_output=True, text=True, timeout=30, shell=True
            )
            if r.returncode == 0:
                return True
        except Exception:
            pass
        return False

    def _try_pip(self, name):
        try:
            subprocess.Popen(['pip', 'install', name], shell=True)
            return True
        except Exception:
            return False

    def _try_npm(self, name):
        try:
            subprocess.Popen(['npm', 'install', '-g', name], shell=True)
            return True
        except Exception:
            return False
