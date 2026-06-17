"""
Test sending formatted message to the workflow (channel version).
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv('SLACK_WEBHOOK_URL')

# Send formatted message
message = """*SCAN COMPLETE - scan_20260617_162309*

*Summary:*
- Pages Scanned: 100
- Total Issues: 670  
- New Issues: 508
- Resolved Issues: 0

*Issue Breakdown:*
- Redirect: 667
- Timeout: 5
- Broken Link: 2

*Download Full Report:*
https://ibm.sharepoint.com/sites/page-monitoring/reports/scan_results_scan_20260617_162309_20260617_171904.xlsx
"""

print("Sending test to #page-monitoring channel...")
response = requests.post(webhook_url, json={"text": message})

if response.status_code == 200:
    print("[OK] Message sent! Check #page-monitoring channel in Slack.")
else:
    print(f"[FAILED] Status: {response.status_code}")
    print(response.text)

# Made with Bob
