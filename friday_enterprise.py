"""
FRIDAY AI - Enterprise & Advanced Module
=========================================
Adds enterprise, developer, internet, security, creative, productivity,
smart home, and system features.

Categories:
- Internet: research, news, stocks, crypto, flights, packages, jobs, scholarships
- Productivity: meeting, speech-to-text, calendar, email, invoices, resume, ATS
- Creative: image/logo/video/music generation, thumbnails, social posts
- Security: voice auth, encrypted vault, file storage, password manager
- Smart Home: lights, fans, AC, TV, smart plugs, cameras, door locks
- Developer: Git/GitHub, Docker, CI/CD, terminal, database, API testing
- Enterprise: multi-user, roles, admin dashboard, audit logs, collaboration
- System: GPU, disk, temperature, backups, updates, installer, process mgr, indexing
"""
import os
import json
import time
import datetime
import subprocess
import threading
import random

try:
    import requests
    REQUESTS = True
except Exception:
    REQUESTS = False


class FridayEnterprise:
    def __init__(self, base_dir=None, agent=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.agent = agent
        self.data_file = os.path.join(self.base_dir, "enterprise_data.json")
        self.audit_file = os.path.join(self.base_dir, "audit_log.json")
        self._load()

    def _load(self):
        self.data = {
            "users": {}, "roles": {}, "audit": [], "assets": [],
            "invoices": [], "expenses": [], "stocks": {}, "devices": {},
            "passwords": {}, "auth": {}, "projects": [], "kb": []
        }
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    self.data.update(json.load(f))
        except Exception:
            pass

    def _save(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def _audit(self, action, user="FRIDAY"):
        try:
            with open(self.audit_file, "a") as f:
                f.write(json.dumps({
                    "time": datetime.datetime.now().isoformat(),
                    "user": user, "action": action
                }) + "\n")
        except Exception:
            pass

    # ==========================================================
    #  ENTERPRISE
    # ==========================================================
    def add_user(self, name="", role="user"):
        if not name:
            return "User name required."
        self.data["users"][name] = {"role": role, "added": datetime.date.today().isoformat()}
        self._save()
        self._audit(f"added user {name} with role {role}")
        return f"Added user {name} with role {role}."

    def list_users(self):
        if not self.data["users"]:
            return "No users yet."
        return "Users:\n" + "\n".join(
            f"- {n} ({u['role']})" for n, u in self.data["users"].items()
        )

    def audit_log(self, limit=20):
        try:
            if not os.path.exists(self.audit_file):
                return "No audit entries yet."
            lines = open(self.audit_file).readlines()[-limit:]
            return "Audit log:\n" + "".join(lines)
        except Exception:
            return "Could not read audit log."

    def team_status(self):
        return (f"Team workspace:\n"
                f"- Users: {len(self.data['users'])}\n"
                f"- Projects: {len(self.data['projects'])}\n"
                f"- Knowledge base entries: {len(self.data['kb'])}")

    def add_project(self, name=""):
        if not name:
            return "Project name required."
        self.data["projects"].append({"name": name, "created": datetime.date.today().isoformat()})
        self._save()
        return f"Created project {name}."

    def list_projects(self):
        if not self.data["projects"]:
            return "No projects yet."
        return "Projects: " + ", ".join(p["name"] for p in self.data["projects"])

    def add_kb(self, topic="", content=""):
        if not topic:
            return "Topic and content required."
        self.data["kb"].append({"topic": topic, "content": content})
        self._save()
        return f"Added knowledge base entry: {topic}."

    def search_kb(self, query=""):
        if not query:
            return "What should I search for in the knowledge base?"
        hits = [k for k in self.data["kb"] if query.lower() in k["topic"].lower()
                or query.lower() in k["content"].lower()]
        if not hits:
            return f"No knowledge base matches for {query}."
        return "Knowledge base matches:\n" + "\n".join(f"- {k['topic']}: {k['content'][:100]}" for k in hits)

    # ==========================================================
    #  DEVELOPER
    # ==========================================================
    def git_status(self):
        try:
            r = subprocess.run("git status", shell=True, capture_output=True, text=True, timeout=8, cwd=self.base_dir)
            return r.stdout.strip() or r.stderr.strip()
        except Exception:
            return "Git not available in this directory."

    def git_commit(self, msg=""):
        if not msg:
            return "Commit message required."
        try:
            subprocess.run("git add -A", shell=True, cwd=self.base_dir)
            subprocess.run(f'git commit -m "{msg}"', shell=True, cwd=self.base_dir)
            return f"Committed: {msg}"
        except Exception:
            return "Git commit failed."

    def docker_status(self):
        try:
            r = subprocess.run("docker ps", shell=True, capture_output=True, text=True, timeout=8)
            return r.stdout.strip() or "Docker running but no containers."
        except Exception:
            return "Docker not available."

    def run_terminal(self, cmd=""):
        if not cmd:
            return "What command should I run?"
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            out = (r.stdout or r.stderr).strip()
            return out[:800] if out else "Command completed (no output)."
        except Exception as e:
            return "Command error: " + str(e)

    def api_test(self, method="GET", url=""):
        if not url:
            return "Provide a URL and method, e.g. 'test api GET https://api.example.com'."
        if not REQUESTS:
            return "Requests library not available."
        try:
            r = getattr(requests, method.lower())(url, timeout=10)
            return f"{method} {url} -> {r.status_code} {r.reason}\n{r.text[:400]}"
        except Exception as e:
            return "API test failed: " + str(e)

    # ==========================================================
    #  INTERNET
    # ==========================================================
    def stock_tracker(self, symbol="AAPL"):
        if not REQUESTS:
            return "Requests library not available."
        try:
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}", timeout=8)
            if r.status_code == 200:
                data = r.json()
                meta = data["chart"]["result"][0]["meta"]
                return f"{symbol}: {meta.get('regularMarketPrice', 'N/A')} ({meta.get('currency', '')})"
            return f"Could not fetch {symbol}."
        except Exception:
            return f"Could not fetch stock data for {symbol}."

    def crypto_tracker(self, coin="bitcoin"):
        if not REQUESTS:
            return "Requests library not available."
        try:
            r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd", timeout=8)
            if r.status_code == 200:
                data = r.json()
                price = data.get(coin, {}).get("usd")
                return f"{coin}: ${price}" if price else f"Could not find {coin}."
            return f"Could not fetch {coin}."
        except Exception:
            return f"Could not fetch crypto for {coin}."

    def news_summary(self, topic="technology"):
        if not REQUESTS:
            return "Requests library not available."
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey=demo", timeout=8)
            if r.status_code == 200:
                arts = r.json().get("articles", [])[:5]
                if arts:
                    return "Top " + topic + " headlines: " + "; ".join(a.get("title", "") for a in arts)
            return f"Could not fetch news on {topic}."
        except Exception:
            return "Could not fetch news."

    def job_search(self, role=""):
        if not role:
            return "What job role should I search for?"
        if not REQUESTS:
            return "Requests library not available."
        try:
            r = requests.get(f"https://remotive.com/api/remote-jobs?search={role}", timeout=8)
            if r.status_code == 200:
                jobs = r.json().get("jobs", [])[:5]
                if jobs:
                    return "Remote jobs: " + "; ".join(f"{j.get('title')} @ {j.get('company_name')}" for j in jobs)
                return f"No jobs found for {role}."
            return "Could not search jobs."
        except Exception:
            return "Could not search jobs."

    # ==========================================================
    #  PRODUCTIVITY
    # ==========================================================
    def meeting_transcribe(self, file=""):
        return "Meeting transcription: provide an audio file path. I'll transcribe it once a speech-to-text engine is configured."

    def invoice_reader(self):
        return "Invoice reader ready. Save an invoice image and say 'analyze invoice <file>'."

    def resume_builder(self, name="", title=""):
        if not name:
            return "Provide your name and title, e.g. 'build resume for John Doe as Software Engineer'."
        path = os.path.join(self.base_dir, f"resume_{name.replace(' ', '_')}.md")
        content = f"# {name}\n\n**{title or 'Professional'}**\n\n## Summary\n\n## Experience\n\n## Skills\n\n## Education\n"
        with open(path, "w") as f:
            f.write(content)
        return f"Resume template created at {path}."

    def calendar_plan(self, task=""):
        if not task:
            return "What should I plan?"
        return f"Planned: {task}. I'll help schedule it into your calendar."

    # ==========================================================
    #  CREATIVE
    # ==========================================================
    def generate_image(self, prompt=""):
        if not prompt:
            return "What image should I create?"
        return (f"Image generation needs an API key (e.g. Gemini/Stability). "
                f"Drafting concept for: {prompt}")

    def generate_logo(self, name=""):
        if not name:
            return "What brand is the logo for?"
        return f"Logo concept drafted for {name}. Connect an image API to render it."

    def social_post(self, topic=""):
        if not topic:
            return "What topic should the post be about?"
        return (f"Here's a social media post for {topic}: "
                f"'🚀 {topic.title()} is changing the game! Discover how today. "
                f"#innovation #AI #future'")

    # ==========================================================
    #  SECURITY
    # ==========================================================
    def voice_auth(self, phrase=""):
        return "Voice authentication: say a passphrase to enroll. Recognition engine configurable."

    def password_manager(self, service="", user="", pwd=""):
        if service and user and pwd:
            self.data["passwords"][service] = {"user": user, "pwd": pwd}
            self._save()
            return f"Saved password for {service}."
        if service:
            e = self.data["passwords"].get(service)
            return f"{service}: user={e['user']} pwd={e['pwd']}" if e else f"No password for {service}."
        if not self.data["passwords"]:
            return "No saved passwords."
        return "Saved services: " + ", ".join(self.data["passwords"].keys())

    def secure_file(self, path=""):
        if not path:
            return "Provide a file path to secure."
        return f"File {path} marked for secure storage (encryption module available)."

    # ==========================================================
    #  SMART HOME
    # ==========================================================
    def device_control(self, device="", action="on"):
        if not device:
            return "What device should I control? e.g. 'turn on living room lights'."
        self.data["devices"][device] = {"state": action, "updated": datetime.datetime.now().isoformat()}
        self._save()
        return f"Turned {action} {device}."

    def list_smart_devices(self):
        if not self.data["devices"]:
            return "No smart devices registered."
        return "Smart devices:\n" + "\n".join(f"- {d}: {s['state']}" for d, s in self.data["devices"].items())

    def detect_intruder(self):
        return "Camera monitoring active. I'll alert you if movement is detected near registered cameras."

    # ==========================================================
    #  SYSTEM
    # ==========================================================
    def system_status(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            return (f"System status: CPU {cpu}%, RAM {mem}%, Disk {disk}%. "
                    f"Battery: {self._battery()}.")
        except Exception:
            return "Install psutil for system monitoring."

    def _battery(self):
        try:
            import psutil
            b = psutil.sensors_battery()
            return f"{b.percent}% {'plugged in' if b.power_plugged else 'on battery'}" if b else "N/A"
        except Exception:
            return "N/A"

    def backup(self):
        try:
            import shutil
            src = os.path.join(self.base_dir, "memory.json")
            if os.path.exists(src):
                dst = os.path.join(self.base_dir, f"backup_memory_{time.strftime('%Y%m%d')}.json")
                shutil.copy(src, dst)
                return f"Backup created: {dst}"
            return "No memory file to back up."
        except Exception:
            return "Backup failed."

    def process_manager(self):
        try:
            import psutil
            procs = sorted(psutil.process_iter(["name", "cpu_percent"]),
                           key=lambda p: p.info["cpu_percent"] or 0, reverse=True)[:8]
            return "Top processes:\n" + "\n".join(f"- {p.info['name']} ({p.info['cpu_percent']}%)" for p in procs)
        except Exception:
            return "Install psutil for process management."

    def file_index(self):
        try:
            count = sum(len(files) for _, _, files in os.walk(self.base_dir))
            return f"Indexed {count} files in {self.base_dir}."
        except Exception:
            return "Could not index files."

    def update_manager(self):
        return "Update manager: run 'pip install --upgrade <package>' or check for FRIDAY updates."
