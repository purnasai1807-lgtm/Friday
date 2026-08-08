"""
FRIDAY AI - Intelligence & Autonomy Module
===========================================
Adds the advanced capabilities that make FRIDAY a world-class AI agent:

  1. 🎯 MISSION MODE          - give a big goal, FRIDAY plans/researches/codes/tests
                               autonomously using the agent society, then reports back.
  2. 🧠 SELF-LEARNING LOOP    - FRIDAY scores its own responses, tracks success by task
                               type, and improves rules/prompts over time.
  3. 🕸️ SEMANTIC MEMORY GRAPH - personal knowledge graph with importance scoring.
  4. 📜 CONVERSATION SUMMARY  - auto-summarize long conversations to remember forever.
  5. 📋 TOOL-USE AUDIT LOG    - transparent log of every action (timestamp + permission).
  6. 🛠️ SELF-HEALING          - check dependencies, report missing libs, fix startup issues.

All modules are optional-import guarded; FRIDAY degrades gracefully.
"""
import os
import re
import json
import time
import datetime
import importlib


class FridayIntelligence:
    def __init__(self, base_dir=None, agent=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.agent = agent  # reference back to FridayAgent
        self.data_file = os.path.join(self.base_dir, "intelligence_data.json")
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
            "missions": [],          # autonomous missions
            "learning": {            # self-learning feedback
                "total": 0,
                "success": 0,
                "by_task": {},
                "rules": {},
            },
            "graph": {               # semantic memory graph
                "nodes": {},
                "edges": [],
            },
            "summaries": [],         # conversation summaries
            "audit": [],             # tool-use audit log
        }

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2)
        except Exception:
            pass

    # ==========================================================
    #  1. 🎯 MISSION MODE - Autonomous task execution
    # ==========================================================
    def start_mission(self, goal):
        """Plan and kick off an autonomous mission."""
        steps = self._plan_mission(goal)
        mission = {
            "goal": goal,
            "steps": steps,
            "status": "planned",
            "created": datetime.datetime.now().isoformat(),
            "results": [],
        }
        self.data["missions"].append(mission)
        self.save_data()
        return mission

    def _plan_mission(self, goal):
        """Break a goal into agent-appropriate steps."""
        g = goal.lower()
        steps = []
        if any(w in g for w in ["website", "portfolio", "app", "web page", "site"]):
            steps = [
                ("planner", "Design the architecture and structure for: " + goal),
                ("research", "Research best practices and gather reference material"),
                ("coding", "Build the core implementation for: " + goal),
                ("reviewer", "Review the generated code/output for quality"),
            ]
        elif any(w in g for w in ["report", "research", "summary", "analysis"]):
            steps = [
                ("research", "Gather comprehensive information on: " + goal),
                ("planner", "Organize the findings into a clear structure"),
                ("reviewer", "Review and refine the final output"),
            ]
        elif any(w in g for w in ["presentation", "slides", "deck"]):
            steps = [
                ("research", "Gather content and facts for: " + goal),
                ("coding", "Generate the presentation content and structure"),
                ("reviewer", "Review the presentation for quality"),
            ]
        else:
            steps = [
                ("planner", "Break down the objective: " + goal),
                ("research", "Gather information needed to complete: " + goal),
                ("coding", "Execute the core work for: " + goal),
                ("reviewer", "Review and verify the completed work"),
            ]
        return [{"agent": a, "task": t} for a, t in steps]

    def run_mission_step(self, mission_index, step_index):
        """Execute a single step of a mission via the agent society."""
        if not self.agent:
            return "Mission mode requires a connected agent."
        try:
            mission = self.data["missions"][mission_index]
            step = mission["steps"][step_index]
            agent_name = step["agent"]
            task = step["task"]
            # Use the multi-agent dispatch helper
            result = self._run_society_agent(agent_name, task)
            mission["results"].append({"step": agent_name, "result": result})
            if step_index >= len(mission["steps"]) - 1:
                mission["status"] = "completed"
            else:
                mission["status"] = "in-progress"
            self.save_data()
            return result
        except Exception as e:
            return f"Mission step failed: {e}"

    def _run_society_agent(self, name, task):
        """Route to a specific agent from the agent society."""
        try:
            from friday_agents import get_agent
            agent = get_agent(name, core=self.agent)
            if agent:
                return agent.run(task)
        except Exception:
            pass
        # Fallback to LLM if available
        if self.agent and self.agent.llm_available:
            return self.agent._llm_response(
                f"Act as a {name} agent. Complete this task:\n{task}")
        return f"[{name}] No agent available and no LLM configured."

    def run_full_mission(self, goal, callback=None):
        """Execute an entire mission end-to-end, returning a report."""
        mission = self.start_mission(goal)
        idx = len(self.data["missions"]) - 1
        report = [f"🎯 MISSION: {goal}", ""]
        for i in range(len(mission["steps"])):
            result = self.run_mission_step(idx, i)
            step = mission["steps"][i]
            report.append(f"Step {i+1} ({step['agent']}):")
            report.append(str(result)[:600])
            report.append("")
            if callback:
                callback(report[-2])
        mission = self.data["missions"][idx]
        report.append(f"✅ Mission status: {mission['status']}")
        return "\n".join(report)

    def mission_status(self):
        missions = self.data.get("missions", [])
        if not missions:
            return "No missions yet. Say 'mission: build my portfolio website' to start one."
        lines = ["🎯 Missions:"]
        for m in missions[-5:]:
            lines.append(f"- [{m.get('status')}] {m.get('goal')}")
        return "\n".join(lines)

    # ==========================================================
    #  2. 🧠 SELF-LEARNING LOOP
    # ==========================================================
    def record_feedback(self, task_category, success, response_text=""):
        """Record whether FRIDAY's response was successful for a task type."""
        learn = self.data.get("learning", {})
        learn["total"] = learn.get("total", 0) + 1
        if success:
            learn["success"] = learn.get("success", 0) + 1
        by_task = learn.get("by_task", {})
        entry = by_task.get(task_category, {"total": 0, "success": 0})
        entry["total"] += 1
        if success:
            entry["success"] += 1
        by_task[task_category] = entry
        learn["by_task"] = by_task
        learn["last_response"] = response_text[:200]
        self.data["learning"] = learn
        self.save_data()
        return self._improvement_hint(task_category)

    def _improvement_hint(self, task_category):
        """Generate an improvement hint based on success rate."""
        by_task = self.data.get("learning", {}).get("by_task", {})
        entry = by_task.get(task_category, {})
        total = entry.get("total", 0)
        success = entry.get("success", 0)
        if total == 0:
            return None
        rate = success / total
        if rate < 0.4:
            hint = f"I'm improving at '{task_category}' (success {rate:.0%}). Let me adjust my approach."
            # Store a rule to improve
            rules = self.data["learning"].setdefault("rules", {})
            rules[task_category] = rules.get(task_category, 0) + 1
            self.save_data()
            return hint
        return None

    def learning_report(self):
        learn = self.data.get("learning", {})
        total = learn.get("total", 0)
        success = learn.get("success", 0)
        rate = (success / total) if total else 0
        lines = [f"🧠 Self-Learning Report"]
        lines.append(f"Total responses tracked: {total}")
        lines.append(f"Success rate: {rate:.0%}")
        by_task = learn.get("by_task", {})
        if by_task:
            lines.append("\nBy task type:")
            for cat, e in sorted(by_task.items(), key=lambda x: -x[1].get("total", 0))[:8]:
                r = e.get("success", 0) / e.get("total", 1)
                lines.append(f"  - {cat}: {r:.0%} ({e.get('total', 0)} samples)")
        return "\n".join(lines)

    # ==========================================================
    #  3. 🕸️ SEMANTIC MEMORY GRAPH
    # ==========================================================
    def kg_add(self, entity, relation, target):
        """Add a node/edge to the personal knowledge graph with importance."""
        graph = self.data.get("graph", {"nodes": {}, "edges": []})
        # Nodes
        for node_name in (entity, target):
            if node_name not in graph["nodes"]:
                graph["nodes"][node_name] = {
                    "importance": 1.0,
                    "mentions": 1,
                    "first_seen": datetime.datetime.now().isoformat(),
                }
            else:
                graph["nodes"][node_name]["importance"] = min(
                    5.0, graph["nodes"][node_name].get("importance", 1.0) + 0.5)
                graph["nodes"][node_name]["mentions"] += 1
        # Edge
        graph["edges"].append({
            "subj": entity, "rel": relation, "obj": target,
            "ts": datetime.datetime.now().isoformat(),
        })
        self.data["graph"] = graph
        self.save_data()
        return f"Linked '{entity}' {relation} '{target}' in your knowledge graph."

    def kg_query(self, entity):
        """Return everything connected to an entity."""
        graph = self.data.get("graph", {"nodes": {}, "edges": []})
        edges = graph.get("edges", [])
        related = [
            e for e in edges
            if entity.lower() in e["subj"].lower() or entity.lower() in e["obj"].lower()
        ]
        if not related:
            return f"No knowledge found about '{entity}'. Say 'remember that X is Y'."
        out = [f"🕸️ Knowledge about {entity}:"]
        for e in related[-10:]:
            if entity.lower() in e["subj"].lower():
                out.append(f"  - {e['rel']} {e['obj']}")
            else:
                out.append(f"  - is {e['rel']} of {e['subj']}")
        return "\n".join(out)

    def kg_top(self, n=5):
        """Return the most important known entities."""
        graph = self.data.get("graph", {"nodes": {}, "edges": []})
        nodes = graph.get("nodes", {})
        if not nodes:
            return "Your knowledge graph is empty. Say 'remember that project X is important'."
        ranked = sorted(nodes.items(), key=lambda x: -x[1].get("importance", 0))[:n]
        return "🕸️ Most important in your knowledge graph:\n" + "\n".join(
            f"  - {k} (importance {v.get('importance', 1):.1f})" for k, v in ranked
        )

    # ==========================================================
    #  4. 📜 CONVERSATION SUMMARY
    # ==========================================================
    def summarize_conversation(self, conversation):
        """Summarize a conversation history into a durable gist."""
        if not conversation:
            return None
        # Build a condensed transcript
        transcript = "\n".join(
            f"{m.get('role')}: {m.get('content')}" for m in conversation[-30:]
        )
        summary = None
        # Use LLM if available
        if self.agent and self.agent.llm_available:
            try:
                summary = self.agent._llm_response(
                    f"Summarize this conversation into 3-5 key points to remember long-term:\n{transcript}")
            except Exception:
                summary = None
        if not summary:
            # Simple extractive summary: key user statements
            points = []
            user_msgs = [m.get("content", "") for m in conversation if m.get("role") == "user"]
            for msg in user_msgs[-8:]:
                msg = msg.strip()
                if len(msg) > 5 and msg not in points:
                    points.append(msg[:120])
            summary = "Key user points: " + "; ".join(points) if points else "Conversation was brief."
        self.data["summaries"].append({
            "summary": summary,
            "time": datetime.datetime.now().isoformat(),
        })
        self.save_data()
        return summary

    def get_summaries(self):
        summaries = self.data.get("summaries", [])
        if not summaries:
            return "No conversation summaries yet."
        return "📜 Recent conversation summaries:\n" + "\n".join(
            f"- {s.get('summary')}" for s in summaries[-5:]
        )

    # ==========================================================
    #  5. 📋 TOOL-USE AUDIT LOG
    # ==========================================================
    def audit(self, tool_name, params, permission, result):
        """Record a tool usage for transparency."""
        self.data["audit"].append({
            "tool": tool_name,
            "params": str(params)[:200],
            "permission": permission,  # 'granted' / 'denied' / 'auto' / 'none'
            "result": str(result)[:200],
            "time": datetime.datetime.now().isoformat(),
        })
        if len(self.data["audit"]) > 500:
            self.data["audit"] = self.data["audit"][-500:]
        self.save_data()

    def audit_log(self, n=10):
        audit = self.data.get("audit", [])
        if not audit:
            return "No tool actions logged yet."
        lines = ["📋 Recent actions:"]
        for a in audit[-n:]:
            lines.append(
                f"  [{a.get('time','')}] {a.get('tool')} "
                f"(permission: {a.get('permission','none')}) -> {a.get('result','')[:60]}")
        return "\n".join(lines)

    # ==========================================================
    #  6. 🛠️ SELF-HEALING DIAGNOSTICS
    # ==========================================================
    REQUIRED_LIBS = {
        "flask": "flask",
        "flask-cors": "flask_cors",
        "speechrecognition": "speech_recognition",
        "pyttsx3": "pyttsx3",
        "requests": "requests",
        "pillow": "PIL",
        "google-generativeai": "google.generativeai",
    }
    OPTIONAL_LIBS = {
        "playwright": "playwright",
        "psutil": "psutil",
        "qrcode": "qrcode",
        "pyperclip": "pyperclip",
        "PyPDF2": "PyPDF2",
        "python-docx": "docx",
        "openpyxl": "openpyxl",
        "python-pptx": "pptx",
        "opencv-python": "cv2",
        "pytesseract": "pytesseract",
        "pyautogui": "pyautogui",
        "plyer": "plyer",
        "cryptography": "cryptography",
        "pyttsx3": "pyttsx3",
    }

    @staticmethod
    def _check_lib(import_name):
        try:
            importlib.import_module(import_name)
            return True
        except Exception:
            return False

    def diagnostics(self):
        """Check dependencies and report status."""
        lines = ["🛠️ FRIDAY Diagnostics:"]
        # Required
        missing_required = []
        for pkg, mod in self.REQUIRED_LIBS.items():
            ok = self._check_lib(mod)
            lines.append(f"  {'✅' if ok else '❌'} {pkg}")
            if not ok:
                missing_required.append(pkg)
        lines.append("\nOptional libraries:")
        missing_opt = []
        for pkg, mod in self.OPTIONAL_LIBS.items():
            if pkg in self.REQUIRED_LIBS:
                continue
            ok = self._check_lib(mod)
            lines.append(f"  {'✅' if ok else '○'} {pkg}")
            if not ok:
                missing_opt.append(pkg)
        # Config check
        if self.agent and self.agent.llm_available:
            lines.append("\nAI: ✅ Gemini connected")
        else:
            lines.append("\nAI: ⚠️ No API key - rule-based mode")
        return "\n".join(lines) + self._fix_hints(missing_required, missing_opt)

    def _fix_hints(self, missing_required, missing_opt):
        hints = []
        if missing_required:
            hints.append("\n\nTo fix required packages, run:\n  pip install " +
                         " ".join(missing_required))
        if missing_opt:
            hints.append("\nOptional features (install only if you want them):\n  pip install " +
                         " ".join(missing_opt))
        return "\n".join(hints)

    def self_heal(self):
        """Attempt to install missing required libraries."""
        import subprocess
        missing = [pkg for pkg, mod in self.REQUIRED_LIBS.items()
                   if not self._check_lib(mod)]
        if not missing:
            return "All required dependencies are present. FRIDAY is healthy."
        try:
            subprocess.run(
                ["python", "-m", "pip", "install"] + missing,
                capture_output=True, timeout=120)
            still_missing = [pkg for pkg, mod in self.REQUIRED_LIBS.items()
                             if not self._check_lib(mod)]
            if not still_missing:
                return f"✅ Installed and verified: {', '.join(missing)}"
            return f"⚠️ Could not fully install. Still missing: {', '.join(still_missing)}"
        except Exception as e:
            return f"Self-heal failed: {e}"

    # ==========================================================
    #  HELP
    # ==========================================================
    def help(self):
        return (
            "FRIDAY Intelligence features:\n"
            "- 'mission: <goal>' - autonomous task execution\n"
            "- 'mission status' - view missions\n"
            "- 'learning report' - self-improvement stats\n"
            "- 'remember that X is Y' / 'recall X' / 'knowledge top'\n"
            "- 'summarize our conversation'\n"
            "- 'audit log' - tool-use transparency\n"
            "- 'diagnose' / 'self heal' - system health"
        )


if __name__ == "__main__":
    intel = FridayIntelligence()
    print(intel.diagnostics())
    print(intel.learning_report())
    print(intel.kg_add("project", "is important to", "user"))
    print(intel.kg_query("project"))
