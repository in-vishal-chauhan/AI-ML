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
    create_jira_ticket,
    fetch_existing_jira_tickets,
    generate_comparison_prompt,
    update_jira_task_status
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from gmail_utils import get_gmail_service, get_latest_message, get_last_10_emails, load_emails, save_emails
import asyncio
import time

app = FastAPI()
# Load environment variables
load_dotenv()

app = FastAPI()
# Simulated dummy email
DUMMY_EMAIL = '''

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

    def run(self, content, existing_tasks):

        print("[KeyPointExtractorAgent] generic extractor")
        prompt = f"""
                You are a smart assistant. Given the following NEW_MEETING_NOTES, identify the service that generated it.
                It can be one of:
                - Fathom
                - Fellow
                - Otter
                - Team Notetaker
                - Fireflies
                - tldv
                - bluedothq
                - sana.ai
                - Mem
                - noteGPT
                - notta
                - or similar tools.
                
                Ignore all emails that are not from these meeting notetaker sources.
                1. For ignoring emails:
                    - Return ONLY JSON format [].
                    - Do not explain.
                    - Do not add any extra content.
                    - Do not suggest or add any information

                2. For qualifying emails:
                    You are an AI Task Manager.
                    Given a list of PROJECT_TASK in JSON format and NEW_MEETING_NOTES or action items.
                    
                    PROJECT_TASK:
                    {existing_tasks}

                    NEW_MEETING_NOTES:
                    {content}
                    
                    Perform the following:
                    Read the NEW_MEETING_NOTES carefully.
                    Identify which tasks from the NEW_MEETING_NOTES semantically match the existing tasks.
                    Update the status of each PROJECT_TASK as per the latest information in the NEW_MEETING_NOTES.

                    Add any new tasks mentioned, with the correct status and assigned team, 
                    [{{"id": "", "key": "", "summary": YOUR_EXTRACTED_TASK, "description": "", "status": "New"}}, ...] in json list.

                    Return a JSON format with two keys: "Update" and "New". Newly created tasks should be in the "New" key, and updated tasks should be in the "Update" key.

                    - Final result must be in JSON format only, nothing else.
                    - DO NOT add new line formatting.
                    - DO NOT repeat the task in JSON object.
                    - DO NOT explain.
                    - DO NOT add any extra content.
                    - DO NOT add suggestion or any information
                    - DO NOT beautify the JSON object.
                    - Return ONLY JSON format
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
        # existing_tasks = fetch_existing_jira_tickets()
        # comparison_prompt = generate_comparison_prompt(existing_tasks, task_json)
        # # Run LLM on the selected prompt
        # result = get_llama_response(comparison_prompt)

        # Write history_id to webhook_log.json
        # Check if task_json is JSON formatted or string formatted
        # if isinstance(task_json, str):
        #     task_json = task_json.strip("\\")
        #     try:
        #         task_json = json.loads(task_json)
        #     except json.JSONDecodeError as e:
        #         print("[JiraAgent] Failed to parse JSON after stripping slashes:", e)
        #         return {}
            
        with open("webhook_log.json", "a") as log_file:
            json.dump(task_json, log_file, indent=0)
            
            
        result = []
        # Check if 'result' is in JSON format or string
        if isinstance(task_json, str):
            try:
                task_json = json.loads(task_json)
            except json.JSONDecodeError:
                print("[JiraAgent] Result is not in JSON format, using as-is.")
                return {}
        # Check if 'duplicate' key exists and is empty
        if task_json and task_json.get('Update'):
            # Check if 'Update' key exists and is empty
            if isinstance(task_json, dict) and 'Update' in task_json and not task_json['Update']:
                print("[JiraAgent] 'Update' key is empty.")
            else:
                result = update_jira_task_status(task_json.get('Update'))
        
        if task_json and task_json.get('New'):
            # Check if 'Update' key exists and is empty
            if isinstance(task_json, dict) and 'New' in task_json and not task_json['New']:
                print("[JiraAgent] 'New' key is empty.")
            else:
                result = create_jira_ticket(task_json.get('New'))
        # else:
        return result
        # if isinstance(result, dict) and 'duplicates' in result and not result['duplicates']:
        #     print("[JiraAgent] 'duplicates' key is empty.")
        # else :
        #     update_jira_task_status(result.get('duplicates'))
        
        # return create_jira_ticket(result.get('unique'))
        # return create_jira_ticket(task_json)

# Orchestrator
# Update the Orchestrator class to support async
class Orchestrator:
    def __init__(self, reader, extractor, jira_agent):
        self.reader = reader
        self.extractor = extractor
        self.jira_agent = jira_agent
        # Fetch existing tasks once at the start
        self.existing_tasks = fetch_existing_jira_tickets()

    async def run(self, email):
        print("[Orchestrator] Running EmailReaderAgent...")
        body = await asyncio.to_thread(self.reader.run, email)  # Run blocking code in a thread
        print("[Orchestrator] Running KeyPointExtractorAgent...")
        keypoints_json = await asyncio.to_thread(self.extractor.run, body, self.existing_tasks)
        print("[Key Points JSON]:", keypoints_json)

        print("[Orchestrator] Running JiraAgent...")
        result = await asyncio.to_thread(self.jira_agent.run, keypoints_json)

        return result

# Update the main block to use async
async def main():
    reader = EmailReaderAgent()
    extractor = KeyPointExtractorAgent()
    jira = JiraAgent()
    orchestrator = Orchestrator(reader, extractor, jira)

    emails = load_emails()
    if not emails:
        emails = await asyncio.to_thread(get_last_10_emails)
        #Save emails to file
        save_emails(emails)
        
    # while emails:
    batch = emails[-2:]  # Get last 2 emails
    for email in batch:
        print(f"Processing: {email}")
        await orchestrator.run(email['body'])  # Await the async run method

    emails = emails[:-2]  # Remove last 2
    save_emails(emails)
    print(f"Remaining emails: {emails}")
    
    if not emails:
        if os.path.exists("emails.json"):
            os.remove("emails.json")
            print("emails.json removed.")
        # time.sleep(60)  # Wait 1 minute


# Run the async main function
if __name__ == '__main__':
    asyncio.run(main())

    
@app.get("/")
def read_root():
    return {"Hello": "AI Meeting Notes"}

# Load AI agents
reader = EmailReaderAgent()
extractor = KeyPointExtractorAgent()
jira = JiraAgent()
orchestrator = Orchestrator(reader, extractor, jira) 
processed_history_ids = set()

@app.post("/webhook/outlook")
async def outlook_webhook(request: Request):
    
    data = await request.json()

    # Write history_id to webhook_log.json
    # with open("webhook_log.json", "a") as log_file:
    #     json.dump(data, log_file, indent=0)
    #     log_file.write("\n")

    message_data = data.get("message", {}).get("data")
    if not message_data:
        return {"status": "No message data"}

    decoded_bytes = base64.b64decode(message_data)
    decoded_str = decoded_bytes.decode("utf-8")
    message_json = json.loads(decoded_str)

    history_id = message_json.get("historyId")
    if not history_id:
        return {"status": "No historyId"}

    # Check if historyId has already been processed
    if history_id in processed_history_ids:
        return {"status": "Duplicate event"}
    
    processed_history_ids.add(history_id)
        
    # Fetch email from Gmail
    gmail = get_gmail_service()
    history = gmail.users().history().list(
        userId='me',
        startHistoryId=history_id,
        historyTypes=['messageAdded']
    ).execute()

    # messages = history.get('history', [])
    latest_message = get_latest_message(gmail)

    print("\n[Webhook] Passing email body to orchestrator...\n")
    # result = orchestrator.run(latest_message.get("body", ""))
    result = await orchestrator.run(latest_message.get("body", ""))
    print("\n[JIRA Ticket Result]:", result)

    await asyncio.sleep(30)
    return JSONResponse("Success", status_code=200)

    # Microsoft sends this for validation on initial webhook registration
    # body = await request.body()
    
    # email_text = body.decode("utf-8")
    # reader = EmailReaderAgent()
    # extractor = KeyPointExtractorAgent()
    # jira = JiraAgent()
    # orchestrator = Orchestrator(reader, extractor, jira)

    # result = orchestrator.run(email_text)
    # return JSONResponse(email_text, status_code=200)
    