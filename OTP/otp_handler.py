import random
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests


def generate_otp(length=6):
    """Generate an OTP consisting of digits."""
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def send_otp_html_email(receiver_email, otp_code):
    """
    Send an HTML email via Gmail containing an OTP code.
    Configuration:
      - Use a Gmail account with 2-Step Verification enabled and an App Password.
      - Ensure SPF, DKIM, and DMARC are configured for your sending domain if applicable.
    """
    sender_email = "procheckapp@gmail.com"  # Replace with your sending email
    sender_password = "kkshlaggmjdddcsk"  # Replace with your Gmail App Password (16 characters, no spaces)
    sender_name = "ProCheck Security"

    subject = "Your ProCheck Password Reset Code"

    # URL for the logo image
    logo_url = "https://img.upanh.tv/2025/03/14/Yellow-and-Green-Modern-Logo.png"

    # Create a MIME message with alternative parts
    msg = MIMEMultipart('related')

    # Set basic headers
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = receiver_email

    # Additional headers to help with deliverability
    msg["X-Priority"] = "3"
    msg["Precedence"] = "bulk"
    msg["Reply-To"] = sender_email
    msg["List-Unsubscribe"] = "<mailto:procheckapp@gmail.com>"

    # Create alternative part for text and HTML
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    # Plain-text alternative
    text_content = f"""
Your OTP is: {otp_code}

Dear user,
You recently requested a password reset for your ProCheck account.
If you didn't request a password reset, please ignore this email.

Contact us: procheckapp@gmail.com | Phone: 0123 456 789
"""

    # HTML content (logo is loaded via URL, not attached)
    html_content = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Your ProCheck Password Reset Code</title>
    <style>
      body {{
        margin: 0; padding: 0;
        background-color: #f7f7f7;
        font-family: Arial, sans-serif;
      }}
      .container {{
        max-width: 600px;
        background-color: #ffffff;
        border-radius: 8px;
        margin: 20px auto;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      }}
      .header, .footer {{
        text-align: center;
        padding: 20px;
      }}
      .content {{
        padding: 0 30px 20px 30px;
      }}
      .otp-box {{
        background-color: #f1f1f1;
        border: 1px solid #dddddd;
        border-radius: 6px;
        padding: 20px;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        letter-spacing: 4px;
        color: #333333;
      }}
      .footer p {{
        font-size: 12px;
        color: #888888;
        line-height: 16px;
        margin: 0;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <!-- Header with logo -->
      <div class="header">
        <img src="{logo_url}" alt="ProCheck Logo" width="80" style="display:block; margin:0 auto;">
      </div>
      <!-- Content -->
      <div class="content">
        <h2 style="text-align: center; color:#333;">Password Reset Verification</h2>
        <p>Hi there,</p>
        <p>You recently requested a password reset for your ProCheck account. Your verification code is:</p>
        <div class="otp-box">{otp_code}</div>
        <p>This code will expire in <strong>10 minutes</strong>.</p>
        <p>If you did not request a password reset, please ignore this email or contact our support team immediately.</p>
        <p>Best regards,<br>The ProCheck Security Team</p>
      </div>
      <!-- Footer with contact information -->
      <div class="footer">
        <p>Need help? Contact us at <a href="mailto:procheckapp@gmail.com" style="color:#007bff; text-decoration:none;">procheckapp@gmail.com</a></p>
        <p>ProCheck Inc. • University of Economics and Law • Vietnam National University</p>
      </div>
    </div>
  </body>
</html>
"""

    msg_alternative.attach(MIMEText(text_content, 'plain'))
    msg_alternative.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        logging.info(f"Email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        logging.error(f"Error sending OTP email: {e}")
        return False


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    receiver_email = "dtdh2425@gmail.com"  # Ensure the recipient email is correct
    otp = generate_otp()
    logging.info(f"Generated OTP: {otp}")
    if send_otp_html_email(receiver_email, otp):
        logging.info("OTP sent successfully.")
    else:
        logging.error("Failed to send OTP.")