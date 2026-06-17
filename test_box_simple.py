"""
Test Box connection using REST API (no SDK needed).
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_box_api():
    """Test Box API connection."""
    
    access_token = os.getenv('BOX_ACCESS_TOKEN')
    folder_id = os.getenv('BOX_FOLDER_ID', '0')
    
    print("=" * 60)
    print("Testing Box API Connection")
    print("=" * 60)
    print(f"\nAccess Token: {access_token[:20]}..." if access_token else "Not set")
    print(f"Folder ID: {folder_id}")
    
    if not access_token:
        print("\n[ERROR] BOX_ACCESS_TOKEN not set")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        # Test 1: Get user info
        print("\n[1/2] Testing API connection...")
        response = requests.get('https://api.box.com/2.0/users/me', headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print(f"[OK] Connected as: {user['name']} ({user['login']})")
        else:
            print(f"[ERROR] API call failed: {response.status_code}")
            print(response.text)
            return False
        
        # Test 2: Get folder info
        print(f"[2/2] Testing folder access (ID: {folder_id})...")
        response = requests.get(f'https://api.box.com/2.0/folders/{folder_id}', headers=headers)
        
        if response.status_code == 200:
            folder = response.json()
            print(f"[OK] Folder accessible: {folder['name']}")
        else:
            print(f"[ERROR] Folder access failed: {response.status_code}")
            print(response.text)
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Box API is working!")
        print("=" * 60)
        print("\nYou can now run scans and reports will upload to Box automatically.")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False

if __name__ == "__main__":
    test_box_api()

# Made with Bob
