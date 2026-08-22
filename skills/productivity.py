"""
Layra Productivity Module
=====================================
Pomodoro timer, Focus Mode, Morning Briefing, and productivity tools.
"""

import logging
import threading
import time
import subprocess
from datetime import datetime

logger = logging.getLogger("layra.productivity")


class ProductivityManager:
    """Pomodoro, Focus Mode, Morning Briefing, and productivity tools."""

    def __init__(self, speaker=None):
        self.speaker = speaker
        self._pomodoro_thread = None
        self._pomodoro_running = False
        self._focus_mode_active = False
        self._pomodoro_count = 0

    # ==========================================
    # Pomodoro Timer
    # ==========================================

    def start_pomodoro(self, work_minutes: int = 25, break_minutes: int = 5) -> str:
        """Start a Pomodoro session (work + break cycle)."""
        if self._pomodoro_running:
            return "Pomodoro already running! Say 'stop pomodoro' to stop."

        self._pomodoro_running = True
        self._pomodoro_count += 1
        count = self._pomodoro_count

        def run():
            logger.info(f"🍅 Pomodoro #{count} started: {work_minutes}min work")
            self._notify(f"Pomodoro #{count} Started", f"Focus for {work_minutes} minutes!")
            self._speak_if_available(f"Pomodoro {count} started! Focus karo, {work_minutes} minutes work time.")

            # Work phase
            time.sleep(work_minutes * 60)

            if not self._pomodoro_running:
                return

            # Work done notification
            self._notify("Work Done! 🎉", f"Take a {break_minutes} minute break!")
            self._speak_if_available(f"Pomodoro complete! {break_minutes} minute break lo. Well done!")

            # Break phase
            time.sleep(break_minutes * 60)

            if not self._pomodoro_running:
                return

            # Break done
            self._notify("Break Over! ⚡", "Time to focus again!")
            self._speak_if_available("Break khatam! Wapas kaam shuru karo.")
            self._pomodoro_running = False

        self._pomodoro_thread = threading.Thread(target=run, daemon=True)
        self._pomodoro_thread.start()
        return f"Pomodoro #{count} started! {work_minutes}min work → {break_minutes}min break. Focus karo! 🍅"

    def stop_pomodoro(self) -> str:
        """Stop the current Pomodoro session."""
        if not self._pomodoro_running:
            return "No Pomodoro is running right now."
        self._pomodoro_running = False
        return "Pomodoro stopped. Take a break, Sir! 🛑"

    def get_pomodoro_status(self) -> str:
        """Get Pomodoro session status."""
        if self._pomodoro_running:
            return f"Pomodoro #{self._pomodoro_count} is running. Stay focused! 🍅"
        return f"No Pomodoro running. Total completed: {self._pomodoro_count}"

    # ==========================================
    # Focus Mode
    # ==========================================

    def enable_focus_mode(self, apps_to_close: list = None) -> str:
        """Enable focus mode: DND on + close distracting apps."""
        self._focus_mode_active = True

        # Enable Do Not Disturb
        subprocess.run(
            "defaults -currentHost write ~/Library/Preferences/ByHost/com.apple.notificationcenterui doNotDisturb -boolean true",
            shell=True
        )

        # Close distracting apps
        distracting = apps_to_close or ["Safari", "Mail", "Messages", "Slack", "Discord", "Twitter", "Instagram"]
        closed = []
        for app in distracting:
            result = subprocess.run(
                ['/usr/bin/osascript', '-e', f'tell application "{app}" to quit'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                closed.append(app)

        logger.info(f"🎯 Focus mode enabled, closed: {closed}")
        msg = "Focus mode ON! Do Not Disturb enabled"
        if closed:
            msg += f". Closed: {', '.join(closed)}"
        return msg

    def disable_focus_mode(self) -> str:
        """Disable focus mode."""
        self._focus_mode_active = False
        subprocess.run(
            "defaults -currentHost write ~/Library/Preferences/ByHost/com.apple.notificationcenterui doNotDisturb -boolean false",
            shell=True
        )
        return "Focus mode OFF! Notifications restored. 🔔"

    # ==========================================
    # Morning Briefing
    # ==========================================

    def get_morning_briefing(self, researcher=None, calendar=None) -> str:
        """Generate a morning briefing with time, weather, events, and news."""
        now = datetime.now()
        hour = now.hour

        # Greeting based on time
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        briefing_parts = [
            f"🌅 {greeting}, Sir!",
            f"📅 Today is {now.strftime('%A, %B %d, %Y')} — {now.strftime('%I:%M %p')}",
            "",
        ]

        # Battery status
        try:
            battery = subprocess.run(
                "pmset -g batt | grep -o '[0-9]*%' | head -1",
                shell=True, capture_output=True, text=True
            ).stdout.strip()
            charging = "charging" if "AC Power" in subprocess.run(
                "pmset -g batt", shell=True, capture_output=True, text=True
            ).stdout else "on battery"
            if battery:
                briefing_parts.append(f"🔋 Battery: {battery} ({charging})")
        except Exception:
            pass

        # Today's calendar events
        if calendar:
            try:
                events = calendar.get_todays_events()
                briefing_parts.append(f"\n{events}")
            except Exception:
                pass

        # Weather (if researcher available)
        if researcher:
            try:
                weather = researcher.get_weather("current location")
                briefing_parts.append(f"\n🌤️ Weather: {weather[:200]}")
            except Exception:
                pass

        # Quick tip
        tips = [
            "💡 Tip: Pomodoro try karo — 25min focus, 5min break!",
            "💡 Tip: Apne top 3 tasks pehle complete karo.",
            "💡 Tip: Ek kaam ek waqt mein — multitasking avoid karo.",
            "💡 Tip: Pani peeyo, stretch karo, fresh raho!",
        ]
        import random
        briefing_parts.append(f"\n{random.choice(tips)}")

        return "\n".join(briefing_parts)

    # ==========================================
    # Spotlight Search
    # ==========================================

    @staticmethod
    def spotlight_search(query: str) -> str:
        """Search using macOS Spotlight."""
        script = f'''
        tell application "System Events"
            key code 49 using command down
            delay 0.5
            keystroke "{query}"
        end tell
        '''
        subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True)
        return f"Searching Spotlight for: {query}"

    # ==========================================
    # Auto Dark Mode
    # ==========================================

    @staticmethod
    def auto_set_appearance() -> str:
        """Automatically set dark/light mode based on time of day."""
        hour = datetime.now().hour
        is_night = hour >= 19 or hour < 7

        value = "true" if is_night else "false"
        mode = "Dark" if is_night else "Light"

        script = f'''
        tell application "System Events"
            tell appearance preferences
                set dark mode to {value}
            end tell
        end tell
        '''
        subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True)
        logger.info(f"🌙 Auto-set {mode} mode (hour: {hour})")
        return f"Auto-set {mode} mode based on current time ({hour}:00)"

    # ==========================================
    # Helpers
    # ==========================================

    def _notify(self, title: str, message: str):
        """Show macOS notification."""
        script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True)

    def _speak_if_available(self, text: str):
        """Speak text if speaker is available."""
        if self.speaker:
            try:
                self.speaker.speak_async(text)
            except Exception:
                pass
