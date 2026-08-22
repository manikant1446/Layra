#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║   Layra - Personal AI Assistant              ║
║   Just A Rather Very Intelligent System      ║
║                                              ║
║   Voice-controlled AI assistant for macOS    ║
╚══════════════════════════════════════════════╝

Usage:
    ./venv/bin/python main.py
    python3 main.py                  # Full mode (wake word + voice)
    python3 main.py --type           # Type mode (keyboard input only)
    python3 main.py --no-voice       # No TTS output (text only)
    python3 main.py --help-commands  # Show available commands
"""

import sys
import signal
import logging
import argparse
import threading
import time
from pathlib import Path

# Setup logging
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout) if '--debug' in sys.argv else logging.NullHandler(),
    ]
)
logger = logging.getLogger("layra")


# ============================================
# Import all modules
# ============================================
from ui.terminal_ui import TerminalUI
from voice.speaker import Speaker
from voice.recognizer import SpeechRecognizer
from brain.gemini_brain import GeminiBrain
from brain.memory import Memory
from skills.system_control import SystemControl
from skills.browser import Browser
from skills.researcher import Researcher
from skills.email_manager import EmailManager
from skills.social_media import SocialMedia
from skills.project_manager import ProjectManager
from skills.utilities import Utilities
from skills.calendar_manager import CalendarManager
from skills.messaging import MessagingManager
from skills.productivity import ProductivityManager
from skills.information import InformationManager
from skills.cybersec_trainer import CyberSecTrainer
from skills.hacklab import HackLabAssistant
from skills.auto_pentest import AutoPentest


class Layra:
    """
    Main Layra orchestrator.
    Connects voice I/O, AI brain, and all skill modules.
    """

    def __init__(self, type_mode: bool = False, voice_enabled: bool = True):
        self.type_mode = type_mode
        self.voice_enabled = voice_enabled
        self.running = False
        self._wake_event = threading.Event()

        # UI
        self.ui = TerminalUI()

        # Voice
        self.speaker = Speaker(
            voice=config.TTS_VOICE,
            voice_hindi=config.TTS_VOICE_HINDI,
            rate=config.TTS_RATE,
            volume=config.TTS_VOLUME,
            pitch=config.TTS_PITCH,
            use_fallback=config.USE_FALLBACK_TTS,
        )
        self.recognizer = SpeechRecognizer(
            model_size=config.WHISPER_MODEL,
            language=config.WHISPER_LANGUAGE,
        )

        # Memory
        self.memory = Memory(config.MEMORY_FILE, config.PREFERENCES_FILE)

        # Skills
        self.system_control = SystemControl()
        self.browser = Browser(default_browser=config.DEFAULT_BROWSER)
        self.researcher = Researcher()
        self.email_manager = EmailManager(credentials_path=config.GMAIL_CREDENTIALS_PATH)
        self.social_media = SocialMedia()
        self.project_manager = ProjectManager(default_workspace=str(config.BASE_DIR))
        self.utilities = Utilities(memory=self.memory, speaker=self.speaker)
        self.calendar_manager = CalendarManager()
        self.messaging = MessagingManager()
        self.productivity = ProductivityManager(speaker=self.speaker)
        self.information = InformationManager()
        self.cybersec = CyberSecTrainer()
        self.hacklab = HackLabAssistant()
        self.pentest = AutoPentest()

        # AI Brain
        self.brain = self._init_brain()

    def _init_brain(self) -> GeminiBrain:
        """Initialize the AI brain with all skill handlers."""
        brain = GeminiBrain(
            api_key=config.GEMINI_API_KEY,
            model_name=config.GEMINI_MODEL,
            personality=config.LAYRA_PERSONALITY,
            memory=self.memory,
        )

        # Register all skill handlers
        brain.register_handlers({
            # System Control
            "open_application": self.system_control.open_application,
            "close_application": self.system_control.close_application,
            "set_volume": self.system_control.set_volume,
            "set_brightness": self.system_control.set_brightness,
            "toggle_wifi": self.system_control.toggle_wifi,
            "toggle_bluetooth": self.system_control.toggle_bluetooth,
            "toggle_dark_mode": self.system_control.toggle_dark_mode,
            "lock_screen": self.system_control.lock_screen,
            "sleep_mac": self.system_control.sleep_mac,
            "take_screenshot": self.system_control.take_screenshot,
            "get_system_info": self.system_control.get_system_info,
            "empty_trash": self.system_control.empty_trash,
            "show_notification": self.system_control.show_notification,
            "control_music": self.system_control.control_music,
            "run_shell_command": self.system_control.run_shell_command,
            # New system features
            "get_battery_status": self.system_control.get_battery_status,
            "get_network_info": self.system_control.get_network_info,
            "get_active_window": self.system_control.get_active_window,
            "toggle_do_not_disturb": self.system_control.toggle_do_not_disturb,
            "get_clipboard_text": self.system_control.get_clipboard_text,
            "copy_to_clipboard": self.system_control.copy_to_clipboard,
            "open_folder": self.system_control.open_folder,
            "open_downloads": self.system_control.open_downloads,
            "open_documents": self.system_control.open_documents,
            "open_desktop": self.system_control.open_desktop,
            "get_running_apps": self.system_control.get_running_apps,
            "hide_application": self.system_control.hide_application,
            "sleep_display": self.system_control.sleep_display,
            "get_uptime": self.system_control.get_uptime,
            "type_text": self.system_control.type_text,
            "press_key": self.system_control.press_key,

            # Browser
            "open_url": self.browser.open_url,
            "search_web": self.browser.search_web,
            "search_youtube": self.browser.search_youtube,

            # Research
            "research_topic": self.researcher.research_topic,
            "get_weather": self.researcher.get_weather,
            "get_news": self.researcher.get_news,

            # Email
            "check_emails": self.email_manager.check_emails,
            "send_email": self.email_manager.send_email,
            "search_emails": self.email_manager.search_emails,

            # Social Media
            "open_social_media": self.social_media.open_social_media,

            # Project Management
            "create_file": self.project_manager.create_file,
            "read_file": self.project_manager.read_file,
            "git_operation": self.project_manager.git_operation,

            # Utilities
            "set_timer": self.utilities.set_timer,
            "take_note": self.utilities.take_note,
            "get_date_time": self.utilities.get_date_time,
            "calculate": self.utilities.calculate,

            # Calendar & Reminders
            "get_todays_events": self.calendar_manager.get_todays_events,
            "get_upcoming_events": self.calendar_manager.get_upcoming_events,
            "add_event": self.calendar_manager.add_event,
            "open_calendar": self.calendar_manager.open_calendar,
            "add_reminder": self.calendar_manager.add_reminder,
            "get_reminders": self.calendar_manager.get_reminders,
            "complete_reminder": self.calendar_manager.complete_reminder,
            "open_reminders": self.calendar_manager.open_reminders,

            # Messaging
            "send_imessage": self.messaging.send_imessage,
            "get_unread_messages": self.messaging.get_unread_messages,
            "open_messages": self.messaging.open_messages,
            "open_whatsapp": self.messaging.open_whatsapp,
            "send_whatsapp_message": self.messaging.send_whatsapp_message,
            "start_facetime": self.messaging.start_facetime,
            "start_audio_call": self.messaging.start_audio_call,

            # Productivity
            "start_pomodoro": self.productivity.start_pomodoro,
            "stop_pomodoro": self.productivity.stop_pomodoro,
            "get_pomodoro_status": self.productivity.get_pomodoro_status,
            "enable_focus_mode": self.productivity.enable_focus_mode,
            "disable_focus_mode": self.productivity.disable_focus_mode,
            "get_morning_briefing": lambda: self.productivity.get_morning_briefing(
                researcher=self.researcher,
                calendar=self.calendar_manager
            ),
            "spotlight_search": self.productivity.spotlight_search,
            "auto_set_appearance": self.productivity.auto_set_appearance,

            # Information
            "get_stock_price": self.information.get_stock_price,
            "get_multiple_stocks": self.information.get_multiple_stocks,
            "convert_currency": self.information.convert_currency,
            "get_inr_rates": self.information.get_inr_rates,
            "translate_text": lambda text, lang="Hindi": self.information.translate_text(
                text, lang, gemini_brain=self.brain
            ),
            "read_screen_text": self.information.read_screen_text,
            "get_wikipedia_summary": self.information.get_wikipedia_summary,
            "get_cricket_score": self.information.get_cricket_score,

            # CyberSecurity Training (Authorized/Educational use only)
            "explain_recon": self.cybersec.explain_recon,
            "whois_lookup": self.cybersec.whois_lookup,
            "dns_lookup": self.cybersec.dns_lookup,
            "ip_info": self.cybersec.ip_info,
            "port_scan": self.cybersec.port_scan,
            "ping_host": self.cybersec.ping_host,
            "traceroute": self.cybersec.traceroute,
            "banner_grab": self.cybersec.banner_grab,
            "subdomain_finder": self.cybersec.subdomain_finder,
            "hacking_phases": self.cybersec.hacking_phases,
            "common_attack_types": self.cybersec.common_attack_types,
            "ctf_resources": self.cybersec.ctf_resources,

            # Practical HackLab (TryHackMe / HackTheBox)
            "password_cracking_guide": self.hacklab.password_cracking_guide,
            "crack_hash_online": self.hacklab.crack_hash_online,
            "sql_injection_guide": self.hacklab.sql_injection_guide,
            "xss_guide": self.hacklab.xss_guide,
            "network_analysis_guide": self.hacklab.network_analysis_guide,
            "metasploit_guide": self.hacklab.metasploit_guide,
            "privesc_guide": self.hacklab.privesc_guide,
            "reverse_shell_guide": self.hacklab.reverse_shell_guide,
            "burpsuite_guide": self.hacklab.burpsuite_guide,
            "ctf_methodology": self.hacklab.ctf_methodology,
            "tryhackme_rooms": self.hacklab.tryhackme_rooms,

            # Auto Pentest (Your own targets only)
            "full_pentest": self.pentest.full_pentest,
            "quick_scan": self.pentest.quick_scan,
            "web_scan": self.pentest.web_scan,
            "brute_ssh": self.pentest.brute_ssh,
        })

        return brain

    def _on_wake_word(self):
        """Callback when wake word is detected."""
        self._wake_event.set()

    def _speak(self, text: str):
        """Speak text if voice is enabled."""
        if self.voice_enabled:
            self.ui.show_speaking()
            self.speaker.speak(text)

    def _process_command(self, user_input: str):
        """Process a user command through the AI brain."""
        if not user_input.strip():
            return

        # Show user input
        self.ui.show_user_input(user_input)

        # Check for special commands
        lower = user_input.lower().strip()

        if lower in ['quit', 'exit', 'bye', 'goodbye', 'layra quit', 'band karo', 'shut down layra']:
            self._speak("Goodbye Sir. All systems shutting down. Have a great day!")
            self.ui.show_goodbye()
            self.running = False
            return

        if lower in ['help', 'commands', 'kya kya kar sakte ho']:
            self.ui.show_help()
            self._speak("Here are all the things I can do for you, Sir. Take a look at the screen.")
            return

        if lower in ['clear', 'clear history', 'forget everything']:
            self.brain.clear_history()
            self._speak("Conversation history cleared, Sir. Fresh start!")
            self.ui.show_success("History cleared")
            return

        # Process through AI brain
        self.ui.show_thinking()

        try:
            response = self.brain.process(user_input)
            if not response or not isinstance(response, str):
                response = "Task completed, Sir."

            # Show and speak the response
            self.ui.show_layra_response(response)
            self._speak(response)

            # Log to memory
            self.memory.log_command(user_input, str(response)[:200])


        except Exception as e:
            error_msg = f"Sorry Sir, something went wrong: {str(e)[:100]}"
            self.ui.show_error(str(e))
            self._speak(error_msg)
            logger.error(f"Command processing error: {e}")

    def run(self):
        """Main run loop."""
        self.running = True

        # Show startup
        self.ui.show_banner()

        # Startup greeting
        greeting = "Good day, Sir. Layra is online and all systems are operational. How can I assist you?"
        hour = time.localtime().tm_hour
        if hour < 12:
            greeting = "Good morning, Sir. Layra is online. All systems operational. Ready for your commands."
        elif hour < 17:
            greeting = "Good afternoon, Sir. Layra at your service. All systems are go."
        elif hour < 21:
            greeting = "Good evening, Sir. Layra is online. What can I do for you?"
        else:
            greeting = "Working late, Sir? Layra is here. All systems operational."

        self.ui.show_layra_response(greeting)
        self._speak(greeting)

        # Start wake word listener if not in type mode
        listener = None
        if not self.type_mode and config.ENABLE_WAKE_WORD:
            try:
                from voice.listener import WakeWordListener
                listener = WakeWordListener(
                    access_key=config.PICOVOICE_ACCESS_KEY,
                    sensitivity=config.WAKE_WORD_SENSITIVITY,
                    on_wake_word=self._on_wake_word,
                )
                listener.start()
                self.ui.show_info("Wake word detection active — say 'Layra'")
            except Exception as e:
                logger.warning(f"Wake word init failed: {e}")
                self.ui.show_warning(f"Wake word unavailable: {e}")
                self.type_mode = True  # Fallback to type mode

        # Start single Enter listener thread if voice mode
        if not self.type_mode:
            self._start_enter_listener()

        # Main loop
        self.ui.show_divider()

        try:
            while self.running:
                if self.type_mode:
                    # Type mode - get text input
                    try:
                        self.ui.console.print("\n[bold cyan]🎤 You:[/bold cyan] ", end="")
                        user_input = input().strip()
                        if user_input:
                            self._process_command(user_input)
                    except EOFError:
                        break
                    except KeyboardInterrupt:
                        break
                else:
                    # Voice mode - wait for wake word or Enter key
                    self.ui.show_listening()

                    # Wait for wake word detection or manual Enter
                    self._wake_event.clear()

                    # Wait for either wake word or enter
                    self._wake_event.wait()

                    if not self.running:
                        break

                    # Clear event immediately after waking
                    self._wake_event.clear()

                    # Wake word detected! Record and process
                    try:
                        if listener:
                            listener.pause()

                        self.ui.show_recording()
                        self._speak("")  # Small pause after activation

                        # Record user speech
                        user_text = self.recognizer.listen_and_transcribe()

                        if user_text:
                            lower_text = user_text.lower().strip()
                            # Strict check: Ignore "Hey Layra", "Hi Layra", "Hello Layra"
                            if (lower_text.startswith("hey layra") or 
                                lower_text.startswith("hey, layra") or 
                                lower_text.startswith("hi layra") or 
                                lower_text.startswith("hello layra")):
                                logger.info("⚠️ Ignored 'Hey Layra' trigger — strictly configured for 'Layra' only.")
                                self.ui.show_info("Ignoring 'Hey Layra'. Please say just 'Layra' to activate.")
                            else:
                                # Strip leading "layra" if present
                                cleaned_text = user_text
                                if lower_text.startswith("layra"):
                                    cleaned_text = user_text[6:].lstrip(" ,.:!").strip()
                                    if not cleaned_text:
                                        cleaned_text = "layra"
                                self._process_command(cleaned_text)
                        else:
                            self.ui.show_info("Didn't catch that. Try again?")

                    finally:
                        if listener:
                            listener.resume()
                        self._wake_event.clear()

                self.ui.show_divider()

        except KeyboardInterrupt:
            pass
        finally:
            # Cleanup
            if listener:
                listener.stop()
            self.speaker.stop()
            self.ui.show_goodbye()

    def _start_enter_listener(self):
        """Start a single background thread to detect Enter key presses non-blockingly."""
        import select

        def enter_loop():
            while self.running:
                try:
                    # Check if sys.stdin is an interactive terminal
                    if not sys.stdin or sys.stdin.closed or not hasattr(sys.stdin, 'isatty') or not sys.stdin.isatty():
                        time.sleep(0.5)
                        continue

                    if select.select([sys.stdin], [], [], 0.2)[0]:
                        line = sys.stdin.readline()
                        if not line:  # EOF
                            time.sleep(0.5)
                            continue
                        if self.running:
                            self._wake_event.set()
                    else:
                        time.sleep(0.05)
                except (EOFError, KeyboardInterrupt):
                    self.running = False
                    self._wake_event.set()
                    break
                except Exception:
                    time.sleep(0.2)

        thread = threading.Thread(target=enter_loop, daemon=True)
        thread.start()


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Layra - Personal AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                  # Full mode with wake word
    python main.py --type           # Type commands (no voice input)
    python main.py --no-voice       # Text output only (no speech)
    python main.py --type --no-voice  # Silent text mode
    python main.py --debug          # Show debug logs
        """
    )

    parser.add_argument('--type', action='store_true',
                        help='Type mode - enter commands via keyboard')
    parser.add_argument('--no-voice', action='store_true',
                        help='Disable voice output (text only)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--help-commands', action='store_true',
                        help='Show available commands and exit')

    args = parser.parse_args()

    # Check for required API key
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_gemini_api_key_here":
        console_temp = __import__('rich.console', fromlist=['Console']).Console()
        console_temp.print("""
[bold red]❌ Gemini API Key not found![/bold red]

To get started:
1. Get a free API key from [bold cyan]https://aistudio.google.com/[/bold cyan]
2. Copy .env.example to .env:  [bold]cp .env.example .env[/bold]
3. Add your key to the .env file: [bold]GEMINI_API_KEY=your_key_here[/bold]

Then run again: [bold]python main.py --type[/bold]
""")
        sys.exit(1)

    if args.help_commands:
        ui = TerminalUI()
        ui.show_banner()
        ui.show_help()
        sys.exit(0)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Run Layra
    layra = Layra(
        type_mode=args.type,
        voice_enabled=not args.no_voice,
    )
    layra.run()


if __name__ == "__main__":
    main()
