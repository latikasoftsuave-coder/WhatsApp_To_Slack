# webhook/views.py
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import send_message_to_slack
from dotenv import load_dotenv

load_dotenv()
VERIFY_TOKEN = "my_secure_token_123"

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return JsonResponse(challenge, safe=False)
        return JsonResponse({"error": "Invalid verify token"}, status=403)

    if request.method == "POST":
        payload = json.loads(request.body)
        allowed_senders = [s.strip() for s in os.getenv("ALLOWED_SENDERS", "").split(",")]
        print("Allowed senders:", allowed_senders)

        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    contacts = value.get("contacts", [])
                    messages = value.get("messages", [])

                    for contact, message in zip(contacts, messages):
                        name = contact.get("profile", {}).get("name", "Unknown")
                        print("Incoming message from:", name)

                        text = message.get("text", {}).get("body", "")
                        if name in allowed_senders:
                            print(f"Forwarding message from {name} to Slack: {text}")
                            send_message_to_slack(name, text)
                        else:
                            print(f"Skipping message from {name}, not in allowed list.")

    return JsonResponse({"status": "ok"})
