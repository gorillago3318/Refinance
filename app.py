from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import logging
import requests

# Explicitly load the .env file
env_path = r"C:\Users\waiki\OneDrive\Desktop\REFINANCE WEI\refinance-automation\.env"
load_dotenv(env_path)

# Retrieve environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Verify environment variables
if not ACCESS_TOKEN or not PHONE_NUMBER_ID or not VERIFY_TOKEN:
    raise RuntimeError("Missing required environment variables. Please check your .env file.")

# Debug: Print loaded environment variables
logging.basicConfig(level=logging.DEBUG)  # Set up logging
logging.debug(f"Loaded ACCESS_TOKEN: {ACCESS_TOKEN[:10]}...")  # Partial for security
logging.debug(f"Loaded PHONE_NUMBER_ID: {PHONE_NUMBER_ID}")
logging.debug(f"Loaded VERIFY_TOKEN: {VERIFY_TOKEN}")

# Initialize Flask app
app = Flask(__name__)

# Placeholder for user data (in-memory storage for simplicity)
user_data_store = {}

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Handles WhatsApp webhook requests.
    """
    if request.method == 'GET':
        return verify_webhook()
    elif request.method == 'POST':
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
    logging.debug(f"Incoming webhook payload: {incoming_payload}")

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
    try:
        entry = payload.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        return value.get('messages', [])
    except (IndexError, KeyError, TypeError) as e:
        logging.error(f"Error extracting messages: {e}")
        return []

def process_user_message(message):
    """
    Processes incoming user messages and generates a response.
    """
    from_number = message.get('from', '').strip()
    if not from_number:
        logging.warning("No 'from' field in message. Skipping.")
        return

    # Determine the type of message (text or button reply)
    if "text" in message:
        user_message = message.get('text', {}).get('body', '').strip()
    elif "interactive" in message and message["interactive"].get("type") == "button_reply":
        user_message = message["interactive"]["button_reply"]["id"]
    else:
        logging.debug("Unsupported message type. Ignoring.")
        return

    # Debug: Print the received message
    logging.info(f"Raw user input received: {user_message}")

    # Retrieve or initialize user data
    user_data = user_data_store.get(from_number, {"step": 0})

    # Handle conversation logic
    try:
        response, updated_user_data = handle_conversation(user_message, user_data)
        user_data_store[from_number] = updated_user_data
    except Exception as e:
        logging.error(f"Error in conversation flow: {e}", exc_info=True)
        response = "Sorry, there was an error processing your message. Please try again."

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

    # Construct payload
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": response}
    }

    try:
        logging.debug(f"Sending payload: {payload}")
        response_data = requests.post(url, headers=headers, json=payload)

        # Log detailed response for debugging
        logging.debug(f"Response Status Code: {response_data.status_code}")
        logging.debug(f"Response Headers: {response_data.headers}")
        logging.debug(f"Response Content: {response_data.text}")

        response_data.raise_for_status()  # Raise error for HTTP responses like 401, 403, etc.
        logging.info(f"Message sent successfully to {recipient_id}.")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPError: {e}")
        logging.error(f"Response Content: {response_data.text}")
    except Exception as general_error:
        logging.error(f"Unexpected error while sending message: {general_error}", exc_info=True)

def handle_conversation(user_message, user_data):
    """
    Handles the conversation logic.
    """
    # Debug: Inspect input and step
    logging.debug(f"Handling message: {user_message}, Current step: {user_data.get('step', 0)}")

    # Example: Simple echo bot with corrected response
    step = user_data.get("step", 0)
    user_data["step"] = step + 1
    response = f"You said: {user_message}. Step is now {user_data['step']}."
    return response, user_data

if __name__ == '__main__':
    # Enable debug mode for Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
