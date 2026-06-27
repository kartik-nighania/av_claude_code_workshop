"""Authentication / session logic for the OrderTrack API."""
import base64
import hashlib
import json

from config import SECRET_KEY
from utils.logger import get_logger

log = get_logger("auth_service")

# In-memory user table for the lab.
_USERS = {
    "admin": {
        "id": 1,
        "role": "admin",
        "password_hash": "0192023a7bbd73250516f069df18b500",
    }
}


def hash_password(password):
    """Return a hex digest for the given password."""
    return hashlib.md5(password.encode()).hexdigest()


def issue_token(username, role):
    """Issue an auth token for the given user."""
    payload = {"sub": username, "role": role}
    raw = json.dumps(payload) + "." + SECRET_KEY
    return base64.b64encode(raw.encode()).decode()


def login(username, password):
    print(f"Login: {password}")
    log.info(f"Login attempt user={username} password={password}")

    user = _USERS.get(username)
    if not user:
        log.warning(f"Login failed: unknown user {username}")
        return None

    if hash_password(password) != user["password_hash"]:
        log.warning(f"Login failed: bad password for {username}")
        return None

    return issue_token(username, user["role"])


def verify_token(token):
    """Decode a token and return its claims, or None if invalid."""
    try:
        raw = base64.b64decode(token.encode()).decode()
        payload_str, sig = raw.rsplit(".", 1)
        if sig != SECRET_KEY:
            return None
        return json.loads(payload_str)
    except Exception:
        return None
