"""
FRIDAY AI - Practical System Utilities Module
==============================================
Adds genuinely useful everyday tools that work OFFLINE (no API key needed):
  1. System health monitor (CPU, RAM, disk, battery)
  2. Unit converter (length, weight, temperature, speed)
  3. Currency converter (live rates via free API, falls back to estimate)
  4. Secure password generator
  5. QR code generator (needs qrcode lib)
  6. Pomodoro / focus timer
  7. Screenshot capture (needs Pillow)
  8. System volume control (Windows)
  9. Clipboard read/write
10. Random facts / quotes / trivia

All modules are optional imports - FRIDAY degrades gracefully.
"""
import os
import re
import json
import random
import datetime
import subprocess
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except Exception:
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False

try:
    import qrcode
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False

try:
    from PIL import ImageGrab
    SCREEN_AVAILABLE = True
except Exception:
    SCREEN_AVAILABLE = False

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except Exception:
    CLIPBOARD_AVAILABLE = False


class FridayUtilities:
    def __init__(self, core=None):
        self.core = core  # reference to FridayAgent for memory/notes
        self.pomodoro_running = False
        self.pomodoro_remaining = 0
        self.facts = [
            "Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs.",
            "Octopuses have three hearts and blue blood.",
            "A day on Venus is longer than a year on Venus.",
            "Bananas are berries, but strawberries are not.",
            "The Eiffel Tower can be 15 cm taller during hot weather.",
            "There are more possible chess games than atoms in the observable universe.",
            "The human brain uses about 20% of your body's energy.",
            "Lightning strikes the Earth about 100 times every second.",
            "The first computer bug was an actual moth found in a Harvard computer in 1947.",
            "Water can boil and freeze at the same time under the right vacuum conditions.",
        ]

    # ==========================================================
    #  1. SYSTEM HEALTH MONITOR
    # ==========================================================
    def system_status(self):
        """Return CPU, RAM, disk and battery usage."""
        if not PSUTIL_AVAILABLE:
            return "System monitoring requires the 'psutil' library. Run: pip install psutil"
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("C:\\")
            lines = ["🖥️ System Status:"]
            lines.append(f"  CPU Usage: {cpu:.0f}%")
            lines.append(f"  RAM: {mem.used/1e9:.1f} GB / {mem.total/1e9:.1f} GB ({mem.percent:.0f}%)")
            lines.append(f"  Disk (C:): {disk.used/1e9:.1f} GB / {disk.total/1e9:.1f} GB ({disk.percent:.0f}%)")
            # Battery
            if hasattr(psutil, "sensors_battery"):
                batt = psutil.sensors_battery()
                if batt:
                    lines.append(f"  Battery: {batt.percent:.0f}% " +
                                 ("(plugged in)" if batt.power_plugged else "(on battery)"))
            # Top processes
            try:
                proc = sorted(psutil.process_iter(["name", "cpu_percent"]),
                              key=lambda p: p.info["cpu_percent"] or 0, reverse=True)[:5]
                lines.append("\n  Top processes (CPU):")
                for p in proc:
                    name = p.info["name"] or "?"
                    lines.append(f"    - {name}: {p.info['cpu_percent'] or 0:.1f}%")
            except Exception:
                pass
            return "\n".join(lines)
        except Exception as e:
            return f"I couldn't read system status: {e}"

    def uptime(self):
        if not PSUTIL_AVAILABLE:
            return "System monitoring requires psutil."
        try:
            boot = psutil.boot_time()
            up = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot)
            d = up.days
            h, rem = divmod(up.seconds, 3600)
            m, _ = divmod(rem, 60)
            return f"🕒 Your system has been up for {d} days, {h} hours, and {m} minutes."
        except Exception:
            return "I couldn't read system uptime."

    # ==========================================================
    #  2. UNIT CONVERTER
    # ==========================================================
    def unit_convert(self, value_str="", from_unit="", to_unit=""):
        """Convert between common units. Supports length, weight, temp, speed."""
        try:
            value = float(re.findall(r"-?\d+(?:\.\d+)?", value_str)[0])
        except Exception:
            return "Please give me a number to convert, like 'convert 10 miles to km'."
        text = f"{value_str} {from_unit} {to_unit}".lower()

        # ---- Temperature ----
        if any(w in text for w in ["fahrenheit", "f to", "to f", "celsius", "c to", "to c",
                                   "°f", "°c", "kelvin", "k to", "to k"]):
            if "fahrenheit" in text or "°f" in text or "f to" in text or "to f" in text:
                if "celsius" in text or "°c" in text or "to c" in text or "c to" in text:
                    c = (value - 32) * 5 / 9
                    return f"🌡️ {value:.1f}°F = {c:.1f}°C."
                if "kelvin" in text or "to k" in text or "k to" in text:
                    k = (value - 32) * 5 / 9 + 273.15
                    return f"🌡️ {value:.1f}°F = {k:.2f}K."
            if "celsius" in text or "°c" in text or "c to" in text or "to c" in text:
                if "kelvin" in text or "to k" in text or "k to" in text:
                    k = value + 273.15
                    return f"🌡️ {value:.1f}°C = {k:.2f}K."
                if "fahrenheit" in text or "°f" in text or "to f" in text or "f to" in text:
                    f = value * 9 / 5 + 32
                    return f"🌡️ {value:.1f}°C = {f:.1f}°F."

        # ---- Length ----
        length = {
            "km": 1000, "kilometer": 1000, "kilometers": 1000,
            "m": 1, "meter": 1, "meters": 1,
            "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
            "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
            "mile": 1609.34, "miles": 1609.34,
            "yard": 0.9144, "yards": 0.9144,
            "feet": 0.3048, "foot": 0.3048, "ft": 0.3048,
            "inch": 0.0254, "inches": 0.0254,
        }
        fu = self._find_unit(from_unit, length)
        tu = self._find_unit(to_unit, length)
        if fu and tu:
            result = value * length[fu] / length[tu]
            return f"📏 {value} {fu} = {result:.4f} {tu}."

        # ---- Weight ----
        weight = {
            "kg": 1, "kilogram": 1, "kilograms": 1, "kilo": 1,
            "g": 0.001, "gram": 0.001, "grams": 0.001,
            "mg": 1e-6, "milligram": 1e-6, "milligrams": 1e-6,
            "lb": 0.453592, "lbs": 0.453592, "pound": 0.453592, "pounds": 0.453592,
            "ounce": 0.0283495, "ounces": 0.0283495, "oz": 0.0283495,
            "ton": 1000, "tons": 1000,
        }
        fu = self._find_unit(from_unit, weight)
        tu = self._find_unit(to_unit, weight)
        if fu and tu:
            result = value * weight[fu] / weight[tu]
            return f"⚖️ {value} {fu} = {result:.4f} {tu}."

        # ---- Speed ----
        speed = {
            "km/h": 1, "kph": 1, "kmh": 1, "km per hour": 1,
            "m/s": 3.6, "mps": 3.6, "meter per second": 3.6,
            "mph": 1.60934, "miles per hour": 1.60934,
            "knot": 1.852, "knots": 1.852,
        }
        fu = self._find_unit(from_unit, speed)
        tu = self._find_unit(to_unit, speed)
        if fu and tu:
            result = value * speed[fu] / speed[tu]
            return f"💨 {value} {fu} = {result:.4f} {tu}."

        return ("I can convert units. Try: 'convert 10 miles to km', 'convert 25 c to f', "
                "'convert 5 kg to pounds', or 'convert 60 mph to km/h'.")

    def _find_unit(self, unit, table):
        if not unit:
            return None
        unit = unit.lower().strip()
        if unit in table:
            return unit
        for k in table:
            if k in unit or unit in k:
                return k
        return None

    # ==========================================================
    #  3. CURRENCY CONVERTER
    # ==========================================================
    def currency_convert(self, value_str="", from_cur="", to_cur=""):
        """Convert currency. Uses free API; falls back to approximate rates."""
        try:
            value = float(re.findall(r"-?\d+(?:\.\d+)?", value_str)[0])
        except Exception:
            return "Please give me an amount, like 'convert 100 usd to eur'."
        currencies = {
            "usd": "USD", "eur": "EUR", "gbp": "GBP", "inr": "INR",
            "jpy": "JPY", "cad": "CAD", "aud": "AUD", "chf": "CHF",
            "cny": "CNY", "brl": "BRL", "rub": "RUB", "krw": "KRW",
            "mxn": "MXN", "sgd": "SGD", "hkd": "HKD", "nzd": "NZD",
            "sek": "SEK", "zar": "ZAR", "try": "TRY", "dollar": "USD",
            "euro": "EUR", "pound": "GBP", "rupee": "INR", "yen": "JPY",
        }
        f = from_cur.lower().strip()
        t = to_cur.lower().strip()
        f_code = None
        t_code = None
        for k, v in currencies.items():
            if k in f or f in k:
                f_code = v
                break
        for k, v in currencies.items():
            if k in t or t in k:
                t_code = v
                break
        if not f_code or not t_code:
            return "I can convert currencies like USD, EUR, GBP, INR, JPY. Try 'convert 100 usd to eur'."
        # Try live API
        if REQUESTS_AVAILABLE:
            try:
                resp = requests.get(
                    f"https://api.frankfurter.app/latest?amount={value}&from={f_code}&to={t_code}",
                    timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    result = data["rates"].get(t_code)
                    if result:
                        return f"💱 {value:.2f} {f_code} = {result:.2f} {t_code} (live rate)."
            except Exception:
                pass
        # Fallback approximate rates (relative to USD)
        approx = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.0, "JPY": 150.0,
                  "CAD": 1.36, "AUD": 1.53, "CHF": 0.88, "CNY": 7.2, "BRL": 5.0}
        if f_code not in approx or t_code not in approx:
            return "I couldn't get live rates right now. Try again later."
        result = value * approx[f_code] / approx[t_code]
        return f"💱 ~{value:.2f} {f_code} ≈ {result:.2f} {t_code} (approximate rate)."

    # ==========================================================
    #  4. PASSWORD GENERATOR
    # ==========================================================
    def password_generator(self, length=12, include_special=True):
        try:
            n = int(length)
        except Exception:
            n = 12
        n = max(6, min(64, n))
        lower = "abcdefghijkmnopqrstuvwxyz"
        upper = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        digits = "23456789"
        special = "!@#$%^&*-_=+?"
        pool = lower + upper + digits
        if include_special:
            pool += special
        # Ensure at least one of each type
        pwd = [random.choice(lower), random.choice(upper), random.choice(digits)]
        if include_special:
            pwd.append(random.choice(special))
        pwd += [random.choice(pool) for _ in range(n - len(pwd))]
        random.shuffle(pwd)
        gen = "".join(pwd)
        strength = "Strong" if (n >= 12 and include_special) else ("Medium" if n >= 8 else "Weak")
        return f"🔑 Generated a {strength} password ({n} chars): {gen}"

    # ==========================================================
    #  5. QR CODE GENERATOR
    # ==========================================================
    def qr_code(self, text="", filename="friday_qr.png"):
        if not text:
            return "What should the QR code contain? Try 'generate a QR code for https://example.com'."
        if not QR_AVAILABLE:
            return "QR code generation requires the 'qrcode' library. Run: pip install qrcode"
        try:
            qr = qrcode.make(text)
            path = os.path.join(BASE_DIR, filename)
            qr.save(path)
            return f"📱 QR code generated and saved to {path} containing: {text}"
        except Exception as e:
            return f"Could not generate QR code: {e}"

    # ==========================================================
    #  6. POMODORO / FOCUS TIMER
    # ==========================================================
    def pomodoro(self, minutes=25):
        """Start a pomodoro focus timer."""
        if self.pomodoro_running:
            return f"🍅 A focus timer is already running ({self.pomodoro_remaining//60} min left). Say 'cancel pomodoro' to stop."
        try:
            m = int(re.findall(r"\d+", str(minutes))[0])
        except Exception:
            m = 25
        self.pomodoro_running = True
        self.pomodoro_remaining = m * 60

        def _tick():
            while self.pomodoro_running and self.pomodoro_remaining > 0:
                time.sleep(1)
                self.pomodoro_remaining -= 1
            if self.pomodoro_running:
                self.pomodoro_running = False
                if self.core:
                    self.core.speak("Focus session complete. Great job! Take a short break.")
                else:
                    print("\n[POMODORO] Focus complete! Take a break.")

        threading.Thread(target=_tick, daemon=True).start()
        return f"🍅 Started a {m}-minute focus timer. I'll let you know when it's done."

    def pomodoro_status(self):
        if not self.pomodoro_running:
            return "No focus timer running. Say 'start a pomodoro for 25 minutes'."
        mm, ss = divmod(self.pomodoro_remaining, 60)
        return f"🍅 Focus timer: {mm:02d}:{ss:02d} remaining."

    def cancel_pomodoro(self):
        if not self.pomodoro_running:
            return "No focus timer running."
        self.pomodoro_running = False
        return "🍅 Focus timer cancelled."

    # ==========================================================
    #  7. SCREENSHOT
    # ==========================================================
    def screenshot(self, filename="friday_screenshot.png"):
        if not SCREEN_AVAILABLE:
            return "Screenshot requires Pillow. Run: pip install pillow"
        try:
            img = ImageGrab.grab()
            path = os.path.join(BASE_DIR, filename)
            img.save(path)
            return f"📸 I captured a screenshot and saved it to {path}."
        except Exception as e:
            return f"Could not capture screenshot: {e}"

    # ==========================================================
    #  8. VOLUME CONTROL (Windows)
    # ==========================================================
    def volume(self, action="up"):
        """Control system volume (requires Windows + nircmd or PowerShell)."""
        a = action.lower()
        try:
            if any(w in a for w in ["mute", "silence"]):
                subprocess.Popen("powershell -c nircmd mutesysvolume 1", shell=True)
                return "🔇 System muted."
            if any(w in a for w in ["unmute", "unmute"]):
                subprocess.Popen("powershell -c nircmd mutesysvolume 0", shell=True)
                return "🔊 System unmuted."
            if any(w in a for w in ["up", "increase", "raise"]):
                subprocess.Popen("powershell -c nircmd changesysvolume 2000", shell=True)
                return "🔊 Volume increased."
            if any(w in a for w in ["down", "decrease", "lower"]):
                subprocess.Popen("powershell -c nircmd changesysvolume -2000", shell=True)
                return "🔉 Volume decreased."
            if any(w in a for w in ["set", "at"]):
                m = re.search(r"(\d{1,3})", a)
                if m:
                    pct = int(m.group(1))
                    subprocess.Popen(f"powershell -c nircmd setsysvolume {int(pct*655.35)}", shell=True)
                    return f"🔊 Volume set to {pct}%."
            return "Try 'volume up', 'volume down', 'mute', or 'set volume to 50'."
        except Exception:
            return "Volume control requires 'nircmd'. Install it and add to PATH."

    # ==========================================================
    #  9. CLIPBOARD
    # ==========================================================
    def clipboard_write(self, text=""):
        if not text:
            return "What should I copy to the clipboard?"
        if not CLIPBOARD_AVAILABLE:
            return "Clipboard access requires 'pyperclip'. Run: pip install pyperclip"
        try:
            pyperclip.copy(text)
            return f"📋 Copied to clipboard: {text[:80]}"
        except Exception as e:
            return f"Could not access clipboard: {e}"

    def clipboard_read(self):
        if not CLIPBOARD_AVAILABLE:
            return "Clipboard access requires 'pyperclip'."
        try:
            content = pyperclip.paste()
            if not content:
                return "📋 The clipboard is empty."
            return f"📋 Clipboard contains: {content[:200]}"
        except Exception:
            return "Could not read the clipboard."

    # ==========================================================
    #  10. RANDOM FACTS / IDIOMS
    # ==========================================================
    def random_fact(self):
        return f"🧠 Did you know? {random.choice(self.facts)}"

    def random_number(self, low=1, high=100):
        try:
            lo = int(re.findall(r"\d+", str(low))[0])
            hi = int(re.findall(r"\d+", str(high))[0])
        except Exception:
            lo, hi = 1, 100
        if lo > hi:
            lo, hi = hi, lo
        return f"🎲 Random number between {lo} and {hi}: {random.randint(lo, hi)}."

    def flip_coin(self):
        return f"🪙 Coin landed on: {random.choice(['Heads', 'Tails'])}."

    def roll_dice(self, sides=6):
        try:
            s = int(re.findall(r"\d+", str(sides))[0])
        except Exception:
            s = 6
        return f"🎲 You rolled a {random.randint(1, s)} (d{s})."


if __name__ == "__main__":
    u = FridayUtilities()
    print(u.system_status())
    print(u.unit_convert("convert 10 miles to km", "miles", "km"))
    print(u.password_generator(16))
    print(u.random_fact())
