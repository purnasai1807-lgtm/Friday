"""
FRIDAY AI - Smart Capabilities Module
======================================
Adds realistic AI-assistant upgrades:
  1. Browser automation (Playwright, optional) - actually DO things online
  2. RAG knowledge base - semantic search over your own files/documents
  3. Proactive morning briefing & routines
  4. Conversation memory & persona
  5. Fact-checking / confidence scoring (filtered)

All modules are optional imports - FRIDAY degrades gracefully if a
library isn't installed.
"""
import os
import re
import json
import glob
import datetime
import hashlib

# ---- Optional: Browser automation ----
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

# ---- Optional: RAG / embeddings ----
try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False

# ---- Simple local embeddings fallback (no external deps) ----
def _simple_embed(text):
    """A tiny keyword-based embedding so RAG works with zero dependencies."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    vec = {}
    for t in tokens:
        vec[t] = vec.get(t, 0) + 1
    return vec


def _cosine(a, b):
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[k] * b[k] for k in common)
    # normalize
    n1 = sum(v * v for v in a.values()) ** 0.5
    n2 = sum(v * v for v in b.values()) ** 0.5
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


class FridaySmart:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.knowledge_index = {}
        self.load_index()
        # Browser automation state
        self.browser = None
        self.page = None

    # ==========================================================
    #  RAG KNOWLEDGE BASE - search your own files
    # ==========================================================
    def index_path(self, path):
        """Index a file or folder of text/docs into the knowledge base."""
        added = 0
        if os.path.isfile(path):
            added += self._index_file(path)
        elif os.path.isdir(path):
            exts = (".txt", ".md", ".py", ".json", ".csv", ".html", ".css", ".js",
                    ".log", ".ini", ".cfg", ".yaml", ".yml", ".toml")
            for f in glob.glob(os.path.join(path, "**", "*"), recursive=True):
                if os.path.isfile(f) and f.lower().endswith(exts):
                    added += self._index_file(f)
        self.save_index()
        return added

    def _index_file(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            if len(content.strip()) < 20:
                return 0
            key = os.path.abspath(path)
            self.knowledge_index[key] = {
                "path": key,
                "name": os.path.basename(key),
                "content": content[:20000],
                "embed": _simple_embed(content[:20000]),
                "updated": datetime.datetime.now().isoformat(),
            }
            return 1
        except Exception:
            return 0

    def load_index(self):
        try:
            idx_path = os.path.join(self.base_dir, "knowledge_index.json")
            if os.path.exists(idx_path):
                with open(idx_path, "r", encoding="utf-8") as fh:
                    self.knowledge_index = json.load(fh)
        except Exception:
            self.knowledge_index = {}

    def save_index(self):
        try:
            idx_path = os.path.join(self.base_dir, "knowledge_index.json")
            with open(idx_path, "w", encoding="utf-8") as fh:
                json.dump(self.knowledge_index, fh, indent=2)
        except Exception:
            pass

    def search(self, query, top_k=3):
        """Search the indexed knowledge base. Returns list of matches."""
        if not self.knowledge_index:
            return []
        q_embed = _simple_embed(query)
        scored = []
        for key, doc in self.knowledge_index.items():
            score = _cosine(q_embed, doc.get("embed", {}))
            # Also keyword boost
            for word in q_embed:
                if word and word in doc["content"].lower():
                    score += 0.15
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k] if score > 0.05]

    def summarize_findings(self, query, top_k=3):
        """Return a readable answer from the knowledge base."""
        results = self.search(query, top_k)
        if not results:
            return None
        parts = [f"Here's what I found in your files about '{query}':"]
        for i, doc in enumerate(results, 1):
            snippet = doc["content"][:400].replace("\n", " ")
            parts.append(f"{i}. From {doc['name']}: ...{snippet}...")
        return "\n".join(parts)

    # ==========================================================
    #  BROWSER AUTOMATION - actually DO things online
    # ==========================================================
    def browser_available(self):
        return PLAYWRIGHT_AVAILABLE

    def browser_status(self):
        if not PLAYWRIGHT_AVAILABLE:
            return "Browser automation is not installed. Run: pip install playwright && playwright install"
        return "Browser automation is ready."

    def open_browser(self):
        """Launch a browser if not already open."""
        if not PLAYWRIGHT_AVAILABLE:
            return False
        if not self.browser:
            try:
                self._pw = sync_playwright().start()
                self.browser = self._pw.chromium.launch(headless=False)
                self.page = self.browser.new_page()
            except Exception:
                return False
        return True

    def goto(self, url):
        if not self.open_browser():
            return "Browser automation unavailable."
        try:
            self.page.goto(url, timeout=20000)
            return f"Opened {url} in the browser."
        except Exception as e:
            return f"Could not open {url}: {e}"

    def search_web_auto(self, query):
        """Search and return top results content (Google)."""
        if not self.open_browser():
            return "Browser automation unavailable."
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self.page.goto(url, timeout=20000)
            self.page.wait_for_timeout(1500)
            results = self.page.eval_on_selector_all(
                "div.g a h3",
                "els => els.slice(0,5).map(e => e.textContent)"
            )
            links = self.page.eval_on_selector_all(
                "div.g a",
                "els => els.slice(0,5).map(a => a.href)"
            )
            if results:
                out = [f"Top results for '{query}':"]
                for i, (t, l) in enumerate(zip(results, links), 1):
                    out.append(f"{i}. {t} - {l}")
                return "\n".join(out)
            # Try extracting visible text as fallback
            text = self.page.evaluate("document.body ? document.body.innerText.slice(0,800) : ''")
            return f"Search opened for '{query}'. Preview: {text}"
        except Exception as e:
            return f"Search failed: {e}"

    def close_browser(self):
        if self.browser:
            try:
                self.browser.close()
                self._pw.stop()
            except Exception:
                pass
            self.browser = None
            self.page = None
            return "Browser closed."
        return "Browser was not open."

    # ==========================================================
    #  PROACTIVE MORNING BRIEFING
    # ==========================================================
    def morning_briefing(self, memory=None):
        """Compose a proactive morning briefing."""
        now = datetime.datetime.now()
        greeting_period = "morning" if now.hour < 12 else ("afternoon" if now.hour < 18 else "evening")
        lines = [f"Good {greeting_period}"]

        name = "sir"
        if memory:
            name = memory.get("user_name") or memory.get("name") or "sir"
        lines = [f"Good {greeting_period}, {name}. Here's your briefing for {now.strftime('%A, %B %d')}."]

        # Weather
        lines.append("\n🌤 Weather:")
        lines.append(self._weather_line())

        # Pending goals
        if memory and memory.get("goals"):
            goals = memory["goals"]
            if isinstance(goals, list) and goals:
                lines.append("\n🎯 Your goals:")
                for g in goals[-5:]:
                    lines.append(f"  - {g}")

        # Notes / reminders
        if memory and memory.get("notes"):
            notes = memory["notes"]
            if isinstance(notes, list) and notes:
                lines.append("\n📝 Recent notes:")
                for n in notes[-3:]:
                    lines.append(f"  - {n}")

        # Expenses
        if memory and memory.get("expenses"):
            exp = memory["expenses"]
            if isinstance(exp, dict) and exp.get("total"):
                lines.append(f"\n💰 Total recorded expenses so far: {exp['total']}")

        lines.append("\nHow can I help you today?")
        return "\n".join(lines)

    def _weather_line(self):
        if REQUESTS_AVAILABLE:
            try:
                resp = requests.get("https://wttr.in/?format=%C+%t+%h+%w", timeout=6)
                if resp.status_code == 200:
                    return f"Current conditions: {resp.text.strip()}."
            except Exception:
                pass
        return "Weather is unavailable right now."

    # ==========================================================
    #  FACT-CHECK / CONFIDENCE (simple heuristic)
    # ==========================================================
    @staticmethod
    def confidence(response_text):
        """Return a confidence label based on simple heuristics."""
        if not response_text:
            return 0.0
        text = response_text.lower()
        doubt = any(w in text for w in ["i couldn't", "unavailable", "failed", "could not",
                                        "not sure", "i don't know", "couldn't"])
        if doubt:
            return 0.3
        if any(w in text for w in ["found", "here's", "the answer is", "current time",
                                   "today is", "weather in"]):
            return 0.9
        return 0.7


if __name__ == "__main__":
    smart = FridaySmart()
    print("Browser available:", smart.browser_available())
    print("Briefing sample:\n", smart.morning_briefing({"user_name": "John"}))
    idx = smart.index_path(".")
    print(f"Indexed {idx} files. Ask FRIDAY 'search my files for X'.")
