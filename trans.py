from faster_whisper import WhisperModel

# Load model (ensure compute_type is compatible with your system)
model = WhisperModel("base", compute_type="float32")

def transcribe_audio(file_path):
    """Transcribes audio using faster-whisper."""
    segments, info = model.transcribe(file_path, beam_size=5)
    transcript = " ".join(segment.text for segment in segments)
    return transcript, info.language

# Example usage
audio_file = "./audio-samples/audio data.mp3"

transcript, language = transcribe_audio(audio_file)

print(f"Detected language: {language}")
print("Transcription:")
print(transcript)
