from utils import load_user_data, save_user_data, send_message_to_whatsapp
from conversation_flow import handle_conversation

# Load user data
user_data = load_user_data()

def process_user_message(message):
    from_number = message.get('from', '')  # Sender's phone number

    # Determine if the message is a text or button reply
    if "text" in message:
        user_message = message.get('text', {}).get('body', '').strip()
    elif "interactive" in message and message["interactive"].get("type") == "button_reply":
        user_message = message["interactive"]["button_reply"]["id"]  # Extract button reply ID
    else:
        print("Debug: Unsupported message type. Ignoring.")
        return

    # Debug: Print user input
    print(f"Debug: User input received - {user_message}")

    # Load or initialize user session
    user = user_data.get(from_number, {'step': 0})
    
    # Ensure to pass correct user_message to handle_conversation
    response, updated_user_data = handle_conversation(user_message, user)
    
    # Update and save user data
    user_data[from_number] = updated_user_data  
    save_user_data(user_data)  

    # Send the response to the user
    if response:
        send_message_to_whatsapp(from_number, response)
