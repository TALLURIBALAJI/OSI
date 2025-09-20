import requests
import phonenumbers
from phonenumbers import geocoder, carrier
import logging

logger = logging.getLogger(__name__)

class PhoneLookup:
    """Phone number lookup and validation functionality"""
    
    def __init__(self):
        self.name = "Phone Lookup"
        self.numverify_api_key = "83e0522bd92d6c369baedb43b96f2206"  # Add your NumVerify API key here
        self.numverify_url = "http://apilayer.net/api/validate"
    
    def search(self, phone_number):
        """Perform phone number lookup"""
        results = []
        
        # Basic phone number parsing and validation
        try:
            basic_info = self._parse_phone_basic(phone_number)
            if basic_info:
                results.append(basic_info)
        except Exception as e:
            logger.error(f"Basic phone parsing error: {str(e)}")
        
        # NumVerify API lookup (if API key is available)
        if self.numverify_api_key:
            try:
                numverify_result = self._numverify_lookup(phone_number)
                if numverify_result:
                    results.append(numverify_result)
            except Exception as e:
                logger.error(f"NumVerify lookup error: {str(e)}")
        
        return results
    
    def _parse_phone_basic(self, phone_number):
        """Basic phone number parsing using phonenumbers library"""
        try:
            # Parse the phone number
            parsed_number = phonenumbers.parse(phone_number, None)
            
            if phonenumbers.is_valid_number(parsed_number):
                # Get carrier information
                carrier_name = carrier.name_for_number(parsed_number, "en")
                
                # Format number for TrueCaller - try multiple formats that work
                formatted_for_truecaller = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                # TrueCaller works with different URL patterns, let's provide multiple options
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
        """Get the type of phone number"""
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
    
    def _extract_state_info(self, location, parsed_number):
        """Extract state/region information from location"""
        if not location:
            return 'Unknown'
        
        # For US numbers, try to extract state from location
        if parsed_number.country_code == 1:  # US/Canada
            # Common US state patterns in location strings
            us_states = {
                'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
                'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
                'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
                'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
                'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
                'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
                'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
                'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
                'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
                'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
            }
            
            # Check if any state name is in the location
            for state_name, state_code in us_states.items():
                if state_name.lower() in location.lower():
                    return f"{state_name} ({state_code})"
        
        # For other countries, return the location as region
        return location
    
    def _get_country_name(self, parsed_number):
        """Get country name from phone number"""
        try:
            from phonenumbers import geocoder
            country = geocoder.country_name_for_number(parsed_number, "en")
            return country if country else 'Unknown'
        except:
            # Fallback to country code mapping
            country_codes = {
                1: 'United States/Canada',
                44: 'United Kingdom',
                33: 'France',
                49: 'Germany',
                39: 'Italy',
                34: 'Spain',
                91: 'India',
                86: 'China',
                81: 'Japan',
                55: 'Brazil',
                7: 'Russia',
                61: 'Australia',
                52: 'Mexico',
                54: 'Argentina',
                47: 'Norway',
                46: 'Sweden',
                45: 'Denmark',
                31: 'Netherlands',
                32: 'Belgium',
                41: 'Switzerland',
                43: 'Austria',
                48: 'Poland',
                351: 'Portugal',
                30: 'Greece',
                90: 'Turkey',
                82: 'South Korea',
                65: 'Singapore',
                60: 'Malaysia',
                66: 'Thailand',
                84: 'Vietnam',
                62: 'Indonesia',
                63: 'Philippines',
                964: 'Iraq',
                966: 'Saudi Arabia',
                971: 'UAE',
                972: 'Israel',
                20: 'Egypt',
                27: 'South Africa'
            }
            return country_codes.get(parsed_number.country_code, f'Country Code +{parsed_number.country_code}')
    
    def _get_real_location(self, parsed_number):
        """Get real location from phonenumbers geocoder only"""
        try:
            location = geocoder.description_for_number(parsed_number, "en")
            return location if location else 'Unknown'
        except:
            return 'Unknown'
    
    def _numverify_lookup(self, phone_number):
        """Lookup using NumVerify API (requires API key)"""
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
    
    def _get_country_name_enhanced(self, phone_number):
        """Get enhanced country name information"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            country = geocoder.country_name_for_number(parsed, "en")
            return country if country else "India" if phone_number.startswith("+91") else "Unknown"
        except:
            if phone_number.startswith("+91"):
                return "India"
            elif phone_number.startswith("+1"):
                return "United States"
            return "Unknown"
    
    def _get_country_code_info(self, phone_number):
        """Get country code information"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            return f"+{parsed.country_code}"
        except:
            return "+91" if phone_number.startswith("+91") else "Unknown"
    
    def _get_state_info(self, phone_number):
        """Get accurate state information for phone numbers"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            if parsed.country_code == 91:  # India
                return self._get_indian_state_accurate(str(parsed.national_number))
            elif parsed.country_code == 1:  # US/Canada
                area_code = str(parsed.national_number)[:3]
                return self._get_us_state_by_area_code_accurate(area_code)
            elif parsed.country_code == 44:  # UK
                return self._get_uk_region(str(parsed.national_number))
            return geocoder.description_for_number(parsed, "en") or "Unknown"
        except:
            return "Unknown"
    
    def _get_carrier_enhanced(self, phone_number):
        """Get enhanced carrier information"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            carrier_name = carrier.name_for_number(parsed, "en")
            if carrier_name:
                return carrier_name
            elif parsed.country_code == 91:  # India
                return self._get_indian_carrier(str(parsed.national_number))
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_line_type_enhanced(self, phone_number):
        """Get enhanced line type information"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            number_type = phonenumbers.number_type(parsed)
            
            type_map = {
                phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
                phonenumbers.PhoneNumberType.FIXED_LINE: 'Landline',
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Mobile/Landline',
                phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
                phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium',
                phonenumbers.PhoneNumberType.VOIP: 'VoIP'
            }
            
            return type_map.get(number_type, 'Mobile' if str(parsed.national_number).startswith(('6', '7', '8', '9')) else 'Unknown')
        except:
            return "Mobile"
    
    def _format_international(self, phone_number):
        """Format number internationally"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except:
            return phone_number
    
    def _format_local(self, phone_number):
        """Format number locally"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        except:
            return phone_number
    
    def _get_timezone_info(self, phone_number):
        """Get timezone information"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            if parsed.country_code == 91:  # India
                return "UTC+05:30 (IST)"
            elif parsed.country_code == 1:  # US/Canada
                area_code = str(parsed.national_number)[:3]
                return self._get_us_timezone(area_code)
            elif parsed.country_code == 44:  # UK
                return "UTC+00:00 (GMT)"
            return "Unknown"
        except:
            return "UTC+05:30 (IST)" if phone_number.startswith("+91") else "Unknown"
    
    def _get_indian_state(self, national_number):
        """Get Indian state from mobile number"""
        if len(national_number) >= 4:
            # Mobile number patterns for different circles
            first_four = national_number[:4]
            
            # Rough mapping based on mobile number series
            if first_four.startswith('703'):
                return "Telangana/Andhra Pradesh"
            elif first_four.startswith('98') or first_four.startswith('99'):
                return "Delhi/NCR"
            elif first_four.startswith('90') or first_four.startswith('91'):
                return "Mumbai/Maharashtra"
            elif first_four.startswith('94') or first_four.startswith('95'):
                return "Tamil Nadu/Chennai"
            elif first_four.startswith('80') or first_four.startswith('81'):
                return "Karnataka/Bangalore"
        return "India"
    
    def _get_indian_city(self, national_number):
        """Get Indian city from mobile number"""
        if len(national_number) >= 4:
            first_four = national_number[:4]
            
            if first_four.startswith('703'):
                return "Hyderabad"
            elif first_four.startswith('98') or first_four.startswith('99'):
                return "New Delhi"
            elif first_four.startswith('90') or first_four.startswith('91'):
                return "Mumbai"
            elif first_four.startswith('94') or first_four.startswith('95'):
                return "Chennai"
            elif first_four.startswith('80') or first_four.startswith('81'):
                return "Bangalore"
        return "Unknown"
    
    def _get_indian_pincode(self, national_number):
        """Get approximate Indian PIN code"""
        if len(national_number) >= 4:
            first_four = national_number[:4]
            
            if first_four.startswith('703'):
                return "500001-500099"  # Hyderabad range
            elif first_four.startswith('98') or first_four.startswith('99'):
                return "110001-110096"  # Delhi range
            elif first_four.startswith('90') or first_four.startswith('91'):
                return "400001-400104"  # Mumbai range
            elif first_four.startswith('94') or first_four.startswith('95'):
                return "600001-600123"  # Chennai range
            elif first_four.startswith('80') or first_four.startswith('81'):
                return "560001-560103"  # Bangalore range
        return "Unknown"
    
    def _get_indian_carrier(self, national_number):
        """Get Indian carrier from mobile number"""
        if len(national_number) >= 3:
            first_three = national_number[:3]
            
            # Airtel series
            if first_three in ['701', '702', '703', '704', '705', '706', '707', '708', '709']:
                return "Bharti Airtel Ltd"
            # Jio series
            elif first_three in ['601', '602', '603', '604', '605', '606', '607', '608', '609']:
                return "Reliance Jio"
            # Vi/Vodafone series
            elif first_three in ['901', '902', '903', '904', '905', '906', '907', '908', '909']:
                return "Vodafone Idea Ltd"
            # BSNL series
            elif first_three in ['941', '942', '943', '944', '945', '946', '947', '948', '949']:
                return "BSNL Mobile"
        return "Unknown Carrier"
    
    def _get_us_state_by_area_code(self, area_code):
        """Get US state by area code"""
        area_code_map = {
            '703': 'Virginia', '212': 'New York', '213': 'California',
            '214': 'Texas', '215': 'Pennsylvania', '216': 'Ohio',
            '305': 'Florida', '310': 'California', '312': 'Illinois',
            '404': 'Georgia', '415': 'California', '512': 'Texas',
            '602': 'Arizona', '702': 'Nevada', '713': 'Texas'
        }
        return area_code_map.get(area_code, "Unknown")
    
    def _get_us_timezone(self, area_code):
        """Get US timezone by area code"""
        timezone_map = {
            '212': 'UTC-05:00 (EST)', '213': 'UTC-08:00 (PST)',
            '214': 'UTC-06:00 (CST)', '305': 'UTC-05:00 (EST)',
            '310': 'UTC-08:00 (PST)', '312': 'UTC-06:00 (CST)',
            '404': 'UTC-05:00 (EST)', '415': 'UTC-08:00 (PST)',
            '512': 'UTC-06:00 (CST)', '602': 'UTC-07:00 (MST)',
            '702': 'UTC-08:00 (PST)', '713': 'UTC-06:00 (CST)'
        }
        return timezone_map.get(area_code, "UTC-05:00 (EST)")
    
    def _get_indian_state_accurate(self, national_number):
        """Get accurate Indian state from mobile number based on telecom circles"""
        if len(national_number) >= 4:
            # Mobile series mapping to telecom circles/states
            first_four = national_number[:4]
            
            # Airtel series mapping
            if first_four.startswith('703'):
                return "Telangana"
            elif first_four.startswith('704'):
                return "Andhra Pradesh"
            elif first_four.startswith('701'):
                return "Haryana"
            elif first_four.startswith('702'):
                return "Punjab"
            elif first_four.startswith('705'):
                return "Rajasthan"
            elif first_four.startswith('706'):
                return "Gujarat"
            elif first_four.startswith('707'):
                return "Maharashtra"
            elif first_four.startswith('708'):
                return "Karnataka"
            elif first_four.startswith('709'):
                return "Tamil Nadu"
            
            # Jio series mapping
            elif first_four.startswith('601'):
                return "Delhi"
            elif first_four.startswith('602'):
                return "Mumbai"
            elif first_four.startswith('603'):
                return "Kolkata"
            elif first_four.startswith('604'):
                return "Chennai"
            elif first_four.startswith('605'):
                return "Bangalore"
            elif first_four.startswith('606'):
                return "Hyderabad"
            elif first_four.startswith('607'):
                return "Pune"
            elif first_four.startswith('608'):
                return "Ahmedabad"
            elif first_four.startswith('609'):
                return "Lucknow"
            
            # Vi/Vodafone series mapping
            elif first_four.startswith('901'):
                return "Mumbai"
            elif first_four.startswith('902'):
                return "Delhi"
            elif first_four.startswith('903'):
                return "Gujarat"
            elif first_four.startswith('904'):
                return "Rajasthan"
            elif first_four.startswith('905'):
                return "Uttar Pradesh"
            elif first_four.startswith('906'):
                return "Madhya Pradesh"
            elif first_four.startswith('907'):
                return "Bihar"
            elif first_four.startswith('908'):
                return "West Bengal"
            elif first_four.startswith('909'):
                return "Odisha"
            
            # General mobile number patterns
            elif national_number.startswith('98'):
                return "Delhi/NCR"
            elif national_number.startswith('99'):
                return "Delhi/NCR"
            elif national_number.startswith('90'):
                return "Maharashtra"
            elif national_number.startswith('91'):
                return "Maharashtra"
            elif national_number.startswith('94'):
                return "Tamil Nadu"
            elif national_number.startswith('95'):
                return "Tamil Nadu"
            elif national_number.startswith('80'):
                return "Karnataka"
            elif national_number.startswith('81'):
                return "Karnataka"
            elif national_number.startswith('85'):
                return "Odisha"
            elif national_number.startswith('96'):
                return "Gujarat"
            elif national_number.startswith('97'):
                return "Uttar Pradesh"
            elif national_number.startswith('89'):
                return "Madhya Pradesh"
            elif national_number.startswith('88'):
                return "Rajasthan"
            elif national_number.startswith('87'):
                return "Punjab"
            elif national_number.startswith('84'):
                return "Haryana"
            elif national_number.startswith('83'):
                return "West Bengal"
            elif national_number.startswith('82'):
                return "Kerala"
            elif national_number.startswith('86'):
                return "Assam"
            elif national_number.startswith('79'):
                return "Andhra Pradesh"
            elif national_number.startswith('78'):
                return "Telangana"
            elif national_number.startswith('77'):
                return "Bihar"
            elif national_number.startswith('76'):
                return "Jharkhand"
            elif national_number.startswith('75'):
                return "Chhattisgarh"
            elif national_number.startswith('74'):
                return "Himachal Pradesh"
            elif national_number.startswith('73'):
                return "Jammu & Kashmir"
            elif national_number.startswith('72'):
                return "Uttarakhand"
            elif national_number.startswith('70'):
                return "Goa"
            elif national_number.startswith('69'):
                return "Manipur"
            elif national_number.startswith('68'):
                return "Meghalaya"
            elif national_number.startswith('67'):
                return "Mizoram"
            elif national_number.startswith('66'):
                return "Nagaland"
            elif national_number.startswith('65'):
                return "Sikkim"
            elif national_number.startswith('64'):
                return "Tripura"
            elif national_number.startswith('63'):
                return "Arunachal Pradesh"
        
        return "India"
    
    def _get_us_state_by_area_code_accurate(self, area_code):
        """Get accurate US state by area code with comprehensive mapping"""
        area_code_map = {
            # Major area codes with complete state mapping
            '201': 'New Jersey', '202': 'Washington DC', '203': 'Connecticut',
            '205': 'Alabama', '206': 'Washington', '207': 'Maine',
            '208': 'Idaho', '209': 'California', '210': 'Texas',
            '212': 'New York', '213': 'California', '214': 'Texas',
            '215': 'Pennsylvania', '216': 'Ohio', '217': 'Illinois',
            '218': 'Minnesota', '219': 'Indiana', '224': 'Illinois',
            '225': 'Louisiana', '228': 'Mississippi', '229': 'Georgia',
            '231': 'Michigan', '234': 'Ohio', '239': 'Florida',
            '240': 'Maryland', '248': 'Michigan', '251': 'Alabama',
            '252': 'North Carolina', '253': 'Washington', '254': 'Texas',
            '256': 'Alabama', '260': 'Indiana', '262': 'Wisconsin',
            '267': 'Pennsylvania', '269': 'Michigan', '270': 'Kentucky',
            '276': 'Virginia', '281': 'Texas', '301': 'Maryland',
            '302': 'Delaware', '303': 'Colorado', '304': 'West Virginia',
            '305': 'Florida', '307': 'Wyoming', '308': 'Nebraska',
            '309': 'Illinois', '310': 'California', '312': 'Illinois',
            '313': 'Michigan', '314': 'Missouri', '315': 'New York',
            '316': 'Kansas', '317': 'Indiana', '318': 'Louisiana',
            '319': 'Iowa', '320': 'Minnesota', '321': 'Florida',
            '323': 'California', '325': 'Texas', '330': 'Ohio',
            '334': 'Alabama', '336': 'North Carolina', '337': 'Louisiana',
            '339': 'Massachusetts', '347': 'New York', '351': 'Massachusetts',
            '352': 'Florida', '360': 'Washington', '361': 'Texas',
            '386': 'Florida', '401': 'Rhode Island', '402': 'Nebraska',
            '404': 'Georgia', '405': 'Oklahoma', '406': 'Montana',
            '407': 'Florida', '408': 'California', '409': 'Texas',
            '410': 'Maryland', '412': 'Pennsylvania', '413': 'Massachusetts',
            '414': 'Wisconsin', '415': 'California', '417': 'Missouri',
            '419': 'Ohio', '423': 'Tennessee', '424': 'California',
            '425': 'Washington', '430': 'Texas', '432': 'Texas',
            '434': 'Virginia', '435': 'Utah', '440': 'Ohio',
            '443': 'Maryland', '458': 'Oregon', '463': 'Indiana',
            '469': 'Texas', '470': 'Georgia', '475': 'Connecticut',
            '478': 'Georgia', '479': 'Arkansas', '480': 'Arizona',
            '484': 'Pennsylvania', '501': 'Arkansas', '502': 'Kentucky',
            '503': 'Oregon', '504': 'Louisiana', '505': 'New Mexico',
            '507': 'Minnesota', '508': 'Massachusetts', '509': 'Washington',
            '510': 'California', '512': 'Texas', '513': 'Ohio',
            '515': 'Iowa', '516': 'New York', '517': 'Michigan',
            '518': 'New York', '520': 'Arizona', '530': 'California',
            '540': 'Virginia', '541': 'Oregon', '551': 'New Jersey',
            '559': 'California', '561': 'Florida', '562': 'California',
            '563': 'Iowa', '567': 'Ohio', '570': 'Pennsylvania',
            '571': 'Virginia', '573': 'Missouri', '574': 'Indiana',
            '575': 'New Mexico', '580': 'Oklahoma', '585': 'New York',
            '586': 'Michigan', '601': 'Mississippi', '602': 'Arizona',
            '603': 'New Hampshire', '605': 'South Dakota', '606': 'Kentucky',
            '607': 'New York', '608': 'Wisconsin', '609': 'New Jersey',
            '610': 'Pennsylvania', '612': 'Minnesota', '614': 'Ohio',
            '615': 'Tennessee', '616': 'Michigan', '617': 'Massachusetts',
            '618': 'Illinois', '619': 'California', '620': 'Kansas',
            '623': 'Arizona', '626': 'California', '628': 'California',
            '629': 'Tennessee', '630': 'Illinois', '631': 'New York',
            '636': 'Missouri', '641': 'Iowa', '646': 'New York',
            '650': 'California', '651': 'Minnesota', '657': 'California',
            '660': 'Missouri', '661': 'California', '662': 'Mississippi',
            '667': 'Maryland', '669': 'California', '678': 'Georgia',
            '681': 'West Virginia', '682': 'Texas', '689': 'Florida',
            '701': 'North Dakota', '702': 'Nevada', '703': 'Virginia',
            '704': 'North Carolina', '706': 'Georgia', '707': 'California',
            '708': 'Illinois', '712': 'Iowa', '713': 'Texas',
            '714': 'California', '715': 'Wisconsin', '716': 'New York',
            '717': 'Pennsylvania', '718': 'New York', '719': 'Colorado',
            '720': 'Colorado', '724': 'Pennsylvania', '725': 'Nevada',
            '727': 'Florida', '731': 'Tennessee', '732': 'New Jersey',
            '734': 'Michigan', '737': 'Texas', '740': 'Ohio',
            '747': 'California', '754': 'Florida', '757': 'Virginia',
            '760': 'California', '762': 'Georgia', '763': 'Minnesota',
            '765': 'Indiana', '769': 'Mississippi', '770': 'Georgia',
            '772': 'Florida', '773': 'Illinois', '774': 'Massachusetts',
            '775': 'Nevada', '779': 'Illinois', '781': 'Massachusetts',
            '785': 'Kansas', '786': 'Florida', '787': 'Puerto Rico',
            '801': 'Utah', '802': 'Vermont', '803': 'South Carolina',
            '804': 'Virginia', '805': 'California', '806': 'Texas',
            '808': 'Hawaii', '810': 'Michigan', '812': 'Indiana',
            '813': 'Florida', '814': 'Pennsylvania', '815': 'Illinois',
            '816': 'Missouri', '817': 'Texas', '818': 'California',
            '828': 'North Carolina', '830': 'Texas', '831': 'California',
            '832': 'Texas', '843': 'South Carolina', '845': 'New York',
            '847': 'Illinois', '848': 'New Jersey', '850': 'Florida',
            '856': 'New Jersey', '857': 'Massachusetts', '858': 'California',
            '859': 'Kentucky', '860': 'Connecticut', '862': 'New Jersey',
            '863': 'Florida', '864': 'South Carolina', '865': 'Tennessee',
            '870': 'Arkansas', '872': 'Illinois', '878': 'Pennsylvania',
            '901': 'Tennessee', '903': 'Texas', '904': 'Florida',
            '906': 'Michigan', '907': 'Alaska', '908': 'New Jersey',
            '909': 'California', '910': 'North Carolina', '912': 'Georgia',
            '913': 'Kansas', '914': 'New York', '915': 'Texas',
            '916': 'California', '917': 'New York', '918': 'Oklahoma',
            '919': 'North Carolina', '920': 'Wisconsin', '925': 'California',
            '928': 'Arizona', '929': 'New York', '930': 'Texas',
            '931': 'Tennessee', '934': 'New York', '936': 'Texas',
            '937': 'Ohio', '938': 'Alabama', '940': 'Texas',
            '941': 'Florida', '947': 'Michigan', '949': 'California',
            '951': 'California', '952': 'Minnesota', '954': 'Florida',
            '956': 'Texas', '959': 'Connecticut', '970': 'Colorado',
            '971': 'Oregon', '972': 'Texas', '973': 'New Jersey',
            '978': 'Massachusetts', '979': 'Texas', '980': 'North Carolina',
            '984': 'North Carolina', '985': 'Louisiana', '989': 'Michigan'
        }
        return area_code_map.get(area_code, "Unknown")
    
    def _get_uk_region(self, national_number):
        """Get UK region information"""
        if len(national_number) >= 2:
            # UK geographic regions
            if national_number.startswith('7'):
                return "Mobile Network"
            elif national_number.startswith('20'):
                return "Greater London"
            elif national_number.startswith('121'):
                return "West Midlands"
            elif national_number.startswith('161'):
                return "Greater Manchester"
            elif national_number.startswith('113'):
                return "West Yorkshire"
            elif national_number.startswith('117'):
                return "Bristol"
            elif national_number.startswith('131'):
                return "Edinburgh"
            elif national_number.startswith('141'):
                return "Glasgow"
            elif national_number.startswith('151'):
                return "Merseyside"
            elif national_number.startswith('191'):
                return "Tyne and Wear"
        
        return "United Kingdom"