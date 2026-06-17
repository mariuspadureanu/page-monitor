"""
Test script to send scan completion notification with report link to Slack.
This simulates what will happen after each scan completes.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import notifier
from src.notifier import Notifier

async def test_scan_complete_notification():
    """Test sending scan completion notification with report link."""
    
    # Configuration
    config = {
        'slack': {
            'enabled': True,
            'webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
            'channel': '#page-monitoring',
            'mention_on_critical': True,
            'critical_threshold': 10,
            'report_base_url': os.getenv('SHAREPOINT_REPORT_URL')
        },
        'email': {
            'enabled': False
        }
    }
    
    # Initialize notifier
    notifier = Notifier(config)
    
    # Sample scan statistics (from your recent scan)
    scan_id = "scan_20260617_162309"
    statistics = {
        'pages_scanned': 100,
        'total_issues': 670,
        'new_issues': 508,
        'resolved_issues': 0,
        'issues_by_type': {
            'redirect': 667,
            'timeout': 5,
            'broken_link': 2
        }
    }
    
    # Report filename (the Excel file you generated)
    report_filename = "scan_results_scan_20260617_162309_20260617_171904.xlsx"
    
    print("=" * 60)
    print("Testing Slack Scan Completion Notification")
    print("=" * 60)
    print(f"\nScan ID: {scan_id}")
    print(f"Report: {report_filename}")
    print(f"SharePoint URL: {config['slack']['report_base_url']}")
    print(f"\nStatistics:")
    print(f"  - Pages Scanned: {statistics['pages_scanned']}")
    print(f"  - Total Issues: {statistics['total_issues']}")
    print(f"  - New Issues: {statistics['new_issues']}")
    print(f"\nSending notification to Slack...")
    
    # Send notification
    success = await notifier.send_scan_complete(
        scan_id=scan_id,
        statistics=statistics,
        report_filename=report_filename
    )
    
    if success:
        print("\n[SUCCESS] Check your Slack channel for the notification.")
        print("\nThe message should include:")
        print("  - Scan completion summary")
        print("  - Statistics breakdown")
        print("  - Download link to the Excel report")
        print("\nNOTE: You'll need to manually upload the report to SharePoint")
        print(f"      at: {config['slack']['report_base_url']}/{report_filename}")
    else:
        print("\n[FAILED] Check the error messages above.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_scan_complete_notification())

# Made with Bob
