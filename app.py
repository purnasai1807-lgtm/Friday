"""
FRIDAY AI - Flask Web Server (Voice-Only)
==========================================
Serves the voice-only UI and exposes API endpoints.
Runs as a standalone process.
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json as _json
from friday_cortex import FridayCortex

# --- Cloud deployment: allow Gemini API key via environment variable ---
# If GEMINI_API_KEY is set, inject it into config.json at startup so the
# brain is live on cloud hosts without committing secrets to git.
def _inject_env_key(config_path="config.json"):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return
    try:
        with open(config_path, "r") as f:
            cfg = _json.load(f)
        if cfg.get("gemini_api_key") != key:
            cfg["gemini_api_key"] = key
            with open(config_path, "w") as f:
                _json.dump(cfg, f, indent=2)
    except Exception:
        pass

_inject_env_key()

app = Flask(__name__)
CORS(app)

cortex = FridayCortex()

# Global state
voice_running = False
status_listeners = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Process a text command from the web UI."""
    global voice_running
    data = request.get_json()
    text = data.get("message", "")
    if not text:
        return jsonify({"response": "I didn't catch that.", "awake": cortex.is_awake})

    if not cortex.is_awake:
        if cortex.check_wake_word(text):
            cortex.is_awake = True
            return jsonify({
                "response": "Yes sir, FRIDAY at your service. How can I help?",
                "awake": True
            })
        else:
            return jsonify({
                "response": "I'm in standby mode. Say 'wake up friday' to activate me.",
                "awake": False
            })

    response = cortex.process(text)
    return jsonify({
        "response": response,
        "awake": cortex.is_awake,
        "pending_permission": True if cortex.pending_permission else False
    })


@app.route("/api/status", methods=["GET"])
def status():
    """Return the assistant's current status."""
    learning = cortex.get_module('learning')
    stats = learning.get_learning_stats() if learning else {}

    return jsonify({
        "name": cortex.name,
        "awake": cortex.is_awake,
        "voice_loop_running": voice_running,
        "llm_available": cortex.llm_available,
        "always_on": cortex.config.get("always_on", True),
        "permission_enabled": cortex.permission_enabled,
        "pending_permission": True if cortex.pending_permission else False,
        "learning_stats": stats
    })


@app.route("/api/confirm", methods=["POST"])
def confirm():
    """User confirms or denies a pending sensitive action."""
    data = request.get_json() or {}
    allow = data.get("allow", True)
    response = cortex.confirm_permission(allow=allow)
    return jsonify({
        "response": response,
        "awake": cortex.is_awake,
        "pending_permission": True if cortex.pending_permission else False
    })


@app.route("/api/wake", methods=["POST"])
def wake():
    """Wake up FRIDAY."""
    cortex.is_awake = True
    return jsonify({"response": "Yes sir, FRIDAY at your service.", "awake": True})


@app.route("/api/sleep", methods=["POST"])
def sleep():
    """Put FRIDAY to sleep."""
    cortex.is_awake = False
    return jsonify({"response": "Going to sleep. Say 'wake up friday' to wake me.", "awake": False})


@app.route("/api/memory", methods=["GET"])
def get_memory():
    """Get saved notes and memory."""
    return jsonify({"notes": cortex.notes, "memory": cortex.memory, "user_name": cortex.user_name})


@app.route("/api/listen", methods=["POST"])
def listen_once():
    """Trigger one voice listen+process cycle from the web UI."""
    global voice_running
    if not cortex.is_awake:
        text = cortex.listen(timeout=6, phrase_limit=5)
        if text and cortex.check_wake_word(text):
            cortex.is_awake = True
            resp = "Yes sir, FRIDAY at your service. How can I help?"
        else:
            resp = "I'm in standby. Say 'wake up friday' to activate me."
            if text:
                resp = f"I heard '{text}', but I'm in standby. Say 'wake up friday'."
    else:
        text = cortex.listen(timeout=6, phrase_limit=6)
        if not text:
            resp = "I didn't catch that. Please try again."
        elif cortex.check_sleep_word(text):
            cortex.is_awake = False
            resp = "Going to sleep."
        else:
            resp = cortex.process(text)
            cortex.speak(resp)
    return jsonify({"response": resp, "awake": cortex.is_awake})


@app.route("/api/learning", methods=["GET"])
def learning_stats():
    """Get self-learning statistics."""
    learning = cortex.get_module('learning')
    if not learning:
        return jsonify({"error": "Learning module not available"})
    stats = learning.get_learning_stats()
    routines = learning.get_routines()
    predictions = learning.predict_next_action()
    return jsonify({
        "stats": stats,
        "routines": routines,
        "predictions": predictions,
        "report": learning.report()
    })


@app.route("/api/vision/analyze", methods=["POST"])
def vision_analyze():
    """Analyze the current screen."""
    vision = cortex.get_module('vision')
    if not vision:
        return jsonify({"error": "Vision module not available"})
    result = vision.analyze_current_screen()
    return jsonify({"analysis": result})


@app.route("/api/vision/read", methods=["POST"])
def vision_read():
    """Read text from the current screen."""
    vision = cortex.get_module('vision')
    if not vision:
        return jsonify({"error": "Vision module not available"})
    result = vision.read_screen()
    return jsonify({"text": result})


@app.route("/api/vision/error", methods=["POST"])
def vision_error():
    """Detect and explain errors on screen."""
    vision = cortex.get_module('vision')
    if not vision:
        return jsonify({"error": "Vision module not available"})
    result = vision.explain_error()
    return jsonify({"analysis": result})


if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "localhost"

    print("=" * 50)
    print("FRIDAY AI is running!")
    print(f"Local:   http://127.0.0.1:5000")
    print(f"Network: http://{local_ip}:5000")
    print("Press Ctrl+C to stop.")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
