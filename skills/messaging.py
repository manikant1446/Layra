"""
Layra Messaging Module
=====================================
Send messages via macOS Messages (iMessage/SMS) and WhatsApp Desktop.
"""

import logging
import subprocess
import time

logger = logging.getLogger("layra.messaging")


def run_applescript(script: str) -> str:
    try:
        result = subprocess.run(
            ['/usr/bin/osascript', '-e', script],
            capture_output=True, text=True, timeout=20
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"AppleScript error: {e}")
        return f"Error: {e}"


class MessagingManager:
    """macOS Messages, iMessage, and WhatsApp integration."""

    # ==========================================
    # iMessage / SMS via Messages App
    # ==========================================

    @staticmethod
    def send_imessage(contact: str, message: str) -> str:
        """Send an iMessage/SMS to a contact or phone number."""
        safe_message = message.replace('"', '\\"').replace("'", "\\'")
        safe_contact = contact.replace('"', '\\"')

        script = f'''
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "{safe_contact}" of targetService
            send "{safe_message}" to targetBuddy
        end tell
        '''
        result = run_applescript(script)
        if "Error" in result:
            # Fallback: try by phone number directly
            script2 = f'''
            tell application "Messages"
                send "{safe_message}" to buddy "{safe_contact}" of (1st account)
            end tell
            '''
            result = run_applescript(script2)

        logger.info(f"💬 Message sent to {contact}")
        return f"Message sent to {contact}: '{message[:50]}...'" if len(message) > 50 else f"Message sent to {contact}: '{message}'"

    @staticmethod
    def get_unread_messages() -> str:
        """Check for unread messages in Messages app."""
        script = '''
        tell application "Messages"
            set unreadCount to 0
            set unreadList to {}
            repeat with aChat in chats
                if unread count of aChat > 0 then
                    set unreadCount to unreadCount + (unread count of aChat)
                    set chatName to name of aChat
                    set end of unreadList to chatName & " (" & (unread count of aChat) & " unread)"
                end if
            end repeat
            if unreadCount is 0 then
                return "No unread messages"
            end if
            set AppleScript's text item delimiters to linefeed
            return "Unread messages: " & unreadCount & linefeed & (unreadList as text)
        end tell
        '''
        result = run_applescript(script)
        logger.info("💬 Checked unread messages")
        return result

    @staticmethod
    def open_messages(contact: str = None) -> str:
        """Open Messages app, optionally focused on a contact."""
        if contact:
            script = f'''
            tell application "Messages"
                activate
                set targetBuddy to buddy "{contact}" of (1st account)
                open conversation with targetBuddy
            end tell
            '''
            run_applescript(script)
            return f"Opened Messages with {contact}"
        else:
            subprocess.run(['open', '-a', 'Messages'])
            return "Messages app opened"

    # ==========================================
    # WhatsApp Desktop
    # ==========================================

    @staticmethod
    def open_whatsapp(contact: str = None) -> str:
        """Open WhatsApp Desktop."""
        subprocess.run(['open', '-a', 'WhatsApp'])
        time.sleep(1.5)
        if contact:
            return f"WhatsApp opened. Search for {contact} to message them."
        return "WhatsApp opened"

    @staticmethod
    def send_whatsapp_message(contact: str, message: str) -> str:
        """Send a WhatsApp message via desktop app using keyboard automation."""
        safe_message = message.replace('"', '\\"').replace("'", "\\'")

        # Open WhatsApp and search for contact
        subprocess.run(['open', '-a', 'WhatsApp'])
        time.sleep(1.5)

        script = f'''
        tell application "WhatsApp"
            activate
        end tell
        delay 1
        tell application "System Events"
            tell process "WhatsApp"
                -- Cmd+F to search
                keystroke "f" using command down
                delay 0.5
                keystroke "{contact}"
                delay 1
                key code 36
                delay 0.8
                -- Type the message
                keystroke "{safe_message}"
                delay 0.3
                key code 36
            end tell
        end tell
        '''
        run_applescript(script)
        logger.info(f"📱 WhatsApp message sent to {contact}")
        return f"WhatsApp message sent to {contact}"

    # ==========================================
    # FaceTime
    # ==========================================

    @staticmethod
    def start_facetime(contact: str) -> str:
        """Start a FaceTime call with a contact."""
        import subprocess
        subprocess.run(['open', f'facetime://{contact}'])
        logger.info(f"📞 FaceTime started with {contact}")
        return f"Starting FaceTime call with {contact}..."

    @staticmethod
    def start_audio_call(contact: str) -> str:
        """Start a FaceTime audio call."""
        import subprocess
        subprocess.run(['open', f'facetime-audio://{contact}'])
        logger.info(f"📞 Audio call started with {contact}")
        return f"Starting audio call with {contact}..."
