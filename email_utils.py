import os
from fastapi import UploadFile
from starlette.datastructures import Headers
from io import BytesIO
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Gmail SMTP Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_calendar_email(
    subject: str,
    recipients: List[EmailStr],
    body: str,
    ics_content: bytes,
    filename: str = "invite.ics",
    method: str = "REQUEST"
):
    """
    Sends an email with an iCalendar attachment to the specified recipients.
    """
    # Create a file-like object for the attachment, with content-type in headers
    # Including 'method' in the content-type is crucial for Outlook/Gmail UI
    ics_file = UploadFile(
        filename=filename, 
        file=BytesIO(ics_content),
        headers=Headers({"content-type": f"text/calendar; method={method}"})
    )
    
    # We need to ensure the cursor is at the beginning
    await ics_file.seek(0)

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.html,
        attachments=[ics_file]
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print(f"EMAIL SENT: {subject} to {recipients}")
    except Exception as e:
        print(f"EMAIL ERROR: {str(e)}")
