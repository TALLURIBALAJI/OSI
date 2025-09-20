import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IPLookup:
    """IP address and geolocation lookup functionality"""
    
    def __init__(self):
        self.name = "IP Lookup"
        self.ip_api_url = "http://ip-api.com/json"
        self.ipwhois_url = "https://ipwhois.app/json"
    
    def search(self, ip_address):
        """Perform IP address lookup"""
        results = []
        
        # IP-API lookup
        try:
            ip_api_result = self._ip_api_lookup(ip_address)
            if ip_api_result:
                results.append(ip_api_result)
        except Exception as e:
            logger.error(f"IP-API lookup error: {str(e)}")
        
        # IPWhois lookup
        try:
            ipwhois_result = self._ipwhois_lookup(ip_address)
            if ipwhois_result:
                results.append(ipwhois_result)
        except Exception as e:
            logger.error(f"IPWhois lookup error: {str(e)}")
        
        return results
    
    def _ip_api_lookup(self, ip_address):
        """Lookup using IP-API service"""
        try:
            response = requests.get(f"{self.ip_api_url}/{ip_address}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    ip_info = {
                        'IP Address': ip_address,
                        'Country': data.get('country', 'N/A'),
                        'Region': data.get('regionName', 'N/A'),
                        'City': data.get('city', 'N/A'),
                        'ZIP Code': data.get('zip', 'N/A'),
                        'ISP': data.get('isp', 'N/A'),
                        'Organization': data.get('org', 'N/A'),
                        'AS': data.get('as', 'N/A'),
                        'Timezone': data.get('timezone', 'N/A'),
                        'Latitude': str(data.get('lat', 'N/A')),
                        'Longitude': str(data.get('lon', 'N/A')),
                        'Security Check': f"https://www.virustotal.com/gui/ip-address/{ip_address}",
                        'Reputation Check': f"https://www.abuseipdb.com/check/{ip_address}",
                        'Shodan Search': f"https://www.shodan.io/host/{ip_address}"
                    }
                    
                    return {
                        'platform': 'IP-API Geolocation',
                        'status': 'found',
                        'details': ip_info
                    }
                else:
                    return {
                        'platform': 'IP-API Geolocation',
                        'status': 'not_found',
                        'details': {'Error': data.get('message', 'IP not found')}
                    }
            
        except Exception as e:
            logger.error(f"IP-API request error: {str(e)}")
            return None
        
        return None
    
    def _ipwhois_lookup(self, ip_address):
        """Lookup using IPWhois service"""
        try:
            response = requests.get(f"{self.ipwhois_url}/{ip_address}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    whois_info = {
                        'IP Address': ip_address,
                        'Type': data.get('type', 'N/A'),
                        'Country': data.get('country', 'N/A'),
                        'Country Code': data.get('country_code', 'N/A'),
                        'Region': data.get('region', 'N/A'),
                        'City': data.get('city', 'N/A'),
                        'ISP': data.get('isp', 'N/A'),
                        'ASN': data.get('asn', 'N/A'),
                        'Org': data.get('org', 'N/A')
                    }
                    
                    return {
                        'platform': 'IPWhois Registry',
                        'status': 'found',
                        'details': whois_info
                    }
                else:
                    return {
                        'platform': 'IPWhois Registry',
                        'status': 'not_found',
                        'details': {'Error': 'IP information not available'}
                    }
            
        except Exception as e:
            logger.error(f"IPWhois request error: {str(e)}")
            return None
        
        return None
    
    def get_ip_from_domain(self, domain):
        """Get IP address from domain name"""
        try:
            import socket
            ip_address = socket.gethostbyname(domain)
            return ip_address
        except Exception as e:
            logger.error(f"Domain to IP conversion error: {str(e)}")
            return None