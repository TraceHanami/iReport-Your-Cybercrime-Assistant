import re
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class ValidationService:
    def __init__(self):
        self.country_code = 'IN'  # Default country code for India
    
    def validate_phone_number(self, phone: str, country: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate phone number using phonenumbers library"""
        if not phone:
            return True, None, None  # Optional field
        
        try:
            # Remove all non-digit characters
            cleaned_phone = re.sub(r'[+\-\s()]', '', phone)
            
            # Indian mobile number validation
            if len(cleaned_phone) == 10 and cleaned_phone[0] in '6789':
                formatted_number = f"+91{cleaned_phone}"
                national_number = f"{cleaned_phone[:5]} {cleaned_phone[5:]}"
                return True, formatted_number, national_number
            
            # International format with country code
            elif len(cleaned_phone) > 10:
                if cleaned_phone.startswith('91') and len(cleaned_phone) == 12:
                    formatted_number = f"+{cleaned_phone}"
                    national_number = f"{cleaned_phone[2:7]} {cleaned_phone[7:]}"
                    return True, formatted_number, national_number
                elif cleaned_phone.startswith('1') and len(cleaned_phone) == 11:
                    # US numbers
                    formatted_number = f"+{cleaned_phone}"
                    national_number = f"({cleaned_phone[1:4]}) {cleaned_phone[4:7]}-{cleaned_phone[7:]}"
                    return True, formatted_number, national_number
            
            return False, None, None
            
        except Exception as e:
            logger.warning(f"Phone number validation failed: {e}")
            return False, None, None
    
    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """Validate email without external dependencies"""
        if not email:
            return True, None
        
        try:
            # Comprehensive email regex pattern
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if re.match(pattern, email):
                # Basic normalization - lowercase the domain part
                local_part, domain = email.split('@')
                normalized_email = f"{local_part}@{domain.lower()}"
                return True, normalized_email
            else:
                return False, None
                
        except Exception as e:
            logger.warning(f"Email validation failed: {e}")
            return False, None
    
    def validate_aadhaar_number(self, aadhaar: str) -> Tuple[bool, Optional[str]]:
        """Validate Aadhaar number format"""
        if not aadhaar:
            return True, None
        
        try:
            cleaned_aadhaar = re.sub(r'[\s-]', '', aadhaar)
            
            # Check length and digits
            if not re.match(r'^\d{12}$', cleaned_aadhaar):
                return False, None
            
            # Simple validation (actual Aadhaar has more complex checksum)
            # For demo purposes, we'll use a basic check
            if cleaned_aadhaar[0] in '012345':
                return False, None  # Aadhaar shouldn't start with 0-5
            
            return True, cleaned_aadhaar
            
        except Exception as e:
            logger.error(f"Aadhaar validation error: {e}")
            return False, None
    
    def _verhoeff_checksum(self, number: str) -> bool:
        """Verhoeff algorithm for Aadhaar checksum validation"""
        # This is a simplified version - actual Aadhaar uses more complex validation
        # For production, use official Aadhaar validation APIs
        multiplication_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        ]
        
        permutation_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
        ]
        
        inverse_table = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
        
        c = 0
        for i, digit in enumerate(reversed(number)):
            digit = int(digit)
            c = multiplication_table[c][permutation_table[(i + 1) % 8][digit]]
        
        return c == 0
    
    def validate_pan_number(self, pan: str) -> Tuple[bool, Optional[str]]:
        """Validate PAN number format"""
        if not pan:
            return True, None  # Optional field
        
        try:
            cleaned_pan = pan.upper().strip()
            pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            
            if not re.match(pattern, cleaned_pan):
                return False, None
            
            return True, cleaned_pan
            
        except Exception as e:
            logger.error(f"PAN validation error: {e}")
            return False, None
    
    def validate_imei_number(self, imei: str) -> Tuple[bool, Optional[str]]:
        """Validate IMEI number with Luhn algorithm"""
        if not imei:
            return True, None  # Optional field
        
        try:
            cleaned_imei = re.sub(r'\D', '', imei)
            
            if len(cleaned_imei) != 15:
                return False, None
            
            # Luhn algorithm validation
            if not self._luhn_checksum(cleaned_imei):
                return False, None
            
            return True, cleaned_imei
            
        except Exception as e:
            logger.error(f"IMEI validation error: {e}")
            return False, None
    
    def _luhn_checksum(self, number: str) -> bool:
        """Luhn algorithm for checksum validation"""
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        
        return checksum % 10 == 0
    
    def validate_sim_number(self, sim: str) -> Tuple[bool, Optional[str]]:
        """Validate SIM number format (ICCID)"""
        if not sim:
            return True, None  # Optional field
        
        try:
            cleaned_sim = re.sub(r'\s', '', sim)
            
            # ICCID is typically 19-20 digits
            if not re.match(r'^\d{19,20}$', cleaned_sim):
                return False, None
            
            return True, cleaned_sim
            
        except Exception as e:
            logger.error(f"SIM validation error: {e}")
            return False, None
    
    def validate_money_amount(self, amount: str) -> Tuple[bool, Optional[float]]:
        """Validate and parse money amount"""
        if not amount:
            return True, None
        
        try:
            # Remove currency symbols, commas, and spaces
            cleaned_amount = re.sub(r'[₹$, ]', '', str(amount))
            
            # Handle Indian numbering system (lakhs, crores)
            if 'lakh' in amount.lower() or 'lac' in amount.lower():
                cleaned_amount = re.sub(r'[^\d.]', '', cleaned_amount)
                parsed_amount = float(cleaned_amount) * 100000
            elif 'crore' in amount.lower():
                cleaned_amount = re.sub(r'[^\d.]', '', cleaned_amount)
                parsed_amount = float(cleaned_amount) * 10000000
            else:
                parsed_amount = float(cleaned_amount)
            
            if parsed_amount >= 0:
                return True, round(parsed_amount, 2)
            else:
                return False, None
                
        except (ValueError, TypeError):
            return False, None
    
    def validate_incident_datetime(self, date_str: str, time_str: str = None) -> Tuple[bool, Optional[datetime]]:
        """Validate incident date and time"""
        try:
            # Validate date
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                return False, None
            
            incident_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Ensure date is not in the future
            if incident_date > date.today():
                return False, None
            
            # Validate time if provided
            if time_str:
                if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
                    return False, None
                
                incident_time = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
                return True, incident_time
            else:
                return True, datetime.combine(incident_date, datetime.min.time())
                
        except ValueError:
            return False, None
    
    def validate_age(self, age: int, min_age: int = 0, max_age: int = 150) -> bool:
        """Validate age range"""
        try:
            age_int = int(age)
            return min_age <= age_int <= max_age
        except (ValueError, TypeError):
            return False
    
    def validate_pincode(self, pincode: str, country: str = 'IN') -> bool:
        """Validate postal code format"""
        if not pincode:
            return True  # Optional field
        
        if country == 'IN':
            # Indian pincode validation (6 digits)
            return bool(re.match(r'^[1-9][0-9]{5}$', pincode))
        else:
            # Generic validation for other countries
            return bool(re.match(r'^[A-Z0-9\- ]{3,10}$', pincode))
    
    def sanitize_text_input(self, text: str, max_length: int = 1000, 
                           allowed_tags: list = None) -> str:
        """Sanitize and truncate text input with HTML tag filtering"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters and scripts
        sanitized = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'<.*javascript:.*?>', '', sanitized, flags=re.IGNORECASE)
        
        # Basic HTML tag filtering
        if allowed_tags:
            # Allow specific tags (implement safe HTML filtering)
            pass
        else:
            # Remove all HTML tags
            sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rsplit(' ', 1)[0] + '...'
        
        return sanitized
    
    def validate_complaint_data(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Dict[str, str]]:
        """Validate complete complaint data"""
        errors = {}
        validated_data = {}
        
        # Required fields validation
        required_fields = ['title', 'description', 'incident_date', 'state', 'district', 
                          'victim_name', 'victim_age', 'victim_gender']
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f"{field.replace('_', ' ').title()} is required"
        
        # Title validation
        if 'title' in data and data['title']:
            title = self.sanitize_text_input(data['title'], 255)
            if len(title) < 5:
                errors['title'] = "Title must be at least 5 characters long"
            else:
                validated_data['title'] = title
        
        # Description validation
        if 'description' in data and data['description']:
            description = self.sanitize_text_input(data['description'], 2000)
            if len(description) < 10:
                errors['description'] = "Description must be at least 10 characters long"
            else:
                validated_data['description'] = description
        
        # Date validation
        if 'incident_date' in data and data['incident_date']:
            time_str = data.get('incident_time')
            valid, datetime_obj = self.validate_incident_datetime(data['incident_date'], time_str)
            if not valid:
                errors['incident_date'] = "Invalid incident date or time"
            else:
                validated_data['incident_date'] = datetime_obj
        
        # Age validation
        if 'victim_age' in data and data['victim_age']:
            if not self.validate_age(data['victim_age'], 0, 150):
                errors['victim_age'] = "Invalid age"
            else:
                validated_data['victim_age'] = int(data['victim_age'])
        
        # Phone validation
        if 'victim_contact' in data and data['victim_contact']:
            valid, formatted, national = self.validate_phone_number(data['victim_contact'])
            if not valid:
                errors['victim_contact'] = "Invalid phone number"
            else:
                validated_data['victim_contact'] = formatted
        
        # Email validation
        if 'anonymous_email' in data and data['anonymous_email']:
            valid, normalized = self.validate_email(data['anonymous_email'])
            if not valid:
                errors['anonymous_email'] = "Invalid email address"
            else:
                validated_data['anonymous_email'] = normalized
        
        # Money amount validation
        if 'estimated_loss' in data and data['estimated_loss']:
            valid, amount = self.validate_money_amount(data['estimated_loss'])
            if not valid:
                errors['estimated_loss'] = "Invalid amount"
            else:
                validated_data['estimated_loss'] = amount
        
        return len(errors) == 0, validated_data, errors

