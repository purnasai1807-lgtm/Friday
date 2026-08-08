"""
FRIDAY AI - Always-On Background Listener Daemon
=================================================
This is the heart of the "works even when VS Code / app is closed" feature.

It runs as a silent background process that:
  - Continuously listens to the microphone
  - Auto-WAKES FRIDAY the instant you say "friday" / "wake up friday"
  - Then listens for your command and processes it
  - Speaks responses through the system voice
  - Runs with NO window and NO buttons — pure voice control

Start it once (or add it to Windows startup) and FRIDAY is always listening,
even when the app or VS Code is closed.

Usage:
  python friday_listener.py            # run in background (no window via start_friday_listener.bat)
  python friday_listener.py --test     # run with console output for testing
"""
import os
import sys
import time
import threading
import signal

from friday_agent import FridayAgent


class FridayListener:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.core = FridayAgent()
        self.core.is_awake = False
        self.running = True
        # Wake word list - keep it simple and robust
        self.wake_words = ["wake up friday", "hey friday", "ok friday", "hello friday", "friday"]
        self.sleep_words = ["go to sleep friday", "sleep friday", "goodbye friday", "shut down friday"]
        self._last_command = ""

    # ---------- Logging ----------
    def log(self, msg):
        if self.verbose:
            print(msg, flush=True)

    # ---------- Wake / Sleep matching ----------
    def check_wake_word(self, text):
        if not text:
            return False
        return any(w in text for w in self.wake_words)

    def check_sleep_word(self, text):
        if not text:
            return False
        return any(w in text for w in self.sleep_words)

    # ---------- Core loop ----------
    def run(self):
        """Continuous listening loop. Runs forever."""
        self.log("[FRIDAY] Always-on listener started.")
        self.core.speak("FRIDAY is online and always listening. Say friday to wake me.")

        while self.running:
            try:
                # Listen for up to 8 seconds
                text = self.core.listen(timeout=8, phrase_limit=6)
                if not text:
                    continue

                if not self.core.is_awake:
                    # STANDBY mode - only react to the wake word
                    if self.check_wake_word(text):
                        self.core.is_awake = True
                        self.log(f"[FRIDAY] Woke up via: {text}")
                        self.core.speak("Yes sir, FRIDAY at your service. How can I help?")
                    continue
                else:
                    # AWAKE mode - process commands
                    if self.check_sleep_word(text):
                        self.core.is_awake = False
                        self.log("[FRIDAY] Going to sleep.")
                        self.core.speak("Going to sleep. Say friday to wake me.")
                        continue

                    self.log(f"[YOU] {text}")
                    response = self.core.process(text)
                    self.log(f"[FRIDAY] {response}")
                    self.core.speak(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"[FRIDAY] Listener error: {e}")
                time.sleep(1)
                continue

    def stop(self):
        self.running = False


def main():
    verbose = "--test" in sys.argv
    listener = FridayListener(verbose=verbose)

    if not verbose:
        # In silent mode, we still want signal handling to allow clean shutdown
        def _handler(sig, frame):
            listener.stop()

        signal.signal(signal.SIGINT, _handler)
        signal.signal(signal.SIGTERM, _handler)

    try:
        listener.run()
    finally:
        pass


if __name__ == "__main__":
    main()
