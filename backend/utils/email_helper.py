from flask_mail import Message
from flask import current_app
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.templates = {
            'case_update': {
                'en': {
                    'subject': 'Case Update - {case_id}',
                    'template': """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                            .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
                            .content { padding: 20px; background: #f8f9fa; }
                            .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
                            .case-id { background: #e74c3c; color: white; padding: 5px 10px; border-radius: 3px; }
                            .update-box { background: white; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1>iReport System</h1>
                            </div>
                            <div class="content">
                                <h2>Case Update</h2>
                                <p>Your case <span class="case-id">{case_id}</span> has been updated.</p>
                                <div class="update-box">
                                    <strong>Update Details:</strong>
                                    <p>{update_message}</p>
                                </div>
                                <p>You can view the complete details by logging into your iReport account.</p>
                            </div>
                            <div class="footer">
                                <p>This is an automated message from iReport System.</p>
                                <p>Please do not reply to this email.</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                },
                'hi': {
                    'subject': 'मामला अद्यतन - {case_id}',
                    'template': """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                            .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
                            .content { padding: 20px; background: #f8f9fa; }
                            .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1>iReport प्रणाली</h1>
                            </div>
                            <div class="content">
                                <h2>मामला अद्यतन</h2>
                                <p>आपका मामला <strong>{case_id}</strong> अपडेट किया गया है।</p>
                                <div style="background: white; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0;">
                                    <strong>अद्यतन विवरण:</strong>
                                    <p>{update_message}</p>
                                </div>
                                <p>आप iReport खाते में लॉग इन करके पूर्ण विवरण देख सकते हैं।</p>
                            </div>
                            <div class="footer">
                                <p>यह iReport प्रणाली से एक स्वचालित संदेश है।</p>
                                <p>कृपया इस ईमेल का उत्तर न दें।</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                }
            },
            'welcome': {
                'en': {
                    'subject': 'Welcome to iReport System',
                    'template': """
                    <!DOCTYPE html>
                    <html>
                    <body>
                        <h2>Welcome to iReport!</h2>
                        <p>Dear {user_name},</p>
                        <p>Your account has been successfully created.</p>
                        <p>You can now file complaints, track cases, and get updates.</p>
                        <p>Thank you for joining iReport!</p>
                    </body>
                    </html>
                    """
                }
            },
            'otp': {
                'en': {
                    'subject': 'Your iReport Verification Code',
                    'template': """
                    <!DOCTYPE html>
                    <html>
                    <body>
                        <h2>Verification Code</h2>
                        <p>Your OTP for iReport verification is:</p>
                        <h1 style="color: #e74c3c; font-size: 32px;">{otp}</h1>
                        <p>This code is valid for 10 minutes.</p>
                        <p><strong>Do not share this code with anyone.</strong></p>
                    </body>
                    </html>
                    """
                }
            }
        }
    
    def send_email(self, to: str, subject: str, body: str, html: Optional[str] = None) -> bool:
        """Send email with optional HTML content"""
        try:
            # Check if mail is configured
            if not hasattr(current_app, 'extensions') or 'mail' not in current_app.extensions:
                logger.warning("Mail extension not configured")
                return False
            
            msg = Message(
                subject=subject,
                recipients=[to],
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', current_app.config.get('MAIL_USERNAME', 'noreply@ireport.com'))
            )
            
            if html:
                msg.html = html
            else:
                msg.body = body
            
            current_app.extensions['mail'].send(msg)
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to}: {e}")
            return False
    
    def send_template_email(self, to: str, template_name: str, language: str = 'en', **kwargs) -> bool:
        """Send email using a template"""
        try:
            if template_name not in self.templates:
                logger.error(f"Email template '{template_name}' not found")
                return False
            
            template_data = self.templates[template_name].get(language, self.templates[template_name]['en'])
            subject = template_data['subject'].format(**kwargs)
            html_content = template_data['template'].format(**kwargs)
            
            return self.send_email(to, subject, "", html_content)
            
        except Exception as e:
            logger.error(f"Error sending template email to {to}: {e}")
            return False
    
    def send_case_update_email(self, user_email: str, case_id: str, update_message: str, language: str = 'en') -> bool:
        """Send case update email"""
        return self.send_template_email(
            user_email,
            'case_update',
            language,
            case_id=case_id,
            update_message=update_message
        )
    
    def send_otp_email(self, user_email: str, otp: str, language: str = 'en') -> bool:
        """Send OTP email"""
        return self.send_template_email(
            user_email,
            'otp',
            language,
            otp=otp
        )
    
    def send_welcome_email(self, user_email: str, user_name: str, language: str = 'en') -> bool:
        """Send welcome email"""
        return self.send_template_email(
            user_email,
            'welcome',
            language,
            user_name=user_name
        )
    
    def send_bulk_emails(self, emails: List[str], subject: str, body: str, html: Optional[str] = None) -> Dict[str, Any]:
        """Send bulk emails with progress tracking"""
        results = {
            'total': len(emails),
            'successful': 0,
            'failed': 0,
            'failed_emails': []
        }
        
        for email in emails:
            if self.send_email(email, subject, body, html):
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['failed_emails'].append(email)
        
        logger.info(f"Bulk email sent: {results['successful']}/{results['total']} successful")
        return results

# Global email service instance
email_service = EmailService()

# Legacy functions for backward compatibility
def send_email(to, subject, body):
    return email_service.send_email(to, subject, body)

def send_case_update_email(user_email, case_id, update_message, language='en'):
    return email_service.send_case_update_email(user_email, case_id, update_message, language)

def send_otp_email(user_email, otp, language='en'):
    """Send OTP email - used by auth routes"""
    return email_service.send_otp_email(user_email, otp, language)