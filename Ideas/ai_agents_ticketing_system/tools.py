import os
import requests
import json
from datetime import datetime, timedelta
from models import get_llama_response

jira_url = "https://aimeetingnotes.atlassian.net/"
auth_user = "vishal.chauhan@tiezinteractive.com"
auth_token = "ATATT3xFfGF0Vh6S4pbDrMVuH0LmyBlPt6iK23czTD8tf5AEbBfR6v939vUkrdyST7tLHmf57D8oD1zIXJlR_D35xr0PEa9sTjJqaB7LISUmRIeaDKwvArMZyMiwzbuFr9LFavbFNL9VwbpN3QrpLh81VM57p4vIPYAuBnGlC9XiHxAo9GWCzTI=0724B1C6"
project_key = "AIM"

# def extract_email_body(email_text):
#     prompt = f"""You are an expert meeting assistant. Read email carefully and extract the meaningful body from the email_text.
#         - Extract data only if email source is notetaker or meeting assistant like Fathom, Otter, Team etc..
#         - Ignore unnecessary text like Hi, Hello or any other formal text or greetings.
#         - Capture only email body has meaning like tasks, instructions, to do list, key points, bullet points, asks, queries, questions, enquiries, key features,
#         assignments, updates, notes, work, to do, list etc, which has meaning complete or execute or perform as a task.
#         - DO NOT add any extra content
#         - DO NOT explain.
#         Content:
#         {email_text}

#         Format:
#         [
#         {{"task": "", "due_date": "", "assigned_team": ""}},
#         ...
#         ]"""
    
#     return get_llama_response(prompt)
#     # body = email_text.split("\n\n", 1)[-1].strip()
#     # return body

def extract_keypoints_as_json(llm_response):
    try:
        return json.loads(llm_response)
    except json.JSONDecodeError:
        return [{"task": "Unable to parse response", "due_date": "", "assign_to": ""}]
    
def extract_email_body(email):
    """Extract the email content - in real use you'd parse MIME structure."""
    return email

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
            "summary": task.get('summary', "No summary"),
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

def fetch_existing_jira_tickets():
    jql=None
    headers = {
        "Content-Type": "application/json"
    }

    if not jql:
        jql = f'project="{project_key}" ORDER BY created DESC'

    query_params = {
        "jql": jql,
        "maxResults": 100,
        "fields": "id,key,summary,description,status"
    }

    response = requests.get(
        f"{jira_url}/rest/api/3/search",
        headers=headers,
        auth=(auth_user, auth_token),
        params=query_params
    )

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json()
    
    issues = []
    for issue in data.get("issues", []):
        issues.append({
            "id": issue["id"],
            "key": issue["key"],
            "summary": issue["fields"]["summary"],
            "description": issue["fields"].get("description", ""),
            "status": issue["fields"]["status"]["name"]
        })

    return issues

def generate_comparison_prompt(existing_tasks, new_tasks):
    return f"""
            Compare the following two task lists.

            Existing JIRA tasks:
            {existing_tasks}

            Newly extracted tasks from meeting:
            {new_tasks}

            Return a JSON object with two keys: "duplicates" and "unique".
            - "duplicates": items from the new list that are semantically the same either in meaning, or in tone or in context as existing ones.
            - "unique": items that are truly new.
            - DO NOT add any extra content
            - DO NOT explain.
            - DO NOT suggest or add any information
            Only return valid JSON.

            In case of duplicates follow the below rules:
            """

def update_jira_task_status(duplicates):

    headers = {
        "Content-Type": "application/json"
    }

    results = []

    if isinstance(duplicates, str):
        try:
            duplicates = json.loads(duplicates)
        except json.JSONDecodeError:
            return [{"error": "Invalid JSON string"}]

    for task in duplicates:
        issue_key = task.get("key")
        if not issue_key:
            results.append({"error": "Missing issue ID"})
            continue

        # Step 1: Get available transitions
        transitions_url = f"{jira_url}/rest/api/3/issue/{issue_key}/transitions"
        resp = requests.get(transitions_url, auth=(auth_user, auth_token), headers=headers)
        if resp.status_code != 200:
            return {"success": False, "error": f"Failed to get transitions: {resp.text}"}

        transitions = resp.json().get("transitions", [])
        transition_id = None



        # Step 2: Find the transition ID for 'Close'
        for t in transitions:
            # You may need to adjust this if your workflow uses 'Closed' or another name
            # if t["name"].lower() in [task.get("status")]:
            if t["name"].lower() in ["close", "done", "resolved", "completed","in progress"]:  
                transition_id = t["id"]
                break

        if not transition_id:
            return {"success": False, "error": "No 'Close' transition found for this issue."}

        # Step 3: Perform the transition
        payload = {
            "transition": {
                "id": transition_id
            }
        }
        resp = requests.post(transitions_url, auth=(auth_user, auth_token), headers=headers, json=payload)
        if resp.status_code not in [200, 204]:
            return {"success": False, "error": f"Failed to close issue: {resp.text}"}

        # Step 4: (Optional) Confirm the status
        issue_url = f"{jira_url}/rest/api/3/issue/{issue_key}"
        resp = requests.get(issue_url, auth=(auth_user, auth_token), headers=headers)
        if resp.status_code == 200:
            status = resp.json()["fields"]["status"]["name"]
            results.append({"success": True, "new_status": status})
        else:
            results.append({"success": True, "message": "Issue updated, but failed to confirm new status."})
    
    return results


def update_jira_task_comment(duplicates):

    headers = {
        "Content-Type": "application/json"
    }

    results = []

    if isinstance(duplicates, str):
        try:
            duplicates = json.loads(duplicates)
        except json.JSONDecodeError:
            return [{"error": "Invalid JSON string"}]

    for task in duplicates:
        issue_id = task.get("id") or task.get("key")
        if not issue_id:
            results.append({"error": "Missing issue ID"})
            continue

        comment_payload = {
            "body": f"🔁 Duplicate detected in meeting notes on {datetime.now().strftime('%Y-%m-%d')}. No new task created."
        }

        # Add a comment to the JIRA ticket
        comment_response = requests.post(
            f"{jira_url}/rest/api/3/issue/{issue_id}/comment",
            auth=(auth_user, auth_token),
            headers=headers,
            data=json.dumps(comment_payload)
        )

        # Optionally: Transition the issue to a specific status (e.g., "Done", "Duplicate", etc.)
        # You'll need to know the correct transition ID for your workflow
        # transition_payload = {"transition": {"id": "31"}}  # Replace 31 with real transition ID
        # transition_response = requests.post(
        #     f"{jira_url}/rest/api/2/issue/{issue_id}/transitions",
        #     auth=(auth_user, auth_token),
        #     headers=headers,
        #     data=json.dumps(transition_payload)
        # )

        if comment_response.status_code in [200, 201]:
            results.append({
                "id": issue_id,
                "status": task.get("status", "No status"),
            })
        else:
            results.append({
                "id": issue_id,
                "error": comment_response.text
            })

        # Write history_id to webhook_log.json
        # with open("webhook_log.json", "a") as log_file:
        #     json.dump(results, log_file, indent=0)
        #     log_file.write("\n")

    return results

