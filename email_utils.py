import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pydantic import EmailStr
from typing import List
from dotenv import load_dotenv

load_dotenv()

async def send_calendar_email(
    subject: str,
    recipients: List[EmailStr],
    body: str,
    ics_content: bytes,
    filename: str = "invite.ics",
    method: str = "REQUEST",
    doctor_name: str = "Doctor",
    appointment_id: str = "N/A",
    start_time_iso: str = None,
    end_time_iso: str = None
):
    """
    Sends a NATIVE Calendar Invitation email.
    Using multipart/alternative and specific headers for Outlook/Gmail auto-sync.
    """
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the root message
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = ", ".join(recipients)
    
    # CRITICAL: This header tells Outlook to treat it as a native appointment
    msg["Content-Class"] = "urn:content-classes:calendarmessage"

    # Create the alternative part for Body (HTML) and Calendar
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)

    # 1. HTML Body + Schema.org Metadata (The Apple/Siri Secret)
    schema_json = f"""
    <script type="application/ld+json">
    {{
      "@context": "http://schema.org",
      "@type": "Event",
      "name": "{subject}",
      "startDate": "{start_time_iso}",
      "endDate": "{end_time_iso}",
      "location": {{
        "@type": "Place",
        "name": "Hospital Clinic",
        "address": {{
          "@type": "PostalAddress",
          "addressLocality": "Hyderabad",
          "addressRegion": "TS",
          "addressCountry": "IN"
        }}
      }},
      "description": "{body}",
      "performer": {{
        "@type": "Person",
        "name": "{doctor_name}"
      }}
    }}
    </script>
    """
    
    full_html = f"""
    <html>
      <body>
        {body}
        {schema_json if start_time_iso else ""}
      </body>
    </html>
    """

    html_part = MIMEText(full_html, "html")
    msg_alt.attach(html_part)

    # 2. Native Calendar Part
    cal_part = MIMEText(ics_content.decode("utf-8"), "calendar")
    cal_part.set_param("method", method)
    cal_part.set_param("charset", "UTF-8")
    del cal_part["Content-Transfer-Encoding"]
    cal_part.add_header("Content-Transfer-Encoding", "8bit")
    msg_alt.attach(cal_part)

    # 3. Traditional Attachment (Backup for mobile/older clients)
    attachment = MIMEBase("text", "calendar", name=filename)
    attachment.set_payload(ics_content)
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    attachment.add_header("Content-ID", f"<{filename}>")
    attachment.set_param("method", method)
    msg.attach(attachment)

    # Send via SMTP
    try:
        # Note: Using synchronous smtplib here for simplicity in construction, 
        # but in a high-concurrency app, aiosmtplib is preferred.
        # Given the task complexity, this ensures the MIME structure is perfect.
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.sendmail(mail_from, recipients, msg.as_string())
        server.quit()
        print(f"EMAIL SENT (NATIVE INVITE): {subject} to {recipients}")
    except Exception as e:
        print(f"EMAIL ERROR: {str(e)}")
