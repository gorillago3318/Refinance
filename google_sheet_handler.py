from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os

# Define the scope and service account file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Load credentials from the service account file
try:
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
except Exception as e:
    print(f"Error loading credentials: {e}")
    credentials = None

# Specify your spreadsheet ID
SPREADSHEET_ID = '1E9X2vRhPIUFRuuIrZmV3DqoTbeIMWMKXr-uZw5Bbu8E'

def append_to_google_sheet(sheet_name, values):
    """
    Appends a row of values to a specified Google Sheet.

    Args:
        sheet_name (str): The name or range of the sheet (e.g., 'Sheet1' or 'Sheet1!A1:D1').
        values (list): A list of values to append as a new row.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    if not credentials:
        print("Google Sheets credentials not initialized.")
        return False

    try:
        # Initialize the Sheets API service
        service = build('sheets', 'v4', credentials=credentials)
        
        # Prepare the request body
        body = {'values': [values]}
        
        # Call the Sheets API to append data
        response = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_name,
            valueInputOption="RAW",
            body=body
        ).execute()

        print(f"Data appended successfully to sheet '{sheet_name}'. Response: {response}")
        return True
    except Exception as e:
        print(f"Error appending to Google Sheets: {e}")
        return False
