"""
Layra Memory Module
============================
Manages short-term conversation context and long-term persistent memory.
Stores user preferences, frequently used commands, and notes.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("layra.memory")


class Memory:
    """
    Persistent memory system for Layra
    Stores user preferences, notes, command history, and custom data.
    """

    def __init__(self, memory_file: Path, preferences_file: Path):
        self.memory_file = memory_file
        self.preferences_file = preferences_file
        self._memory = self._load(memory_file, default={
            "notes": [],
            "reminders": [],
            "command_history": [],
            "user_facts": {},
            "habits": {},
            "custom_data": {},
            "created_at": datetime.now().isoformat()
        })
        self._preferences = self._load(preferences_file, default={
            "user_name": "Sir",
            "preferred_browser": "Safari",
            "preferred_language": "hinglish",
            "home_city": "New Delhi",
            "favorite_apps": [],
            "wake_up_greeting": True,
        })

    def _load(self, file_path: Path, default: dict) -> dict:
        """Load data from JSON file or return defaults."""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load {file_path}: {e}")
        return default

    def _save_memory(self):
        """Save memory to disk."""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump(self._memory, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Could not save memory: {e}")

    def _save_preferences(self):
        """Save preferences to disk."""
        try:
            self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.preferences_file, 'w') as f:
                json.dump(self._preferences, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Could not save preferences: {e}")

    # --- Notes ---
    def add_note(self, content: str, title: str = None) -> str:
        """Add a note to memory."""
        note = {
            "title": title or f"Note {len(self._memory['notes']) + 1}",
            "content": content,
            "created_at": datetime.now().isoformat(),
        }
        self._memory["notes"].append(note)
        self._save_memory()
        logger.info(f"📝 Note saved: {note['title']}")
        return f"Note saved: {note['title']}"

    def get_notes(self, count: int = 5) -> list:
        """Get recent notes."""
        return self._memory["notes"][-count:]

    def search_notes(self, keyword: str) -> list:
        """Search notes by keyword."""
        keyword_lower = keyword.lower()
        return [
            n for n in self._memory["notes"]
            if keyword_lower in n.get("content", "").lower()
            or keyword_lower in n.get("title", "").lower()
        ]

    # --- Command History ---
    def log_command(self, command: str, result: str = ""):
        """Log a command to history."""
        entry = {
            "command": command,
            "result": result[:200],
            "timestamp": datetime.now().isoformat()
        }
        self._memory["command_history"].append(entry)
        # Keep only last 100 commands
        if len(self._memory["command_history"]) > 100:
            self._memory["command_history"] = self._memory["command_history"][-100:]
        self._save_memory()

    def get_recent_commands(self, count: int = 10) -> list:
        """Get recent command history."""
        return self._memory["command_history"][-count:]

    # --- Reminders ---
    def add_reminder(self, content: str, due_time: str = None) -> str:
        """Add a reminder."""
        reminder = {
            "content": content,
            "due_time": due_time,
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        self._memory["reminders"].append(reminder)
        self._save_memory()
        return f"Reminder set: {content}"

    def get_pending_reminders(self) -> list:
        """Get incomplete reminders."""
        return [r for r in self._memory["reminders"] if not r.get("completed")]

    # --- Custom Data ---
    def set(self, key: str, value):
        """Store custom key-value data."""
        self._memory["custom_data"][key] = value
        self._save_memory()

    def get(self, key: str, default=None):
        """Retrieve custom data."""
        return self._memory["custom_data"].get(key, default)

    # --- User Facts & Learning ---
    def remember_fact(self, key: str, value: str) -> str:
        """Store a fact or preference about the user."""
        if "user_facts" not in self._memory:
            self._memory["user_facts"] = {}
        self._memory["user_facts"][key] = value
        self._save_memory()
        logger.info(f"🧠 Memory learned: {key} = {value}")
        return f"Learned & Saved: {key} -> {value}"

    def forget_fact(self, key: str) -> str:
        """Remove a stored user fact."""
        if "user_facts" in self._memory and key in self._memory["user_facts"]:
            del self._memory["user_facts"][key]
            self._save_memory()
            return f"Forgotten: {key}"
        return f"Fact '{key}' not found"

    def get_all_facts(self) -> dict:
        """Retrieve all stored user facts and habits."""
        return self._memory.get("user_facts", {})

    def auto_analyze_habits(self):
        """Analyze command history to automatically detect user habits."""
        history = self._memory.get("command_history", [])
        if not history:
            return

        # App usage frequency
        app_counts = {}
        song_counts = {}
        for item in history:
            cmd = item.get("command", "").lower()
            if "open " in cmd:
                app = cmd.split("open ")[-1].strip()
                app_counts[app] = app_counts.get(app, 0) + 1
            if "play " in cmd:
                song = cmd.split("play ")[-1].strip()
                song_counts[song] = song_counts.get(song, 0) + 1

        top_apps = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_songs = sorted(song_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        habits = self._memory.get("habits", {})
        if top_apps:
            habits["most_used_apps"] = [app[0] for app in top_apps]
        if top_songs:
            habits["frequently_requested_music"] = [s[0] for s in top_songs]

        self._memory["habits"] = habits
        self._save_memory()

    def get_memory_context(self) -> str:
        """Build a clean summary string of all learned memory context for the AI prompt."""
        self.auto_analyze_habits()
        lines = []

        # Stored preferences
        user_name = self.get_preference("user_name", "Sir")
        lines.append(f"- User Name: {user_name}")
        lines.append(f"- Home City: {self.home_city}")

        # Explicit user facts learned
        facts = self.get_all_facts()
        if facts:
            lines.append("- Learned User Facts & Habits:")
            for k, v in facts.items():
                lines.append(f"  • {k.replace('_', ' ').title()}: {v}")

        # Auto-detected habits
        habits = self._memory.get("habits", {})
        if habits.get("most_used_apps"):
            lines.append(f"- Frequently Used Apps: {', '.join(habits['most_used_apps'])}")
        if habits.get("frequently_requested_music"):
            lines.append(f"- Favorite/Recent Songs: {', '.join(habits['frequently_requested_music'])}")

        # Recent notes if any
        notes = self.get_notes(3)
        if notes:
            lines.append("- Recent User Notes:")
            for n in notes:
                lines.append(f"  • [{n.get('title')}]: {n.get('content')}")

        return "\n".join(lines)

    # --- Preferences ---
    def get_preference(self, key: str, default=None):
        """Get a user preference."""
        return self._preferences.get(key, default)

    def set_preference(self, key: str, value):
        """Set a user preference."""
        self._preferences[key] = value
        self._save_preferences()
        logger.info(f"⚙️ Preference updated: {key} = {value}")

    @property
    def user_name(self) -> str:
        return self._preferences.get("user_name", "Sir")

    @property
    def home_city(self) -> str:
        return self._preferences.get("home_city", "New Delhi")

