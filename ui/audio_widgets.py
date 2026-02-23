"""
Audio UI widgets for PyQt5 application.

Provides components for audio file upload and background transcription.
"""

import logging
from typing import Optional

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class TranscriptionWorker(QThread):
    """
    Background worker thread for audio transcription.

    Runs Whisper transcription in a separate thread to prevent UI freezing.
    Emits signals for completion, error, and progress updates.
    """

    # Signals
    transcription_complete = pyqtSignal(dict)  # Emits transcription results
    transcription_error = pyqtSignal(str)      # Emits error message
    progress_update = pyqtSignal(str)          # Emits status messages

    def __init__(self, file_path: str, language: Optional[str], audio_service):
        """
        Initialize transcription worker.

        Args:
            file_path: Path to audio file to transcribe
            language: Optional language code ('en', 'uk', etc.)
            audio_service: AudioService instance
        """
        super().__init__()
        self.file_path = file_path
        self.language = language
        self.audio_service = audio_service
        self._is_running = True

    def run(self):
        """Execute transcription in background thread."""
        try:
            logger.info(f"Starting transcription: {self.file_path}")
            self.progress_update.emit("Loading Whisper model...")

            # Convert language name to code if needed
            lang_code = None
            if self.language:
                if self.language.lower() in ['ukrainian', 'українська']:
                    lang_code = 'uk'
                elif self.language.lower() in ['english', 'англійська']:
                    lang_code = 'en'
                else:
                    lang_code = self.language[:2].lower()

            # Perform transcription
            self.progress_update.emit("Transcribing audio...")
            result = self.audio_service.transcribe_file(self.file_path, language=lang_code)

            if self._is_running:
                logger.info("Transcription completed successfully")
                self.transcription_complete.emit(result)

        except ValueError as e:
            # Validation errors
            logger.error(f"Validation error: {e}")
            if self._is_running:
                self.transcription_error.emit(str(e))

        except RuntimeError as e:
            # Transcription errors
            logger.error(f"Transcription error: {e}")
            if self._is_running:
                self.transcription_error.emit(str(e))

        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error during transcription: {e}", exc_info=True)
            if self._is_running:
                self.transcription_error.emit(f"Unexpected error: {e}")

    def stop(self):
        """Stop the worker thread."""
        self._is_running = False
        logger.info("Transcription worker stopped")
