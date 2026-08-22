"""
Layra Speech-to-Text Recognizer
========================================
Captures audio from microphone and transcribes to text
using SpeechRecognition (Google STT / Whisper) with dynamic VAD.
"""

import logging
import time
import speech_recognition as sr

logger = logging.getLogger("layra.recognizer")


class SpeechRecognizer:
    """
    Records audio from microphone and transcribes to text.
    Uses dynamic ambient energy adjustment for instant silence detection.
    """

    def __init__(self, model_size: str = "base", language: str = None):
        """
        Args:
            model_size: Whisper model size
            language: Force language (None = auto-detect Hindi/English)
        """
        self.language = language or "en-IN"
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 120
        self.recognizer.dynamic_energy_adjustment_ratio = 1.2
        self.recognizer.pause_threshold = 2.2         # Increased pause buffer (2.2s) so brief pauses don't cut off speech
        self.recognizer.non_speaking_duration = 0.8   # Extra silence padding so trailing words are not chopped off
        self.recognizer.phrase_threshold = 0.1        # Lower threshold so soft/short words are captured

    def listen_and_transcribe(self) -> str:
        """
        Record audio from microphone and transcribe to text.
        Automatically stops recording when user stops speaking.
        """
        logger.info("🎤 Listening for command... (Speak now)")

        try:
            with sr.Microphone() as source:
                # Fast ambient noise calibration (0.15s) so starting words aren't eaten
                self.recognizer.adjust_for_ambient_noise(source, duration=0.15)
                time.sleep(0.05)  # Mic ready buffer

                # Record audio until user finishes speaking (max 30s phrase, 12s initial timeout)
                audio = self.recognizer.listen(
                    source,
                    timeout=12.0,
                    phrase_time_limit=30.0
                )


            logger.info("⚡ Processing speech...")

            # Transcribe using Google Speech Recognition (free, supports Hinglish/Hindi/English)
            try:
                text = self.recognizer.recognize_google(audio, language="en-IN")
                logger.info(f"📝 Transcribed (en-IN): '{text}'")
                return text
            except sr.UnknownValueError:
                # Fallback to Hindi detection if en-IN didn't catch it
                try:
                    text = self.recognizer.recognize_google(audio, language="hi-IN")
                    logger.info(f"📝 Transcribed (hi-IN): '{text}'")
                    return text
                except sr.UnknownValueError:
                    logger.warning("⚠️ Could not understand audio (UnknownValueError)")
                    return ""
            except sr.RequestError as e:
                logger.error(f"⚠️ Speech Recognition service error: {e}")
                return ""

        except sr.WaitTimeoutError:
            logger.info("⏱️ Listening timed out (no speech detected)")
            return ""
        except Exception as e:
            logger.error(f"❌ Speech recognition error: {e}")
            return ""
