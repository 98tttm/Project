import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_assignment_html_email(receiver_email, project):
    """
    Send an HTML email via Gmail containing a Project Assignment Notification.
    Make sure to configure your Gmail account (with an App Password) before using.
    """
    sender_email = "procheckapp@gmail.com"       # Replace with your sending email
    sender_password = "kkshlaggmjdddcsk"           # Replace with your Gmail App Password
    sender_name = "ProCheck Notification"
    subject = f"[ProCheck] You have been assigned to project: {project.name}"
    logo_url = "https://img.upanh.tv/2025/03/14/Yellow-and-Green-Modern-Logo.png"

    msg = MIMEMultipart('related')
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = receiver_email
    msg["X-Priority"] = "3"
    msg["Precedence"] = "bulk"
    msg["Reply-To"] = sender_email
    msg["List-Unsubscribe"] = "<mailto:procheckapp@gmail.com>"

    text_content = f"""
Hello,

You have been assigned to the project "{project.name}".
Project ID: {project.project_id}
Manager: {project.manager}
Status: {project.status}
Start Date: {project.start_date}
End Date: {project.end_date}

If you have any questions, please contact us.

Best regards,
ProCheck Team
"""
    html_content = f"""\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Project Assignment Notification</title>
    <style>
      body {{
        margin: 0; 
        padding: 0;
        background-color: #f7f7f7;
        font-family: Arial, sans-serif;
      }}
      .container {{
        max-width: 600px;
        margin: 20px auto;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        overflow: hidden;
      }}
      .header {{
        text-align: center;
        padding: 20px;
      }}
      .content {{
        padding: 0 30px 20px 30px;
      }}
      .footer {{
        text-align: center;
        padding: 20px;
        background-color: #fafafa;
      }}
      .project-box {{
        background-color: #f1f1f1;
        border: 1px solid #dddddd;
        border-radius: 6px;
        padding: 20px;
        margin: 10px 0;
      }}
      .project-box h3 {{
        margin: 0;
        color: #333;
      }}
      .project-box p {{
        margin: 5px 0;
        color: #555;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <img src="{logo_url}" alt="ProCheck Logo" width="80" style="display:block; margin:0 auto;">
      </div>
      <div class="content">
        <h2 style="text-align:center; color:#333;">Project Assignment</h2>
        <p>Hello,</p>
        <p>You have been assigned to the following project:</p>
        <div class="project-box">
          <h3>{project.name}</h3>
          <p><strong>ID:</strong> {project.project_id}</p>
          <p><strong>Manager:</strong> {project.manager}</p>
          <p><strong>Status:</strong> {project.status}</p>
          <p><strong>Description:</strong> {project.description}</p>
          <p><strong>Start Date:</strong> {project.start_date}</p>
          <p><strong>End Date:</strong> {project.end_date}</p>
        </div>
        <p>If you have any questions or believe this is an error, please contact our support team.</p>
        <p>Best regards,<br>The ProCheck Team</p>
      </div>
      <div class="footer">
        <p style="font-size:12px; color:#888;">
          Need help? Contact us at 
          <a href="mailto:procheckapp@gmail.com" style="color:#007bff; text-decoration:none;">procheckapp@gmail.com</a><br/>
          ProCheck Inc. &bull; University of Economics and Law &bull; Vietnam National University
        </p>
      </div>
    </div>
  </body>
</html>
"""
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    msg_alternative.attach(MIMEText(text_content, 'plain'))
    msg_alternative.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        logger.info(f"Assignment email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending assignment email to {receiver_email}: {e}")
        return False