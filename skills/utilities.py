"""
Layra Utilities Module
================================
Timer, calculator, notes, date/time, and misc utilities.
"""

import logging
import threading
import time
import math
from datetime import datetime

logger = logging.getLogger("layra.utilities")


class Utilities:
    """Collection of utility functions for daily tasks."""

    def __init__(self, memory=None, speaker=None):
        """
        Args:
            memory: Memory instance for saving notes
            speaker: Speaker instance for timer announcements
        """
        self.memory = memory
        self.speaker = speaker
        self._active_timers = []

    # ==========================================
    # Timer & Alarms
    # ==========================================

    def set_timer(self, minutes: float, label: str = None) -> str:
        """Set a countdown timer."""
        label = label or f"{minutes} minute timer"
        seconds = minutes * 60

        def timer_callback():
            time.sleep(seconds)
            msg = f"Timer complete! {label}"
            logger.info(f"⏰ {msg}")

            # Try to announce via voice
            if self.speaker:
                self.speaker.speak(f"Sir, your timer is up. {label}")

            # Show notification
            try:
                import subprocess
                subprocess.run([
                    '/usr/bin/osascript', '-e',
                    f'display notification "{label}" with title "⏰ Timer Complete" sound name "Glass"'
                ])
            except Exception:
                pass

        thread = threading.Thread(target=timer_callback, daemon=True)
        thread.start()
        self._active_timers.append({"label": label, "minutes": minutes, "thread": thread})

        logger.info(f"⏱️ Timer set: {label} ({minutes} min)")
        return f"Timer set for {minutes} minutes: {label}"

    # ==========================================
    # Notes
    # ==========================================

    def take_note(self, content: str, title: str = None) -> str:
        """Save a note."""
        if self.memory:
            return self.memory.add_note(content, title)
        else:
            # Fallback: save to a file
            from pathlib import Path
            notes_dir = Path.home() / "Layra" / "data"
            notes_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            note_file = notes_dir / f"note_{timestamp}.txt"
            note_title = title or f"Note - {timestamp}"
            note_file.write_text(f"# {note_title}\n\n{content}\n\nCreated: {datetime.now().isoformat()}")
            return f"Note saved: {note_title}"

    def get_notes(self) -> str:
        """Retrieve recent notes."""
        if self.memory:
            notes = self.memory.get_notes(5)
            if not notes:
                return "No notes found"
            result = "Your recent notes:\n"
            for i, note in enumerate(notes, 1):
                result += f"{i}. {note['title']}: {note['content'][:100]}\n"
            return result
        return "Memory module not available"

    # ==========================================
    # Date & Time
    # ==========================================

    def get_date_time(self) -> str:
        """Get current date and time."""
        now = datetime.now()
        day_name = now.strftime("%A")
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        return f"Today is {day_name}, {date_str}. The time is {time_str}."

    # ==========================================
    # Calculator
    # ==========================================

    def calculate(self, expression: str) -> str:
        """Safely evaluate a mathematical expression."""
        try:
            # Safe math evaluation - only allow math operations
            allowed_names = {
                k: v for k, v in math.__dict__.items()
                if not k.startswith("__")
            }
            allowed_names.update({
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'int': int, 'float': float, 'pow': pow, 'sum': sum,
            })

            # Remove anything that could be dangerous
            for dangerous in ['import', 'exec', 'eval', 'open', 'os', 'sys', '__']:
                if dangerous in expression.lower():
                    return f"Cannot evaluate: {expression} (contains restricted keywords)"

            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"{expression} = {result}"

        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Calculation error: {e}"

    # ==========================================
    # Jokes & Fun
    # ==========================================

    def get_joke(self) -> str:
        """Get a random joke."""
        try:
            import requests
            response = requests.get(
                "https://official-joke-api.appspot.com/random_joke",
                timeout=5
            )
            if response.status_code == 200:
                joke = response.json()
                return f"{joke['setup']}\n{joke['punchline']}"
        except Exception:
            pass

        # Fallback jokes
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why do Java developers wear glasses? Because they can't C#!",
            "What's a programmer's favorite hangout place? Foo Bar!",
            "Why was the computer cold? It left its Windows open!",
            "How many programmers does it take to change a light bulb? None. It's a hardware problem.",
        ]
        import random
        return random.choice(jokes)

    # ==========================================
    # Motivational Quotes
    # ==========================================

    def get_motivation(self) -> str:
        """Get a motivational quote."""
        quotes = [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Innovation distinguishes between a leader and a follower. - Steve Jobs",
            "Stay hungry, stay foolish. - Steve Jobs",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "It does not matter how slowly you go as long as you do not stop. - Confucius",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Churchill",
            "The only limit to our realization of tomorrow is our doubts of today. - FDR",
            "Believe you can and you're halfway there. - Theodore Roosevelt",
            "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
            "Kaam karo, success khud aayega. - Layra",
        ]
        import random
        return random.choice(quotes)
