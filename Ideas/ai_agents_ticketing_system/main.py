import os
import json
import base64
import uvicorn
from dotenv import load_dotenv
from models import get_llama_response
from tools import (
    extract_email_body,
    extract_fathom_data,
    extract_otter_data,
    extract_team_notetaker_data,
    create_jira_ticket
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from gmail_utils import get_gmail_service

app = FastAPI()
# Load environment variables
load_dotenv()

app = FastAPI()
# Simulated dummy email
DUMMY_EMAIL = '''
From: projectmanager@example.com
Subject: Meeting Follow-up

FATHOM
Meeting with Bijal Sanghavi
Showcase by our AI/ML team :)
May 01, 2025  •  52 mins  •  View Meeting or Ask Fathom
Action Items 
    Add phone call functionality to AI receptionist project
    Vishal Chauhan
            
    Implement voice-based functionality for AI receptionist
    Paras Majethiya
            
    Add tool to allow LLM to perform more reasoning in AI receptionist
    Paras Majethiya
            
    Research/implement basic receptionist features (e.g. 9-5 hrs, holidays) for AI agent
    Paras Majethiya
            
    Make current AI receptionist implementation more robust
    Vishal Chauhan
            
    Update project ideas document w/ brainstormed use cases, mark difficulty levels
    Vishal Chauhan

Meeting Summary

Meeting Purpose
    Showcase and discuss the AI/ML team's development of an AI receptionist agent for handling customer inquiries.

Key Takeaways
    The team has developed an AI receptionist prototype for handling price inquiries in the textile industry, with potential for expansion to other industries

    Current implementation handles text and voice inputs via WhatsApp, with plans to add phone call functionality

    The system uses AI to translate queries, extract relevant parameters, and query a database to provide accurate responses

    Future enhancements include adding more robust functionality, improving error handling, and expanding use cases beyond simple price inquiries

Topics
Project Overview and Vision
    Developed an AI-based receptionist agent for handling customer inquiries, initially focused on textile industry price queries

    Vision is to create a versatile AI receptionist that can handle various tasks like answering basic questions, providing company information, and potentially scheduling appointments

    Aimed at being a competitive product in the US market for AI receptionist solutions

Technical Implementation
    Uses WhatsApp API for communication channel

    Implements a Python script to process incoming messages

    Utilizes AI for language translation and parameter extraction

    Queries a MySQL database to retrieve product information

    Sends responses back through the appropriate channel (e.g., WhatsApp)

Current Capabilities
    Handles text and voice inputs via WhatsApp

    Processes queries in multiple languages

    Extracts relevant parameters (e.g., color, quality, material) from natural language inputs

    Queries a database to retrieve accurate price information

    Responds in the original query language

Future Enhancements
    Add phone call functionality for voice interactions

    Implement more robust error handling and system redundancy

    Expand use cases beyond price inquiries (e.g., general customer support, appointment scheduling)

    Integrate with calendar APIs for scheduling functionality

    Improve AI's ability to handle more complex queries and provide suggestions

Training and Development Process
    Team explored multiple AI tools and LLM (Large Language Model) implementations

    Used M8N (similar to Zapier) for no-code automation integration

    Focus on understanding AI concepts and integrating with everyday systems like WhatsApp and email

Next Steps
    Make the current implementation more robust

    Add voice-based functionality

    Integrate another tool to allow LLM to perform more complex reasoning

    Complete the main AI training implementation by May 19th

    Explore additional use cases and enhancements after the core training is complete

'''

# Agent 1: Read email
class EmailReaderAgent:
    def __init__(self):
        self.name = "EmailReaderAgent"

    def run(self, email):
        return extract_email_body(email)

# Agent 2: Extract key points using LLM to decide the source and tool
class KeyPointExtractorAgent:
    def __init__(self):
        self.name = "KeyPointExtractorAgent"

    def run(self, content):
        source_prompt = f"""
            You are a smart assistant. Given the following meeting email, identify the service that generated it.
            It can be one of:
            - Fathom
            - Otter
            - Team Notetaker

            Only return one of the following exactly: "Fathom", "Otter", or "Team Notetaker".

            Email:
            {content}
            """
        source = get_llama_response(source_prompt).strip().lower()
        
        # Check if 'content' is in JSON format
        try:
            content_json = json.loads(content)
            content = content_json.get('Body', content)  # Extract 'body' if available
        except json.JSONDecodeError:
            print("[KeyPointExtractorAgent] Content is not in JSON format, using as-is.")

        if isinstance(content, dict):  # If content is a dictionary (JSON), convert to string
            content = json.dumps(content)

        # Decide tool based on LLM-identified source
        if "fathom" in source:
            print("[KeyPointExtractorAgent] Identified: Fathom")
            prompt = extract_fathom_data(content)
        elif "otter" in source:
            print("[KeyPointExtractorAgent] Identified: Otter")
            prompt = extract_otter_data(content)
        elif "team" in source:
            print("[KeyPointExtractorAgent] Identified: Team Notetaker")
            prompt = extract_team_notetaker_data(content)
        else:
            print("[KeyPointExtractorAgent] Source unidentified, using generic extractor")
            prompt = f"""
                Extract action items from the following content and return a JSON list in this format:

                [
                {{"task": "", "due_date": "", "assigned_team": ""}},
                ...
                ]

                Content:
                {content}
                """
            
        # Run LLM on the selected prompt
        result = get_llama_response(prompt)

        try:
            return result
        except Exception as e:
            print("[KeyPointExtractorAgent] Failed to parse JSON:", e)
            return []

# Agent 3: Create ticket in JIRA
class JiraAgent:
    def __init__(self):
        self.name = "JiraAgent"

    def run(self, task_json):
        return create_jira_ticket(task_json)

# Orchestrator
class Orchestrator:
    def __init__(self, reader, extractor, jira_agent):
        self.reader = reader
        self.extractor = extractor
        self.jira_agent = jira_agent

    def run(self, email):
        print("[Orchestrator] Running EmailReaderAgent...")
        body = self.reader.run(email)

        print("[Orchestrator] Running KeyPointExtractorAgent...")
        keypoints_json = self.extractor.run(body)
        print("[Key Points JSON]:", keypoints_json)

        print("[Orchestrator] Running JiraAgent...")
        result = self.jira_agent.run(keypoints_json)

        return result 

if __name__ == '__main__':
    reader = EmailReaderAgent()
    extractor = KeyPointExtractorAgent()
    jira = JiraAgent()
    orchestrator = Orchestrator(reader, extractor, jira)

    result = orchestrator.run(DUMMY_EMAIL)
    print("\n[JIRA Response]:", result)
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Load AI agents
reader = EmailReaderAgent()
extractor = KeyPointExtractorAgent()
jira = JiraAgent()
orchestrator = Orchestrator(reader, extractor, jira) 

@app.post("/webhook/outlook")
async def outlook_webhook(request: Request):
    
    data = await request.json()
    message_data = data.get("message", {}).get("data")
    if not message_data:
        return {"status": "No message data"}

    decoded_bytes = base64.b64decode(message_data)
    decoded_str = decoded_bytes.decode("utf-8")
    message_json = json.loads(decoded_str)

    history_id = message_json.get("historyId")
    if not history_id:
        return {"status": "No historyId"}

    # Fetch email from Gmail
    gmail = get_gmail_service()
    history = gmail.users().history().list(
        userId='me',
        startHistoryId=history_id,
        historyTypes=['messageAdded']
    ).execute()

    messages = history.get('history', [])
    for entry in messages:
        for msg in entry.get("messages", []):
            msg_id = msg["id"]
            message = gmail.users().messages().get(userId="me", id=msg_id, format="full").execute()

            payload = message.get("payload", {})
            parts = payload.get("parts", [])

            # Try to find plain text part
            body_data = ""
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    body_data = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break

            if not body_data:
                body_data = base64.urlsafe_b64decode(payload.get("body", {}).get("data", "")).decode("utf-8")

            print("\n[Webhook] Passing email body to orchestrator...\n")
            result = orchestrator.run(body_data)
            print("\n[JIRA Ticket Result]:", result)

    return {"status": "processed"}

    # Microsoft sends this for validation on initial webhook registration
    # body = await request.body()
    
    # email_text = body.decode("utf-8")
    # reader = EmailReaderAgent()
    # extractor = KeyPointExtractorAgent()
    # jira = JiraAgent()
    # orchestrator = Orchestrator(reader, extractor, jira)

    # result = orchestrator.run(email_text)
    # return JSONResponse(email_text, status_code=200)
    