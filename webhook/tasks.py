import os
import requests
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_message_to_slack(sender_name, message_text):
    if not SLACK_WEBHOOK_URL:
        print("No Slack webhook URL Configured!")
        return
    payload = {
        "text" : f"Message from {sender_name}: {message_text}"
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    print("Slack response:",response.status_code,response.text)