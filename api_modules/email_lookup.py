import requests
import logging
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)

class EmailLookup:
    """Email address lookup and validation functionality"""
    
    def __init__(self):
        self.name = "Email Lookup"
        self.hibp_api_url = "https://haveibeenpwned.com/api/v3"
        self.hibp_api_key = None  # Add your HIBP API key here
        
    def search(self, email):
        """Perform email address lookup"""
        results = []
        
        # Basic email validation
        try:
            validation_result = self._validate_email(email)
            results.append(validation_result)
        except Exception as e:
            logger.error(f"Email validation error: {str(e)}")
        
        # Have I Been Pwned lookup (if API key available)
        if self.hibp_api_key:
            try:
                hibp_result = self._hibp_lookup(email)
                if hibp_result:
                    results.append(hibp_result)
            except Exception as e:
                logger.error(f"HIBP lookup error: {str(e)}")
        else:
            # Add a note about HIBP API requirement
            results.append({
                'platform': 'Have I Been Pwned',
                'status': 'api_key_required',
                'details': {
                    'Note': 'HIBP API key required for breach checking',
                    'Info': 'Sign up at https://haveibeenpwned.com/API/Key'
                }
            })
        
        # Domain analysis
        try:
            domain_result = self._analyze_domain(email)
            if domain_result:
                results.append(domain_result)
        except Exception as e:
            logger.error(f"Domain analysis error: {str(e)}")
        
        return results
    
    def _validate_email(self, email):
        """Basic email validation"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        is_valid = bool(re.match(email_regex, email))
        
        # Extract domain
        domain = email.split('@')[1] if '@' in email else ''
        
        # Common email providers
        common_providers = {
            'gmail.com': 'Google Gmail',
            'yahoo.com': 'Yahoo Mail',
            'outlook.com': 'Microsoft Outlook',
            'hotmail.com': 'Microsoft Hotmail',
            'icloud.com': 'Apple iCloud',
            'protonmail.com': 'ProtonMail',
            'aol.com': 'AOL Mail'
        }
        
        provider = common_providers.get(domain.lower(), 'Unknown/Corporate')
        
        validation_info = {
            'Email Address': email,
            'Format Valid': 'Yes' if is_valid else 'No',
            'Domain': domain,
            'Provider': provider,
            'Type': 'Personal' if domain.lower() in common_providers else 'Corporate/Other'
        }
        
        return {
            'platform': 'Email Validation',
            'status': 'found' if is_valid else 'invalid',
            'details': validation_info
        }
    
    def _hibp_lookup(self, email):
        """Check Have I Been Pwned for data breaches"""
        if not self.hibp_api_key:
            return None
        
        try:
            headers = {
                'hibp-api-key': self.hibp_api_key,
                'User-Agent': 'OSINT-Framework-Portal'
            }
            
            # Check for breaches
            breach_url = f"{self.hibp_api_url}/breachedaccount/{quote(email)}"
            response = requests.get(breach_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                breaches = response.json()
                
                breach_info = {
                    'Email Address': email,
                    'Breaches Found': str(len(breaches)),
                    'Status': 'Compromised' if breaches else 'Clean'
                }
                
                if breaches:
                    # Get latest breach
                    latest_breach = max(breaches, key=lambda x: x.get('BreachDate', ''))
                    breach_info['Latest Breach'] = latest_breach.get('Name', 'Unknown')
                    breach_info['Breach Date'] = latest_breach.get('BreachDate', 'Unknown')
                    breach_info['Compromised Data'] = ', '.join(latest_breach.get('DataClasses', []))
                    
                    # List all breaches
                    all_breaches = [breach.get('Name', 'Unknown') for breach in breaches]
                    breach_info['All Breaches'] = ', '.join(all_breaches[:5])  # Limit to first 5
                
                return {
                    'platform': 'Have I Been Pwned',
                    'status': 'compromised' if breaches else 'clean',
                    'details': breach_info
                }
            
            elif response.status_code == 404:
                return {
                    'platform': 'Have I Been Pwned',
                    'status': 'clean',
                    'details': {
                        'Email Address': email,
                        'Status': 'No breaches found',
                        'Breaches Found': '0'
                    }
                }
            
        except Exception as e:
            logger.error(f"HIBP request error: {str(e)}")
            return None
        
        return None
    
    def _analyze_domain(self, email):
        """Analyze the email domain"""
        try:
            domain = email.split('@')[1] if '@' in email else ''
            
            if not domain:
                return None
            
            # Try to get MX records to verify domain
            try:
                import dns.resolver
                mx_records = dns.resolver.resolve(domain, 'MX')
                mx_exists = len(mx_records) > 0
            except:
                mx_exists = False
            
            domain_info = {
                'Domain': domain,
                'MX Records': 'Found' if mx_exists else 'Not Found',
                'Mail Server Status': 'Active' if mx_exists else 'Inactive/Unknown'
            }
            
            return {
                'platform': 'Domain Analysis',
                'status': 'found',
                'details': domain_info
            }
            
        except Exception as e:
            logger.error(f"Domain analysis error: {str(e)}")
            return None