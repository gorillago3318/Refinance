import requests
import os

# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def send_message_to_whatsapp(response):
    """
    Sends a message to a WhatsApp user via the WhatsApp Business API.

    Args:
        response (dict): The payload for the API request, containing message details.

    Returns:
        dict: The API response if the request is successful.
        None: If the request fails.
    """
    url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        # Make the API request
        response_data = requests.post(url, headers=headers, json=response)
        response_data.raise_for_status()  # Raise an error for non-2xx responses
        print(f"Message sent successfully: {response_data.json()}")
        return response_data.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        return None
