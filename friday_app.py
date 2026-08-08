"""
FRIDAY AI - Desktop Application (Pure Voice-Only, No Chat)
============================================================
A JARVIS-like desktop assistant that auto-wakes when you say "friday".
Continuous background voice listening - NO chat input, NO text box, NO buttons.
All interaction is 100% voice: speak a command, and FRIDAY responds with voice.

Uses the AI Agent engine (FridayAgent) for real conversational AI.
"""
import os
import threading
import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
from friday_agent import FridayAgent
from friday_listener import FridayListener

# Use the best available resampling filter
try:
    _RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    _RESAMPLE = Image.LANCZOS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Available GIFs in the folder (used as animated background/theme)
GIFS = [f for f in os.listdir(BASE_DIR) if f.lower().endswith(".gif")]

# Colors
BG = "#0a0e17"
PANEL = "#111827"
CARD = "#1a2332"
ACCENT = "#00d4ff"
ACCENT2 = "#00ff9d"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"


class FridayApp:
    def __init__(self):
        self.core = FridayAgent()
        self.listener = FridayListener(verbose=False)
        # Share the same core between the UI and the listener
        self.listener.core = self.core
        self.root = tk.Tk()
        self.root.title("FRIDAY AI - Voice Assistant")
        self.root.geometry("520x680")
        self.root.configure(bg=BG)
        self.root.minsize(420, 560)

        # GIF frames for animation
        self.gif_frames = []
        self.gif_photo = None
        self.setup_ui()
        self.load_gif()

        # Start continuous background voice listening (no buttons needed)
        self.listener_thread = threading.Thread(target=self.listener.run, daemon=True)
        self.listener_thread.start()

    def setup_ui(self):
        """Build the pure-voice desktop interface (no chat, no text input)."""
        # Title bar
        header = tk.Frame(self.root, bg=PANEL, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        title = tk.Label(header, text="FRIDAY", font=title_font,
                         fg=ACCENT, bg=PANEL)
        title.pack(side="left", padx=20, pady=10)

        subtitle = tk.Label(header, text="AI Voice Assistant - No Chat", 
                            fg=MUTED, bg=PANEL, font=("Segoe UI", 10))
        subtitle.pack(side="left", padx=5)

        # AI mode indicator
        self.ai_label = tk.Label(header, text="AI OFF", fg="#f87171", bg=PANEL,
                                 font=("Segoe UI", 9, "bold"))
        self.ai_label.pack(side="right", padx=5)
        if self.core.llm_ready:
            self.ai_label.config(text="AI ON", fg=ACCENT2)

        # Status indicator
        self.status_dot = tk.Label(header, text=" ● ", fg="#6b7280", bg=PANEL,
                                   font=("Segoe UI", 14))
        self.status_dot.pack(side="right", padx=20)
        self.status_label = tk.Label(header, text="Standby", fg=MUTED, bg=PANEL,
                                     font=("Segoe UI", 10))
        self.status_label.pack(side="right")

        # Main body
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # Center card - visual + listening status (NO chat/log panel)
        card = tk.Frame(body, bg=CARD)
        card.pack(fill="both", expand=True)
        card.pack_propagate(False)

        # Animated GIF / visual theme
        self.gif_label = tk.Label(card, bg=CARD)
        self.gif_label.pack(pady=30)

        # Big listening status text (pure voice)
        self.mic_label = tk.Label(card, text="● ALWAYS LISTENING\nSay 'friday' to wake me",
                                  fg=ACCENT, bg=CARD,
                                  font=("Segoe UI", 13, "bold"))
        self.mic_label.pack(fill="x", padx=15, pady=10)

        hint = tk.Label(card, text="Pure voice control - no chat.\n"
                                   "Try: 'open notepad', 'what's the weather', 'read the screen'",
                        fg=MUTED, bg=CARD, font=("Segoe UI", 10),
                        justify="center")
        hint.pack(padx=20, pady=(5, 20))

        # Capabilities list footer
        cap_title = tk.Label(card, text="VOICE CAPABILITIES", fg=ACCENT, bg=CARD,
                             font=("Segoe UI", 10, "bold"))
        cap_title.pack(pady=(5, 5))
        caps = ["🗣️ Voice Assistant", "🖥️ Computer Control", "👁️ Vision-Based AI",
                "🧠 Self-Learning Memory", "🤖 Multi-Agent System", "📋 Planner Agent",
                "🔍 Research Agent", "👨\u200d💻 Coding Agent", "🌐 Browser Agent",
                "💰 Finance Agent", "🎯 Goal Tracking", "🧬 Digital Twin",
                "🔐 Permission Control", "🌤️ Weather", "⏰ Reminders", "😂 Jokes"]
        for c in caps:
            tk.Label(card, text=c, fg=MUTED, bg=CARD,
                     font=("Segoe UI", 9)).pack(anchor="center")

        # Poll for status updates from the listener thread
        self.poll_status()

    def poll_status(self):
        """Update UI status from the shared core state."""
        try:
            if self.core.is_awake:
                self.status_dot.config(fg=ACCENT2)
                self.status_label.config(text="Awake", fg=ACCENT2)
                self.mic_label.config(text="● AWAKE\nListening for commands")
            else:
                self.status_dot.config(fg="#6b7280")
                self.status_label.config(text="Standby", fg=MUTED)
                self.mic_label.config(text="● ALWAYS LISTENING\nSay 'friday' to wake me")
        except Exception:
            pass
        self.root.after(500, self.poll_status)

    def load_gif(self):
        """Load an animated GIF for the visual theme."""
        preferred = [g for g in GIFS if "iron" in g.lower() or "matrix" in g.lower()
                     or "cyber" in g.lower() or "nft" in g.lower()]
        chosen = preferred[0] if preferred else (GIFS[0] if GIFS else None)
        if not chosen:
            self.gif_label.config(text="[FRIDAY]", fg=ACCENT, bg=CARD,
                                  font=("Segoe UI", 24, "bold"))
            return
        path = os.path.join(BASE_DIR, chosen)
        try:
            img = Image.open(path)
            target = (220, 220)
            img = img.resize(target, _RESAMPLE)
            self.gif_frames = []
            try:
                while True:
                    frame = img.copy().convert("RGBA")
                    self.gif_frames.append(frame)
                    img.seek(img.tell() + 1)
            except EOFError:
                pass
            if not self.gif_frames:
                self.gif_frames = [img.convert("RGBA")]
            self.gif_idx = 0
            self.animate_gif()
        except Exception:
            self.gif_label.config(text="[FRIDAY]", fg=ACCENT, bg=CARD,
                                  font=("Segoe UI", 24, "bold"))

    def animate_gif(self):
        """Animate the GIF frames."""
        if not self.gif_frames:
            return
        try:
            frame = self.gif_frames[self.gif_idx]
            self.gif_photo = ImageTk.PhotoImage(frame)
            self.gif_label.config(image=self.gif_photo)
            self.gif_idx = (self.gif_idx + 1) % len(self.gif_frames)
            self.root.after(80, self.animate_gif)
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FridayApp()
    app.run()
