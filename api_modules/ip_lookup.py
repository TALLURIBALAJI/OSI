import requests
import logging
import re
import socket
from datetime import datetime

logger = logging.getLogger(__name__)

class IPLookup:
    """IP address and geolocation lookup functionality"""
    
    def __init__(self):
        self.name = "IP Lookup"
        self.ip_api_url = "http://ip-api.com/json"
        self.ipwhois_url = "https://ipwhois.app/json"
        self.ipinfo_url = "https://ipinfo.io"
    
    def search(self, ip_address):
        """Perform comprehensive IP address lookup"""
        results = []
        
        # Validate IP address format
        try:
            validation_result = self._validate_ip(ip_address)
            results.append(validation_result)
        except Exception as e:
            logger.error(f"IP validation error: {str(e)}")
        
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
        
        # Security & Reputation Analysis
        try:
            security_result = self._security_analysis(ip_address)
            if security_result:
                results.append(security_result)
        except Exception as e:
            logger.error(f"Security analysis error: {str(e)}")
        
        # Network Information
        try:
            network_result = self._network_analysis(ip_address)
            if network_result:
                results.append(network_result)
        except Exception as e:
            logger.error(f"Network analysis error: {str(e)}")
        
        return results
    
    def _validate_ip(self, ip_address):
        """Validate IP address format and determine type"""
        try:
            # Check if it's a valid IPv4 address
            socket.inet_aton(ip_address)
            ip_type = "IPv4"
            
            # Check if it's private/reserved
            octets = ip_address.split('.')
            first_octet = int(octets[0])
            second_octet = int(octets[1])
            
            if first_octet == 10:
                ip_class = "Private (Class A)"
            elif first_octet == 172 and 16 <= second_octet <= 31:
                ip_class = "Private (Class B)"
            elif first_octet == 192 and second_octet == 168:
                ip_class = "Private (Class C)"
            elif first_octet == 127:
                ip_class = "Loopback"
            elif first_octet == 169 and second_octet == 254:
                ip_class = "Link-Local"
            elif 224 <= first_octet <= 239:
                ip_class = "Multicast"
            elif 240 <= first_octet <= 255:
                ip_class = "Reserved"
            else:
                ip_class = "Public"
                
        except socket.error:
            try:
                # Check if it's IPv6
                socket.inet_pton(socket.AF_INET6, ip_address)
                ip_type = "IPv6"
                ip_class = "Unknown"
            except socket.error:
                ip_type = "Invalid"
                ip_class = "Invalid Format"
        
        validation_info = {
            'IP Address': ip_address,
            'Format': 'Valid' if ip_type != 'Invalid' else 'Invalid',
            'IP Version': ip_type,
            'Classification': ip_class,
            'Status': 'Valid for lookup' if ip_class == 'Public' else 'Limited lookup (Private/Reserved IP)'
        }
        
        return {
            'platform': 'IP Validation',
            'status': 'valid' if ip_type != 'Invalid' else 'invalid',
            'details': validation_info
        }

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
                        'Country Code': data.get('countryCode', 'N/A'),
                        'Region': data.get('regionName', 'N/A'),
                        'City': data.get('city', 'N/A'),
                        'ZIP Code': data.get('zip', 'N/A'),
                        'ISP': data.get('isp', 'N/A'),
                        'Organization': data.get('org', 'N/A'),
                        'AS Number': data.get('as', 'N/A'),
                        'Timezone': data.get('timezone', 'N/A'),
                        'Latitude': str(data.get('lat', 'N/A')),
                        'Longitude': str(data.get('lon', 'N/A')),
                        'Mobile/Proxy': 'Yes' if data.get('mobile') or data.get('proxy') else 'No',
                        'VPN Detection': 'Yes' if data.get('hosting') else 'No'
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
    
    def _security_analysis(self, ip_address):
        """Provide security analysis and OSINT links"""
        try:
            security_info = {
                'IP Address': ip_address,
                'VirusTotal': f"https://www.virustotal.com/gui/ip-address/{ip_address}",
                'AbuseIPDB': f"https://www.abuseipdb.com/check/{ip_address}",
                'Shodan': f"https://www.shodan.io/host/{ip_address}",
                'ThreatCrowd': f"https://www.threatcrowd.org/ip.php?ip={ip_address}",
                'ThreatMiner': f"https://www.threatminer.org/host.php?q={ip_address}",
                'IBM X-Force': f"https://exchange.xforce.ibmcloud.com/ip/{ip_address}",
                'URLVoid': f"https://www.urlvoid.com/ip/{ip_address}",
                'IP Quality Score': f"https://www.ipqualityscore.com/free-ip-lookup-proxy-vpn-test/lookup/{ip_address}",
                'AlienVault OTX': f"https://otx.alienvault.com/indicator/ip/{ip_address}",
                'Cisco Talos': f"https://talosintelligence.com/reputation_center/lookup?search={ip_address}"
            }
            
            return {
                'platform': 'Security & Threat Intelligence',
                'status': 'found',
                'details': security_info
            }
            
        except Exception as e:
            logger.error(f"Security analysis error: {str(e)}")
            return None
    
    def _network_analysis(self, ip_address):
        """Provide network analysis and additional OSINT sources"""
        try:
            network_info = {
                'IP Address': ip_address,
                'BGP Toolkit': f"https://bgp.he.net/ip/{ip_address}",
                'IPinfo.io': f"https://ipinfo.io/{ip_address}",
                'DB-IP': f"https://db-ip.com/{ip_address}",
                'IP2Location': f"https://www.ip2location.com/demo/{ip_address}",
                'MaxMind': f"https://www.maxmind.com/en/geoip-demo",
                'ARIN WHOIS': f"https://whois.arin.net/rest/ip/{ip_address}",
                'RIPE Database': f"https://apps.db.ripe.net/db-web-ui/query?searchtext={ip_address}",
                'LACNIC': f"https://lacnic.net/cgi-bin/lacnic/whois?query={ip_address}",
                'APNIC': f"https://wq.apnic.net/apnic-bin/whois.pl?searchtext={ip_address}",
                'Robtex': f"https://www.robtex.com/ip-lookup/{ip_address}",
                'SecurityTrails': f"https://securitytrails.com/list/ip/{ip_address}",
                'DNS History': f"https://completedns.com/dns-history/?domain={ip_address}",
                'Reverse DNS': 'Use nslookup or dig commands for reverse lookup'
            }
            
            return {
                'platform': 'Network & Registry Information',
                'status': 'found',
                'details': network_info
            }
            
        except Exception as e:
            logger.error(f"Network analysis error: {str(e)}")
            return None