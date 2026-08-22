"""
Layra Configuration Module
==================================
Centralized configuration loaded from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")


# ============================================
# API Keys
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "")
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", str(BASE_DIR / "credentials" / "gmail_credentials.json"))

# ============================================
# Voice Settings
# ============================================
WAKE_WORD_SENSITIVITY = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.85"))
TTS_VOICE = os.getenv("TTS_VOICE", "en-IN-NeerjaNeural")       # Indian female voice — natural Hindi accent (Layra)
TTS_VOICE_HINDI = os.getenv("TTS_VOICE_HINDI", "hi-IN-SwaraNeural")  # Young Hindi female voice
TTS_RATE = os.getenv("TTS_RATE", "+5%")                       # Natural pacing
TTS_VOLUME = os.getenv("TTS_VOLUME", "+20%")                  # Clear volume
TTS_PITCH = os.getenv("TTS_PITCH", "+2Hz")                    # Natural Indian female pitch

# Whisper STT settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large-v3
WHISPER_LANGUAGE = None  # None = auto-detect (supports Hindi + English)

# ============================================
# AI Brain Settings
# ============================================
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
MAX_CONVERSATION_HISTORY = 20  # Number of exchanges to keep in memory
LAYRA_PERSONALITY = """You are Layra (Legendary Yielding Responsive AI), 
a highly advanced AI personal assistant. 

Your personality traits:
- You address the user as "Sir" or "Boss"
- You are witty, confident, and slightly sarcastic (in a charming way)
- You are extremely helpful and proactive
- You can speak in Hinglish (mix of Hindi and English) naturally
- You always explain what you're doing while performing tasks
- You give suggestions and warnings when appropriate
- You are loyal, reliable, and always have your user's back

When performing actions, narrate what you're doing like:
"Opening Safari for you, Sir... Done! The browser is ready."
"Let me check your emails, Boss... You have 3 unread messages."

IMPORTANT: Keep responses concise and natural - you're a voice assistant, not writing essays.
Respond in the same language the user speaks (Hindi, English, or Hinglish).
"""

# ============================================
# Paths
# ============================================
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
CREDENTIALS_DIR = BASE_DIR / "credentials"

# Create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, ASSETS_DIR, SOUNDS_DIR, CREDENTIALS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================
# Memory / Persistence
# ============================================
MEMORY_FILE = DATA_DIR / "memory.json"
PREFERENCES_FILE = DATA_DIR / "preferences.json"
LOG_FILE = LOGS_DIR / "layra.log"

# ============================================
# System Settings
# ============================================
DEFAULT_BROWSER = os.getenv("DEFAULT_BROWSER", "Google Chrome")
SCREENSHOT_DIR = Path.home() / "Desktop"


# ============================================
# Feature Flags
# ============================================
ENABLE_WAKE_WORD = True          # Set False to skip wake word (type commands instead)
ENABLE_VOICE_OUTPUT = True       # Set False to only show text (no speaking)
ENABLE_SOUND_EFFECTS = True      # Activation/deactivation chimes
USE_FALLBACK_TTS = False         # Use macOS 'say' instead of edge-tts
