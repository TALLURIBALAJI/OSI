import re
import ipaddress
from urllib.parse import urlparse

class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email or len(email) > 254:
            return False
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, email))
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        if not phone:
            return False
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Basic validation: should start with + or digit, be between 7-15 digits
        if not cleaned:
            return False
        
        if cleaned.startswith('+'):
            digits = cleaned[1:]
        else:
            digits = cleaned
        
        return digits.isdigit() and 7 <= len(digits) <= 15
    
    @staticmethod
    def validate_domain(domain):
        """Validate domain format"""
        if not domain or len(domain) > 253:
            return False
        
        # Remove protocol if present
        if domain.startswith(('http://', 'https://')):
            domain = urlparse(domain).netloc
        
        # Remove www if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Basic domain validation
        domain_regex = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_regex, domain))
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username:
            return False
        
        # Remove @ if present
        if username.startswith('@'):
            username = username[1:]
        
        # Username should be 1-50 characters, alphanumeric plus underscore and dash
        if len(username) > 50:
            return False
        
        username_regex = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(username_regex, username))
    
    @staticmethod
    def validate_name(name):
        """Validate full name format"""
        if not name or len(name) > 100:
            return False
        
        # Allow letters, spaces, apostrophes, and hyphens
        name_regex = r"^[a-zA-Z\s'-]+$"
        return bool(re.match(name_regex, name.strip()))
    
    @staticmethod
    def validate_ip(ip):
        """Validate IP address format (IPv4 or IPv6)"""
        if not ip:
            return False
        
        try:
            ipaddress.ip_address(ip.strip())
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_input(input_str):
        """Basic input sanitization"""
        if not input_str:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        sanitized = input_str
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_search_input(search_type, query):
        """Validate search input based on type"""
        if not search_type or not query:
            return False, "Search type and query are required"
        
        # Sanitize input
        query = InputValidator.sanitize_input(query)
        
        # Validate based on type
        validators = {
            'email': InputValidator.validate_email,
            'phone': InputValidator.validate_phone,
            'ip': InputValidator.validate_ip,
            'domain': InputValidator.validate_domain,
            'username': InputValidator.validate_username,
            'name': InputValidator.validate_name
        }
        
        validator = validators.get(search_type)
        if not validator:
            return False, f"Invalid search type: {search_type}"
        
        if not validator(query):
            return False, f"Invalid {search_type} format"
        
        return True, query