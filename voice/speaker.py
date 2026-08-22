"""
Layra Text-to-Speech Speaker
======================================
Converts text to speech using edge-tts (Microsoft Neural voices)
with fallback to macOS native 'say' command.
"""

import asyncio
import subprocess
import tempfile
import logging
import os
import threading

logger = logging.getLogger("layra.speaker")


class Speaker:
    """
    Text-to-Speech engine using edge-tts for high-quality neural voices.
    Falls back to macOS 'say' command if edge-tts is unavailable.
    """

    def __init__(self, voice: str = "en-GB-RyanNeural", voice_hindi: str = "hi-IN-MadhurNeural",
                 rate: str = "+0%", volume: str = "+25%", pitch: str = "-10Hz", use_fallback: bool = False):
        """
        Args:
            voice: English voice name for edge-tts
            voice_hindi: Hindi voice name for edge-tts
            rate: Speech rate adjustment
            volume: Volume adjustment
            pitch: Deep pitch adjustment (e.g. -10Hz for deep baritone)
            use_fallback: Force use macOS 'say' command
        """
        self.voice = voice
        self.voice_hindi = voice_hindi
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        self.use_fallback = use_fallback
        self._is_speaking = False
        self._stop_flag = False
        self._lock = threading.Lock()

    def _detect_language(self, text: str) -> str:
        """
        Simple language detection based on character analysis.
        Returns 'hindi' if Devanagari characters found, else 'english'.
        """
        hindi_chars = 0
        total_chars = 0
        for char in text:
            if char.isalpha():
                total_chars += 1
                # Devanagari Unicode range
                if '\u0900' <= char <= '\u097F':
                    hindi_chars += 1

        if total_chars == 0:
            return "english"
        return "hindi" if (hindi_chars / total_chars) > 0.3 else "english"

    async def _speak_edge_tts(self, text: str, voice: str = None):
        """Speak using edge-tts (async)."""
        try:
            import edge_tts

            if voice is None:
                lang = self._detect_language(text)
                voice = self.voice_hindi if lang == "hindi" else self.voice

            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=self.rate,
                volume=self.volume,
                pitch=self.pitch
            )

            # Save to temp file and play
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            await communicate.save(temp_path)

            if self._stop_flag:
                return

            # Play audio using afplay (macOS native)
            process = subprocess.Popen(
                ["afplay", temp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            process.wait()

            # Cleanup
            try:
                os.unlink(temp_path)
            except Exception:
                pass

        except ImportError:
            logger.warning("edge-tts not installed, using macOS fallback")
            self._speak_macos(text)
        except Exception as e:
            logger.error(f"edge-tts error: {e}, falling back to macOS say")
            self._speak_macos(text)

    def _speak_macos(self, text: str):
        """Speak using macOS native 'say' command (fallback)."""
        try:
            # Clean text for shell safety
            clean_text = text.replace('"', '\\"').replace("'", "\\'")
            subprocess.run(
                ["say", "-v", "Samantha", clean_text],
                check=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            logger.warning("TTS timeout")
        except Exception as e:
            logger.error(f"macOS TTS error: {e}")

    def speak(self, text: str, voice: str = None):
        """
        Speak the given text (blocking call).
        Automatically detects language and selects appropriate voice.
        
        Args:
            text: Text to speak
            voice: Override voice name (optional)
        """
        if not text or not text.strip():
            return

        with self._lock:
            self._is_speaking = True
            self._stop_flag = False

        logger.info(f"🗣️ Speaking: '{text[:80]}...'")

        try:
            if self.use_fallback:
                self._speak_macos(text)
            else:
                # Run async edge-tts in sync context
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If already in async context, run in new thread
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            pool.submit(lambda: asyncio.run(self._speak_edge_tts(text, voice))).result()
                    else:
                        loop.run_until_complete(self._speak_edge_tts(text, voice))
                except RuntimeError:
                    asyncio.run(self._speak_edge_tts(text, voice))
        finally:
            with self._lock:
                self._is_speaking = False

    def speak_async(self, text: str, voice: str = None):
        """Speak in a background thread (non-blocking)."""
        thread = threading.Thread(target=self.speak, args=(text, voice), daemon=True)
        thread.start()
        return thread

    def stop(self):
        """Stop current speech."""
        self._stop_flag = True
        # Kill any running afplay processes
        try:
            subprocess.run(["killall", "afplay"], capture_output=True)
        except Exception:
            pass
        # Also kill any 'say' processes
        try:
            subprocess.run(["killall", "say"], capture_output=True)
        except Exception:
            pass

    @property
    def is_speaking(self):
        return self._is_speaking

    def play_sound(self, sound_path: str):
        """Play a sound effect file."""
        try:
            if os.path.exists(sound_path):
                subprocess.Popen(
                    ["afplay", sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        except Exception as e:
            logger.warning(f"Could not play sound: {e}")
