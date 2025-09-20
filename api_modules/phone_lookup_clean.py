import phonenumbers
from phonenumbers import geocoder, carrier
import requests
import logging

logger = logging.getLogger(__name__)

class PhoneLookup:
    def __init__(self):
        """Initialize phone lookup with real data extraction only"""
        self.numverify_api_key = None  # Add your NumVerify API key here if available
        self.numverify_url = "http://apilayer.net/api/validate"
    
    def lookup(self, phone_number):
        """
        Main lookup function - returns only real, verifiable data
        """
        results = []
        
        # Primary lookup using phonenumbers library (real data only)
        basic_result = self._parse_phone_basic(phone_number)
        if basic_result:
            results.append(basic_result)
        
        # Optional: NumVerify API lookup (if API key is configured)
        if self.numverify_api_key:
            numverify_result = self._numverify_lookup(phone_number)
            if numverify_result:
                results.append(numverify_result)
        
        return results if results else [{'platform': 'Phone Number Parser', 'status': 'not_found', 'details': {}}]
    
    def _parse_phone_basic(self, phone_number):
        """Basic phone number parsing using phonenumbers library - REAL DATA ONLY"""
        try:
            # Parse the phone number
            parsed_number = phonenumbers.parse(phone_number, None)
            
            if phonenumbers.is_valid_number(parsed_number):
                # Get real carrier information from phonenumbers library
                carrier_name = carrier.name_for_number(parsed_number, "en")
                
                # Format number for TrueCaller
                formatted_for_truecaller = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                truecaller_number = formatted_for_truecaller.replace('+', '')
                truecaller_with_plus = formatted_for_truecaller
                
                phone_info = {
                    'Phone Number': phone_number,
                    'Formatted': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                    'Country Code': f"+{parsed_number.country_code}",
                    'National Number': str(parsed_number.national_number),
                    'Country': self._get_country_name(parsed_number),
                    'State/Region': self._get_real_location(parsed_number),
                    'Carrier': carrier_name if carrier_name else 'Unknown',
                    'Type': self._get_number_type(parsed_number),
                    'Valid': 'Yes',
                    'Possible': 'Yes' if phonenumbers.is_possible_number(parsed_number) else 'No',
                    'Reverse Lookup': f'https://www.google.com/search?q="{phone_number}"',
                    'Whitepages Search': f'https://www.whitepages.com/phone/{phone_number.replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")}',
                    'TrueCaller Profile': f'https://www.truecaller.com/search/in/{truecaller_number}',
                    'GetContact Profile': f'https://www.getcontact.com/en/number/{truecaller_with_plus}',
                    'Mobile Tracker': f'https://www.mobilenumbertracker.com/search.php?mobileno={truecaller_number}',
                    'Reverse Phone Lookup': f'https://www.reversephonelookup.com/number/{phone_number.replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")}',
                    'Phone Validator': f'https://www.phonevalidator.com/index.aspx?number={formatted_for_truecaller}'
                }
                
                return {
                    'platform': 'Phone Number Parser',
                    'status': 'found',
                    'details': phone_info
                }
            else:
                return {
                    'platform': 'Phone Number Parser',
                    'status': 'invalid',
                    'details': {'Error': 'Invalid phone number format'}
                }
                
        except phonenumbers.NumberParseException as e:
            return {
                'platform': 'Phone Number Parser',
                'status': 'error',
                'details': {'Error': f'Parse error: {str(e)}'}
            }
    
    def _get_number_type(self, parsed_number):
        """Get the type of phone number - real data only"""
        number_type = phonenumbers.number_type(parsed_number)
        
        type_map = {
            phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
            phonenumbers.PhoneNumberType.FIXED_LINE: 'Fixed Line',
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed Line or Mobile',
            phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
            phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
            phonenumbers.PhoneNumberType.SHARED_COST: 'Shared Cost',
            phonenumbers.PhoneNumberType.VOIP: 'VoIP',
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
            phonenumbers.PhoneNumberType.PAGER: 'Pager',
            phonenumbers.PhoneNumberType.UAN: 'UAN',
            phonenumbers.PhoneNumberType.VOICEMAIL: 'Voicemail'
        }
        
        return type_map.get(number_type, 'Unknown')
    
    def _get_country_name(self, parsed_number):
        """Get country name from phone number - real data only"""
        try:
            country = geocoder.country_name_for_number(parsed_number, "en")
            return country if country else 'Unknown'
        except:
            return 'Unknown'
    
    def _get_real_location(self, parsed_number):
        """Get real location from phonenumbers geocoder only"""
        try:
            location = geocoder.description_for_number(parsed_number, "en")
            return location if location else 'Unknown'
        except:
            return 'Unknown'
    
    def _numverify_lookup(self, phone_number):
        """Lookup using NumVerify API - real data only"""
        if not self.numverify_api_key:
            return None
        
        try:
            params = {
                'access_key': self.numverify_api_key,
                'number': phone_number,
                'country_code': '',
                'format': 1
            }
            
            response = requests.get(self.numverify_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('valid'):
                    numverify_info = {
                        'Phone Number': phone_number,
                        'Valid': 'Yes' if data.get('valid') else 'No',
                        'Country': data.get('country_name', 'Unknown'),
                        'Country Code': data.get('country_code', 'Unknown'),
                        'State': data.get('region', 'Unknown'),
                        'Carrier': data.get('carrier', 'Unknown'),
                        'Line Type': data.get('line_type', 'Unknown'),
                        'International Format': data.get('international_format', 'Unknown'),
                        'Local Format': data.get('local_format', 'Unknown'),
                        'Timezone': data.get('timezone', 'Unknown')
                    }
                    
                    return {
                        'platform': 'NumVerify API',
                        'status': 'found',
                        'details': numverify_info
                    }
                else:
                    return {
                        'platform': 'NumVerify API',
                        'status': 'invalid',
                        'details': {'Error': 'Invalid phone number'}
                    }
            
        except Exception as e:
            logger.error(f"NumVerify request error: {str(e)}")
            return None
        
        return None