"""
FRIDAY AI - Multi-Language Voice Support
========================================
Adds real multi-language voice recognition and text-to-speech.

- Speech recognition per language via Google's recognizer (language codes)
- Text-to-speech in the selected language via pyttsx3 voice selection
- Auto-detection of input language (best-effort)
- Simple phrase translation fallback using optional googletrans

Works with the always-on listener AND the web app.
"""
import os
import json

# Optional libs
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
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except Exception:
    GOOGLETRANS_AVAILABLE = False


# Map of supported languages to Google speech recognition codes
LANGUAGES = {
    "english": "en-US",
    "hindi": "hi-IN",
    "spanish": "es-ES",
    "french": "fr-FR",
    "german": "de-DE",
    "italian": "it-IT",
    "portuguese": "pt-BR",
    "japanese": "ja-JP",
    "korean": "ko-KR",
    "chinese": "zh-CN",
    "russian": "ru-RU",
    "arabic": "ar-SA",
    "tamil": "ta-IN",
    "telugu": "te-IN",
    "bengali": "bn-BD",
    "marathi": "mr-IN",
    "gujarati": "gu-IN",
    "kannada": "kn-IN",
    "malayalam": "ml-IN",
    "punjabi": "pa-IN",
}


# Map of language -> pyttsx3 voice name substrings (best effort)
TTS_VOICES = {
    "english": ["english"],
    "hindi": ["hindi"],
    "spanish": ["spanish", "espanol", "es"],
    "french": ["french"],
    "german": ["german", "deutsch"],
    "italian": ["italian"],
    "portuguese": ["portuguese", "portugues"],
    "japanese": ["japanese"],
    "korean": ["korean"],
    "chinese": ["chinese", "mandarin"],
    "russian": ["russian"],
    "arabic": ["arabic"],
    "tamil": ["tamil"],
    "telugu": ["telugu"],
    "bengali": ["bengali"],
    "marathi": ["marathi"],
    "gujarati": ["gujarati"],
    "kannada": ["kannada"],
    "malayalam": ["malayalam"],
    "punjabi": ["punjabi"],
}


class FridayLanguage:
    def __init__(self, agent=None):
        self.agent = agent
        self.lang = "english"
        self._load_config()

    def _load_config(self):
        cfg = {}
        if self.agent and getattr(self.agent, "config", None):
            cfg = self.agent.config
        elif os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as fh:
                    cfg = json.load(fh)
            except Exception:
                pass
        self.lang = str(cfg.get("language", "english")).lower()
        if self.lang not in LANGUAGES:
            self.lang = "english"

    @property
    def code(self):
        return LANGUAGES.get(self.lang, "en-US")

    def set_language(self, lang):
        """Set the active language by name."""
        lang = lang.lower().strip()
        if lang in LANGUAGES:
            self.lang = lang
            if self.agent and hasattr(self.agent, "config") and hasattr(self.agent, "save_config"):
                self.agent.config["language"] = lang
                self.agent.save_config()
            return f"Language set to {lang.title()}. I am now listening for {lang.title()}."
        return ("Language '" + lang + "' not supported. Available: "
                + ", ".join(sorted(LANGUAGES.keys())))

    def list_languages(self):
        return "Supported languages: " + ", ".join(sorted(LANGUAGES.keys()))

    # ---------- Speech Recognition in selected language ----------
    def listen(self, timeout=8, phrase_limit=8):
        if not SR_AVAILABLE:
            return None
        try:
            import speech_recognition as sr
            rec = sr.Recognizer()
            with sr.Microphone() as source:
                rec.adjust_for_ambient_noise(source, duration=0.5)
                audio = rec.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            try:
                return rec.recognize_google(audio, language=self.code).lower()
            except Exception:
                return None
        except Exception:
            return None

    # ---------- Text-to-Speech in selected language ----------
    def _get_tts_engine(self):
        if not TTS_AVAILABLE:
            return None
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 170)
            try:
                voices = engine.getProperty("voices")
                for v in voices:
                    vname = (v.name or "").lower()
                    for sub in TTS_VOICES.get(self.lang, []):
                        if sub in vname:
                            engine.setProperty("voice", v.id)
                            return engine
            except Exception:
                pass
            return engine
        except Exception:
            return None

    def speak(self, text):
        engine = self._get_tts_engine()
        if engine:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass
            return text
        return text

    # ---------- Translation ----------
    def translate(self, text, target="english"):
        target = target.lower().strip()
        if target not in LANGUAGES:
            target = "english"
        if not GOOGLETRANS_AVAILABLE:
            return "Translation needs googletrans. Run: pip install googletrans==4.0.0-rc1"
        try:
            tr = Translator()
            dest_codes = {
                "english": "en", "hindi": "hi", "spanish": "es", "french": "fr",
                "german": "de", "italian": "it", "portuguese": "pt", "japanese": "ja",
                "korean": "ko", "chinese": "zh-cn", "russian": "ru", "arabic": "ar",
                "tamil": "ta", "telugu": "te", "bengali": "bn", "marathi": "mr",
                "gujarati": "gu", "kannada": "kn", "malayalam": "ml", "punjabi": "pa",
            }
            dest = dest_codes.get(target, "en")
            result = tr.translate(text, dest=dest)
            return result.text
        except Exception as e:
            return "Translation failed: " + str(e)

    # ---------- Detect language ----------
    def detect(self, text):
        if not GOOGLETRANS_AVAILABLE:
            return "english"
        try:
            tr = Translator()
            detected = tr.detect(text)
            code = detected.lang
            for name, gcode in LANGUAGES.items():
                if gcode.startswith(code) or code.startswith(gcode.split("-")[0]):
                    return name
            return "english"
        except Exception:
            return "english"

    def help(self):
        return ("Language features:\n"
                "- 'set language to hindi/spanish/french/...'\n"
                "- 'list languages'\n"
                "- 'translate <text> to <language>'\n"
                "- 'what languages do you support?'")
