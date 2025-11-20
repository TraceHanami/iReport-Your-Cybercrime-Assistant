import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

with app.app_context():
    try:
        msg = Message(
            subject='Test Email from iReport',
            sender=app.config['MAIL_USERNAME'],
            recipients=['clesturbruclee@gmail.com']  # Change to your actual email
        )
        msg.body = 'This is a test email from iReport backend.'
        
        mail.send(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {e}")
        import traceback
        traceback.print_exc()