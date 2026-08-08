"""
FRIDAY AI - Self-Learning Memory Engine
=========================================
The "adaptive brain" that makes FRIDAY smarter over time.

Capabilities:
1. Learn daily routines and habits
2. Learn favorite websites and apps
3. Learn coding style preferences
4. Learn frequently used commands
5. Predict what the user will need
6. Build and maintain a personal knowledge graph
7. Track relationships between people, projects, and tasks
8. Self-evaluate and suggest improvements

Architecture:
- PatternDetector: recognizes habits and routines from command history
- PreferenceEngine: learns user preferences across apps, websites, coding style
- KnowledgeGraph: relationship tracking with importance scoring
- Predictor: suggests actions based on time, context, and history
- SelfEvaluator: analyzes own performance and suggests improvements
"""
import os
import re
import json
import time
import datetime
import math
from collections import Counter, defaultdict


class FridayLearning:
    def __init__(self, cortex=None):
        self.cortex = cortex
        self.base_dir = cortex.base_dir if cortex else os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.base_dir, "learning_data.json")
        self.data = self._load()

        # Pattern tracking
        self.command_history = self.data.get("command_history", [])
        self.routines = self.data.get("routines", {})
        self.preferences = self.data.get("preferences", {})
        self.knowledge_graph = self.data.get("knowledge_graph", {"nodes": {}, "edges": []})
        self.predictions = self.data.get("predictions", [])
        self.improvements = self.data.get("improvements", [])

    def _load(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "command_history": [],
            "routines": {},
            "preferences": {},
            "knowledge_graph": {"nodes": {}, "edges": []},
            "predictions": [],
            "improvements": [],
            "performance": {"total": 0, "success": 0, "by_category": {}},
        }

    def save(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    # ==================== LEARNING CORE ====================
    def learn_from_command(self, command, response, success=True):
        """Record a command and its outcome for learning."""
        entry = {
            "command": command,
            "response": response[:200] if response else "",
            "success": success,
            "timestamp": datetime.datetime.now().isoformat(),
            "hour": datetime.datetime.now().hour,
            "day_of_week": datetime.datetime.now().strftime("%A"),
        }
        self.command_history.append(entry)
        if len(self.command_history) > 2000:
            self.command_history = self.command_history[-2000:]
        self._detect_patterns()
        self._update_performance(command, success)
        self.save()

    def _detect_patterns(self):
        """Analyze command history to detect routines and preferences."""
        if len(self.command_history) < 5:
            return

        # Detect time-based routines
        hour_counter = defaultdict(list)
        for entry in self.command_history:
            h = entry.get("hour")
            if h is not None:
                hour_counter[h].append(entry["command"])

        # Find frequent commands at specific hours
        for hour, cmds in hour_counter.items():
            if len(cmds) >= 3:
                most_common = Counter(cmds).most_common(3)
                time_label = f"{hour:02d}:00"
                if time_label not in self.routines:
                    self.routines[time_label] = {
                        "commands": [c for c, _ in most_common],
                        "count": len(cmds),
                        "last_seen": datetime.datetime.now().isoformat(),
                    }
                else:
                    self.routines[time_label]["count"] = len(cmds)
                    self.routines[time_label]["last_seen"] = datetime.datetime.now().isoformat()

        # Detect favorite apps/websites
        app_commands = [e["command"] for e in self.command_history
                       if any(w in e["command"].lower() for w in ["open", "launch", "start"])]
        app_counter = Counter(app_commands)
        for cmd, count in app_counter.most_common(10):
            if count >= 2:
                self.preferences[f"app_{cmd}"] = {"count": count, "last_used": datetime.datetime.now().isoformat()}

        # Detect frequently used commands
        all_cmds = [e["command"] for e in self.command_history]
        cmd_counter = Counter(all_cmds)
        for cmd, count in cmd_counter.most_common(20):
            if count >= 3:
                self.preferences[f"cmd_{cmd[:50]}"] = {"count": count}

    def _update_performance(self, command, success):
        perf = self.data.setdefault("performance", {"total": 0, "success": 0, "by_category": {}})
        perf["total"] += 1
        if success:
            perf["success"] += 1

        # Categorize
        category = self._categorize(command)
        by_cat = perf.setdefault("by_category", {})
        cat_entry = by_cat.get(category, {"total": 0, "success": 0})
        cat_entry["total"] += 1
        if success:
            cat_entry["success"] += 1
        by_cat[category] = cat_entry

    def _categorize(self, command):
        cmd = command.lower()
        if any(w in cmd for w in ["open", "launch", "start", "switch"]):
            return "app_control"
        if any(w in cmd for w in ["click", "type", "press", "scroll", "drag"]):
            return "ui_control"
        if any(w in cmd for w in ["search", "find", "google", "research"]):
            return "search"
        if any(w in cmd for w in ["weather", "time", "date", "calculate"]):
            return "information"
        if any(w in cmd for w in ["code", "write", "build", "create", "make"]):
            return "creation"
        if any(w in cmd for w in ["install", "setup", "configure"]):
            return "setup"
        if any(w in cmd for w in ["read", "analyze", "screen", "ocr"]):
            return "vision"
        return "other"

    # ==================== ROUTINES ====================
    def get_routines(self):
        """Return learned routines keyed by time."""
        return dict(self.routines)

    def get_prediction_for_time(self, hour=None):
        """Predict what the user might want based on time and history."""
        if hour is None:
            hour = datetime.datetime.now().hour
        time_label = f"{hour:02d}:00"
        routine = self.routines.get(time_label)
        if routine:
            return routine.get("commands", [])
        return []

    def get_daily_prediction(self):
        """Get a prediction of what the user might want right now."""
        now = datetime.datetime.now()
        hour = now.hour
        predictions = []

        # Time-based predictions
        if 7 <= hour <= 9:
            predictions = ["morning briefing", "check emails", "open calendar", "check weather"]
        elif 9 <= hour <= 12:
            predictions = ["open code editor", "open github", "check tasks", "open documentation"]
        elif 12 <= hour <= 13:
            predictions = ["play music", "check news", "open lunch playlist"]
        elif 13 <= hour <= 17:
            predictions = ["continue coding", "run tests", "open terminal", "check emails"]
        elif 17 <= hour <= 19:
            predictions = ["evening summary", "check calendar", "open news"]
        elif 19 <= hour <= 22:
            predictions = ["play music", "open entertainment", "relax"]
        else:
            predictions = ["goodnight routine", "lock screen", "set alarm"]

        # Override with learned routines
        learned = self.get_prediction_for_time(hour)
        if learned:
            predictions = learned + predictions

        return predictions[:5]

    # ==================== PREFERENCES ====================
    def get_preferences(self):
        """Return learned user preferences."""
        return dict(self.preferences)

    def get_favorite_apps(self):
        """Get the user's most frequently opened apps."""
        apps = []
        for key, val in self.preferences.items():
            if key.startswith("app_") and val.get("count", 0) >= 2:
                cmd = key.replace("app_", "")
                apps.append({"command": cmd, "count": val["count"]})
        return sorted(apps, key=lambda x: -x["count"])

    def get_frequent_commands(self):
        """Get frequently used commands."""
        cmds = []
        for key, val in self.preferences.items():
            if key.startswith("cmd_") and val.get("count", 0) >= 3:
                cmds.append({"command": key.replace("cmd_", ""), "count": val["count"]})
        return sorted(cmds, key=lambda x: -x["count"])

    # ==================== KNOWLEDGE GRAPH ====================
    def kg_add(self, subject, relation, obj):
        """Add a relationship to the personal knowledge graph."""
        graph = self.knowledge_graph
        for node_name in (subject, obj):
            if node_name not in graph["nodes"]:
                graph["nodes"][node_name] = {
                    "importance": 1.0,
                    "mentions": 1,
                    "first_seen": datetime.datetime.now().isoformat(),
                    "types": set()
                }
            else:
                graph["nodes"][node_name]["importance"] = min(5.0, graph["nodes"][node_name].get("importance", 1.0) + 0.5)
                graph["nodes"][node_name]["mentions"] += 1

        # Infer node types
        self._infer_type(graph["nodes"][subject], relation, obj)
        self._infer_type(graph["nodes"][obj], relation, subject, reverse=True)

        graph["edges"].append({
            "subj": subject,
            "rel": relation,
            "obj": obj,
            "ts": datetime.datetime.now().isoformat(),
        })
        self.save()
        return f"Linked '{subject}' {relation} '{obj}' in your knowledge graph."

    def _infer_type(self, node, relation, other, reverse=False):
        """Infer entity types from relationships."""
        types = node.get("types", [])
        relation_lower = relation.lower()
        other_lower = other.lower()

        if any(w in relation_lower for w in ["works at", "employed by", "job"]):
            if "person" not in types:
                types.append("person")
            if "company" not in types:
                types.append("company")
        if any(w in relation_lower for w in ["likes", "loves", "enjoys", "favorite"]):
            if "person" not in types:
                types.append("person")
        if any(w in relation_lower for w in ["project", "working on"]):
            if "person" not in types:
                types.append("person")
            if "project" not in types:
                types.append("project")

        node["types"] = types[:5]  # Limit types

    def kg_query(self, entity):
        """Query everything connected to an entity."""
        edges = self.knowledge_graph.get("edges", [])
        related = [e for e in edges
                   if entity.lower() in e["subj"].lower() or entity.lower() in e["obj"].lower()]
        if not related:
            return f"No knowledge found about '{entity}'. Say 'remember that X is Y'."
        facts = []
        for e in related[-10:]:
            if entity.lower() in e["subj"].lower():
                facts.append(f"{e['rel']} {e['obj']}")
            else:
                facts.append(f"is {e['rel']} of {e['subj']}")
        return f"About {entity}:\n" + "\n".join(f"  - {f}" for f in facts)

    def kg_top(self, n=5):
        """Return the most important known entities."""
        nodes = self.knowledge_graph.get("nodes", {})
        if not nodes:
            return "Your knowledge graph is empty. Say 'remember that X is Y'."
        ranked = sorted(nodes.items(), key=lambda x: -x[1].get("importance", 0))[:n]
        return "Most important in your knowledge graph:\n" + "\n".join(
            f"  - {k} (importance {v.get('importance', 1):.1f}, types: {', '.join(v.get('types', []))})"
            for k, v in ranked
        )

    def kg_summarize_person(self, name):
        """Build a rich summary of a person from the knowledge graph."""
        edges = self.knowledge_graph.get("edges", [])
        nodes = self.knowledge_graph.get("nodes", {})
        related = [e for e in edges if name.lower() in e["subj"].lower()]
        if not related:
            return f"I don't have any information about {name}."

        info = [f"Knowledge about {name}:"]
        node = nodes.get(name, {})
        if node.get("types"):
            info.append(f"  Types: {', '.join(node['types'])}")
        if node.get("importance"):
            info.append(f"  Importance: {node['importance']:.1f}")
        for e in related:
            info.append(f"  {e['rel']} {e['obj']}")

        return "\n".join(info)

    # ==================== PREDICTIONS ====================
    def predict_next_action(self):
        """Predict what the user might want to do next."""
        predictions = []
        now = datetime.datetime.now()
        hour = now.hour
        weekday = now.strftime("%A")

        # Time-based predictions
        if 7 <= hour <= 9 and weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            predictions.append(("morning briefing", 0.8))
        if 9 <= hour <= 11:
            predictions.append(("open code editor", 0.7))
        if 12 <= hour <= 13:
            predictions.append(("check news", 0.6))
        if 13 <= hour <= 17:
            predictions.append(("continue coding", 0.7))
        if 17 <= hour <= 19:
            predictions.append(("evening summary", 0.6))
        if 19 <= hour <= 22:
            predictions.append(("open entertainment", 0.7))
        if hour >= 22 or hour < 7:
            predictions.append(("goodnight routine", 0.7))

        # History-based predictions
        learned = self.get_prediction_for_time(hour)
        for cmd in learned:
            predictions.append((cmd, 0.5))

        # Sort by confidence
        predictions.sort(key=lambda x: -x[1])
        return predictions[:5]

    # ==================== SELF-EVALUATION ====================
    def get_performance_report(self):
        """Analyze FRIDAY's own performance."""
        perf = self.data.get("performance", {"total": 0, "success": 0, "by_category": {}})
        total = perf.get("total", 0)
        success = perf.get("success", 0)
        rate = (success / total) if total else 0

        lines = ["Self-Evaluation Report:"]
        lines.append(f"Total actions: {total}")
        lines.append(f"Success rate: {rate:.0%}")

        by_cat = perf.get("by_category", {})
        if by_cat:
            lines.append("\nBy category:")
            for cat, stats in sorted(by_cat.items(), key=lambda x: -x[1].get("total", 0)):
                r = stats.get("success", 0) / stats.get("total", 1)
                lines.append(f"  {cat}: {r:.0%} ({stats.get('total', 0)} actions)")

        # Improvement suggestions
        weak_areas = [cat for cat, stats in by_cat.items()
                     if stats.get("total", 0) > 5 and stats.get("success", 0) / stats.get("total", 1) < 0.6]
        if weak_areas:
            lines.append(f"\nAreas needing improvement: {', '.join(weak_areas)}")

        return "\n".join(lines)

    def suggest_improvement(self):
        """Generate a self-improvement suggestion."""
        perf = self.data.get("performance", {})
        by_cat = perf.get("by_category", {})

        # Find weakest area
        weakest = None
        weakest_rate = 1.0
        for cat, stats in by_cat.items():
            if stats.get("total", 0) >= 3:
                rate = stats.get("success", 0) / stats.get("total", 1)
                if rate < weakest_rate:
                    weakest_rate = rate
                    weakest = cat

        if weakest and weakest_rate < 0.6:
            suggestion = f"I'm struggling with '{weakest}' tasks (success rate: {weakest_rate:.0%}). "
            if weakest == "vision":
                suggestion += "I should improve my screen reading accuracy."
            elif weakest == "ui_control":
                suggestion += "I should practice more precise clicking and typing."
            elif weakest == "search":
                suggestion += "I should refine my web search queries."
            else:
                suggestion += "I need more practice in this area."
            self.improvements.append({
                "suggestion": suggestion,
                "area": weakest,
                "timestamp": datetime.datetime.now().isoformat(),
            })
            self.save()
            return suggestion
        return "I'm performing well. Keep teaching me new skills!"

    # ==================== REPORTING ====================
    def report(self):
        """Generate a comprehensive learning report."""
        lines = ["=== FRIDAY Self-Learning Report ===\n"]

        # Routines
        lines.append("Learned Routines:")
        for time_label, info in sorted(self.routines.items()):
            lines.append(f"  {time_label}: {', '.join(info.get('commands', [])[:2])}")
        if not self.routines:
            lines.append("  (no routines learned yet)")

        # Preferences
        lines.append("\nPreferences:")
        fav_apps = self.get_favorite_apps()
        if fav_apps:
            lines.append("  Favorite apps:")
            for app in fav_apps[:5]:
                lines.append(f"    - {app['command']} ({app['count']} times)")
        else:
            lines.append("  (no preferences learned yet)")

        # Knowledge graph
        lines.append("\nKnowledge Graph:")
        nodes = self.knowledge_graph.get("nodes", {})
        edges = self.knowledge_graph.get("edges", [])
        lines.append(f"  Nodes: {len(nodes)}")
        lines.append(f"  Connections: {len(edges)}")

        # Performance
        lines.append("\nPerformance:")
        perf = self.data.get("performance", {})
        total = perf.get("total", 0)
        success = perf.get("success", 0)
        rate = (success / total) if total else 0
        lines.append(f"  Actions: {total}, Success rate: {rate:.0%}")

        # Predictions
        lines.append("\nCurrent Predictions:")
        predictions = self.predict_next_action()
        for pred, conf in predictions:
            lines.append(f"  - {pred} ({conf:.0%} confidence)")

        return "\n".join(lines)

    def get_learning_stats(self):
        """Get learning statistics for the UI."""
        return {
            "routines_learned": len(self.routines),
            "preferences_learned": len(self.preferences),
            "knowledge_nodes": len(self.knowledge_graph.get("nodes", {})),
            "knowledge_edges": len(self.knowledge_graph.get("edges", [])),
            "total_actions": self.data.get("performance", {}).get("total", 0),
            "success_rate": self._success_rate(),
            "predictions": len(self.predictions),
        }

    def _success_rate(self):
        perf = self.data.get("performance", {})
        total = perf.get("total", 0)
        success = perf.get("success", 0)
        return (success / total) if total else 0
