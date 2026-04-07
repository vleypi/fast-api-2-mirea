import re

SECRET_KEY = "super_secret_key"
SESSION_TTL = 300
SESSION_RENEW_AFTER = 180

FAKE_USERS = {
    "user123": {"password": "password123", "name": "User 123",      "email": "user123@example.com"},
    "admin":   {"password": "admin123",    "name": "Administrator",  "email": "admin@example.com"},
}

ACCEPT_LANGUAGE_RE = re.compile(
    r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(,[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(;q=[01](\.\d)?)?)*$"
)
