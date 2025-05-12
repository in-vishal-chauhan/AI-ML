import os
import requests
import json
from datetime import datetime, timedelta
from models import get_llama_response

def extract_email_body(email_text):
    prompt = f"""Read email carefully and extract the meaningful body from the email_text.
        - Ignore unnecessary text like Hi, Hello or any other formal text or greetings.
        - Capture only email body has meaning like tasks, instructions, to do list, key points, bullet points, asks, queries, questions, enquiries, key features,
        assignments, updates, notes, work, to do, list etc, which has meaning complete or execute or perform as a task.
        - DO NOT add any extra content
        - DO NOT explain.
        Content:
        {email_text}

        Format:
        [
        {{"task": "", "due_date": "", "assigned_team": ""}},
        ...
        ]"""
    
    return get_llama_response(prompt)
    # body = email_text.split("\n\n", 1)[-1].strip()
    # return body

def extract_keypoints_as_json(llm_response):
    try:
        return json.loads(llm_response)
    except json.JSONDecodeError:
        return [{"task": "Unable to parse response", "due_date": "", "assign_to": ""}]
    
def extract_email_body(email):
    """Extract the email content - in real use you'd parse MIME structure."""
    return email.strip()


def extract_fathom_data(content):
    print("[Tool: extract_fathom_data] Creating Fathom prompt for LLM...")
    prompt = f"""
        You are an expert meeting assistant.

        Extract all **actionable tasks** from the following Fathom meeting notes.

        Return the result as a JSON list in this format:
        [
        {{"task": "", "due_date": "", "assigned_team": ""}},
        ...
        ]

        - Do not explain.
        - Do not add any extra content.
        - Do not suggest or add any information
        - Only create json format

        Fathom Meeting Notes:
        {content}
        """
    return prompt


def extract_otter_data(content):
    print("[Tool: extract_otter_data] Creating Otter prompt for LLM...")
    prompt = f"""
        You are a highly accurate Otter AI summarizer.

        From the following Otter-generated meeting summary, extract all **action items**.

        Return your output as a JSON list in this format:
        [
        {{"task": "", "due_date": "", "assigned_team": ""}},
        ...
        ]

        - Do not explain.
        - Do not add any extra content.
        - Do not suggest or add any information
        - Only create json format

        Otter Summary:
        {content}
        """
    return prompt


def extract_team_notetaker_data(content):
    print("[Tool: extract_team_notetaker_data] Creating Team Notetaker prompt for LLM...")
    prompt = f"""
        You're an intelligent assistant parsing meeting notes from Team Notetaker.

        Identify all **key tasks** mentioned in the email.

        Return your output as a JSON list in this format:
        [
        {{"task": "", "due_date": "", "assigned_team": ""}},
        ...
        ]
        
        - Do not explain.
        - Do not add any extra content.
        - Do not suggest or add any information
        - Only create json format
        
        Team Notetaker Content:
        {content}
        """
    return prompt



def create_jira_ticket(task_json):
    jira_url = "https://aimeetingnotes.atlassian.net/"
    auth_user = "vishal.chauhan@tiezinteractive.com"
    auth_token = "ATATT3xFfGF0Vh6S4pbDrMVuH0LmyBlPt6iK23czTD8tf5AEbBfR6v939vUkrdyST7tLHmf57D8oD1zIXJlR_D35xr0PEa9sTjJqaB7LISUmRIeaDKwvArMZyMiwzbuFr9LFavbFNL9VwbpN3QrpLh81VM57p4vIPYAuBnGlC9XiHxAo9GWCzTI=0724B1C6"
    project_key = "AIM"

    headers = {
        "Content-Type": "application/json"
    }

    results = []
    print("====================",task_json)
    if isinstance(task_json, str):
        try:
            task_json = json.loads(task_json)
        except json.JSONDecodeError:
            return [{"error": "Invalid JSON string"}]
            
    for task in task_json:
        due_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        assigned_team = task.get('assigned_team', 'aimeetingnotes')
        issue_data = {
            "fields": {
            "project": {"key": project_key},
            "summary": task.get('task', "No summary"),
            "description": f"Due: {due_date}\nTeam: {assigned_team}\nAssignee: {assigned_team}",
            "duedate":due_date,
            "issuetype": {"name": "Task"},
            "labels": ["New"],
            }
        }

        response = requests.post(
            f"{jira_url}/rest/api/2/issue",
            auth=(auth_user, auth_token),
            headers=headers,
            data=json.dumps(issue_data)
        )

        if response.status_code in [200, 201]:
            results.append(response.json())
        else:
            results.append({"error": response.text})
    return results
