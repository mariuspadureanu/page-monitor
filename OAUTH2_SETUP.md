# OAuth2 Email Setup Guide

This guide explains how to set up OAuth2 authentication for email notifications in IBM Page Monitor.

## Why OAuth2?

✅ **More Secure**: No password storage
✅ **Token-based**: Can be revoked anytime
✅ **Industry Standard**: Used by Gmail, Office 365, IBM Cloud
✅ **IBM Compliant**: Meets enterprise security requirements
✅ **Audit Trail**: All access is logged

---

## Supported Providers

- **Gmail** (Google Workspace)
- **Office 365** (Microsoft 365)
- **IBM Cloud Email**

---

## Setup Instructions

### Option 1: Gmail / Google Workspace

#### Step 1: Create OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Gmail API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. Create OAuth2 Credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app" or "Web application"
   - Name: "IBM Page Monitor"
   - Click "Create"
   - **Save the Client ID and Client Secret**

#### Step 2: Get Refresh Token

Run this Python script to get your refresh token:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_refresh_token():
    creds = None

    # Create flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',  # Download from Google Cloud Console
        SCOPES
    )

    # Run local server for authorization
    creds = flow.run_local_server(port=0)

    print("\n=== OAuth2 Credentials ===")
    print(f"Refresh Token: {creds.refresh_token}")
    print(f"Client ID: {creds.client_id}")
    print(f"Client Secret: {creds.client_secret}")

    return creds.refresh_token

if __name__ == '__main__':
    token = get_refresh_token()
```

#### Step 3: Configure Environment Variables

Add to `.env`:

```env
# Gmail OAuth2
EMAIL_PROVIDER=gmail
OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_REFRESH_TOKEN=your-refresh-token
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=alerts@example.com
```

#### Step 4: Update config.yaml

```yaml
notifications:
  email:
    enabled: true
    auth_method: oauth2
    provider: gmail
    client_id: "${OAUTH_CLIENT_ID}"
    client_secret: "${OAUTH_CLIENT_SECRET}"
    refresh_token: "${OAUTH_REFRESH_TOKEN}"
    from_address: "${EMAIL_FROM}"
    to_addresses:
      - "${EMAIL_TO}"
```

---

### Option 2: Office 365 / Microsoft 365

#### Step 1: Register Application in Azure

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
   - Name: "IBM Page Monitor"
   - Supported account types: "Accounts in this organizational directory only"
   - Redirect URI: "http://localhost:8080" (for getting token)
   - Click "Register"

4. Note the **Application (client) ID**

5. Create Client Secret:
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: "IBM Page Monitor"
   - Expires: Choose duration
   - Click "Add"
   - **Copy the secret value immediately** (won't be shown again)

6. Set API Permissions:
   - Go to "API permissions"
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Select "Delegated permissions"
   - Add: `Mail.Send`, `SMTP.Send`
   - Click "Add permissions"
   - Click "Grant admin consent" (requires admin)

#### Step 2: Get Refresh Token

Use this script:

```python
from msal import PublicClientApplication
import webbrowser

CLIENT_ID = "your-client-id"
TENANT_ID = "your-tenant-id"  # or "common"
SCOPES = ["https://outlook.office365.com/SMTP.Send"]

app = PublicClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}"
)

# Get authorization code
flow = app.initiate_device_flow(scopes=SCOPES)
print(flow['message'])

# Wait for user to authenticate
result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    print("\n=== OAuth2 Credentials ===")
    print(f"Refresh Token: {result.get('refresh_token')}")
    print(f"Access Token: {result['access_token']}")
else:
    print(f"Error: {result.get('error_description')}")
