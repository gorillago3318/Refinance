from flask import Flask, request, jsonify
from conversation_flow import handle_conversation
import os
import requests
import json
import logging

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Placeholder for user data (in-memory storage for simplicity)
user_data_store = {}

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Handles WhatsApp webhook requests.
    """
    if request.method == 'GET':
        return verify_webhook()
    
    if request.method == 'POST':
        return handle_incoming_messages()

def verify_webhook():
    """Verifies the webhook for WhatsApp."""
    token_sent = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token_sent == VERIFY_TOKEN:
        logging.info("Webhook verified successfully.")
        return challenge, 200
    logging.warning("Webhook verification failed.")
    return "Forbidden", 403

def handle_incoming_messages():
    """Handles incoming POST requests from WhatsApp."""
    incoming_payload = request.get_json()
    logging.debug(f"Debug: Incoming webhook payload: {json.dumps(incoming_payload, indent=2)}")

    try:
        messages = extract_messages(incoming_payload)
        if messages:
            for message in messages:
                process_user_message(message)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

def extract_messages(payload):
    """Extracts messages from the incoming payload."""
    entry = payload.get('entry', [{}])[0]
    changes = entry.get('changes', [{}])[0]
    value = changes.get('value', {})
    return value.get('messages', [])

def process_user_message(message):
    """
    Processes incoming user messages and generates a response.
    """
    from_number = message.get('from', '')  # User's WhatsApp ID
    user_message = message.get('text', {}).get('body', '').strip()
    
    logging.debug(f"User input received from {from_number}: {user_message}")

    # Retrieve or initialize user data
    user_data = user_data_store.setdefault(from_number, {"step": 0})

    # Handle text-based input
    response, updated_user_data = handle_conversation(user_message, user_data)
    user_data_store[from_number] = updated_user_data

    # Send the response
    send_message_to_whatsapp(from_number, response)

def send_message_to_whatsapp(recipient_id, response):
    """
    Sends a message to WhatsApp using the Meta API.
    """
    url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Construct payload based on response type
    if isinstance(response, dict):  # Buttons or structured responses
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": response["text"]},
                "action": {"buttons": response["buttons"]}
            }
        }
    else:  # Plain text response
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {"body": response}
        }

    try:
        logging.debug(f"Debug: Sending payload: {json.dumps(payload)}")
        response_data = requests.post(url, headers=headers, json=payload)
        response_data.raise_for_status()  # Raise an error for bad responses
        logging.info(f"Message sent successfully to {recipient_id}.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message: {e}")

if __name__ == '__main__':
    app.run(debug=True)
