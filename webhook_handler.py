from flask import jsonify
from message_processor import process_user_message

VERIFY_TOKEN = "myCustomVerifyToken123"

def handle_webhook(request):
    if request.method == 'GET':
        token_sent = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    if request.method == 'POST':
        incoming_msg = request.get_json()
        entry = incoming_msg.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        # Handle status updates
        if 'statuses' in value:
            for status in value.get('statuses', []):
                print(f"Status update received: {status.get('status')} for ID {status.get('id')}")
            return jsonify({"status": "status received"}), 200

        # Handle actual messages
        if 'messages' in value:
            messages = value.get('messages', [])
            for message in messages:
                process_user_message(message)
            return jsonify({"status": "message processed"}), 200

    return jsonify({"status": "no actionable data"}), 200
