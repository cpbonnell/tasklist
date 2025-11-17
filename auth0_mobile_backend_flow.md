# Auth0 Login Flow for Flet Mobile + FastAPI Backend

## Architecture Overview

In a mobile deployment, your application will have two components:

1. **Flet Mobile App** (Thin Client) - Runs on user's device, contains NO
   secrets
2. **FastAPI Backend** (Cloud) - Contains Auth0 credentials and handles token
   exchange

## The Problem

You cannot use `page.login(provider)` in mobile apps because:

- Auth providers require `client_id` and `client_secret`
- Secrets cannot be embedded in mobile apps (they can be extracted via reverse
  engineering)
- Mobile apps need a different OAuth2 flow than web apps

## The Solution: Authorization Code Flow with PKCE

### What is PKCE?

PKCE (Proof Key for Code Exchange) is an OAuth2 extension designed for public
clients (like mobile apps) that cannot securely store secrets. It prevents
authorization code interception attacks.

### High-Level Flow

```
┌─────────────┐         ┌──────────┐         ┌─────────────┐
│ Flet Mobile │         │  Auth0   │         │   FastAPI   │
│     App     │         │          │         │   Backend   │
└──────┬──────┘         └────┬─────┘         └──────┬──────┘
       │                     │                       │
       │ 1. Login button     │                       │
       │    clicked          │                       │
       │                     │                       │
       │ 2. Open browser     │                       │
       │    with Auth0 URL   │                       │
       │────────────────────>│                       │
       │    (+ PKCE params)  │                       │
       │                     │                       │
       │ 3. User logs in     │                       │
       │────────────────────>│                       │
       │                     │                       │
       │ 4. Redirect with    │                       │
       │    auth code        │                       │
       │<────────────────────│                       │
       │                     │                       │
       │ 5. Send code to     │                       │
       │    backend          │                       │
       │───────────────────────────────────────────>│
       │                     │                       │
       │                     │ 6. Exchange code      │
       │                     │    for tokens         │
       │                     │<──────────────────────│
       │                     │    (using secret)     │
       │                     │                       │
       │                     │ 7. Return tokens      │
       │                     │───────────────────────>
       │                     │                       │
       │ 8. Return session   │                       │
       │    to app           │                       │
       │<───────────────────────────────────────────│
       │                     │                       │
```

## Detailed Implementation Steps

### Step 1: User Clicks "Login" Button in Flet App

When the user clicks login:

1. **Generate PKCE parameters** in the mobile app:
    - Create a random `code_verifier` (43-128 character random string)
    - Generate `code_challenge` = BASE64URL(SHA256(code_verifier))
    - Store `code_verifier` locally (you'll need it later)

2. **Build Auth0 authorization URL**:
   ```
   https://YOUR_DOMAIN.auth0.com/authorize?
     response_type=code&
     client_id=YOUR_CLIENT_ID&
     redirect_uri=YOUR_APP_SCHEME://callback&
     scope=openid profile email&
     code_challenge=GENERATED_CHALLENGE&
     code_challenge_method=S256&
     state=RANDOM_STATE_STRING
   ```

3. **Open the URL** in the system browser or in-app browser
    - Use `page.launch_url()` or a webview component
    - The URL should redirect to Auth0's login page

### Step 2: User Authenticates with Auth0

- User sees Auth0's Universal Login page
- User enters credentials (or uses social login)
- Auth0 validates credentials

### Step 3: Auth0 Redirects Back to Your App

After successful authentication, Auth0 redirects to:

```
YOUR_APP_SCHEME://callback?
  code=AUTHORIZATION_CODE&
  state=RANDOM_STATE_STRING
```

Your Flet app needs to:

1. Register a custom URL scheme (e.g., `myapp://callback`)
2. Listen for the callback URL
3. Extract the `code` parameter
4. Verify the `state` parameter matches what you sent

### Step 4: Send Code to FastAPI Backend

Your mobile app makes an API call to your backend:

```python
# Mobile app code
response = requests.post(
    "https://your-api.com/auth/exchange",
    json={
        "code": authorization_code,
        "code_verifier": code_verifier,  # The one you generated in Step 1
        "redirect_uri": "YOUR_APP_SCHEME://callback"
    }
)
```

### Step 5: FastAPI Backend Exchanges Code for Tokens

Your FastAPI backend endpoint:

```python
@app.post("/auth/exchange")
async def exchange_code(data: dict):
    # Backend makes request to Auth0
    response = requests.post(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        json={
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,  # Secret stays on backend!
            "code": data["code"],
            "code_verifier": data["code_verifier"],
            "redirect_uri": data["redirect_uri"]
        }
    )

    tokens = response.json()
    # tokens contains: access_token, id_token, refresh_token

    # Validate the ID token
    # Create a session for the user
    # Return session token to mobile app

    return {
        "session_token": create_session(tokens),
        "user_info": decode_id_token(tokens["id_token"])
    }
```

### Step 6: Mobile App Stores Session

The mobile app receives the session token and stores it securely:

- Use secure storage (iOS Keychain, Android Keystore)
- Include session token in subsequent API requests
- Use the session token to authenticate all backend calls

## Key Implementation Details

### Custom URL Scheme Registration

**For iOS**: Configure in `Info.plist` or app settings
**For Android**: Configure in `AndroidManifest.xml`
**For Flet**: You may need to use `page.on_route_change` or handle deep links

### PKCE Implementation in Python

```python
import hashlib
import base64
import secrets


def generate_pkce_pair():
    """Generate code_verifier and code_challenge"""
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')

    return code_verifier, code_challenge
```

### Session Management

Instead of giving the mobile app the actual Auth0 tokens, your backend should:

1. Store the Auth0 tokens securely (in a database or Redis)
2. Generate a session token (e.g., JWT signed by your backend)
3. Return only the session token to the mobile app
4. Use the session token to identify the user in subsequent API calls

This gives you more control and allows you to:

- Revoke sessions independently
- Refresh Auth0 tokens in the background
- Track user sessions across devices

## Auth0 Configuration

In your Auth0 dashboard:

1. **Application Type**: Set to "Native"
2. **Allowed Callback URLs**: Add your custom URL scheme
    - Example: `myapp://callback`
3. **Allowed Logout URLs**: Add your logout callback
4. **Token Endpoint Authentication Method**: Choose "None" for the mobile client
    - Create a separate Auth0 application for the backend if needed

## Alternative: Backend-Hosted Login Page

If handling custom URL schemes is complex, consider:

1. Backend serves a login page at `https://your-api.com/login`
2. Mobile app opens this page in a webview
3. Page handles the Auth0 flow entirely on backend
4. After login, page sends session token back to app via JavaScript bridge
5. Mobile app extracts token and closes webview

This approach is simpler but provides a less native experience.

## Security Considerations

1. **PKCE is mandatory** - Never skip it for mobile apps
2. **Validate state parameter** - Prevents CSRF attacks
3. **Use HTTPS everywhere** - For backend API calls
4. **Secure token storage** - Use platform-specific secure storage
5. **Short-lived sessions** - Implement token refresh
6. **Certificate pinning** - Consider for API calls (advanced)

## Summary

**Mobile App Responsibilities:**

- Generate PKCE parameters
- Open Auth0 login in browser
- Capture authorization code from callback
- Send code to backend
- Store session token securely

**Backend Responsibilities:**

- Store Auth0 credentials securely
- Exchange authorization code for tokens
- Validate tokens
- Manage user sessions
- Provide session tokens to mobile app
- Refresh tokens as needed

This architecture keeps secrets secure on the backend while providing a smooth
authentication experience for mobile users.
