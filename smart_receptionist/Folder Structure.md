<!-- ai_receptionist/
│
├── app.py                 # Entry point (Flask routes)
├── config.py              # Environment variables loader
├── logger.py              # Centralized logging setup
│
├── services/
│   ├── whisper_service.py     # Transcription logic
│   ├── twilio_service.py      # WhatsApp message sending + audio download
│   ├── groq_service.py        # Groq API wrapper
│   ├── database_service.py    # DB connection and query
│   └── receptionist.py        # AI receptionist logic using other services
│
└── temp/                 # Temp audio files, if needed -->
# 📁 Project Structure

| Path                          | Description                                           |
|-------------------------------|-------------------------------------------------------|
| `smart_receptionist/app.py`   | Main Flask app with routes (`/webhook`, `/`)         |
| `smart_receptionist/config.py`| Loads environment variables from `.env`              |
| `smart_receptionist/logger.py`| Sets up centralized file + console logging           |
|                               |                                                       |
| `smart_receptionist/services/`| **Service layer – core business logic**              |
| ├── `whisper_service.py`      | Audio transcription using Faster-Whisper             |
| ├── `twilio_service.py`       | WhatsApp message sending and media downloading       |
| ├── `groq_service.py`         | Groq API wrapper for LLaMA3 translation/extraction   |
| ├── `database_service.py`     | MySQL connection and product rate querying           |
| └── `receptionist.py`         | Main receptionist flow: handles user interaction     |
|                               |                                                       |
| `smart_receptionist/temp/`    | Temporary audio files (auto-deleted after use)       |
