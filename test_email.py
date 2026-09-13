import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


SENDER_EMAIL = "yusufzeenah12@gmail.com"           # Your Gmail address
SENDER_PASSWORD = "plfzsaoiomclsmwz"        # The App Password (no spaces)
RECIPIENT = "yusufzeenah12@gmail.com"               # Send to yourself for testing
# --------------------------------------------------------

# Create the email
msg = MIMEMultipart()
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT
msg['Subject'] = f'Test Email — {datetime.now().strftime("%B %d, %Y at %H:%M")}'

# Email body
body = """
Hello,

This is a test email from your Python automation script.

If you received this, your email setup is working correctly.

Best regards,
Automated Reporting System
"""
msg.attach(MIMEText(body, 'plain'))

# Send it
try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
    
    print("Email sent successfully!")
    print("Check your inbox (and spam folder just in case).")
    
except smtplib.SMTPAuthenticationError:
    print("AUTHENTICATION FAILED.")
    print("Make sure you are using the App Password, not your regular password.")
    print("The App Password is 16 characters, no spaces.")
    
except Exception as e:
    print(f"Failed to send: {e}")