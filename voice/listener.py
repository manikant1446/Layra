"""
Layra Wake Word Listener
=================================
Always-on microphone listener that detects the "Layra" wake word
using Picovoice Porcupine engine (runs 100% offline).
"""

import threading
import logging
import struct
import time

logger = logging.getLogger("layra.listener")


class WakeWordListener:
    """
    Continuously listens for the wake word "Layra" using Porcupine.
    Runs in a background thread and calls the callback when detected.
    """

    def __init__(self, access_key: str, sensitivity: float = 0.7, on_wake_word=None):
        """
        Args:
            access_key: Picovoice access key
            sensitivity: Detection sensitivity (0.0 to 1.0)
            on_wake_word: Callback function when wake word is detected
        """
        self.access_key = access_key
        self.sensitivity = sensitivity
        self.on_wake_word = on_wake_word
        self._running = False
        self._thread = None
        self._porcupine = None
        self._recorder = None

    def _initialize(self):
        """Initialize Porcupine, openwakeword, or VAD listener."""
        if not self.access_key or self.access_key == "your_picovoice_key_here":
            logger.info("ℹ️ Picovoice key not configured, using automatic VAD Voice Listener (100% Free)")
            self._use_vad = True
            return

        self._use_vad = False
        try:
            import pvporcupine
            from pvrecorder import PvRecorder

            try:
                self._porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=["layra"],
                    sensitivities=[self.sensitivity]
                )
                logger.info("✅ Wake word 'Layra' loaded (Porcupine)")
            except pvporcupine.PorcupineInvalidArgumentError:
                self._porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=["computer"],
                    sensitivities=[self.sensitivity]
                )
                logger.warning("⚠️ 'Layra' keyword not available, using 'Computer' instead")

            self._recorder = PvRecorder(
                device_index=-1,
                frame_length=self._porcupine.frame_length
            )
            logger.info("✅ Audio recorder initialized")

        except Exception as e:
            logger.warning(f"⚠️ Picovoice init failed ({e}). Falling back to automatic VAD Voice Listener.")
            self._use_vad = True

    def _listen_loop(self):
        """Main listening loop — runs in background thread."""
        try:
            self._initialize()

            if getattr(self, '_use_vad', False):
                # 100% FREE open-source wake-word / VAD listener
                self._listen_openwakeword_or_vad()
                return

            self._recorder.start()
            logger.info("🎤 Listening for wake word (Porcupine)...")

            while self._running:
                try:
                    if getattr(self, '_paused', False):
                        time.sleep(0.1)
                        continue

                    pcm = self._recorder.read()
                    keyword_index = self._porcupine.process(pcm)

                    if keyword_index >= 0:
                        logger.info("🔊 Wake word detected!")
                        if self.on_wake_word:
                            self.on_wake_word()
                except Exception as e:
                    if self._running:
                        logger.error(f"Error in listen loop: {e}")
                        time.sleep(0.1)

        except Exception as e:
            logger.error(f"Wake word listener failed: {e}")
        finally:
            self._cleanup()

    def _trigger_wake(self, name: str = "Voice"):
        """Trigger wake word with debounce cooldown."""
        if getattr(self, '_paused', False):
            return

        now = time.time()
        if not hasattr(self, '_last_trigger_time'):
            self._last_trigger_time = 0

        if now - self._last_trigger_time > 2.0:
            self._last_trigger_time = now
            logger.info(f"🔊 {name} trigger activated!")
            if self.on_wake_word:
                self.on_wake_word()

    def _listen_openwakeword_or_vad(self):
        """100% Free local wake-word detector using openwakeword or VAD sounddevice."""
        try:
            import openwakeword
            from openwakeword.model import Model
            import sounddevice as sd
            import numpy as np

            logger.info("🎤 Initializing OpenWakeWord (100% Free local detection for 'Layra')...")
            oww_model = Model(wakeword_models=["hey_layra_v0.1"], inference_framework="onnx")
            self._oww_model = oww_model

            def audio_callback(indata, frames, time_info, status):
                if not self._running or getattr(self, '_paused', False):
                    return
                # Boost input audio gain (2.5x) to capture clear single-word "Layra" speech
                boosted_indata = np.clip(indata * 2.5, -1.0, 1.0)
                audio_int16 = (boosted_indata * 32767).astype(np.int16).flatten()
                prediction = oww_model.predict(audio_int16)
                for model_name, score in prediction.items():
                    # Threshold 0.12 ensures single word "Layra" triggers reliably
                    if score > 0.12:
                        self._trigger_wake("Layra")

            with sd.InputStream(samplerate=16000, channels=1, blocksize=1280, callback=audio_callback):
                logger.info("🎤 Wake Word active — Just say 'Layra' to activate")
                while self._running:
                    time.sleep(0.1)


        except Exception as e:
            logger.warning(f"Openwakeword loop info ({e}), using simple Voice Activity Trigger")
            self._listen_simple_vad()

    def _listen_simple_vad(self):
        """Dynamic VAD trigger based on mic sound level with auto-ambient noise adaptation."""
        try:
            import sounddevice as sd
            import numpy as np

            logger.info("🎤 Voice Activity Trigger active — speak to activate Layra")

            self.ambient_noise_level = 10.0

            def audio_callback(indata, frames, time_info, status):
                if not self._running or getattr(self, '_paused', False):
                    return
                # Boost mic audio for VAD
                boosted = indata * 2.2
                volume = float(np.abs(boosted).mean() * 1000)

                # Exponential moving average for baseline ambient room noise
                if volume < 25.0:
                    self.ambient_noise_level = 0.95 * self.ambient_noise_level + 0.05 * volume

                # Dynamic speech trigger threshold for quiet speaking
                threshold = max(20.0, self.ambient_noise_level + 10.0)

                if volume > threshold:
                    self._trigger_wake("Voice activity")

            with sd.InputStream(samplerate=16000, channels=1, blocksize=2048, callback=audio_callback):
                while self._running:
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"VAD listener failed: {e}")

    def pause(self):
        """Pause wake word detection."""
        self._paused = True

    def resume(self):
        """Resume wake word detection."""
        self._paused = False
        self._last_trigger_time = 0
        if hasattr(self, '_oww_model') and self._oww_model:
            try:
                self._oww_model.reset()
            except Exception:
                pass

    def start(self):
        """Start listening for wake word in a background thread."""
        if self._running:
            logger.warning("Listener already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info("🚀 Wake word listener started")

    def stop(self):
        """Stop the listener."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        self._cleanup()
        logger.info("🛑 Wake word listener stopped")

    def _cleanup(self):
        """Release resources."""
        if self._recorder:
            try:
                self._recorder.stop()
                self._recorder.delete()
            except Exception:
                pass
            self._recorder = None

        if self._porcupine:
            try:
                self._porcupine.delete()
            except Exception:
                pass
            self._porcupine = None

    @property
    def is_running(self):
        return self._running


class FallbackListener:
    """
    Fallback listener that uses keyboard input instead of wake word.
    Used when Porcupine is not available or ENABLE_WAKE_WORD is False.
    """

    def __init__(self, on_wake_word=None):
        self.on_wake_word = on_wake_word
        self._running = False
        self._thread = None

    def _listen_loop(self):
        """Listen for Enter key press as wake word substitute."""
        while self._running:
            try:
                user_input = input()  # Wait for Enter key
                if self._running and self.on_wake_word:
                    self.on_wake_word()
            except EOFError:
                break
            except Exception:
                break

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    @property
    def is_running(self):
        return self._running