```

#### Step 3: Configure Environment Variables

Add to `.env`:

```env
# Office 365 OAuth2
EMAIL_PROVIDER=office365
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_REFRESH_TOKEN=your-refresh-token
EMAIL_FROM=your-email@company.com
EMAIL_TO=alerts@company.com
```

---

### Option 3: IBM Cloud Email

#### Step 1: Create IBM Cloud Service Credentials

1. Go to [IBM Cloud Console](https://cloud.ibm.com/)
2. Navigate to your email service
3. Create service credentials
4. Copy the OAuth2 credentials

#### Step 2: Configure Environment Variables

Add to `.env`:

```env
# IBM Cloud OAuth2
EMAIL_PROVIDER=ibm
OAUTH_CLIENT_ID=your-ibm-client-id
OAUTH_CLIENT_SECRET=your-ibm-client-secret
OAUTH_REFRESH_TOKEN=your-ibm-refresh-token
EMAIL_FROM=noreply@ibm.com
EMAIL_TO=alerts@ibm.com
```

---

## Configuration Reference

### Full config.yaml Example

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#page-monitoring"
    mention_on_critical: true
    critical_threshold: 10

  email:
    enabled: true
    auth_method: oauth2 # 'oauth2' or 'password'

    # OAuth2 settings
    provider: gmail # 'gmail', 'office365', or 'ibm'
    client_id: "${OAUTH_CLIENT_ID}"
    client_secret: "${OAUTH_CLIENT_SECRET}"
    refresh_token: "${OAUTH_REFRESH_TOKEN}"

    # Email settings
    from_address: "${EMAIL_FROM}"
    to_addresses:
      - "${EMAIL_TO}"

    # Schedule
    send_daily_summary: true
    send_weekly_report: true
    send_monthly_report: true
```

### Environment Variables (.env)

```env
# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email OAuth2
EMAIL_PROVIDER=gmail
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_REFRESH_TOKEN=your-refresh-token
EMAIL_FROM=monitor@example.com
EMAIL_TO=alerts@example.com
```

---

## Troubleshooting

### Error: "Invalid grant"

- **Cause**: Refresh token expired or revoked
- **Solution**: Generate a new refresh token

### Error: "Insufficient permissions"

- **Cause**: Missing API permissions
- **Solution**: Add required scopes and grant admin consent

### Error: "Token refresh failed"

- **Cause**: Client secret expired or incorrect
- **Solution**: Generate new client secret in Azure/Google Console

### Error: "SMTP authentication failed"

- **Cause**: OAuth2 not enabled for SMTP
- **Solution**: Enable "Less secure app access" or use app-specific password

---

## Security Best Practices

1. **Store credentials securely**:
   - Use environment variables
   - Never commit `.env` to git
   - Use IBM Secrets Manager in production

2. **Rotate tokens regularly**:
   - Set expiration on client secrets
   - Refresh tokens periodically
   - Monitor for unauthorized access

3. **Limit permissions**:
   - Only grant `Mail.Send` permission
   - Don't grant `Mail.Read` or other unnecessary scopes

4. **Monitor usage**:
   - Check OAuth2 audit logs
   - Set up alerts for unusual activity
   - Review token usage regularly

5. **Use service accounts**:
   - Create dedicated service account for monitoring
   - Don't use personal email accounts
   - Set up proper access controls

---

## Testing OAuth2 Setup

Test your OAuth2 configuration:

```python
import asyncio
from src.email_oauth2 import OAuth2EmailAuth

async def test_oauth2():
    auth = OAuth2EmailAuth(
        provider='gmail',
        client_id='your-client-id',
        client_secret='your-client-secret',
        refresh_token='your-refresh-token'
    )

    try:
        token = await auth.get_access_token()
        print(f"✅ OAuth2 working! Token: {token[:20]}...")
    except Exception as e:
        print(f"❌ OAuth2 failed: {e}")

asyncio.run(test_oauth2())
```

---

## Alternative: Slack Only (Simplest)

If OAuth2 setup is too complex, you can disable email and use Slack only:

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"

  email:
    enabled: false # Disable email completely
```

This is the simplest and most secure option if your team uses Slack.

---

## Support

For issues with OAuth2 setup:

1. Check provider documentation (Google, Microsoft, IBM)
2. Verify all credentials are correct
3. Check API permissions and admin consent
4. Review application logs for detailed errors

For IBM-specific questions, contact your IT security team.
