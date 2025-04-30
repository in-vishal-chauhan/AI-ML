# AI Receptionist (Agentic Framework)

## Requirements
- Python 3.8+
- MySQL Database with 'products' table:
  - color (varchar)
  - material (varchar)
  - quality (varchar)
  - price (float)

## Setup
1. Clone project.
2. Install libraries:
   pip install -r requirements.txt
3. Configure database and Groq API key inside app.py
4. Run Flask server:
   python app.py
5. Test webhook using Postman or WhatsApp API.

## Example Incoming JSON
POST to http://localhost:5000/webhook
```json
{
    "from": "whatsapp:+911234567890",
    "message": "Red Cotton Super Deluxe ka rate kya hai?"
}
