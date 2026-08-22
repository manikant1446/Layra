"""
Layra System Control Module
=====================================
Controls macOS system operations using AppleScript, shell commands,
and native macOS utilities. This is the backbone of Layra's Mac control.
"""

from __future__ import annotations

import subprocess
import logging
import os
import time
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("layra.system")


def _get_spotify_track_uri(song_name: str) -> str | None:
    """
    Search Spotify for a track and return its URI (spotify:track:XXX).
    Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env.
    Uses the Client Credentials flow — no user login needed.
    """
    import os, urllib.request, urllib.parse, json, base64
    client_id = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        return None  # Credentials not configured — fall back to keyboard nav

    try:
        # Step 1: Get access token
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        token_req = urllib.request.Request(
            "https://accounts.spotify.com/api/token",
            data=b"grant_type=client_credentials",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        token_data = json.loads(urllib.request.urlopen(token_req, timeout=6).read())
        token = token_data.get("access_token")
        if not token:
            return None

        # Step 2: Search for the track
        query = urllib.parse.quote(song_name)
        search_req = urllib.request.Request(
            f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1",
            headers={"Authorization": f"Bearer {token}"},
        )
        results = json.loads(urllib.request.urlopen(search_req, timeout=6).read())
        tracks = results.get("tracks", {}).get("items", [])
        if tracks:
            uri = tracks[0]["uri"]  # e.g. spotify:track:7qiZfU4dY1lWllzX7mPBI3
            logger.info(f"🎵 Spotify API found: {tracks[0]['name']} → {uri}")
            return uri
    except Exception as e:
        logger.warning(f"Spotify API lookup failed: {e}")

    return None


def run_applescript(script: str) -> str:
    """Execute an AppleScript and return the output."""
    try:
        result = subprocess.run(
            ['/usr/bin/osascript', '-e', script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0 and result.stderr:
            logger.warning(f"AppleScript warning: {result.stderr.strip()}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error("AppleScript timed out")
        return "Command timed out"
    except Exception as e:
        logger.error(f"AppleScript error: {e}")
        return f"Error: {e}"


def run_shell(command: str, timeout: int = 30) -> str:
    """Execute a shell command and return the output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr:
            output += f"\nError: {result.stderr.strip()}"
        return output or "Command executed successfully"
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"


class SystemControl:
    """Complete macOS system control via AppleScript and shell commands."""

    # ==========================================
    # Application Management
    # ==========================================

    @staticmethod
    def open_application(app_name: str) -> str:
        """Open a macOS application."""
        script = f'tell application "{app_name}" to activate'
        run_applescript(script)
        logger.info(f"📱 Opened: {app_name}")
        return f"Opened {app_name}"

    @staticmethod
    def close_application(app_name: str) -> str:
        """Close/quit an application."""
        script = f'tell application "{app_name}" to quit'
        run_applescript(script)
        logger.info(f"❌ Closed: {app_name}")
        return f"Closed {app_name}"

    @staticmethod
    def list_running_apps() -> str:
        """List all currently running applications."""
        script = '''
        tell application "System Events"
            set appList to name of every process whose background only is false
            set AppleScript's text item delimiters to ", "
            return appList as text
        end tell
        '''
        return run_applescript(script)

    @staticmethod
    def switch_to_app(app_name: str) -> str:
        """Switch focus to a specific app."""
        script = f'''
        tell application "{app_name}"
            activate
            set frontmost to true
        end tell
        '''
        run_applescript(script)
        return f"Switched to {app_name}"

    # ==========================================
    # Volume Control
    # ==========================================

    @staticmethod
    def set_volume(level: int) -> str:
        """Set volume (0-100), -1 to mute, -2 to unmute."""
        if level == -1:
            run_applescript('set volume with output muted')
            return "Volume muted"
        elif level == -2:
            run_applescript('set volume without output muted')
            return "Volume unmuted"
        else:
            level = max(0, min(100, level))
            # macOS volume is 0-7 for osascript
            mac_level = round(level * 7 / 100)
            run_applescript(f'set volume output volume {level}')
            return f"Volume set to {level}%"

    @staticmethod
    def get_volume() -> str:
        """Get current volume level."""
        result = run_applescript('output volume of (get volume settings)')
        return f"Current volume: {result}%"

    # ==========================================
    # Screen Brightness
    # ==========================================

    @staticmethod
    def set_brightness(level: float) -> str:
        """Set screen brightness (0.0 to 1.0 or 0 to 100)."""
        try:
            level = float(level)
        except (ValueError, TypeError):
            level = 0.5

        if level > 1.0:
            level = level / 100.0
        level = max(0.0, min(1.0, level))

        success = False

        # Primary: Native macOS DisplayServices C Framework (Controls hardware screen backlight)
        try:
            import ctypes
            try:
                Quartz = ctypes.CDLL('/System/Library/Frameworks/Quartz.framework/Quartz')
                Quartz.CGMainDisplayID.restype = ctypes.c_uint32
                main_disp = Quartz.CGMainDisplayID()
            except Exception:
                main_disp = 1

            ds = ctypes.CDLL('/System/Library/PrivateFrameworks/DisplayServices.framework/DisplayServices')
            ds.DisplayServicesSetBrightness.argtypes = [ctypes.c_uint32, ctypes.c_float]
            ds.DisplayServicesSetBrightness.restype = ctypes.c_int

            for display_id in set([main_disp, 1, 0, 2]):
                err = ds.DisplayServicesSetBrightness(display_id, float(level))
                if err == 0:
                    success = True
        except Exception as e:
            logger.warning(f"DisplayServices brightness error: {e}")

        # Secondary: CoreDisplay framework fallback
        if not success:
            try:
                import ctypes
                CoreDisplay = ctypes.CDLL('/System/Library/Frameworks/CoreDisplay.framework/CoreDisplay')
                CoreDisplay.CoreDisplay_Display_SetUserBrightness.argtypes = [ctypes.c_uint32, ctypes.c_double]
                CoreDisplay.CoreDisplay_Display_SetUserBrightness(1, float(level))
                success = True
            except Exception:
                pass

        # Tertiary fallback: brightness CLI tool
        if not success:
            res = run_shell(f'brightness {level}')
            if "failed" not in res.lower() and "error" not in res.lower() and "not found" not in res.lower():
                success = True

        logger.info(f"💡 Brightness set to {int(level * 100)}%")
        return f"Brightness set to {int(level * 100)}%"

    # ==========================================
    # Connectivity
    # ==========================================

    @staticmethod
    def toggle_wifi(enable: bool) -> str:
        """Toggle Wi-Fi on/off."""
        # Get the Wi-Fi interface name
        interface = run_shell("networksetup -listallhardwareports | awk '/Wi-Fi/{getline; print $2}'")
        if not interface:
            interface = "en0"  # Default

        action = "on" if enable else "off"
        run_shell(f'networksetup -setairportpower {interface} {action}')
        return f"Wi-Fi turned {action}"

    @staticmethod
    def toggle_bluetooth(enable: bool) -> str:
        """Toggle Bluetooth on/off."""
        action = "1" if enable else "0"
        # Try using blueutil if installed
        result = run_shell(f'blueutil --power {action}')
        if "not found" in result.lower():
            # Fallback to AppleScript
            return "Bluetooth toggle requires 'blueutil'. Install with: brew install blueutil"
        status = "on" if enable else "off"
        return f"Bluetooth turned {status}"

    # ==========================================
    # Display & Appearance
    # ==========================================

    @staticmethod
    def toggle_dark_mode(enable: bool) -> str:
        """Toggle dark mode."""
        value = "true" if enable else "false"
        script = f'''
        tell application "System Events"
            tell appearance preferences
                set dark mode to {value}
            end tell
        end tell
        '''
        run_applescript(script)
        mode = "Dark" if enable else "Light"
        return f"{mode} mode activated"

    @staticmethod
    def is_dark_mode() -> bool:
        """Check if dark mode is active."""
        result = run_applescript('''
        tell application "System Events"
            tell appearance preferences
                return dark mode
            end tell
        end tell
        ''')
        return result.lower() == "true"

    # ==========================================
    # Power Management
    # ==========================================

    @staticmethod
    def lock_screen() -> str:
        """Lock the screen."""
        run_shell('/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend')
        return "Screen locked"

    @staticmethod
    def sleep_mac() -> str:
        """Put Mac to sleep."""
        run_applescript('tell application "System Events" to sleep')
        return "Going to sleep"

    @staticmethod
    def restart_mac() -> str:
        """Restart the Mac (with confirmation)."""
        return "Restart requested. Please confirm by saying 'yes restart' for safety."

    @staticmethod
    def shutdown_mac() -> str:
        """Shutdown the Mac (with confirmation)."""
        return "Shutdown requested. Please confirm by saying 'yes shutdown' for safety."

    # ==========================================
    # Screenshot
    # ==========================================

    @staticmethod
    def take_screenshot(filename: str = None) -> str:
        """Take a screenshot."""
        if not filename:
            filename = f"layra_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        desktop = Path.home() / "Desktop"
        filepath = desktop / filename
        run_shell(f'screencapture -x "{filepath}"')
        return f"Screenshot saved to {filepath}"

    # ==========================================
    # System Information
    # ==========================================

    @staticmethod
    def get_system_info() -> str:
        """Get comprehensive system information."""
        info = {}

        # Battery
        battery = run_shell("pmset -g batt | grep -o '[0-9]*%'")
        charging = "charging" if "AC Power" in run_shell("pmset -g batt") else "on battery"
        info["battery"] = f"{battery} ({charging})"

        # Storage
        storage = run_shell("df -h / | tail -1 | awk '{print \"Used: \" $3 \" / \" $2 \" (\" $5 \" used)\"}'")
        info["storage"] = storage

        # RAM
        ram = run_shell("top -l 1 -s 0 | grep PhysMem")
        info["memory"] = ram.replace("PhysMem:", "RAM:").strip()

        # CPU
        cpu = run_shell("top -l 1 -s 0 | grep 'CPU usage'")
        info["cpu"] = cpu.replace("CPU usage:", "CPU:").strip()

        # Uptime
        uptime = run_shell("uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}'")
        info["uptime"] = uptime.strip()

        result_parts = [f"{k}: {v}" for k, v in info.items()]
        return "\n".join(result_parts)

    # ==========================================
    # Finder & Files
    # ==========================================

    @staticmethod
    def open_finder(path: str = None) -> str:
        """Open Finder at a specific path."""
        if path:
            run_shell(f'open "{path}"')
            return f"Opened Finder at {path}"
        else:
            run_shell('open ~')
            return "Opened Finder at home directory"

    @staticmethod
    def empty_trash() -> str:
        """Empty the Trash."""
        script = '''
        tell application "Finder"
            empty trash
        end tell
        '''
        run_applescript(script)
        return "Trash emptied"

    @staticmethod
    def get_clipboard() -> str:
        """Get clipboard contents."""
        return run_shell('pbpaste')

    @staticmethod
    def set_clipboard(text: str) -> str:
        """Set clipboard contents."""
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode())
        return "Text copied to clipboard"

    # ==========================================
    # Notifications
    # ==========================================

    @staticmethod
    def show_notification(title: str, message: str) -> str:
        """Show a macOS notification."""
        script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        run_applescript(script)
        return f"Notification shown: {title}"

    # ==========================================
    # Music Control
    # ==========================================

    @staticmethod
    def control_music(action: str, song_name: str = None, playlist_name: str = None) -> str:
        """Control Apple Music / Spotify playback."""
        import urllib.parse

        if action in ["play", "resume"]:
            run_applescript('try\ntell application "Spotify" to play\nend try\ntry\ntell application "Music" to play\nend try')
            return "Music playing"

        elif action == "pause":
            run_applescript('try\ntell application "Spotify" to pause\nend try\ntry\ntell application "Music" to pause\nend try')
            return "Music paused"

        elif action == "next":
            run_applescript('try\ntell application "Spotify" to next track\nend try\ntry\ntell application "Music" to next track\nend try')
            return "Skipped to next track"

        elif action == "previous":
            run_applescript('try\ntell application "Spotify" to previous track\nend try\ntry\ntell application "Music" to previous track\nend try')
            return "Going to previous track"

        elif action == "play_liked":
            # Open Spotify's Liked Songs (Saved Tracks) collection — fixed URI
            run_applescript('tell application "Spotify" to activate')
            time.sleep(0.2)
            run_shell("open 'spotify:collection:tracks'")
            time.sleep(1.2)
            # Trigger playback via Spotify AppleScript play
            run_applescript('tell application "Spotify" to play')
            time.sleep(0.5)
            state = run_applescript('tell application "Spotify" to return player state as string')
            if state == "playing":
                track = run_applescript('tell application "Spotify" to return name of current track')
                return f"Playing your Liked Songs. Now on: {track}"
            else:
                # Fallback: Space bar
                run_applescript('tell application "System Events" to tell process "Spotify" to key code 49')
                return "Playing your Liked Songs playlist"

        elif action == "play_playlist" and playlist_name:
            # Search for the playlist by name and open the first playlist result
            encoded = urllib.parse.quote(playlist_name)
            run_applescript('tell application "Spotify" to activate')
            time.sleep(0.2)
            run_shell(f"open 'spotify:search:{encoded}'")
            time.sleep(1.5)

            # Navigate: ESC to exit search box, Tab to Playlists section, Enter to open
            nav_script = '''
            tell application "System Events"
                tell process "Spotify"
                    key code 53
                    delay 0.2
                    repeat 6 times
                        key code 48
                        delay 0.15
                    end repeat
                    key code 36
                    delay 0.3
                end tell
            end tell
            '''
            run_applescript(nav_script)
            time.sleep(0.8)
            run_applescript('tell application "Spotify" to play')
            time.sleep(0.3)
            state = run_applescript('tell application "Spotify" to return player state as string')
            if state == "playing":
                return f"Playing playlist: {playlist_name}"
            else:
                run_applescript('tell application "System Events" to tell process "Spotify" to key code 49')
                return f"Opening playlist: {playlist_name}"

        elif action == "play_song" and song_name:
            import re

            # ── Tier 1: Spotify Web API (if credentials configured) ─────────────
            track_uri = _get_spotify_track_uri(song_name)
            if track_uri:
                run_applescript('tell application "Spotify" to activate')
                time.sleep(0.3)
                run_applescript(f'tell application "Spotify" to play track "{track_uri}"')
                time.sleep(0.8)
                state = run_applescript('tell application "Spotify" to return player state as string')
                if state == "playing":
                    track = run_applescript('tell application "Spotify" to return name of current track')
                    return f"Now playing on Spotify: {track}"

            # ── Tier 2: Spotify AppleScript Direct Play Track ───────────────────
            run_applescript('tell application "Spotify" to activate')
            time.sleep(0.3)
            run_applescript(f'tell application "Spotify" to play track "spotify:search:{song_name}"')
            time.sleep(1.0)
            state = run_applescript('tell application "Spotify" to return player state as string')
            if state == "playing":
                track = run_applescript('tell application "Spotify" to return name of current track')
                return f"Now playing on Spotify: {track}"

            # ── Tier 3: Spotify UI Key Navigation ──────────────────────────────
            clean_query = song_name
            try:
                itunes_url = f"https://itunes.apple.com/search?term={urllib.parse.quote(song_name)}&entity=song&limit=1"
                req = urllib.request.Request(itunes_url, headers={'User-Agent': 'Mozilla/5.0'})
                res = json.loads(urllib.request.urlopen(req, timeout=3).read())
                if res.get("results"):
                    t = res["results"][0]
                    clean_query = f"{t.get('trackName', '')} {t.get('artistName', '')}".strip()
            except Exception:
                pass

            encoded = urllib.parse.quote(clean_query)
            run_shell(f"open 'spotify:search:{encoded}'")
            time.sleep(1.2)
            # Press Enter to select & play top result
            run_applescript('''
            tell application "System Events"
                tell process "Spotify"
                    key code 36
                    delay 0.3
                    key code 49
                end tell
            end tell
            ''')
            time.sleep(0.5)
            state = run_applescript('tell application "Spotify" to return player state as string')
            if state == "playing":
                return f"Now playing on Spotify: {clean_query}"

            # ── Tier 4: YouTube Direct Video Play Fallback ───────────────────────
            try:
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_name + ' song')}"
                req = urllib.request.Request(
                    search_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                )
                html = urllib.request.urlopen(req, timeout=4).read().decode('utf-8', errors='ignore')
                video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
                if video_ids:
                    first_video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                    run_shell(f"open '{first_video_url}'")
                    return f"Playing song on YouTube: {song_name}"
            except Exception as e:
                logger.warning(f"YouTube song playback fallback error: {e}")

            return f"Opened search for {song_name}"


        else:
            return f"Unknown music action: {action}"

    # ==========================================
    # Shell Command Execution
    # ==========================================

    @staticmethod
    def run_shell_command(command: str) -> str:
        """
        Execute a shell command. 
        Safety: blocks dangerous commands.
        """
        # Safety check - block dangerous commands
        dangerous = ['rm -rf /', 'rm -rf ~', 'mkfs', 'dd if=', ':(){', 'shutdown', 'reboot']
        for d in dangerous:
            if d in command.lower():
                return f"⚠️ Blocked dangerous command: {command}"

        return run_shell(command, timeout=30)

    # ==========================================
    # Battery Status
    # ==========================================

    @staticmethod
    def get_battery_status() -> str:
        """Get detailed battery status."""
        import re
        raw = run_shell("pmset -g batt")
        percentage = run_shell("pmset -g batt | grep -o '[0-9]*%' | head -1")
        is_charging = "charging" if "AC Power" in raw else "on battery"
        time_left = ""
        match = re.search(r'(\d+:\d+) remaining', raw)
        if match:
            time_left = f", {match.group(1)} remaining"
        return f"Battery: {percentage} ({is_charging}{time_left})"

    # ==========================================
    # Network Information
    # ==========================================

    @staticmethod
    def get_network_info() -> str:
        """Get current network/IP information."""
        local_ip = run_shell("ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null")
        public_ip = run_shell("curl -s --max-time 4 https://api.ipify.org 2>/dev/null")
        wifi_name = run_shell("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I 2>/dev/null | awk '/ SSID/{print $2}'")
        info = []
        if wifi_name:
            info.append(f"WiFi: {wifi_name}")
        if local_ip:
            info.append(f"Local IP: {local_ip}")
        if public_ip and len(public_ip) < 20:
            info.append(f"Public IP: {public_ip}")
        return "\n".join(info) if info else "Network info unavailable"

    # ==========================================
    # Active Window / Focus
    # ==========================================

    @staticmethod
    def get_active_window() -> str:
        """Get the currently focused application and window title."""
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            set frontWindow to ""
            try
                set frontWindow to name of front window of (first application process whose frontmost is true)
            end try
            return frontApp & " — " & frontWindow
        end tell
        '''
        return run_applescript(script)

    # ==========================================
    # Do Not Disturb
    # ==========================================

    @staticmethod
    def toggle_do_not_disturb(enable: bool) -> str:
        """Toggle Do Not Disturb mode."""
        if enable:
            run_shell("defaults -currentHost write ~/Library/Preferences/ByHost/com.apple.notificationcenterui doNotDisturb -boolean true 2>/dev/null")
            run_shell("killall NotificationCenter 2>/dev/null; true")
            return "Do Not Disturb enabled"
        else:
            run_shell("defaults -currentHost write ~/Library/Preferences/ByHost/com.apple.notificationcenterui doNotDisturb -boolean false 2>/dev/null")
            run_shell("killall NotificationCenter 2>/dev/null; true")
            return "Do Not Disturb disabled"

    # ==========================================
    # Clipboard
    # ==========================================

    @staticmethod
    def get_clipboard_text() -> str:
        """Read current clipboard content."""
        content = run_shell("pbpaste")
        if not content:
            return "Clipboard is empty"
        return f"Clipboard: {content[:500]}"

    @staticmethod
    def copy_to_clipboard(text: str) -> str:
        """Copy text to clipboard."""
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
        return f"Copied to clipboard"

    # ==========================================
    # Finder Shortcuts
    # ==========================================

    @staticmethod
    def open_folder(path: str) -> str:
        """Open a folder in Finder."""
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            run_shell(f'open "{expanded}"')
            return f"Opened: {expanded}"
        return f"Folder not found: {path}"

    @staticmethod
    def open_downloads() -> str:
        """Open Downloads folder."""
        run_shell("open ~/Downloads")
        return "Opened Downloads folder"

    @staticmethod
    def open_documents() -> str:
        """Open Documents folder in Finder."""
        run_shell("open ~/Documents")
        return "Opened Documents folder"

    @staticmethod
    def open_desktop() -> str:
        """Open Desktop folder in Finder."""
        run_shell("open ~/Desktop")
        return "Opened Desktop"

    # ==========================================
    # Running Apps
    # ==========================================

    @staticmethod
    def get_running_apps() -> str:
        """List all currently running user-visible apps."""
        script = '''
        tell application "System Events"
            set appList to name of every process whose background only is false
            set AppleScript's text item delimiters to ", "
            return appList as text
        end tell
        '''
        result = run_applescript(script)
        return f"Running apps: {result}"

    @staticmethod
    def hide_application(app_name: str) -> str:
        """Hide an application window."""
        script = f'''
        tell application "System Events"
            set visible of process "{app_name}" to false
        end tell
        '''
        run_applescript(script)
        return f"Hidden: {app_name}"

    # ==========================================
    # Display & Power
    # ==========================================

    @staticmethod
    def sleep_display() -> str:
        """Turn off display only (not Mac sleep)."""
        run_shell("pmset displaysleepnow")
        return "Display sleeping"

    @staticmethod
    def get_uptime() -> str:
        """Get system uptime."""
        uptime = run_shell("uptime | awk -F'up ' '{print $2}' | awk -F', [0-9]* user' '{print $1}'")
        return f"System uptime: {uptime.strip()}"

    # ==========================================
    # Keyboard / Text
    # ==========================================

    @staticmethod
    def type_text(text: str) -> str:
        """Type text into the currently focused application."""
        safe_text = text.replace('"', '\\"').replace("'", "\\'")
        script = f'tell application "System Events" to keystroke "{safe_text}"'
        run_applescript(script)
        return f"Typed: {text[:60]}"

    @staticmethod
    def press_key(key: str) -> str:
        """Press a keyboard key or shortcut."""
        key_map = {
            "enter": "key code 36",
            "escape": "key code 53",
            "space": "key code 49",
            "tab": "key code 48",
            "delete": "key code 51",
            "cmd+c": 'keystroke "c" using command down',
            "cmd+v": 'keystroke "v" using command down',
            "cmd+z": 'keystroke "z" using command down',
            "cmd+s": 'keystroke "s" using command down',
            "cmd+q": 'keystroke "q" using command down',
            "cmd+w": 'keystroke "w" using command down',
            "cmd+t": 'keystroke "t" using command down',
        }
        k = key.lower().strip()
        action = key_map.get(k, f'keystroke "{k}"')
        script = f'tell application "System Events" to {action}'
        run_applescript(script)
        return f"Pressed: {key}"
