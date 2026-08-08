"""
FRIDAY AI - Multi-Agent System
===============================
Implements a society of specialized AI agents that collaborate to complete
complex tasks autonomously. Each agent has a clear responsibility.

Agents:
  - PlannerAgent: breaks big goals into steps
  - ResearchAgent: gathers information from the web
  - CodingAgent: writes code
  - BrowserAgent: opens/controls browser
  - VisionAgent: analyzes images/screenshots/OCR
  - MemoryAgent: manages long-term & semantic memory
  - AutomationAgent: runs automated workflows
  - SecurityAgent: checks safety of actions
  - ReviewerAgent: reviews/validates output
  - FinanceAgent: financial summaries
"""
import os
import re
import json
import time
import datetime
import threading
import subprocess
import webbrowser

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False


class Agent:
    """Base agent class."""
    name = "agent"

    def __init__(self, core=None):
        self.core = core  # reference to FridayAgent for shared memory/tools

    def run(self, task, **context):
        """Execute the agent's job. Returns a string result."""
        raise NotImplementedError


class PlannerAgent(Agent):
    name = "planner"

    def run(self, task, **context):
        """Break a big goal into actionable steps."""
        steps = self._plan(task)
        headline = f"📋 I've planned this task into {len(steps)} steps:\n"
        body = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(steps))
        steps_copy = "\n".join(steps)
        # Store the plan in memory for other agents
        if self.core:
            self.core.remember("last_plan", steps_copy)
        return headline + body

    def _plan(self, task):
        t = task.lower()
        if "presentation" in t or "slides" in t:
            return [
                "Research the topic using the Research Agent",
                "Write the content and outline",
                "Generate or collect images",
                "Create the slide deck and save it",
            ]
        if "code" in t or "app" in t or "program" in t or "script" in t:
            return [
                "Clarify requirements and design the architecture",
                "Write the code with the Coding Agent",
                "Test and debug the code",
                "Document and package the result",
            ]
        if "research" in t or "report" in t or "summary" in t:
            return [
                "Define the research questions",
                "Gather information from the web",
                "Organize findings",
                "Write the final report",
            ]
        if "email" in t or "message" in t:
            return [
                "Identify the recipient and purpose",
                "Draft the message",
                "Review and refine tone",
                "Send or save for approval",
            ]
        return [
            f"Understand the objective: {task}",
            "Break it into milestones",
            "Assign each step to the right agent",
            "Execute and verify results",
        ]


class ResearchAgent(Agent):
    name = "research"

    def run(self, task, **context):
        """Search the web and summarize findings."""
        if not REQUESTS_AVAILABLE:
            return "Research Agent: web access not available."
        try:
            query = task.replace(" ", "+")
            # Use Wikipedia summary as a reliable source
            resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace('Wikipedia', '').strip().replace(' ', '_')}",
                timeout=8, headers={"User-Agent": "FRIDAY-AI/1.0"}
            )
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get("extract", "")
                if extract:
                    return f"🔍 Research on '{task}':\n{extract[:800]}"
            # Fallback: open a web search
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"🔍 I opened a web search for '{task}' in your browser."
        except Exception:
            webbrowser.open(f"https://www.google.com/search?q={task.replace(' ', '+')}")
            return f"🔍 I opened a web search for '{task}'."


class CodingAgent(Agent):
    name = "coding"

    def run(self, task, **context):
        """Write code based on the request."""
        req = task.lower()
        if self.core and self.core.llm_available:
            return self.core._llm_response(
                f"Write working code for this request. Provide the code and a brief explanation:\n{task}"
            ) or "Coding Agent: I couldn't generate code right now."
        # Rule-based code generation
        code_examples = {
            "sort": 'def sort_list(lst):\n    return sorted(lst)\n\nprint(sort_list([3,1,2]))',
            "hello": 'print("Hello, world!")',
            "fibonacci": 'def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a+b\n    return a',
            "flask": 'from flask import Flask\napp = Flask(__name__)\n\n@app.route("/")\ndef home():\n    return "Hello from FRIDAY!"\n\nif __name__ == "__main__":\n    app.run(debug=True)',
        }
        for key, code in code_examples.items():
            if key in req:
                return f"💻 Here's the code:\n\n```python\n{code}\n```"
        if "function" in req or "method" in req:
            return "💻 Sure! Describe the function you want (e.g. 'a function to sort a list') and I'll write it."
        return "💻 I can write code. Tell me what you need (e.g. 'write a python script'), or give me a Gemini key for full code generation."


