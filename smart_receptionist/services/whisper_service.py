from faster_whisper import WhisperModel
from logger import get_logger

logger = get_logger(__name__)

model = WhisperModel("base", compute_type="float32")

def transcribe_audio(file_path):
    try:
        segments, info = model.transcribe(file_path, beam_size=5, language="en")
        transcript = " ".join([segment.text for segment in segments])
        return transcript, info.language
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise
