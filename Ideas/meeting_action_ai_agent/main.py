
from fastapi import FastAPI, Request
from agents.orchestrator_agent import orchestrate

app = FastAPI()

@app.post("/email-webhook")
async def webhook(request: Request):
    payload = await request.json()
    result = orchestrate(payload)
    return result
