import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_confirmation_email(to_email, booking_details):
    """
    Send booking confirmation email using SMTP.
    Expects env vars: EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
    """
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not sender_email or not sender_password:
        return {"success": False, "error": "Email credentials not configured"}

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "Lumière Dining - Reservation Confirmed"

    first_name = booking_details.get('name', 'Guest').split()[0]
    
    body = f"""
    Dear {first_name},

    Thank you for choosing Lumière Dining. We are pleased to confirm your reservation.

    📄 Reservation Details:
    ------------------------
    📅 Date: {booking_details.get('date')}
    ⏰ Time: {booking_details.get('time')}
    👥 Party Size: {booking_details.get('party_size')}
    📝 Requests: {booking_details.get('special_requests') or 'None'}

    Address: 123 Gourmet Blvd, Flavor Town.
    
    If you need to modify your booking, please reply to this email.

    Warm Regards,
    The Lumière Dining Team
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
