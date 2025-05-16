
from tools.email_tool import parse_email
from tools.note_identification_tool import identify_note_source
from tools.action_item_extractor_tool import extract_action_items
from tools.ticket_creation_tool import create_ticket
from tools.log_response_tool import log_ticket_response
from service.grok_api import GrokAPI
# def orchestrate(email_payload):
#     email_data = parse_email(email_payload)
#     is_note = identify_note_source(email_data["body"])
#     if not is_note:
#         return {"status": "Not a note email"}
#     actions = extract_action_items(email_data["body"])
#     if not actions:
#         return {"status": "No actions found"}
#     result = create_ticket(email_data["from"], actions)
#     log_ticket_response(email_data["from"], actions, result)
#     return result

def orchestrate(self, email_body):
        groq = GrokAPI()
        system_prompt = """
        You are an orchestrator.

        Your task is to decide whether the email is formal email or Note Taker like TickTick, Fathom, FireFlies, Otter or etc which contains todo list, activity, action item or key points.
        - If it's formal email then return 'formal'
        - If it's Note taker email then extract key points, activity, action items, to do list, etc.
        - Convert those all data in json format
        - return that json data

        Based on your decision, return ONLY json formatted data
        Do not explain. Just return the exact json data extracted from email body.
        """

        json_data = groq.ask(system_prompt, email_body).strip()
        return json_data
