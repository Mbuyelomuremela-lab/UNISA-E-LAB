from flask import session, current_app
from datetime import datetime, timedelta
import secrets
import string


def session_timeout():
    now = datetime.utcnow()
    last_active = session.get('last_active')
    if last_active:
        last = datetime.fromisoformat(last_active)
        if now > last + timedelta(seconds=current_app.config.get('PERMANENT_SESSION_LIFETIME', 1800)):
            session.clear()
    session['last_active'] = now.isoformat()


def generate_secure_password(length=7):
    allowed_symbols = '.@#'
    alphabet = string.ascii_letters + string.digits + allowed_symbols
    if length not in (6, 7):
        length = 7
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if validate_password_strength(password):
            return password


def validate_password_strength(password):
    allowed_symbols = '.@#'
    allowed_chars = set(string.ascii_letters + string.digits + allowed_symbols)

    if len(password) < 6 or len(password) > 7:
        return False
    if not any(c.isalpha() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in allowed_symbols for c in password):
        return False
    if not all(c in allowed_chars for c in password):
        return False
    return True
