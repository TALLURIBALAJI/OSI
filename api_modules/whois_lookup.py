import whois
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WhoisLookup:
    """WHOIS domain lookup functionality"""
    
    def __init__(self):
        self.name = "WHOIS Lookup"
    
    def search(self, domain):
        """Perform WHOIS lookup on a domain"""
        results = []
        
        try:
            # Remove protocol if present
            if domain.startswith(('http://', 'https://')):
                domain = domain.split('://', 1)[1]
            
            # Remove www if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Get WHOIS data
            whois_data = whois.whois(domain)
            
            if whois_data:
                # Parse WHOIS information
                whois_info = {
                    'Domain Name': domain,
                    'Registrar': str(whois_data.registrar) if whois_data.registrar else 'N/A',
                    'Creation Date': str(whois_data.creation_date) if whois_data.creation_date else 'N/A',
                    'Expiration Date': str(whois_data.expiration_date) if whois_data.expiration_date else 'N/A',
                    'Updated Date': str(whois_data.updated_date) if whois_data.updated_date else 'N/A',
                    'Status': ', '.join(whois_data.status) if whois_data.status else 'N/A',
                    'Name Servers': ', '.join(whois_data.name_servers) if whois_data.name_servers else 'N/A',
                    'Visit Website': f"https://{domain}",
                    'Check SSL': f"https://www.ssllabs.com/ssltest/analyze.html?d={domain}",
                    'Archive History': f"https://web.archive.org/web/*/{domain}",
                    'Security Scan': f"https://www.virustotal.com/gui/domain/{domain}"
                }
                
                results.append({
                    'platform': 'WHOIS Registry',
                    'status': 'found',
                    'details': whois_info
                })
            
            # Get DNS information
            dns_info = self._get_dns_info(domain)
            if dns_info:
                results.append({
                    'platform': 'DNS Records',
                    'status': 'found',
                    'details': dns_info
                })
                
        except Exception as e:
            logger.error(f"WHOIS lookup error for {domain}: {str(e)}")
            results.append({
                'platform': 'WHOIS Registry',
                'status': 'error',
                'details': {'Error': f'Unable to retrieve WHOIS data: {str(e)}'}
            })
        
        return results
    
    def _get_dns_info(self, domain):
        """Get DNS information for domain"""
        try:
            import dns.resolver
            
            dns_info = {}
            
            # A records
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                dns_info['A Records'] = ', '.join([str(record) for record in a_records])
            except:
                dns_info['A Records'] = 'N/A'
            
            # MX records
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                dns_info['MX Records'] = ', '.join([str(record) for record in mx_records])
            except:
                dns_info['MX Records'] = 'N/A'
            
            # NS records
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                dns_info['NS Records'] = ', '.join([str(record) for record in ns_records])
            except:
                dns_info['NS Records'] = 'N/A'
            
            return dns_info
            
        except ImportError:
            # dnspython not available, skip DNS lookup
            return None
        except Exception as e:
            logger.error(f"DNS lookup error for {domain}: {str(e)}")
            return None