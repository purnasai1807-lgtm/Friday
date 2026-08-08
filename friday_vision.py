"""
FRIDAY AI - Vision-Based Desktop AI
======================================
The "eyes" of FRIDAY. This module can:

1. Read anything on screen (OCR + LLM analysis)
2. Detect errors in code or documents
3. Explain charts and graphs
4. Understand games and apps
5. Read PDFs without opening them
6. Help during programming (code review from screen)
7. Analyze error messages
8. Read and summarize documents from screen captures

Architecture:
- ScreenCapture: high-quality screenshot with region selection
- OCRReader: extract text from screen using Tesseract
- VisionAnalyzer: use LLM vision to understand screen content
- ErrorDetector: identify errors in code, docs, and UI
- DocumentReader: read PDFs, DOCX, images without opening
- CodeAssistant: analyze code on screen, suggest fixes
"""
import os
import re
import json
import time
import datetime
import base64

try:
    from PIL import ImageGrab, Image
    PILLOW_AVAILABLE = True
except Exception:
    PILLOW_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except Exception:
    PYTESSERACT_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception:
    PYAUTOGUI_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False


class FridayVision:
    def __init__(self, cortex=None):
        self.cortex = cortex
        self.base_dir = cortex.base_dir if cortex else os.path.dirname(os.path.abspath(__file__))
        self.cache_dir = os.path.join(self.base_dir, "vision_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.last_analysis = None

    # ==================== SCREEN CAPTURE ====================
    def capture_screen(self, region=None):
        """Capture the full screen or a region."""
        if not PYAUTOGUI_AVAILABLE or not PILLOW_AVAILABLE:
            return None, "Screen capture requires pyautogui and Pillow."
        try:
            if region and len(region) == 4:
                img = pyautogui.screenshot(region=region)
            else:
                img = pyautogui.screenshot()
            path = os.path.join(self.cache_dir, f"screen_{int(time.time())}.png")
            img.save(path)
            return path, "Screenshot captured."
        except Exception as e:
            return None, f"Capture failed: {e}"

    def capture_window(self, title_fragment):
        """Capture a specific window (requires pygetwindow)."""
        try:
            import pygetwindow as gw
            windows = [w for w in gw.getAllWindows() if title_fragment.lower() in w.title.lower()]
            if not windows:
                return None, f"Window containing '{title_fragment}' not found."
            win = windows[0]
            if win.isMinimized:
                win.restore()
            region = (win.left, win.top, win.width, win.height)
            time.sleep(0.3)
            return self.capture_screen(region=region)
        except Exception as e:
            return None, f"Window capture failed: {e}"

    # ==================== OCR ====================
    def read_text(self, image_path=None):
        """Extract text from an image or the current screen."""
        if not PYTESSERACT_AVAILABLE:
            return "OCR requires pytesseract. Install: pip install pytesseract"
        try:
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
            else:
                if not PYAUTOGUI_AVAILABLE:
                    return "Need pyautogui for screen capture."
                img = pyautogui.screenshot()
            text = pytesseract.image_to_string(img)
            return text.strip() if text.strip() else "No text detected on screen."
        except Exception as e:
            return f"OCR failed: {e}"

    def read_screen_structured(self):
        """Read screen text with bounding box data for structured understanding."""
        if not PYTESSERACT_AVAILABLE or not PYAUTOGUI_AVAILABLE:
            return []
        try:
            img = pyautogui.screenshot()
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            words = []
            for i, word in enumerate(data.get('text', [])):
                if word.strip():
                    words.append({
                        "text": word,
                        "x": data['left'][i],
                        "y": data['top'][i],
                        "w": data['width'][i],
                        "h": data['height'][i],
                        "conf": data['conf'][i],
                    })
            return words
        except Exception:
            return []

    # ==================== SCREEN ANALYSIS ====================
    def read_screen(self):
        """Read and return what's on the current screen."""
        path, msg = self.capture_screen()
        if not path:
            return msg
        text = self.read_text(path)
        return text

    def analyze_current_screen(self):
        """Deep analysis of the current screen using LLM vision."""
        path, msg = self.capture_screen()
        if not path:
            return msg

        # Try LLM vision analysis
        if self.cortex and self.cortex.llm_available:
            try:
                import PIL.Image
                import google.generativeai as genai
                genai.configure(api_key=self.cortex.api_key)
                model = genai.GenerativeModel(self.cortex.model_name)
                img = PIL.Image.open(path)
                prompt = (
                    "Analyze this screenshot in detail. Describe:\n"
                    "1. What application is open\n"
                    "2. What content is visible\n"
                    "3. Any errors, warnings, or important info\n"
                    "4. Actionable items the user might want to do\n"
                    "Be concise and specific."
                )
                resp = model.generate_content([prompt, img])
                analysis = resp.text.strip()
                self.last_analysis = {"path": path, "analysis": analysis, "timestamp": datetime.datetime.now().isoformat()}
                return f"Screen analysis:\n{analysis}"
            except Exception:
                pass

        # Fallback: OCR only
        text = self.read_text(path)
        return f"Screen content:\n{text[:1000]}"

    def explain_error(self):
        """Detect and explain errors on screen."""
        words = self.read_screen_structured()
        error_texts = []
        for w in words:
            t = w['text'].lower()
            if any(e in t for e in ['error', 'exception', 'failed', 'warning', 'traceback', 'undefined', 'null', 'bug']):
                error_texts.append(w['text'])

        if not error_texts:
            return "I don't see any obvious errors on the screen. Try 'analyze screen' for a full analysis."

        error_block = " ".join(error_texts[:20])

        # Try LLM analysis
        if self.cortex and self.cortex.llm_available:
            try:
                path, _ = self.capture_screen()
                if path:
                    import PIL.Image
                    import google.generativeai as genai
                    genai.configure(api_key=self.cortex.api_key)
                    model = genai.GenerativeModel(self.cortex.model_name)
                    img = PIL.Image.open(path)
                    resp = model.generate_content(
                        f"This screen shows an error. Explain what the error is and how to fix it:\n{error_block}",
                        [img]
                    )
                    return f"Error detected: {error_block}\n\nAnalysis: {resp.text.strip()}"
            except Exception:
                pass

        return f"Possible errors detected: {error_block}"

    def explain_chart(self):
        """Analyze and explain a chart or graph on screen."""
        path, msg = self.capture_screen()
        if not path:
            return msg

        if self.cortex and self.cortex.llm_available:
            try:
                import PIL.Image
                import google.generativeai as genai
                genai.configure(api_key=self.cortex.api_key)
                model = genai.GenerativeModel(self.cortex.model_name)
                img = PIL.Image.open(path)
                resp = model.generate_content(
                    "This is a chart or graph. Describe what type of chart it is, "
                    "what data it shows, and what insights can be drawn from it. "
                    "Be specific about axes, trends, and values.",
                    [img]
                )
                return f"Chart analysis: {resp.text.strip()}"
            except Exception:
                pass
        return "I captured the screen. Configure an AI key for chart analysis."

    def read_pdf(self, path):
        """Read a PDF file and summarize it without opening."""
        if not PDF_AVAILABLE:
            return "PDF reading requires PyPDF2. Install: pip install PyPDF2"
        if not os.path.exists(path):
            return f"File not found: {path}"
        try:
            reader = PdfReader(path)
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
            if not text.strip():
                return "Could not extract text from this PDF. It might be scanned."
            if self.cortex and self.cortex.llm_available:
                summary = self.cortex._llm_response(
                    f"Summarize this document in 3-5 key points:\n\n{text[:4000]}"
                )
                if summary:
                    return f"PDF Summary ({os.path.basename(path)}):\n{summary}"
            return text[:1500]
        except Exception as e:
            return f"PDF read error: {e}"

    def read_document(self, path):
        """Read any document (PDF, DOCX, TXT, MD) and summarize."""
        if not os.path.exists(path):
            return f"File not found: {path}"

        ext = os.path.splitext(path)[1].lower()
        text = ""

        try:
            if ext == ".pdf" and PDF_AVAILABLE:
                reader = PdfReader(path)
                text = "\n".join(p.extract_text() or "" for p in reader.pages)
            elif ext in (".docx", ".doc") and DOCX_AVAILABLE:
                doc = docx.Document(path)
                text = "\n".join(p.text for p in doc.paragraphs)
            elif ext in (".txt", ".md", ".csv", ".json"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            else:
                return f"Unsupported file type: {ext}"
        except Exception as e:
            return f"Error reading {path}: {e}"

        if not text.strip():
            return "No text content found in this file."

        if self.cortex and self.cortex.llm_available:
            summary = self.cortex._llm_response(
                f"Summarize this document in 3-5 clear bullet points:\n\n{text[:4000]}"
            )
            if summary:
                return f"{os.path.basename(path)}:\n{summary}"

        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 20]
        return "\n".join(lines[:6])[:1500]

    def analyze_code_on_screen(self):
        """Analyze code visible on screen for bugs and improvements."""
        path, msg = self.capture_screen()
        if not path:
            return msg

        words = self.read_screen_structured()
        code_text = " ".join(w['text'] for w in words)

        if self.cortex and self.cortex.llm_available:
            try:
                import PIL.Image
                import google.generativeai as genai
                genai.configure(api_key=self.cortex.api_key)
                model = genai.GenerativeModel(self.cortex.model_name)
                img = PIL.Image.open(path)
                resp = model.generate_content(
                    f"Review this code visible on screen. Identify bugs, improvements, and best practices:\n{code_text}",
                    [img]
                )
                return f"Code review: {resp.text.strip()}"
            except Exception:
                pass
        return f"Code detected: {code_text[:500]}"

    def describe_image(self, path=None):
        """Describe any image in detail."""
        if path is None:
            path, _ = self.capture_screen()
            if not path:
                return "No image available."

        if self.cortex and self.cortex.llm_available:
            try:
                import PIL.Image
                import google.generativeai as genai
                genai.configure(api_key=self.cortex.api_key)
                model = genai.GenerativeModel(self.cortex.model_name)
                img = PIL.Image.open(path)
                resp = model.generate_content(
                    "Describe this image in detail. What do you see?",
                    [img]
                )
                return resp.text.strip()
            except Exception:
                pass
        return "Image captured. Configure an AI key for detailed analysis."

    def find_element_by_vision(self, description):
        """Use LLM vision to find UI elements by description."""
        path, msg = self.capture_screen()
        if not path:
            return None

        if self.cortex and self.cortex.llm_available:
            try:
                import PIL.Image
                import google.generativeai as genai
                genai.configure(api_key=self.cortex.api_key)
                model = genai.GenerativeModel(self.cortex.model_name)
                img = PIL.Image.open(path)
                resp = model.generate_content(
                    f"Find the pixel coordinates (center) of the UI element: '{description}'. "
                    f"Respond with only 'X,Y' (e.g., '450,300'). If not found, say 'NOT_FOUND'.",
                    [img]
                )
                result = resp.text.strip()
                if 'NOT_FOUND' not in result:
                    m = re.search(r"(\d{1,4})\s*,\s*(\d{1,4})", result)
                    if m:
                        return (int(m.group(1)), int(m.group(2)))
            except Exception:
                pass
        return None
