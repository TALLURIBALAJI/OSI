# OSINT Framework Portal

A professional-grade OSINT (Open Source Intelligence) framework portal that enables ethical investigators, security researchers, and HR professionals to gather publicly available information for identity validation and due diligence research.

## 🎯 Project Goal

This website uses free APIs to fetch public data based on:
- Email addresses
- Phone numbers  
- Domain names
- Social media handles
- Full names

**Impact**: Supports ethical investigators and HR professionals in validating identities while respecting privacy and using only publicly available information.

## 🚀 Features

- **Multi-Source Search**: Email, phone, domain, social media, and name-based searches
- **Real-time Results**: Fast API responses with comprehensive data aggregation
- **Export Capabilities**: Generate PDF reports and CSV exports
- **Security First**: Rate limiting, input validation, and security headers
- **Responsive Design**: Modern UI that works on all devices
- **Ethical Framework**: Focuses only on publicly available information

## 🛠️ Tech Stack

### Frontend
- **HTML5/CSS3**: Responsive design with modern styling
- **JavaScript**: Vanilla JS for API interactions and dynamic UI
- **Font Awesome**: Professional iconography

### Backend
- **Python Flask**: RESTful API server
- **Flask-CORS**: Cross-origin resource sharing
- **ReportLab**: PDF generation
- **Requests**: HTTP API interactions

### APIs & Services
- **WHOIS**: Domain registration information
- **IP-API**: Geolocation and ISP data
- **Phone Number Parser**: Carrier and location lookup
- **Have I Been Pwned**: Data breach checking (API key required)
- **Social Media**: Platform presence detection

## 📁 Project Structure

```
final/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── index.html               # Homepage
├── search.html              # Search interface
├── about.html               # About page
├── style.css                # Styling
├── script.js                # Frontend JavaScript
├── api_modules/             # Backend API modules
│   ├── __init__.py
│   ├── whois_lookup.py      # Domain WHOIS lookups
│   ├── ip_lookup.py         # IP geolocation
│   ├── phone_lookup.py      # Phone number analysis
│   ├── email_lookup.py      # Email validation & breach check
│   ├── social_lookup.py     # Social media presence
│   ├── export_handler.py    # PDF/CSV generation
│   ├── input_validator.py   # Input validation & sanitization
│   └── security.py          # Rate limiting & security
└── README.md                # This file
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 1. Clone or Download
```bash
# If using git
git clone <repository-url>
cd final

# Or download and extract the ZIP file
```

### 2. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt
```

### 3. Optional API Keys
For enhanced functionality, you can add API keys to the respective modules:

- **Have I Been Pwned API**: Add your API key to `api_modules/email_lookup.py`
- **NumVerify Phone API**: Add your API key to `api_modules/phone_lookup.py`

### 4. Run the Application
```bash
# Start the Flask backend
python app.py
```

The backend will run on `http://localhost:5000`

### 5. Open the Frontend
Open `index.html` in your web browser or serve it with a simple HTTP server:

```bash
# Option 1: Open directly in browser
# Navigate to the project folder and double-click index.html

# Option 2: Use Python's built-in server
python -m http.server 8000
# Then visit http://localhost:8000
```

## 📖 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Search
```http
POST /api/search
Content-Type: application/json

{
  "type": "email|phone|domain|username|name",
  "query": "search_term"
}
```

**Response:**
```json
{
  "status": "success",
  "search_type": "email",
  "query": "user@example.com",
  "results": [
    {
      "platform": "Platform Name",
      "status": "found|not_found|error|clean|compromised",
      "details": {
        "key": "value"
      }
    }
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 2. Export PDF
```http
POST /api/export/pdf
Content-Type: application/json

{
  "results": [...],
  "query": "search_term"
}
```

#### 3. Export CSV
```http
POST /api/export/csv
Content-Type: application/json

{
  "results": [...],
  "query": "search_term"
}
```

### Rate Limiting
- Search: 30 requests per minute
- Export: 5 requests per minute

## 🔒 Security Features

- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: Prevents API abuse
- **Security Headers**: CSRF, XSS, and clickjacking protection
- **CORS Configuration**: Restricted to specific origins
- **Error Handling**: Secure error messages without sensitive data exposure

## 📊 Search Types & Capabilities

### Email Search
- Format validation
- Domain analysis
- Breach checking (with API key)
- Social media hints

### Phone Search
- Number validation and formatting
- Carrier identification
- Geographic location
- Number type detection

### Domain Search
- WHOIS registration data
- DNS record analysis
- Creation and expiration dates
- Name server information

### Username Search
- Social media platform checking
- Profile existence detection
- Cross-platform analysis

### Name Search
- Professional network hints
- Username generation suggestions
- Search strategy recommendations

## 🔄 Usage Examples

### 1. Email Search
```javascript
fetch('http://localhost:5000/api/search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    type: 'email',
    query: 'user@example.com'
  })
})
```

### 2. Phone Search
```javascript
fetch('http://localhost:5000/api/search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    type: 'phone',
    query: '+1234567890'
  })
})
```

## ⚖️ Legal & Ethical Guidelines

This tool is designed for **ethical use only**:

- ✅ **Legitimate purposes**: Identity verification, due diligence, security research
- ✅ **Public information**: Only searches publicly available data
- ✅ **Authorized use**: Ensure you have permission for your research
- ❌ **Harassment**: Do not use for stalking or harassment
- ❌ **Illegal activities**: Respect all applicable laws and regulations
- ❌ **Privacy violation**: Do not access private or confidential information

## 🚨 Troubleshooting

### Common Issues

1. **Backend not starting**
   ```bash
   # Check if all dependencies are installed
   pip install -r requirements.txt
   
   # Check for port conflicts
   netstat -an | findstr :5000
   ```

2. **CORS errors in browser**
   - Ensure the backend is running on `http://localhost:5000`
   - Check that CORS is properly configured in `app.py`

3. **API connection errors**
   - Verify the backend URL in `script.js` matches your setup
   - Check browser console for detailed error messages

4. **Rate limiting**
   - Wait for the rate limit window to reset
   - Consider implementing authentication for higher limits

### Performance Tips

- **API Keys**: Add optional API keys for enhanced data
- **Caching**: Implement caching for frequently searched terms
- **Database**: Consider adding a database for result storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and ethical research purposes. Please ensure compliance with all applicable laws and platform terms of service.

## 🔗 References

- [OSINT Framework](https://osintframework.com/) - Original inspiration
- [Have I Been Pwned API](https://haveibeenpwned.com/API/Key)
- [IP-API Documentation](https://ip-api.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 📞 Support

For questions or issues:
1. Check this README
2. Review the troubleshooting section
3. Check browser console for errors
4. Verify all dependencies are installed

---

**⚠️ Important Disclaimer**: This tool is intended for legitimate security research, identity verification, and due diligence purposes only. Users are responsible for ensuring their use complies with all applicable laws and ethical guidelines.