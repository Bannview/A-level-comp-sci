import os
import random
import smtplib
from email.mime.text import MIMEText


def generate_otp(receiver_email):
    """Generate and email a six-digit one-time password."""
    sender = os.getenv("SMTP_SENDER")
    password = os.getenv("SMTP_APP_PASSWORD")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not sender or not password:
        raise RuntimeError(
            "Set SMTP_SENDER and SMTP_APP_PASSWORD before using email OTP."
        )

    final_otp = "".join(str(random.randint(0, 9)) for _ in range(6))
    message = MIMEText(final_otp)
    message["Subject"] = "OTP code for Stock Alert System"
    message["From"] = sender
    message["To"] = receiver_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(message)

    return final_otp


def validate_otp(user_otp, generated_otp, user_email=None):
    """Return True only when the submitted code matches."""
    return bool(user_otp) and user_otp == generated_otp
