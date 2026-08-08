# FRIDAY AI - Voice-Only Implementation Plan

## Goal

Make FRIDAY 100% voice-controlled (no chat bot) with ALL capabilities wired
into the always-on voice listener pipeline.

## Tasks

- [x] 1. Wire `friday_control`, `friday_vision`, `friday_learning` into `FridayAgent`
     (used by friday_listener.py) so all features are reachable by voice.
- [x] 2. Strip the chat text input/log out of `friday_app.py` (pure voice desktop).
- [x] 3. Add needed optional libraries to `requirements.txt`.
- [x] 4. Update docs (README.md / HOW_TO_USE.md) to reflect voice-only + list commands.
- [x] 5. Verify listener loads all modules (syntax check).
