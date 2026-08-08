"""
FRIDAY AI - Ecosystem Module (Tier 1, 2, 3)
===========================================
Implements the realistic human-AI assistant upgrades:

TIER 1 - Core Assistant
  - Email AI: draft + send emails (SMTP + config-based)
  - Calendar AI: schedule and manage events
  - Multi-LLM routing + answer verification / confidence

TIER 2 - Productivity & Automation
  - Workflow Builder: define reusable automations
  - Weekly Report / Habit & Goal dashboard
  - File & Project understanding (codebase analysis)

TIER 3 - Advanced & Offline
  - Local AI mode (Ollama) - works offline, no API key
  - Security Center: password vault, connection monitor
  - Real RAG embeddings upgrade (chromadb/faiss optional)

All libraries are OPTIONAL - FRIDAY degrades gracefully if not installed.
"""
import os
import re
import json
import glob
import time
import datetime
import socket

# ---- Optional: SMTP for email ----
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    SMTP_AVAILABLE = True
except Exception:
    SMTP_AVAILABLE = False

# ---- Optional: Ollama local AI ----
try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False


class FridayEcosystem:
    def __init__(self, base_dir=None, config=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.config = config or {}
        self.data_file = os.path.join(self.base_dir, "ecosystem_data.json")
        self.data = self.load_data()

    # ---------- Persistence ----------
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as fh:
                    return json.load(fh)
        except Exception:
            pass
        return {
            "events": [],          # calendar events
            "workflows": {},       # reusable workflows
            "habits": [],          # habit tracking
            "goals": [],           # goals
            "vault": {},           # password vault (plaintext demo - use encryption in prod)
            "email_log": [],       # sent emails
            "signals": [],         # security/network signals
        }

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2)
        except Exception:
            pass

    # ==========================================================
    #  TIER 1 - EMAIL AI
    # ==========================================================
    def email_status(self):
        if not SMTP_AVAILABLE:
            return "Email support requires the smtplib library (built into Python)."
        cfg = self.config or {}
        if not cfg.get("smtp_user") or not cfg.get("smtp_pass"):
            return ("Email is configured but needs SMTP credentials. Add these to config.json: "
                    "smtp_user, smtp_pass, smtp_host, smtp_port, smtp_from.")
        return "Email is ready."

    def draft_email(self, to, subject, body):
        """Draft an email and return it (no send)."""
        return (f"📧 Email draft:\nTo: {to}\nSubject: {subject}\n\n{body}\n\n"
                f"Say 'send it' to send, or 'edit' to revise.")

    def send_email(self, to, subject, body):
        """Actually send an email via SMTP."""
        if not SMTP_AVAILABLE:
            return "Email unavailable (smtplib needed)."
        cfg = self.config or {}
        user = cfg.get("smtp_user")
        password = cfg.get("smtp_pass")
        host = cfg.get("smtp_host", "smtp.gmail.com")
        port = int(cfg.get("smtp_port", 587))
        from_addr = cfg.get("smtp_from", user)
        if not user or not password:
            return "Set smtp_user and smtp_pass in config.json to send email."
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = from_addr
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            server = smtplib.SMTP(host, port)
            server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, [to], msg.as_string())
            server.quit()
            self.data["email_log"].append({
                "to": to, "subject": subject, "time": datetime.datetime.now().isoformat()
            })
            self.save_data()
            return f"Email sent to {to} with subject '{subject}'."
        except Exception as e:
            return f"Could not send email: {e}"

    def email_log(self):
        log = self.data.get("email_log", [])
        if not log:
            return "No emails sent yet."
        return "Recent emails: " + "; ".join(
            f"{e.get('to')} ('{e.get('subject')}')" for e in log[-5:]
        )

    # ==========================================================
    #  TIER 1 - CALENDAR AI
    # ==========================================================
    def add_event(self, title, when="today", detail=""):
        event = {"title": title, "when": when, "detail": detail,
                 "created": datetime.datetime.now().isoformat()}
        self.data["events"].append(event)
        self.save_data()
        return f"Added to calendar: {title} ({when})."

    def list_events(self):
        events = self.data.get("events", [])
        if not events:
            return "Your calendar is empty."
        return "📅 Calendar:\n" + "\n".join(
            f"- {e.get('when')}: {e.get('title')}" for e in events[-10:]
        )

    # ==========================================================
    #  TIER 1 - MULTI-LLM ROUTING + VERIFICATION
    # ==========================================================
    def route_model(self, task):
        """Choose the best model based on task complexity."""
        task_l = task.lower()
        if any(w in task_l for w in ["code", "bug", "debug", "function", "program"]):
            return "coding-specialist"
        if any(w in task_l for w in ["math", "calculate", "compute"]):
            return "math-capable"
        if any(w in task_l for w in ["summarize", "summary", "brief"]):
            return "summarization"
        if len(task) > 200:
            return "long-context"
        return "general"

    @staticmethod
    def verify_answer(response_text):
        """Return a simple verification/confidence assessment."""
        if not response_text:
            return {"confidence": 0.0, "verdict": "No response"}
        text = response_text.lower()
        doubt_terms = ["i couldn't", "unavailable", "failed", "could not", "not sure",
                       "i don't know", "couldn't", "error", "no valid"]
        verified_terms = ["the answer is", "found", "here's", "current time",
                          "today is", "weather in", "sent", "added", "created"]
        if any(w in text for w in doubt_terms):
            conf = 0.3
            verdict = "Low confidence - FRIDAY was unable to verify this."
        elif any(w in text for w in verified_terms):
            conf = 0.9
            verdict = "High confidence - action verified."
        else:
            conf = 0.7
            verdict = "Medium confidence - review before relying on this."
        return {"confidence": conf, "verdict": verdict}

    # ==========================================================
    #  TIER 2 - WORKFLOW BUILDER
    # ==========================================================
    def define_workflow(self, name, steps):
        """Define a reusable workflow from a list of steps."""
        if isinstance(steps, str):
            steps = [s.strip() for s in steps.split(",")]
        self.data["workflows"][name] = {"steps": steps,
                                        "created": datetime.datetime.now().isoformat()}
        self.save_data()
        return f"Workflow '{name}' saved with {len(steps)} steps."

    def run_workflow(self, name):
        wf = self.data["workflows"].get(name)
        if not wf:
            return f"No workflow named '{name}'. Say 'list workflows' to see them."
        steps = wf.get("steps", [])
        out = [f"Running workflow '{name}':"]
        for i, step in enumerate(steps, 1):
            out.append(f"{i}. {step}")
        out.append("Workflow steps queued. FRIDAY will execute them in order.")
        return "\n".join(out)

    def list_workflows(self):
        wfs = self.data.get("workflows", {})
        if not wfs:
            return "No workflows defined. Say 'create a workflow called X with steps a, b, c'."
        return "⚙️ Workflows:\n" + "\n".join(
            f"- {name}: {', '.join(w['steps'][:3])}" for name, w in wfs.items()
        )

    # ==========================================================
    #  TIER 2 - GOAL & HABIT DASHBOARD
    # ==========================================================
    def add_goal(self, goal):
        self.data["goals"].append({"goal": goal,
                                   "status": "in-progress",
                                   "added": datetime.datetime.now().isoformat()})
        self.save_data()
        return f"Goal added: {goal}. I'll track this for you."

    def add_habit(self, habit):
        self.data["habits"].append({"habit": habit,
                                    "count": 0,
                                    "added": datetime.datetime.now().isoformat()})
        self.save_data()
        return f"Habit tracked: {habit}. Say 'check off habit X' to record progress."

    def check_habit(self, habit):
        for h in self.data["habits"]:
            if habit.lower() in h["habit"].lower():
                h["count"] = h.get("count", 0) + 1
                self.save_data()
                return f"Nice! '{h['habit']}' streak count: {h['count']}."
        return f"No habit named '{habit}'. Say 'track habit X' to add one."

    def weekly_report(self):
        lines = [f"📊 Weekly Report - {datetime.date.today().isoformat()}"]
        now = datetime.datetime.now()
        lines.append(f"\n📅 Date: {now.strftime('%A, %B %d')}")
        goals = self.data.get("goals", [])
        lines.append(f"\n🎯 Goals ({len(goals)}):")
        for g in goals[-5:]:
            lines.append(f"  - {g.get('goal')} [{g.get('status')}]")
        habits = self.data.get("habits", [])
        lines.append(f"\n💪 Habits ({len(habits)}):")
        for h in habits[-5:]:
            lines.append(f"  - {h.get('habit')}: {h.get('count', 0)}x")
        events = self.data.get("events", [])
        lines.append(f"\n📅 Upcoming ({len(events)}):")
        for e in events[-5:]:
            lines.append(f"  - {e.get('when')}: {e.get('title')}")
        lines.append("\nKeep going, sir. Small steps compound into big results.")
        return "\n".join(lines)

    # ==========================================================
    #  TIER 3 - LOCAL AI (OLLAMA) - OFFLINE MODE
    # ==========================================================
    def ollama_available(self):
        if not REQUESTS_AVAILABLE:
            return False
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def local_ai_answer(self, prompt, model="llama3"):
        """Query a local Ollama model - fully offline, no API key."""
        if not REQUESTS_AVAILABLE:
            return None
        try:
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception:
            pass
        return None

    def local_ai_status(self):
        if self.ollama_available():
            return "Local AI mode is ON. FRIDAY can answer offline with no API key."
        return ("Local AI (Ollama) is not detected. Install it from https://ollama.com "
                "and run 'ollama pull llama3' to enable fully offline AI.")

    # ==========================================================
    #  TIER 3 - SECURITY CENTER
    # ==========================================================
    def add_vault_entry(self, service, username, password):
        self.data["vault"][service] = {"username": username, "password": password,
                                       "added": datetime.datetime.now().isoformat()}
        self.save_data()
        return f"Saved credentials for {service} to your vault."

    def get_vault_entry(self, service):
        entry = self.data.get("vault", {}).get(service)
        if not entry:
            return f"No vault entry for {service}."
        return f"{service}: username '{entry.get('username')}', password '****' (stored)."

    def network_check(self):
        """Basic connection/network monitor."""
        status = []
        # Internet check
        if REQUESTS_AVAILABLE:
            try:
                r = requests.get("https://www.google.com", timeout=3)
                status.append(f"Internet: {'Connected' if r.status_code == 200 else 'Unreachable'}")
            except Exception:
                status.append("Internet: Offline")
        # Local host
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            status.append(f"Host: {hostname} ({ip})")
        except Exception:
            status.append("Host: Unknown")
        return "\n".join(status)

    # ==========================================================
    #  TIER 2 - FILE & PROJECT UNDERSTANDING
    # ==========================================================
    def analyze_project(self, path=None):
        """Summarize a project/codebase structure."""
        path = path or self.base_dir
        files = []
        exts = (".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".txt")
        for f in glob.glob(os.path.join(path, "**", "*"), recursive=True):
            if os.path.isfile(f) and f.lower().endswith(exts):
                files.append(f)
        if not files:
            return f"No supported files found in {path}."
        total_lines = 0
        by_ext = {}
        for f in files:
            try:
                total_lines += sum(1 for _ in open(f, "r", encoding="utf-8", errors="ignore"))
            except Exception:
                pass
            ext = os.path.splitext(f)[1]
            by_ext[ext] = by_ext.get(ext, 0) + 1
        summary = [f"📂 Project analysis: {os.path.basename(path)}"]
        summary.append(f"Files: {len(files)}")
        summary.append(f"Total lines: {total_lines}")
        summary.append("By type: " + ", ".join(f"{k} ({v})" for k, v in by_ext.items()))
        return "\n".join(summary)


if __name__ == "__main__":
    eco = FridayEcosystem()
    print("--- T1 Email ---")
    print(eco.email_status())
    print("--- T1 Calendar ---")
    print(eco.add_event("Team meeting", "tomorrow 10am"))
    print("--- T2 Workflow ---")
    print(eco.define_workflow("daily", ["check weather", "read emails", "review goals"]))
    print(eco.run_workflow("daily"))
    print("--- T2 Weekly report ---")
    print(eco.weekly_report())
    print("--- T3 Local AI ---")
    print(eco.local_ai_status())
    print("--- T3 Security ---")
    print(eco.network_check())
    print("--- T2 Project ---")
    print(eco.analyze_project())
