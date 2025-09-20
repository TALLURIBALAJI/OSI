from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import logging
from datetime import datetime
import json

# Import our custom modules
from api_modules.whois_lookup import WhoisLookup
from api_modules.ip_lookup import IPLookup
from api_modules.phone_lookup import PhoneLookup
from api_modules.email_lookup import EmailLookup
from api_modules.social_lookup import SocialLookup
from api_modules.export_handler import ExportHandler
from api_modules.input_validator import InputValidator
from api_modules.security import rate_limit, validate_json_request, add_security_headers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configure CORS
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"])

# Add security headers to all responses
@app.after_request
def after_request(response):
    return add_security_headers(response)

# Initialize API modules
whois_lookup = WhoisLookup()
ip_lookup = IPLookup()
phone_lookup = PhoneLookup()
email_lookup = EmailLookup()
social_lookup = SocialLookup()
export_handler = ExportHandler()

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "OSINT Framework Portal API is running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/search', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=60)  # 30 requests per minute
@validate_json_request()
def search():
    """Main search endpoint that handles different types of searches"""
    try:
        data = request.get_json()
        
        search_type = data.get('type')
        search_query = data.get('query')
        
        # Validate input
        is_valid, result = InputValidator.validate_search_input(search_type, search_query)
        if not is_valid:
            return jsonify({"error": result}), 400
        
        # Use sanitized query
        search_query = result
        
        logger.info(f"Search request: type={search_type}, query={search_query}")
        
        results = []
        
        if search_type == 'email':
            results = email_lookup.search(search_query)
        elif search_type == 'phone':
            results = phone_lookup.search(search_query)
        elif search_type == 'ip':
            results = ip_lookup.search(search_query)
        elif search_type == 'domain':
            results = whois_lookup.search(search_query)
        elif search_type == 'name':
            results = social_lookup.search_by_name(search_query)
        elif search_type == 'username':
            results = social_lookup.search_by_username(search_query)
        else:
            return jsonify({"error": "Invalid search type"}), 400
        
        return jsonify({
            "status": "success",
            "search_type": search_type,
            "query": search_query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/export/pdf', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)  # 5 exports per minute
@validate_json_request()
def export_pdf():
    """Export search results to PDF"""
    try:
        data = request.get_json()
        
        if not data or 'results' not in data:
            return jsonify({"error": "Results data required"}), 400
        
        pdf_buffer = export_handler.generate_pdf(data['results'], data.get('query', ''))
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"osint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"PDF export error: {str(e)}")
        return jsonify({"error": "PDF generation failed"}), 500

@app.route('/api/export/csv', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)  # 5 exports per minute
@validate_json_request()
def export_csv():
    """Export search results to CSV"""
    try:
        data = request.get_json()
        
        if not data or 'results' not in data:
            return jsonify({"error": "Results data required"}), 400
        
        csv_buffer = export_handler.generate_csv(data['results'], data.get('query', ''))
        
        return send_file(
            csv_buffer,
            as_attachment=True,
            download_name=f"osint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"CSV export error: {str(e)}")
        return jsonify({"error": "CSV generation failed"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('exports', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)