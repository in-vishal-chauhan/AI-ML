from faster_whisper import WhisperModel
from logger import get_logger

logger = get_logger(__name__)

model = WhisperModel("base", compute_type="float32")

def transcribe_audio(file_path):
    try:
        segments, information = model.transcribe(file_path, beam_size=5)
        transcript = " ".join([segment.text for segment in segments])
        return transcript, information.language
    except Exception as e:
        logger.error(f"Audio transcription failed'. Error: {str(e)}")
        raise
