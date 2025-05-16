
def parse_email(email_payload):
    return {
        "from": email_payload.get("from", ""),
        "subject": email_payload.get("subject", ""),
        "body": email_payload.get("body", ""),
    }
