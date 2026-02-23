"""
Audio transcription service using OpenAI Whisper.

Provides speech-to-text conversion for audio files with support for
Ukrainian and English languages. Runs entirely offline using local Whisper models.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class AudioService:
    """
    Service for audio transcription using OpenAI Whisper.

    Features:
    - Lazy model loading (only loads on first use)
    - Automatic language detection
    - File validation (format, size, duration)
    - Support for WAV, MP3, OGG, M4A, FLAC, WEBM formats
    """

    def __init__(self, model_size: str = "medium", max_file_size_mb: int = 100,
                 max_duration_minutes: int = 30, device: str = "cpu"):
        """
        Initialize audio service.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large, large-v3)
            max_file_size_mb: Maximum allowed file size in megabytes
            max_duration_minutes: Maximum allowed audio duration in minutes
            device: Device to run model on ('cpu' or 'cuda')
        """
        self.model = None
        self.model_size = model_size
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.max_duration_seconds = max_duration_minutes * 60
        self.device = device

        # Supported audio formats
        self.supported_formats = {'.wav', '.mp3', '.ogg', '.m4a', '.flac', '.webm'}

        logger.info(f"AudioService initialized with model={model_size}, device={device}")

    def _load_model(self):
        """Lazy load Whisper model on first use."""
        if self.model is not None:
            return

        try:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"Whisper model loaded successfully")
        except ImportError:
            raise RuntimeError(
                "openai-whisper is not installed. "
                "Install with: pip install openai-whisper"
            )
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}")

    def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate audio file before transcription.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            return False, f"File not found: {file_path}"

        # Check file extension
        if path.suffix.lower() not in self.supported_formats:
            formats = ', '.join(sorted(self.supported_formats))
            return False, f"Unsupported format '{path.suffix}'. Supported: {formats}"

        # Check file size
        file_size = path.stat().st_size
        if file_size > self.max_file_size_bytes:
            max_mb = self.max_file_size_bytes / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            return False, f"File too large ({actual_mb:.1f}MB). Maximum: {max_mb:.0f}MB"

        # Check if file is readable and get duration
        try:
            import soundfile as sf
            with sf.SoundFile(file_path) as audio:
                duration = len(audio) / audio.samplerate

                if duration > self.max_duration_seconds:
                    max_min = self.max_duration_seconds / 60
                    actual_min = duration / 60
                    return False, f"Audio too long ({actual_min:.1f}min). Maximum: {max_min:.0f}min"

        except Exception as e:
            # If soundfile fails, try pydub as fallback
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(file_path)
                duration = len(audio) / 1000.0  # pydub returns milliseconds

                if duration > self.max_duration_seconds:
                    max_min = self.max_duration_seconds / 60
                    actual_min = duration / 60
                    return False, f"Audio too long ({actual_min:.1f}min). Maximum: {max_min:.0f}min"

            except Exception as e2:
                return False, f"Cannot read audio file. It may be corrupted. Error: {e2}"

        return True, ""

    def transcribe_file(self, file_path: str, language: Optional[str] = None) -> Dict:
        """
        Transcribe audio file to text.

        Args:
            file_path: Path to audio file
            language: Optional language code (e.g., 'en', 'uk'). If None, auto-detect.

        Returns:
            Dictionary with transcription results:
            {
                'text': str,              # Transcribed text
                'language': str,          # Detected/specified language
                'duration': float,        # Audio duration in seconds
                'segments': list,         # Word-level segments with timestamps
                'original_filename': str, # Original filename
                'file_size_bytes': int,   # File size
                'audio_format': str,      # File extension
                'whisper_model_version': str  # Model used
            }
        """
        # Validate file first
        is_valid, error_msg = self.validate_audio_file(file_path)
        if not is_valid:
            raise ValueError(error_msg)

        # Load model if needed
        self._load_model()

        # Get file metadata
        path = Path(file_path)
        file_size = path.stat().st_size
        audio_format = path.suffix.lower().lstrip('.')

        try:
            logger.info(f"Transcribing: {file_path}")

            # Prepare transcription options
            options = {
                'task': 'transcribe',  # Don't translate, just transcribe
                'fp16': False if self.device == 'cpu' else True,
            }

            if language:
                # Convert language codes: 'en' or 'english' -> 'en', 'uk' or 'ukrainian' -> 'uk'
                lang_code = language[:2].lower() if len(language) > 2 else language.lower()
                options['language'] = lang_code

            # Transcribe
            result = self.model.transcribe(file_path, **options)

            # Get audio duration
            try:
                import soundfile as sf
                with sf.SoundFile(file_path) as audio:
                    duration = len(audio) / audio.samplerate
            except:
                # Estimate from segments if soundfile fails
                if result.get('segments'):
                    duration = result['segments'][-1]['end']
                else:
                    duration = 0.0

            logger.info(f"Transcription complete. Language: {result['language']}, Duration: {duration:.1f}s")

            return {
                'text': result['text'].strip(),
                'language': result['language'],
                'duration': duration,
                'segments': result.get('segments', []),
                'original_filename': path.name,
                'file_size_bytes': file_size,
                'audio_format': audio_format,
                'whisper_model_version': self.model_size,
            }

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {e}")

    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            'model_size': self.model_size,
            'device': self.device,
            'is_loaded': self.model is not None,
            'supported_formats': list(self.supported_formats),
            'max_file_size_mb': self.max_file_size_bytes / (1024 * 1024),
            'max_duration_minutes': self.max_duration_seconds / 60,
        }
