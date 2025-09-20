import requests
import logging
from urllib.parse import quote
import time

logger = logging.getLogger(__name__)

class SocialLookup:
    """Social media and username lookup functionality"""
    
    def __init__(self):
        self.name = "Social Lookup"
        self.platforms = {
            'GitHub': 'https://github.com/{}',
            'Twitter': 'https://twitter.com/{}',
            'Instagram': 'https://instagram.com/{}',
            'LinkedIn': 'https://linkedin.com/in/{}',
            'Reddit': 'https://reddit.com/user/{}',
            'TikTok': 'https://tiktok.com/@{}',
            'YouTube': 'https://youtube.com/@{}',
            'Facebook': 'https://facebook.com/{}',
            'Pinterest': 'https://pinterest.com/{}',
            'Telegram': 'https://t.me/{}'
        }
    
    def search_by_username(self, username):
        """Search for username across social media platforms"""
        results = []
        
        # Clean username
        username = username.strip().replace('@', '')
        
        # Check each platform
        for platform, url_template in self.platforms.items():
            try:
                result = self._check_platform(platform, username, url_template)
                if result:
                    results.append(result)
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error checking {platform} for {username}: {str(e)}")
        
        # Add summary
        found_platforms = [r for r in results if r['status'] == 'found']
        summary = {
            'Username': username,
            'Total Platforms Checked': str(len(self.platforms)),
            'Profiles Found': str(len(found_platforms)),
            'Found On': ', '.join([r['platform'] for r in found_platforms]) if found_platforms else 'None'
        }
        
        results.insert(0, {
            'platform': 'Username Search Summary',
            'status': 'summary',
            'details': summary
        })
        
        return results
    
    def search_by_name(self, full_name):
        """Search for full name (limited without advanced APIs)"""
        results = []
        
        # Basic name analysis
        name_parts = full_name.strip().split()
        
        name_info = {
            'Full Name': full_name,
            'First Name': name_parts[0] if name_parts else '',
            'Last Name': name_parts[-1] if len(name_parts) > 1 else '',
            'Name Parts': str(len(name_parts)),
            'Google Search': f'https://www.google.com/search?q={quote(full_name)}',
            'LinkedIn Search': f'https://www.linkedin.com/search/results/people/?keywords={quote(full_name)}',
            'Facebook Search': f'https://www.facebook.com/search/people/?q={quote(full_name)}',
            'Twitter Search': f'https://twitter.com/search?q={quote(full_name)}&src=typed_query&f=user',
            'Instagram Search': f'https://www.instagram.com/explore/tags/{full_name.replace(" ", "").lower()}/',
            'Search Suggestions': self._get_name_search_suggestions(full_name)
        }
        
        results.append({
            'platform': 'Name Analysis',
            'status': 'info',
            'details': name_info
        })
        
        # Generate potential usernames
        potential_usernames = self._generate_usernames(full_name)
        if potential_usernames:
            username_info = {
                'Based on Name': full_name,
                'Potential Usernames': ', '.join(potential_usernames[:10]),  # Limit to first 10
                'Search Tip': 'Try searching these usernames individually'
            }
            
            results.append({
                'platform': 'Username Suggestions',
                'status': 'info',
                'details': username_info
            })
        
        return results
    
    def _check_platform(self, platform, username, url_template):
        """Check if username exists on a specific platform"""
        try:
            url = url_template.format(username)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            # Different platforms have different indicators of existence
            status = self._analyze_response(platform, response, username)
            
            if status == 'found':
                details = {
                    'Platform': platform,
                    'Username': username,
                    'Profile URL': url,
                    'Status': 'Profile Found',
                    'Response Code': str(response.status_code),
                    'Visit Profile': url  # Direct link for frontend
                }
            elif status == 'not_found':
                details = {
                    'Platform': platform,
                    'Username': username,
                    'Status': 'Not Found',
                    'Response Code': str(response.status_code),
                    'Check Manually': url  # Still provide link to check manually
                }
            else:  # unknown
                details = {
                    'Platform': platform,
                    'Username': username,
                    'Status': 'Unknown (Check Manually)',
                    'Profile URL': url,
                    'Response Code': str(response.status_code),
                    'Manual Check': url  # Link for manual verification
                }
            
            return {
                'platform': platform,
                'status': status,
                'details': details
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'platform': platform,
                'status': 'error',
                'details': {
                    'Platform': platform,
                    'Username': username,
                    'Error': f'Request failed: {str(e)}'
                }
            }
    
    def _analyze_response(self, platform, response, username):
        """Analyze HTTP response to determine if profile exists"""
        status_code = response.status_code
        content = response.text.lower()
        
        # Common indicators
        not_found_indicators = [
            'user not found',
            'page not found',
            'profile not found',
            'this account doesn\'t exist',
            'sorry, that page doesn\'t exist',
            'the specified user does not exist'
        ]
        
        found_indicators = [
            f'@{username.lower()}',
            f'/{username.lower()}',
            'profile',
            'followers',
            'following'
        ]
        
        if status_code == 404:
            return 'not_found'
        elif status_code == 200:
            # Check content for indicators
            if any(indicator in content for indicator in not_found_indicators):
                return 'not_found'
            elif any(indicator in content for indicator in found_indicators):
                return 'found'
            else:
                return 'unknown'
        elif status_code in [403, 429]:
            return 'unknown'  # Rate limited or forbidden
        else:
            return 'unknown'
    
    def _generate_usernames(self, full_name):
        """Generate potential usernames from a full name"""
        name_parts = [part.lower() for part in full_name.strip().split()]
        
        if not name_parts:
            return []
        
        usernames = []
        
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            
            # Common username patterns
            usernames.extend([
                f"{first}{last}",
                f"{first}.{last}",
                f"{first}_{last}",
                f"{first}-{last}",
                f"{last}{first}",
                f"{first[0]}{last}",
                f"{first}{last[0]}",
                f"{first}{last}123",
                f"{first}.{last}.official",
                f"real{first}{last}"
            ])
        
        # Single name
        if len(name_parts) == 1:
            name = name_parts[0]
            usernames.extend([
                name,
                f"{name}123",
                f"real{name}",
                f"{name}official",
                f"the{name}"
            ])
        
        return list(set(usernames))  # Remove duplicates
    
    def _get_name_search_suggestions(self, full_name):
        """Get search suggestions for a full name"""
        suggestions = [
            f'Google: "{full_name}"',
            f'LinkedIn: Search professionals named "{full_name}"',
            f'Facebook: People search for "{full_name}"',
            f'Instagram: Search hashtags and usernames',
            f'Twitter: Search tweets and profiles'
        ]
        
        return ' | '.join(suggestions)