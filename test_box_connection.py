"""
Test Box connection and upload functionality.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from boxsdk import Client, OAuth2

# Load environment variables
load_dotenv()

def test_box_connection():
    """Test Box connection and upload."""
    
    print("=" * 60)
    print("Testing Box Connection")
    print("=" * 60)
    
    # Get credentials
    client_id = os.getenv('BOX_CLIENT_ID')
    client_secret = os.getenv('BOX_CLIENT_SECRET')
    access_token = os.getenv('BOX_ACCESS_TOKEN')
    folder_id = os.getenv('BOX_FOLDER_ID', '0')
    
    print(f"\nClient ID: {client_id[:20]}..." if client_id else "Client ID: Not set")
    print(f"Access Token: {access_token[:20]}..." if access_token else "Access Token: Not set")
    print(f"Folder ID: {folder_id}")
    
    if not access_token:
        print("\n[ERROR] BOX_ACCESS_TOKEN not set in .env file")
        return False
    
    try:
        # Initialize Box client
        print("\n[1/4] Initializing Box client...")
        oauth = OAuth2(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token
        )
        client = Client(oauth)
        
        # Test connection
        print("[2/4] Testing connection...")
        user = client.user().get()
        print(f"[OK] Connected as: {user.name} ({user.login})")
        
        # Test folder access
        print(f"[3/4] Testing folder access (ID: {folder_id})...")
        folder = client.folder(folder_id).get()
        print(f"[OK] Folder accessible: {folder.name}")
        
        # Test file upload
        print("[4/4] Testing file upload...")
        
        # Find an existing report to upload
        reports_dir = Path("reports")
        if reports_dir.exists():
            excel_files = list(reports_dir.glob("scan_results_*.xlsx"))
            if excel_files:
                test_file = excel_files[0]
                print(f"Uploading test file: {test_file.name}")
                
                # Upload file
                uploaded_file = folder.upload(str(test_file), file_name=f"TEST_{test_file.name}")
                
                # Create shared link
                shared_link = uploaded_file.get_shared_link(access='open')
                download_url = shared_link['url']
                
                print(f"[OK] File uploaded successfully!")
                print(f"\nDownload URL: {download_url}")
                print(f"\nYou can access the file at: {download_url}")
                
                # Clean up test file
                print("\nCleaning up test file...")
                uploaded_file.delete()
                print("[OK] Test file deleted from Box")
                
            else:
                print("[SKIP] No report files found to test upload")
        else:
            print("[SKIP] Reports directory not found")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Box integration is working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Box connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if BOX_ACCESS_TOKEN is valid (may have expired)")
        print("2. Regenerate Developer Token in Box Developer Console")
        print("3. Verify folder ID is correct")
        print("=" * 60)
        return False

if __name__ == "__main__":
    test_box_connection()

# Made with Bob
