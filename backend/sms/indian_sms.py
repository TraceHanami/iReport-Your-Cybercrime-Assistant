import requests
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IndianSMSService:
    def __init__(self):
        self.fast2sms_api_key = os.getenv('FAST2SMS_API_KEY', '')
        self.sender_id = "FSTSMS"  # Default Fast2SMS sender ID
        
        logger.info(f"Indian SMS Service initialized - Fast2SMS: {'✅' if self.fast2sms_api_key else '❌'}")
    
    def send_otp(self, phone_number, message):
        """
        Send OTP to Indian mobile numbers using Fast2SMS
        Falls back to console output if not configured
        """
        formatted_number = self._format_phone_number(phone_number)
        
        # Try Fast2SMS first, then fallback to console
        success, result = self._try_fast2sms(formatted_number, message)
        if success:
            return success, result
        
        # Fallback to console
        return self._fallback_console(formatted_number, message)
    
    def send_sms(self, phone_number, message):
        """
        Generic SMS sending method
        """
        return self.send_otp(phone_number, message)
    
    @property
    def is_configured(self):
        """Check if Fast2SMS is configured"""
        return bool(self.fast2sms_api_key and self.fast2sms_api_key not in ['', 'your_fast2sms_api_key_here'])
    
    def _format_phone_number(self, phone_number):
        """Format phone number for Fast2SMS"""
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, str(phone_number)))
        
        # Fast2SMS needs 10-digit Indian numbers (without country code)
        if cleaned.startswith('91') and len(cleaned) == 12:
            return cleaned[2:]  # Remove 91 prefix
        elif len(cleaned) == 10:
            return cleaned  # Already 10 digits
        elif len(cleaned) > 10:
            return cleaned[-10:]  # Take last 10 digits
        else:
            return cleaned
    
    def _try_fast2sms(self, mobile, message):
        """Send SMS using Fast2SMS API"""
        if not self.is_configured:
            return False, "Fast2SMS not configured"
        
        try:
            url = "https://www.fast2sms.com/dev/bulkV2"
            
            # Fast2SMS API payload
            payload = {
                "sender_id": self.sender_id,
                "message": message,
                "route": "v3",
                "numbers": mobile  # Should be 10-digit number without country code
            }
            
            headers = {
                'authorization': self.fast2sms_api_key,
                'Content-Type': "application/json"
            }
            
            logger.info(f"Sending SMS via Fast2SMS to {mobile}")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            result = response.json()
            
            logger.info(f"Fast2SMS Response: {result}")
            
            if result.get('return', False):
                logger.info(f"✅ Fast2SMS SMS sent to {mobile}")
                return True, "OTP sent via Fast2SMS"
            else:
                error = result.get('message', 'Unknown error')
                logger.error(f"❌ Fast2SMS failed: {error}")
                
                # Handle payment requirement specifically
                if "complete one transaction" in error.lower() or "100 INR" in error:
                    return False, "Fast2SMS requires initial payment of 100 INR to activate API. Using console mode."
                else:
                    return False, f"Fast2SMS: {error}"
                
        except Exception as e:
            logger.error(f"Fast2SMS error: {e}")
            return False, f"Fast2SMS error: {str(e)}"
    
    def _fallback_console(self, mobile, message):
        """Fallback: Display OTP in console for development"""
        logger.info(f"📱 SMS for {mobile}: {message}")
        print(f"\n{'='*60}")
        print(f"📱 INDIAN SMS - DEVELOPMENT MODE")
        print(f"{'='*60}")
        print(f"📞 Phone: +91{mobile}")
        print(f"💬 Message: {message}") 
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💡 Status: Fast2SMS not configured - Message shown in console")
        print(f"{'='*60}\n")
        return True, "Message displayed in console (development mode)"

# Global instance
indian_sms_service = IndianSMSService()