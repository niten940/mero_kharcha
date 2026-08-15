"""
Email notification module — sends transactional emails via Mailtrap SMTP.

Triggered by:
  - Budget limit exceeded (every time an expense pushes total over the limit)
  - Sensitive profile update (email or password change)
  - Password reset link
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")


def _send_email(to_email: str, subject: str, body_html: str) -> None:
    """
    Send an HTML email via Mailtrap SMTP.

    Args:
        to_email (str): Recipient email address.
        subject (str): Email subject line.
        body_html (str): HTML content of the email body.

    Raises:
        RuntimeError: If the SMTP connection or send fails.
    """
    sender = f"Mero Kharcha <{MAIL_FROM}>"
    receiver = f"User <{to_email}>"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(sender, receiver, msg.as_string())
    except Exception as e:
        raise RuntimeError(f"Failed to send email to {to_email}: {e}")

def send_budget_exceeded_email(
    to_email: str,
    full_name: str,
    monthly_limit: float,
    current_total: float,
) -> None:
    """
    Notify the user that their monthly expense total has exceeded the budget limit.

    Args:
        to_email (str): Recipient email address.
        full_name (str): User's full name for personalization.
        monthly_limit (float): The user's set monthly budget limit.
        current_total (float): Current month's total expenses after the latest addition.

    Returns:
        None
    """
    exceeded_by = round(current_total - monthly_limit, 2)
    subject = "⚠️ Mero Kharcha — Monthly Budget Exceeded"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #e74c3c;">Budget Limit Exceeded</h2>
        <p>Hi <strong>{full_name}</strong>,</p>
        <p>Your monthly expense total has exceeded your set budget limit.</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 400px;">
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Monthly Limit</td>
            <td style="padding: 8px; border: 1px solid #ddd;">NPR {monthly_limit:,.2f}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Current Total</td>
            <td style="padding: 8px; border: 1px solid #ddd; color: #e74c3c;">
              NPR {current_total:,.2f}
            </td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Exceeded By</td>
            <td style="padding: 8px; border: 1px solid #ddd; color: #e74c3c;">
              NPR {exceeded_by:,.2f}
            </td>
          </tr>
        </table>
        <p style="margin-top: 16px;">
          Review your expenses in <strong>Mero Kharcha</strong> to stay on track.
        </p>
        <p style="color: #999; font-size: 12px;">
          This is an automated notification from Mero Kharcha.
        </p>
      </body>
    </html>
    """
    _send_email(to_email, subject, body_html)


def send_profile_update_email(
    to_email: str,
    full_name: str,
    changed_field: str,
) -> None:
    """
    Notify the user that a sensitive profile field has been changed.

    Args:
        to_email (str): Recipient email address.
        full_name (str): User's full name for personalization.
        changed_field (str): Human-readable name of the changed field
            (e.g. 'email address', 'password').

    Returns:
        None
    """
    subject = "🔔 Mero Kharcha — Profile Updated"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2980b9;">Profile Update Notice</h2>
        <p>Hi <strong>{full_name}</strong>,</p>
        <p>
          Your <strong>{changed_field}</strong> was recently updated on your
          Mero Kharcha account.
        </p>
        <p>
          If you made this change, no action is needed.
          If you did not make this change, please reset your password immediately
          or contact support.
        </p>
        <p style="color: #999; font-size: 12px;">
          This is an automated notification from Mero Kharcha.
        </p>
      </body>
    </html>
    """
    _send_email(to_email, subject, body_html)


def send_password_reset_email(
    to_email: str,
    full_name: str,
    reset_token: str,
) -> None:
    """
    Send a password reset link to the user.

    Args:
        to_email (str): Recipient email address.
        full_name (str): User's full name for personalization.
        reset_token (str): The purpose-scoped JWT reset token.

    Returns:
        None
    """
    reset_link = f"http://localhost:5173/Resetpass?token={reset_token}"
    subject = "🔑 Mero Kharcha — Password Reset Request"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #27ae60;">Password Reset Request</h2>
        <p>Hi <strong>{full_name}</strong>,</p>
        <p>
          We received a request to reset your Mero Kharcha password.
          Click the button below to set a new password.
        </p>
        <a href="{reset_link}"
           style="display: inline-block; margin: 16px 0; padding: 12px 24px;
                  background-color: #27ae60; color: white; text-decoration: none;
                  border-radius: 4px; font-weight: bold;">
          Reset Password
        </a>
        <p>This link expires in <strong>30 minutes</strong>.</p>
        <p>If you did not request a password reset, ignore this email.</p>
        <p style="color: #999; font-size: 12px;">
          This is an automated notification from Mero Kharcha.
        </p>
      </body>
    </html>
    """
    _send_email(to_email, subject, body_html)