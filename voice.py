from faster_whisper import WhisperModel

model = WhisperModel("base", compute_type="float32")
audio_file_path = "./audio-samples/gujarati.mp3"
segments, info = model.transcribe(audio_file_path, beam_size=5)
print("Detected language:", info.language)
print("Transcription:")
for segment in segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
