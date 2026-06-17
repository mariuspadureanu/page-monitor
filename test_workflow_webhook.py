"""
Send a simple test to the workflow webhook to register the 'text' field.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv('SLACK_WEBHOOK_URL')

# Send simple test payload
payload = {
    "text": "This is a test message with the text field"
}

print("Sending test to workflow webhook...")
response = requests.post(webhook_url, json=payload)

if response.status_code == 200:
    print("[OK] Test sent successfully!")
    print("\nNow go back to your Workflow Builder and:")
    print("1. Click 'Insert a variable'")
    print("2. Select 'From a webhook'")
    print("3. You should now see a 'text' variable")
    print("4. Select that 'text' variable")
    print("5. Save the workflow")
else:
    print(f"[FAILED] Status: {response.status_code}")
    print(response.text)

# Made with Bob
