import os
import requests
import re
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# --- Configuration ---
KC_URL = os.getenv("KC_URL", "https://keycloak.alex.mn")
REALM = os.getenv("KC_REALM", "datalake")
CLIENT_ID = os.getenv("KC_CLIENT_ID", "fds")
CLIENT_SECRET = os.getenv("KC_CLIENT_SECRET", "21fojC3lDpZkAM1KP5ebobA4JtVeCyzI")
USERNAME = os.getenv("KC_USERNAME", "amarmend")
PASSWORD = os.getenv("KC_PASSWORD", "Qks2025+k8s")
REDIRECT_URI = os.getenv("KC_REDIRECT_URI", "http://localhost:8080/callback")

app = FastAPI()


def get_auth_code():
    """Simulates the browser flow to get a one-time authorization_code."""
    session = requests.Session()
    session.verify = False

    auth_url = f"{KC_URL}/realms/{REALM}/protocol/openid-connect/auth"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid"
    }

    # 1. Hit the auth endpoint to get the login page
    resp = session.get(auth_url, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Check for error message
    error_elem = soup.find("div", class_="alert-error") or soup.find("span", class_="pf-v5-c-alert__title")
    if error_elem:
        raise Exception(f"Keycloak error: {error_elem.get_text(strip=True)}")

    form = soup.find("form", id="kc-form-login")
    if not form:
        raise Exception("Login form not found - check client configuration")
    action_url = form["action"]

    # 2. Submit credentials to get the redirect with the code
    login_data = {"username": USERNAME, "password": PASSWORD}
    login_resp = session.post(action_url, data=login_data, allow_redirects=False)

    # 3. Parse the code from the Location header
    location = login_resp.headers.get("Location")
    if not location:
        raise Exception("No redirect location - login may have failed")

    match = re.search(r"code=([^&]+)", location)
    if not match:
        raise Exception("No auth code in redirect URL")

    return session, match.group(1)


def exchange_token(session, auth_code):
    """Exchange auth code for token."""
    token_url = f"{KC_URL}/realms/{REALM}/protocol/openid-connect/token"

    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }

    response = session.post(token_url, data=payload)

    if response.status_code != 200:
        raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")

    return response.json()


@app.get("/auth_code_health")
def auth_code_health():
    """Health check endpoint that verifies auth code flow works."""
    try:
        session, auth_code = get_auth_code()
        exchange_token(session, auth_code)
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
