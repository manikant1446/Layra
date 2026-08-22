"""
Layra Calendar & Reminders Module
=====================================
macOS Calendar and Reminders integration via AppleScript.
"""

import logging
import subprocess
from datetime import datetime, timedelta

logger = logging.getLogger("layra.calendar")


def run_applescript(script: str) -> str:
    try:
        result = subprocess.run(
            ['/usr/bin/osascript', '-e', script],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"AppleScript error: {e}")
        return f"Error: {e}"


class CalendarManager:
    """macOS Calendar & Reminders integration."""

    # ==========================================
    # Calendar Events
    # ==========================================

    @staticmethod
    def get_todays_events() -> str:
        """Get all events for today."""
        script = '''
        set today to current date
        set startOfDay to today - (time of today)
        set endOfDay to startOfDay + 86399

        set eventList to {}
        tell application "Calendar"
            set allCalendars to every calendar
            repeat with cal in allCalendars
                set calEvents to (every event of cal whose start date ≥ startOfDay and start date ≤ endOfDay)
                repeat with evt in calEvents
                    set evtTime to time string of (start date of evt)
                    set evtName to summary of evt
                    set end of eventList to evtTime & " - " & evtName
                end repeat
            end repeat
        end tell

        if length of eventList is 0 then
            return "No events today"
        end if

        set AppleScript's text item delimiters to linefeed
        return eventList as text
        '''
        result = run_applescript(script)
        logger.info("📅 Fetched today's events")
        return f"Today's events:\n{result}"

    @staticmethod
    def get_upcoming_events(days: int = 7) -> str:
        """Get events for the next N days."""
        script = f'''
        set today to current date
        set startOfDay to today - (time of today)
        set endDate to startOfDay + ({days} * 86400)

        set eventList to {{}}
        tell application "Calendar"
            set allCalendars to every calendar
            repeat with cal in allCalendars
                set calEvents to (every event of cal whose start date ≥ startOfDay and start date ≤ endDate)
                repeat with evt in calEvents
                    set evtDate to date string of (start date of evt)
                    set evtTime to time string of (start date of evt)
                    set evtName to summary of evt
                    set end of eventList to evtDate & " " & evtTime & " - " & evtName
                end repeat
            end repeat
        end tell

        if length of eventList is 0 then
            return "No upcoming events in next {days} days"
        end if

        set AppleScript's text item delimiters to linefeed
        return eventList as text
        '''
        result = run_applescript(script)
        logger.info(f"📅 Fetched events for next {days} days")
        return f"Upcoming events (next {days} days):\n{result}"

    @staticmethod
    def add_event(title: str, date_str: str = None, duration_minutes: int = 60) -> str:
        """Add a new calendar event."""
        if not date_str:
            # Default to tomorrow at 10am
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime("%B %d, %Y at 10:00 AM")

        script = f'''
        tell application "Calendar"
            set targetCal to first calendar whose name is "Calendar"
            set newEvent to make new event at end of events of targetCal with properties {{summary:"{title}", start date:date "{date_str}", end date:(date "{date_str}") + {duration_minutes * 60} seconds}}
        end tell
        return "Event created"
        '''
        result = run_applescript(script)
        logger.info(f"📅 Created event: {title}")
        return f"Event created: '{title}' on {date_str}"

    @staticmethod
    def open_calendar() -> str:
        """Open the Calendar app."""
        subprocess.run(['open', '-a', 'Calendar'])
        return "Calendar opened"

    # ==========================================
    # Reminders
    # ==========================================

    @staticmethod
    def add_reminder(text: str, due_date: str = None) -> str:
        """Add a new reminder."""
        if due_date:
            script = f'''
            tell application "Reminders"
                set newReminder to make new reminder with properties {{name:"{text}", due date:date "{due_date}"}}
            end tell
            return "Reminder added"
            '''
        else:
            script = f'''
            tell application "Reminders"
                set newReminder to make new reminder with properties {{name:"{text}"}}
            end tell
            return "Reminder added"
            '''
        run_applescript(script)
        logger.info(f"⏰ Reminder added: {text}")
        return f"Reminder added: '{text}'" + (f" due {due_date}" if due_date else "")

    @staticmethod
    def get_reminders() -> str:
        """Get all incomplete reminders."""
        script = '''
        tell application "Reminders"
            set reminderList to {}
            set incompleteReminders to (every reminder whose completed is false)
            repeat with r in incompleteReminders
                set end of reminderList to name of r
            end repeat
            if length of reminderList is 0 then
                return "No pending reminders"
            end if
            set AppleScript's text item delimiters to linefeed
            return reminderList as text
        end tell
        '''
        result = run_applescript(script)
        logger.info("⏰ Fetched reminders")
        return f"Pending reminders:\n{result}"

    @staticmethod
    def complete_reminder(name: str) -> str:
        """Mark a reminder as complete."""
        script = f'''
        tell application "Reminders"
            set matchingReminders to (every reminder whose name contains "{name}" and completed is false)
            if length of matchingReminders > 0 then
                set completed of first item of matchingReminders to true
                return "Reminder completed"
            else
                return "Reminder not found"
            end if
        end tell
        '''
        result = run_applescript(script)
        logger.info(f"✅ Reminder completed: {name}")
        return result

    @staticmethod
    def open_reminders() -> str:
        """Open the Reminders app."""
        subprocess.run(['open', '-a', 'Reminders'])
        return "Reminders opened"