# Global validation service instance
validation_service = ValidationService()

# Legacy functions for backward compatibility
def validate_phone_number(phone: str) -> Tuple[bool, str]:
    valid, formatted, national = validation_service.validate_phone_number(phone)
    return valid, national or ""

def validate_email(email: str) -> bool:
    valid, normalized = validation_service.validate_email(email)
    return valid

def validate_aadhaar_number(aadhaar: str) -> bool:
    valid, cleaned = validation_service.validate_aadhaar_number(aadhaar)
    return valid

def validate_pan_number(pan: str) -> bool:
    valid, cleaned = validation_service.validate_pan_number(pan)
    return valid

def validate_imei_number(imei: str) -> bool:
    valid, cleaned = validation_service.validate_imei_number(imei)
    return valid

def validate_sim_number(sim: str) -> bool:
    valid, cleaned = validation_service.validate_sim_number(sim)
    return valid

def validate_money_amount(amount: str) -> Tuple[bool, Optional[float]]:
    return validation_service.validate_money_amount(amount)

def validate_incident_date(date_str: str) -> bool:
    valid, datetime_obj = validation_service.validate_incident_datetime(date_str)
    return valid

def validate_incident_time(time_str: str) -> bool:
    return bool(re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str))

def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    return validation_service.sanitize_text_input(text, max_length)