class BrowserAgent(Agent):
    name = "browser"

    def run(self, task, **context):
        """Open websites or perform basic browser actions."""
        t = task.lower()
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "github": "https://www.github.com",
            "whatsapp": "https://web.whatsapp.com",
            "linkedin": "https://www.linkedin.com",
            "wikipedia": "https://www.wikipedia.org",
            "chatgpt": "https://chat.openai.com",
            "gemini": "https://gemini.google.com",
            "netflix": "https://www.netflix.com",
        }
        for name, url in sites.items():
            if name in t:
                webbrowser.open(url)
                return f"🌐 Browser Agent: Opening {name.title()}."
        if "." in task:
            url = task if task.startswith("http") else f"https://{task}"
            webbrowser.open(url)
            return f"🌐 Browser Agent: Opening {url}."
        return "🌐 Which site should I open? (e.g. youtube, google, gmail, github, whatsapp)"


class VisionAgent(Agent):
    name = "vision"

    def run(self, task, **context):
        """Analyze images, screenshots, OCR."""
        t = task.lower()
        try:
            import PIL.Image
        except Exception:
            return "Vision Agent: Pillow not installed."
        # If a screenshot analysis is requested
        if "screenshot" in t or "screen" in t:
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshot.png")
                img.save(path)
                return f"👁️ Vision Agent: I captured a screenshot and saved it to {path}. "
            except Exception:
                return "👁️ Vision Agent: Could not capture screenshot."
        # OCR
        if "ocr" in t or "read text" in t or "extract text" in t:
            return "👁️ Vision Agent: OCR requires pytesseract. I can describe images or capture screenshots."
        # Generic image analysis message
        if "image" in t or "photo" in t:
            return ("👁️ Vision Agent: I can analyze images. Point me to an image file "
                    "or ask me to 'capture a screenshot'. With a Gemini key I can describe images in detail.")
        return "👁️ Vision Agent: I can capture screenshots or analyze images. Try 'capture the screen' or 'analyze this image'."


class MemoryAgent(Agent):
    name = "memory"

    def run(self, task, **context):
        """Manage long-term and semantic memory."""
        if not self.core:
            return "Memory Agent: no core available."
        t = task.lower()
        if "remember" in t or "save" in t:
            # "remember that X is Y"
            m = re.search(r"(?:remember that|remember|save)\s+(.+)", t)
            if m:
                content = m.group(1).strip()
                if " is " in content:
                    k, v = content.split(" is ", 1)
                    self.core.remember(k.strip(), v.strip())
                    return f"🧠 Memory Agent: Remembered that {k.strip()} is {v.strip()}."
                self.core.notes.append(content)
                self.core.save_memory()
                return f"🧠 Memory Agent: Saved '{content}' to memory."
        if "show" in t or "list" in t or "recall" in t or "what do you remember" in t:
            mem = self.core.memory
            notes = self.core.notes[-10:]
            result = "🧠 Memory Agent - What I remember:\n"
            if mem:
                result += "Facts:\n" + "\n".join(f"  - {k}: {v}" for k, v in list(mem.items())[:10])
            else:
                result += "Facts: (none yet)\n"
            if notes:
                result += "\nNotes:\n" + "\n".join(f"  - {n}" for n in notes)
            else:
                result += "Notes: (none yet)"
            return result
        return "🧠 Memory Agent: Ask me to 'remember something' or to 'show what you remember'."


class AutomationAgent(Agent):
    name = "automation"

    def run(self, task, **context):
        """Run or define automated workflows."""
        if not self.core:
            return "Automation Agent: no core available."
        # Store a reusable workflow
        core_memories = self.core.memory
        workflows = core_memories.get("_workflows", {})
        if "create workflow" in task.lower() or "automate" in task.lower():
            name = "workflow_" + str(int(time.time()))
            workflows[name] = task
            self.core.remember("_workflows", workflows)
            return f"⚙️ Automation Agent: Created reusable workflow '{name}'."
        return ("⚙️ Automation Agent: I can define workflows. Say 'create a workflow that checks the weather "
                "and opens my email' and I'll save it for reuse.")


class SecurityAgent(Agent):
    name = "security"

    def run(self, task, **context):
        """Evaluate the safety of a proposed action."""
        t = task.lower()
        dangerous = ["delete", "format", "rm -rf", "drop table", "shutdown", "restart", "wipe", "malware", "hack"]
        found = [d for d in dangerous if d in t]
        if found:
            return (f"🛡️ Security Agent: This action involves potentially dangerous keywords "
                    f"({', '.join(found)}). I recommend requiring explicit user permission before proceeding.")
        return "🛡️ Security Agent: This action appears safe. No sensitive operations detected."


class ReviewerAgent(Agent):
    name = "reviewer"

    def run(self, task, **context):
        """Review and validate output."""
        if not task or len(task) < 5:
            return "🔍 Reviewer Agent: Nothing substantial to review."
        # Simple quality check
        issues = []
        if "TODO" in task or "fixme" in task.lower():
            issues.append("Contains unfinished TODO/FIXME markers")
        if len(task) > 2000:
            issues.append("Response is very long; consider summarizing")
        if not issues:
            return "✅ Reviewer Agent: Output looks good. No issues detected."
        return "🔍 Reviewer Agent: Found issues:\n" + "\n".join(f"  - {i}" for i in issues)


