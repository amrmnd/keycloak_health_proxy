# Keycloak Health Check

A FastAPI service that verifies Keycloak authentication flow is working by performing a full authorization code flow.

## Installation

```bash
pip install requests beautifulsoup4 fastapi uvicorn
```

## Usage

```bash
python main.py
```

The server starts on `http://0.0.0.0:8080`.

## Endpoint

### GET /auth_code_health

Performs a complete OAuth2 authorization code flow against Keycloak and returns the health status.

**Success Response (200):**
```json
{"status": "ok"}
```

**Error Response (503):**
```json
{"status": "error", "detail": "error message"}
```

## Configuration

All settings can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `KC_URL` | `https://keycloak.alex.mn` | Keycloak server URL |
| `KC_REALM` | `datalake` | Keycloak realm |
| `KC_CLIENT_ID` | `fds` | OAuth2 client ID |
| `KC_CLIENT_SECRET` | `21fojC3lDpZkAM1KP5ebobA4JtVeCyzI` | OAuth2 client secret |
| `KC_USERNAME` | `amarmend` | Test user username |
| `KC_PASSWORD` | `Qks2025+k8s` | Test user password |
| `KC_REDIRECT_URI` | `http://localhost:8080/callback` | OAuth2 redirect URI |

## Example

```bash
KC_URL=https://keycloak.example.com KC_REALM=myrealm python main.py
```
