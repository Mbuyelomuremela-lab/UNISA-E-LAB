import os
import ssl
import smtplib
from email.message import EmailMessage


def _get_email_config():
    host = os.environ.get('EMAIL_HOST')
    port = int(os.environ.get('EMAIL_PORT', 587))
    username = os.environ.get('EMAIL_USERNAME')
    password = os.environ.get('EMAIL_PASSWORD')
    use_tls = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
    use_ssl = os.environ.get('EMAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')
    sender = os.environ.get('EMAIL_DEFAULT_SENDER') or username
    site_url = os.environ.get('SITE_URL', 'http://localhost:5000')

    if not host or not username or not password:
        raise ValueError('EMAIL_HOST, EMAIL_USERNAME, and EMAIL_PASSWORD must be configured.')

    return {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'use_tls': use_tls,
        'use_ssl': use_ssl,
        'sender': sender,
        'site_url': site_url,
    }


def _send_email(subject, recipient, body):
    config = _get_email_config()

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = config['sender']
    message['To'] = recipient
    message.set_content(body)

    context = ssl.create_default_context()
    if config['use_ssl']:
        with smtplib.SMTP_SSL(config['host'], config['port'], context=context) as server:
            server.login(config['username'], config['password'])
            server.send_message(message)
    else:
        with smtplib.SMTP(config['host'], config['port']) as server:
            if config['use_tls']:
                server.starttls(context=context)
            server.login(config['username'], config['password'])
            server.send_message(message)


def send_new_user_password(email, password):
    config = _get_email_config()
    subject = 'Welcome to Sunnyside Lab Portal'
    body = (
        f'Hello,\n\n'
        f'An account has been created for you in the Sunnyside Lab Portal.\n\n'
        f'Login details:\n'
        f'Email: {email}\n'
        f'Password: {password}\n\n'
        f'Please log in at {config["site_url"]}/login and change your password after your first login.\n\n'
        f'If you did not expect this email, please contact your administrator.\n\n'
        f'Thank you,\n'
        f'Sunnyside Lab Team'
    )
    _send_email(subject, email, body)


def send_password_reset_by_admin(email, password):
    config = _get_email_config()
    subject = 'Your Sunnyside Lab Portal password was reset'
    body = (
        f'Hello,\n\n'
        f'Your account password has been reset by an administrator.\n\n'
        f'New login details:\n'
        f'Email: {email}\n'
        f'Password: {password}\n\n'
        f'Please log in at {config["site_url"]}/login and change your password immediately after login.\n\n'
        f'If you did not request this change, contact your administrator right away.\n\n'
        f'Thank you,\n'
        f'Sunnyside Lab Team'
    )
    _send_email(subject, email, body)


def send_password_change_confirmation(email):
    config = _get_email_config()
    subject = 'Your Sunnyside Lab Portal password has been updated'
    body = (
        f'Hello,\n\n'
        f'Your password has been successfully changed. If you did not perform this action, please contact your administrator immediately.\n\n'
        f'You can log in at {config["site_url"]}/login.\n\n'
        f'Thank you,\n'
        f'Sunnyside Lab Team'
    )
    _send_email(subject, email, body)