class FinanceAgent(Agent):
    name = "finance"

    def run(self, task, **context):
        """Build financial summaries and insights."""
        if not self.core:
            return "Finance Agent: no core available."
        expenses = self.core.memory.get("_expenses", [])
        currency = self.core.memory.get("currency", "$")
        if "add expense" in task.lower() or "expense" in task.lower():
            m = re.search(r"(\d+(?:\.\d+)?)", task)
            if m:
                amount = float(m.group(1))
                expenses.append({"amount": amount, "date": datetime.datetime.now().isoformat()})
                self.core.remember("_expenses", expenses)
                return f"💰 Finance Agent: Added {currency}{amount:.2f} to expenses."
            return "💰 How much is the expense? (e.g. 'add expense of 25.50')"
        if "summary" in task.lower() or "total" in task.lower() or "spent" in task.lower():
            total = sum(e["amount"] for e in expenses)
            count = len(expenses)
            return (f"💰 Finance Agent: You have {count} recorded expenses totaling {currency}{total:.2f}. "
                    f"Say 'add expense of X' to track more.")
        return "💰 Finance Agent: I can track expenses. Say 'add expense of 25.50' or 'show my expense summary'."


class DigitalTwinAgent(Agent):
    name = "digital_twin"

    def run(self, task, **context):
        """Learn user habits and build a personal knowledge graph."""
        if not self.core:
            return "Digital Twin Agent: no core available."
        t = task.lower()
        if "learn" in t or "preference" in t:
            m = re.search(r"(?:i (?:prefer|like|love|enjoy)|my favorite)\s+(.+)", t)
            if m:
                pref = m.group(1).strip()
                prefs = self.core.memory.get("_preferences", [])
                prefs.append(pref)
                self.core.remember("_preferences", prefs)
                return f"🧬 Digital Twin Agent: Learned your preference: {pref}."
            return "🧬 Tell me something about yourself (e.g. 'I prefer coffee', 'my favorite color is blue')."
        if "profile" in t or "about me" in t or "twin" in t:
            prefs = self.core.memory.get("_preferences", [])
            facts = self.core.memory
            result = "🧬 Digital Twin Agent - Your profile:\n"
            if prefs:
                result += "Preferences:\n" + "\n".join(f"  - {p}" for p in prefs)
            else:
                result += "Preferences: (none yet)\n"
            non_fact_keys = [k for k in facts if not k.startswith("_")]
            if non_fact_keys:
                result += "\nFacts:\n" + "\n".join(f"  - {k}: {facts[k]}" for k in non_fact_keys[:10])
            else:
                result += "Facts: (none yet)"
            return result
        return "🧬 Digital Twin Agent: I can build a profile of you. Say 'I prefer coffee' or 'show my profile'."


class GoalAgent(Agent):
    name = "goal"

    def run(self, task, **context):
        """Track goals and habits."""
        if not self.core:
            return "Goal Agent: no core available."
        t = task.lower()
        goals = self.core.memory.get("_goals", {})
        if "set a goal" in t or "new goal" in t or "goal to" in t or "add goal" in t:
            m = re.search(r"(?:set a goal|new goal|add goal|goal to)\s+(.+)", t)
            if m:
                goal = m.group(1).strip()
                gid = f"g{int(time.time())}"
                goals[gid] = {"text": goal, "created": datetime.datetime.now().isoformat(), "done": False}
                self.core.remember("_goals", goals)
                return f"🎯 Goal Agent: Added goal '{goal}'. Ask to 'show my goals' to track progress."
            return "🎯 What's your goal? (e.g. 'set a goal to exercise 3 times a week')"
        if "show my goals" in t or "goals" in t:
            if not goals:
                return "🎯 You have no goals yet. Say 'set a goal to ...'."
            lines = []
            for gid, g in goals.items():
                status = "✅" if g["done"] else "⬜"
                lines.append(f"  {status} {g['text']}")
            return "🎯 Goal Agent - Your goals:\n" + "\n".join(lines)
        return "🎯 Goal Agent: Say 'set a goal to ...' or 'show my goals'."


# Registry of all agents
AGENTS = {
    "planner": PlannerAgent,
    "research": ResearchAgent,
    "coding": CodingAgent,
    "browser": BrowserAgent,
    "vision": VisionAgent,
    "memory": MemoryAgent,
    "automation": AutomationAgent,
    "security": SecurityAgent,
    "reviewer": ReviewerAgent,
    "finance": FinanceAgent,
    "digital_twin": DigitalTwinAgent,
    "goal": GoalAgent,
}


def get_agent(name, core=None):
    """Instantiate an agent by name."""
    cls = AGENTS.get(name)
    if cls:
        return cls(core)
    return None


def available_agents():
    """Return list of agent names."""
    return list(AGENTS.keys())
