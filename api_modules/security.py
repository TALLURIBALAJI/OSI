from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict, deque
import threading

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_allowed(self, identifier, max_requests=10, window_seconds=60):
        """Check if request is allowed based on rate limit"""
        with self.lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Clean old requests
            while self.requests[identifier] and self.requests[identifier][0] < window_start:
                self.requests[identifier].popleft()
            
            # Check if under limit
            if len(self.requests[identifier]) < max_requests:
                self.requests[identifier].append(now)
                return True
            
            return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests=10, window_seconds=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as identifier
            identifier = request.environ.get('REMOTE_ADDR', 'unknown')
            
            if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
                return jsonify({
                    "error": "Rate limit exceeded. Please try again later.",
                    "retry_after": window_seconds
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_request():
    """Validate that request contains valid JSON"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            
            try:
                data = request.get_json()
                if data is None:
                    return jsonify({"error": "Invalid JSON"}), 400
            except Exception:
                return jsonify({"error": "Invalid JSON"}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response