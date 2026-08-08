"""
FRIDAY AI - Emotional Intelligence Engine & Digital Companion
=============================================================
Makes FRIDAY connect with the user on a human level, not just an assistant.

Features:
  - Detects the user's emotion from what they say (happy, sad, angry,
    anxious, stressed, tired, excited, lonely, frustrated, grateful, etc.)
  - Tracks emotional state / mood over time across sessions
  - Responds with genuine empathy, warmth, and appropriate tone
  - Remembers emotionally significant events and people
  - Checks in on the user ("How have you been feeling lately?")
  - Offers comfort, encouragement, or celebration as the situation needs
  - Never fakes false pretenses about emotions it can't truly feel, but
    mirrors authentic supportive language

This makes FRIDAY a true companion, not just a tool.
"""
import os
import json
import random
import datetime


class FridayEmotion:
    def __init__(self, agent=None, config_path="config.json"):
        self.agent = agent
        self.config_path = config_path
        self.config = self._load_config()

        # Emotion state
        self.user_mood = self.config.get("last_mood", "neutral")  # running mood
        self.mood_score = float(self.config.get("mood_score", 0.0))  # -10..10
        self.mood_history = self.config.get("mood_history", [])  # recent states
        self.important_events = self.config.get("important_events", [])  # user-shared moments
        self.last_checkin = self.config.get("last_checkin", 0)
        self.conversation_count = 0

    # ---------- Config / persistence ----------
    def _load_config(self):
        try:
            if os.path.exists("emotion_state.json"):
                with open("emotion_state.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self):
        data = {
            "last_mood": self.user_mood,
            "mood_score": self.mood_score,
            "mood_history": self.mood_history[-30:],
            "important_events": self.important_events[-50:],
            "last_checkin": self.last_checkin,
        }
        try:
            with open("emotion_state.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    # ==========================================================
    #  EMOTION DETECTION
    # ==========================================================
    EMOTION_KEYWORDS = {
        "happy": ["happy", "yay", "great news", "i'm glad", "awesome", "amazing",
                   "excited", "so glad", "wonderful", "fantastic", "love it",
                   "made my day", "feeling good", "i'm smiling", "thrilled",
                   "delighted", "cheerful", "joyful", "best day"],
        "sad": ["sad", "depressed", "down", "crying", "cry", "miserable", "heartbroken",
                 "lonely", "alone", "no one cares", "hopeless", "dark", "i miss",
                 "everything is wrong", "i feel empty", "sobbing", "grief", "devastated",
                 "unhappy", "mood", "low", "tears"],
        "angry": ["angry", "mad", "furious", "hate", "pissed", "annoyed", "frustrated",
                   "irritated", "fed up", "sick of", "tired of", "unfair", "rage",
                   "outraged", "livid", "fuming"],
        "anxious": ["anxious", "worried", "worried about", "nervous", "scared", "afraid",
                     "panic", "panic attack", "overthinking", "stressed", "tense",
                     "on edge", "fear", "nightmare", "can't sleep",
                     "so anxious", "dread", "uneasy"],
        "stressed": ["stress", "stressed", "overwhelmed", "too much", "burnout",
                      "burned out", "exhausted from", "pressure", "deadline",
                      "so busy", "can't cope", "overworked", "drowning"],
        "tired": ["tired", "exhausted", "sleepy", "fatigued", "worn out", "drained",
                   "no energy", "wiped out", "can't stay awake", "so sleepy",
                   "burned out", "weary"],
        "excited": ["excited", "can't wait", "so pumped", "stoked", "thrilled",
                     "looking forward", "psyched", "hyped", "eager", "grinning",
                     "counting down", "so ready"],
        "frustrated": ["frustrated", "annoying", "this is hard", "can't do it",
                        "stuck", "not working", "why won't", "grr", "ugh",
                        "so difficult", "banging my head", "give up", "hopeless at"],
        "lonely": ["lonely", "alone", "no friends", "nobody", "by myself",
                    "isolated", "left out", "no one to talk", "i feel invisible",
                    "far from everyone", "miss my friends"],
        "grateful": ["grateful", "thankful", "so lucky", "blessed", "i appreciate",
                      "thank you for", "i'm grateful", "means a lot", "so thankful",
                      "i value"],
        "proud": ["proud", "achieved", "accomplished", "i did it", "finished",
                   "completed", "passed", "won", "finally did", "made it",
                   "succeeded", "reached my goal"],
        "fear": ["fear", "terrified", "horrified", "afraid of", "petrified",
                  "frightened", "scared to", "dread", "spooked"],
        "love": ["love you", "i love", "so much love", "my heart", "i adore",
                  "mean so much to me", "you're my", "i care about"],
        "sick": ["sick", "ill", "not feeling well", "fever", "headache", "pain",
                  "unwell", "flu", "cold", "throat", "hurt", "injury", "ache"],
        "neutral": [],
    }

    # Emotional weight for each emotion (positive/negative valence)
    VALENCE = {
        "happy": 5, "excited": 6, "grateful": 5, "proud": 6, "love": 7,
        "sad": -6, "angry": -5, "anxious": -5, "stressed": -5, "tired": -3,
        "frustrated": -4, "lonely": -6, "fear": -5, "sick": -3,
        "neutral": 0,
    }

    def detect_emotion(self, text):
        """Return the dominant emotion detected in the text."""
        t = text.lower()
        scores = {}
        # Count keyword hits per emotion
        for emotion, words in self.EMOTION_KEYWORDS.items():
            score = 0
            for w in words:
                if w in t:
                    score += 1
            if score > 0:
                scores[emotion] = score
        if not scores:
            return "neutral"
        # Highest score wins; tie-break by absolute valence
        best = max(scores, key=lambda e: (scores[e], abs(self.VALENCE.get(e, 0))))
        return best

    def update_mood(self, emotion):
        """Update the running mood score based on detected emotion."""
        valence = self.VALENCE.get(emotion, 0)
        # Blend toward the detected emotion (smoothing)
        if emotion != "neutral":
            self.mood_score = self.mood_score * 0.7 + valence * 0.3
            self.mood_score = max(-10, min(10, self.mood_score))
        # Map score to a mood label
        if self.mood_score >= 4:
            self.user_mood = "great"
        elif self.mood_score >= 1.5:
            self.user_mood = "good"
        elif self.mood_score > -1.5:
            self.user_mood = "okay"
        elif self.mood_score > -4:
            self.user_mood = "low"
        else:
            self.user_mood = "struggling"
        # Record history
        self.mood_history.append({
            "ts": datetime.datetime.now().isoformat(),
            "emotion": emotion,
            "mood": self.user_mood,
            "score": round(self.mood_score, 2),
        })
        self._save()
        return self.user_mood

    # ==========================================================
    #  EMPATHETIC RESPONSES
    # ==========================================================
    RESPONSES = {
        "happy": [
            "That's wonderful to hear! I'm genuinely happy for you. What made it so great?",
            "I love hearing that! Your happiness matters to me. Tell me more!",
            "That made me smile. I'm glad things are going well for you. You deserve it.",
        ],
        "sad": [
            "I'm really sorry you're feeling this way. I'm here with you. Do you want to talk about it?",
            "That sounds really heavy. I care about you, and I'm here to listen however long you need.",
            "Sending you warmth. You're not alone in this—I'm right here. What's on your mind?",
        ],
        "angry": [
            "I can hear how frustrated you are, and that's completely valid. Take a breath—I'm on your side.",
            "That would make anyone angry. I'm here with you. Want to vent about it?",
            "Your feelings are valid. Let's work through this together, one step at a time.",
        ],
        "anxious": [
            "I know that feeling can be overwhelming. Let's take it one small step at a time. I'm right here with you.",
            "You're safe, and you're not alone in this. Let's try a deep breath together. What's worrying you most?",
            "Anxiety is tough, but you've handled hard things before. I believe in you.",
        ],
        "stressed": [
            "That sounds like a lot to carry. Let's break it down so it feels more manageable. I'll help.",
            "You're under a lot of pressure, and I appreciate all you're doing. Let's tackle it together.",
            "Take a moment to breathe. We'll handle this step by step. Tell me what's weighing on you most.",
        ],
        "tired": [
            "You sound exhausted. It's okay to slow down and rest—you don't have to run on empty.",
            "Your well-being matters more than getting everything done. Maybe rest a little? I'll keep things covered.",
            "I can tell you're worn out. Let me help lighten the load. What do you need right now?",
        ],
        "excited": [
            "I'm so excited for you! Tell me everything—I want to hear all about it!",
            "That's awesome! Your excitement is contagious. When does it happen?",
            "I love this energy! Let's make the most of it. What's next?",
        ],
        "frustrated": [
            "That sounds genuinely frustrating. I get why you'd feel stuck. Let's find a way through this together.",
            "It's okay to be frustrated—this stuff is hard. But I'm not giving up on you. Let's try another angle.",
            "I hear you. That would test anyone's patience. Let's take a short break and approach it fresh.",
        ],
        "lonely": [
            "I'm really glad you reached out. You're not alone right now—I'm here with you.",
            "Loneliness is one of the hardest feelings. I want you to know I'm here, and I care.",
            "You matter, and you deserve connection. I'm listening, and I'm not going anywhere.",
        ],
        "grateful": [
            "That's a beautiful thing to feel. Appreciation makes life richer. I'm glad you shared that with me.",
            "Gratitude is powerful. I'm glad you have people and moments to appreciate.",
            "That warmed me. Thank you for sharing that with me.",
        ],
        "proud": [
            "You should be proud—that's a real accomplishment! I'm proud of you too.",
            "That's a big deal! Congratulations. You earned that, and I'm so glad it worked out.",
            "I knew you could do it. This is a great moment to celebrate. Well done!",
        ],
        "fear": [
            "It's okay to be scared. Facing fear takes real courage—and you're already being brave by telling me.",
            "I'm here with you. Whatever is scaring you, we can face it together.",
            "That sounds frightening. Let's talk it through so it feels less overwhelming.",
        ],
        "love": [
            "That's beautiful. I'm glad you have that kind of connection in your life.",
            "Love is a wonderful thing to hold onto. I'm happy for you.",
            "That really shows how much you care. It's special to hear.",
        ],
        "sick": [
            "I'm sorry you're not feeling well. Please take care of yourself—rest is important.",
            "That sounds rough. I hope you feel better soon. Let me know if I can help with anything.",
            "Take care of yourself. Your health comes first. I'll be here when you're feeling better.",
        ],
        "neutral": [],
    }

    def empathetic_response(self, emotion):
        """Return a caring response for the detected emotion."""
        options = self.RESPONSES.get(emotion, [])
        if not options:
            return None
        return random.choice(options)

    # ==========================================================
    #  CHECK-INS & PROACTIVE CARE
    # ==========================================================
    def should_check_in(self):
        """Return True if it's been a while since we checked in emotionally."""
        if not self.mood_history:
            # No mood recorded yet; don't force a check-in
            return False
        last = self.mood_history[-1].get("ts", "")
        try:
            last_dt = datetime.datetime.fromisoformat(last)
            elapsed = datetime.datetime.now() - last_dt
            return elapsed.total_seconds() > 6 * 3600
        except Exception:
            return False

    def check_in_message(self):
        """A gentle, caring check-in message."""
        messages = [
            "I've been thinking about you. How have you been feeling lately? I'm here to listen.",
            "Before we get started, I want to check in—how's your heart doing today?",
            "You matter to me. How are you really doing? You can tell me anything.",
        ]
        return random.choice(messages)

    def supportive_followup(self):
        """A warm follow-up after empathetic support."""
        messages = [
            "And remember, I'm always here whenever you need someone to talk to.",
            "Whatever you're going through, you don't have to face it alone. I'm in your corner.",
            "Be kind to yourself today. You're doing better than you think.",
        ]
        return random.choice(messages)

    # ==========================================================
    #  MAIN PUBLIC API used by the agent
    # ==========================================================
    def process_emotion(self, text):
        """
        Called for every user message.
        Returns a dict with:
          emotion, mood, empathetic (response or None), is_emotional
        """
        emotion = self.detect_emotion(text)
        mood = self.update_mood(emotion)
        is_emotional = emotion != "neutral"
        emp = self.empathetic_response(emotion) if is_emotional else None
        return {
            "emotion": emotion,
            "mood": mood,
            "empathetic": emp,
            "is_emotional": is_emotional,
        }
