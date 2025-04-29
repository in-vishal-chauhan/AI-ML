import logging
from faster_whisper import WhisperModel

# Set up logging
logging.basicConfig(
    filename="transcription.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load model (ensure compute_type is compatible with your system)
model = WhisperModel("base", compute_type="float32")

def transcribe_audio(file_path):
    """Transcribes audio using faster-whisper and logs the details."""
    logging.info(f"Starting transcription for file: {file_path}")
    segments, info = model.transcribe(file_path, beam_size=5)
    
    transcript = []
    for segment in segments:
        line = f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}"
        logging.info(line)
        transcript.append(segment.text)

    full_transcript = " ".join(transcript)
    logging.info(f"Detected language: {info.language}")
    logging.info("Transcription complete.\n")

    return full_transcript, info.language

# Example usage
audio_file = "./audio-samples/audio data.mp3"
transcript, language = transcribe_audio(audio_file)

print(f"Detected language: {language}")
print("Transcription:")
print(transcript)
