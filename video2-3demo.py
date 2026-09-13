import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
from datetime import datetime


def email_report(
    to_emails,
    report_path,
    chart_path,
    sender_email,
    sender_password,
    smtp_server='smtp.gmail.com',
    smtp_port=587
):
    """
    Send the automated report to a distribution list.
    
    CRITICAL: Never hardcode passwords in your script.
    Use environment variables or a separate config file.
    """


   # Step 1: Create the email message object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = 'Weekly Sales Report — ' + datetime.now().strftime("%B %d, %Y")



   # Step 2: Write the email body
    body = (
        "Hello Team,\n"
        "\n"
        "The automated weekly sales report is attached.\n"
        "\n"
        "Report Generated: " + datetime.now().strftime('%B %d, %Y at %H:%M') + "\n"
        "\n"
        "Key highlights and charts are included in the attachments.\n"
        "\n"
        "This report was generated and sent automatically by our reporting system.\n"
        "If you have questions, please reply to this email.\n"
        "\n"
        "Best regards,\n"
        "Automated Reporting System"
    )
    
    msg.attach(MIMEText(body, 'plain'))




   # Step 3: Attach the Excel report
    with open(report_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename="' + os.path.basename(report_path) + '"'
        )
        msg.attach(part)



   # Step 4: Attach the chart image
    with open(chart_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename="' + os.path.basename(chart_path) + '"'
        )
        msg.attach(part)



   # Step 5: Connect to Gmail and send
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print("Report emailed to", len(to_emails), "recipient(s)")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Check your email and password.")
        print("For Gmail: Make sure you are using an App Password,")
        print("not your regular Gmail password.")
        return False
        
    except Exception as e:
        print("Failed to send email:", e)
        return False




# Test the email function

# Load Environment Variables
def load_env():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# To set up gmail app password follow these steps
#1 go to https://myaccount.google.com/security
#2 enable 2-factor authentication
#3 search for App Passwords under google account settings
#4 click create password, name it Python Authomation
#5 it will display 16 digit password, copy the password and save it some where.
#6 come to vs code environment and create .env file and add the following lines
#7 sender_email = your gmail address
#8 sender_password = your 16 digit app password 
#9 Recipients = comma separated email addresses of recipients
#10 data_source = path to the data source file, for example C:/Users/zeena/Desktop/NECA ICT Academy Advanced AI 2026/practice_folder/weekly_sales_report_20250310.xlsx


# Define Email Credentials and Recipients

sender = os.environ.get('SENDER_EMAIL')
password = os.environ.get('SENDER_PASSWORD')
recipients = os.environ.get('RECIPIENTS', 'yusufzeenah12@gmail.com').split(',')


# Paths to your generated files
report_file = "weekly_sales_report_20260712.xlsx"
chart_file = "report_charts_20260712.png"

# Send it
result = email_report(recipients, report_file, chart_file, sender, password)

if result:
    print()
    print("Check your inbox. The report should arrive within a few seconds.")
else:
    print()
    print("Email failed. Check the error message above.")



# Scheduler Setup (Optional)
# You can use Windows Task Scheduler or cron jobs on Linux/Mac to run this script automatically

