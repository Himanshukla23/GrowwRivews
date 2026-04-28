"""
Phase 6: Gmail Delivery
Sends a concise notification email to stakeholders with a link to the Google Doc.
Uses the Gmail API via OAuth2.
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv
from src.google_auth_helper import get_google_credentials

load_dotenv()


def _build_email_html(product_name: str, doc_link: str, theme_count: int) -> str:
    """Builds a concise, professional HTML email body."""
    date_str = datetime.now().strftime("%B %d, %Y")

    return f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #00B386, #00D09C); padding: 24px; border-radius: 8px 8px 0 0;">
            <h2 style="color: white; margin: 0;">📊 Weekly Product Pulse</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 4px 0 0 0;">{product_name} — {date_str}</p>
        </div>
        <div style="background: #f9f9f9; padding: 24px; border: 1px solid #e0e0e0;">
            <p>Hi Team,</p>
            <p>The weekly review analysis for <strong>{product_name}</strong> is ready.
               We identified <strong>{theme_count} key themes</strong> from user feedback this week.</p>
            <p style="text-align: center; margin: 24px 0;">
                <a href="{doc_link}"
                   style="background: #00B386; color: white; padding: 12px 32px;
                          text-decoration: none; border-radius: 6px; font-weight: bold;">
                    View Full Report →
                </a>
            </p>
            <p style="color: #666; font-size: 13px;">
                This report was generated automatically by the Weekly Product Pulse System.
            </p>
        </div>
    </div>
    """


def send_summary_email(
    doc_link: str,
    product_name: str = "Groww",
    theme_count: int = 0,
    recipient: Optional[str] = None,
) -> bool:
    """
    Sends a notification email to the stakeholder with a link to the report.

    Args:
        doc_link: URL of the Google Doc containing the full report.
        product_name: Product name for the email subject.
        theme_count: Number of themes detected (for the email body).
        recipient: Email address. Defaults to RECIPIENT_EMAIL from .env.

    Returns:
        True if the email was sent successfully.

    Raises:
        ValueError: If no recipient is configured.
    """
    if recipient is None:
        recipient = os.getenv("RECIPIENT_EMAIL")

    if not recipient or recipient == "stakeholder@example.com":
        raise ValueError(
            "RECIPIENT_EMAIL is not configured. Set it in your .env file."
        )

    creds = get_google_credentials()
    service = build("gmail", "v1", credentials=creds)

    # Build the email
    date_str = datetime.now().strftime("%Y-%m-%d")
    subject = f"[Report] Weekly Product Pulse - {product_name} - {date_str}"

    message = MIMEMultipart("alternative")
    message["to"] = recipient
    message["subject"] = subject

    # Plain text fallback
    plain_body = (
        f"Weekly Product Pulse Report for {product_name} is ready.\n"
        f"Themes detected: {theme_count}\n"
        f"View the full report: {doc_link}\n"
    )

    # HTML body
    html_body = _build_email_html(product_name, doc_link, theme_count)

    message.attach(MIMEText(plain_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    # Save email artifacts
    import glob
    artifact_dirs = sorted(glob.glob("data/artifacts/*"))
    if artifact_dirs:
        latest_dir = artifact_dirs[-1]
        with open(f"{latest_dir}/email.html", "w", encoding="utf-8") as f:
            f.write(html_body)
        with open(f"{latest_dir}/email.txt", "w", encoding="utf-8") as f:
            f.write(plain_body)
        print(f"[Phase 6] Email artifacts saved to: {latest_dir}")

    # Encode and send
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    service.users().messages().send(
        userId="me",
        body={"raw": raw_message},
    ).execute()

    print(f"[Phase 6] Email sent to {recipient}: {subject}")
    return True
