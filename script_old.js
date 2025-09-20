// Global variables
let currentSearchData = [];
const API_BASE_URL = 'http://localhost:5000/api';

// DOM elements
const searchForm = document.getElementById('searchForm');
const searchType = document.getElementById('searchType');
const searchInput = document.getElementById('searchInput');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const exportPDF = document.getElementById('exportPDF');
const exportCSV = document.getElementById('exportCSV');

// Sample data for demonstration
const mockData = {
    email: {
        'john.doe@example.com': [
            {
                platform: 'HaveIBeenPwned',
                status: 'breach',
                details: {
                    'Breaches Found': '3',
                    'Last Breach': 'LinkedIn (2021)',
                    'Exposed Data': 'Email, Password',
                    'Risk Level': 'High'
                }
            },
            {
                platform: 'Social Media',
                status: 'found',
                details: {
                    'LinkedIn': 'John Doe - Software Engineer',
                    'Twitter': '@johndoe_dev',
                    'GitHub': 'johndoe',
                    'Last Active': '2024-01-15'
                }
            }
        ]
    },
    phone: {
        '+12025550147': [
            {
                platform: 'Carrier Lookup',
                status: 'found',
                details: {
                    'Carrier': 'Verizon Wireless',
                    'Type': 'Mobile',
                    'Region': 'Washington, DC',
                    'Status': 'Active'
                }
            },
            {
                platform: 'Social Media',
                status: 'found',
                details: {
                    'WhatsApp': 'Active',
                    'Telegram': 'Not Found',
                    'Signal': 'Privacy Protected',
                    'Last Seen': '2024-01-20'
                }
            }
        ]
    },
    name: {
        'John Doe': [
            {
                platform: 'Public Records',
                status: 'found',
                details: {
                    'Age': '32',
                    'Location': 'Washington, DC',
                    'Occupation': 'Software Engineer',
                    'Education': 'MIT (2014)'
                }
            },
            {
                platform: 'Professional Networks',
                status: 'found',
                details: {
                    'LinkedIn': 'Senior Software Engineer at TechCorp',
                    'GitHub': '50+ repositories',
                    'Stack Overflow': '2.5k reputation',
                    'Company': 'TechCorp Inc.'
                }
            }
        ]
    },
    username: {
        '@johndoe_dev': [
            {
                platform: 'Twitter/X',
                status: 'found',
                details: {
                    'Followers': '1,234',
                    'Following': '456',
                    'Tweets': '2,891',
                    'Joined': 'March 2019'
                }
            },
            {
                platform: 'Cross-Platform',
                status: 'found',
                details: {
                    'Instagram': '@johndoe_dev (Private)',
                    'TikTok': 'Not Found',
                    'Reddit': 'u/johndoe_dev',
                    'YouTube': 'JohnDoe Dev (125 subscribers)'
                }
            }
        ]
    },
    domain: {
        'example.com': [
            {
                platform: 'Domain Registration',
                status: 'found',
                details: {
                    'Registrar': 'GoDaddy',
                    'Created': '1995-08-14',
                    'Expires': '2025-08-13',
                    'Status': 'Active'
                }
            },
            {
                platform: 'Technical Details',
                status: 'found',
                details: {
                    'IP Address': '93.184.216.34',
                    'Hosting': 'Edgecast Networks',
                    'SSL Certificate': 'Valid (DigiCert)',
                    'DNS': 'Cloudflare'
                }
            }
        ]
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
        searchType.addEventListener('change', updatePlaceholder);
        
        // Initialize placeholder
        updatePlaceholder();
    }

    if (exportPDF) {
        exportPDF.addEventListener('click', () => exportResults('pdf'));
    }

    if (exportCSV) {
        exportCSV.addEventListener('click', () => exportResults('csv'));
    }

    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

function updatePlaceholder() {
    const type = searchType.value;
    const placeholders = {
        email: 'Enter an email (example@gmail.com)',
        phone: 'Enter a phone number (+1 202 555 0147)',
        name: 'Enter a full name (John Doe)',
        username: 'Enter a username/handle (@username)',
        domain: 'Enter a domain (example.com)'
    };
    
    searchInput.placeholder = placeholders[type];
    searchInput.value = '';
}

function handleSearch(e) {
    e.preventDefault();
    
    const type = searchType.value;
    const query = searchInput.value.trim();
    
    if (!query) {
        showNotification('Please enter a search query', 'warning');
        return;
    }

    // Show loading state
    showLoading();
    
    // Simulate API call delay
    setTimeout(() => {
        performSearch(type, query);
    }, 1500);
}

function showLoading() {
    resultsSection.style.display = 'block';
    resultsGrid.innerHTML = `
        <div class="loading-container" style="text-align: center; padding: 3rem;">
            <div class="loading"></div>
            <p style="margin-top: 1rem; color: var(--text-secondary);">Searching databases...</p>
        </div>
    `;
}

function performSearch(type, query) {
    // Get mock data or simulate no results
    const data = mockData[type]?.[query] || generateNoResults(query);
    currentSearchData = data;
    
    displayResults(data, query);
}

function generateNoResults(query) {
    return [
        {
            platform: 'Search Complete',
            status: 'not-found',
            details: {
                'Query': query,
                'Databases Searched': '15',
                'Results Found': '0',
                'Search Time': '1.2 seconds'
            }
        }
    ];
}

function displayResults(results, query) {
    if (!results || results.length === 0) {
        resultsGrid.innerHTML = `
            <div class="no-results">
                <h3>No results found</h3>
                <p>Try a different search term or type.</p>
            </div>
        `;
        return;
    }

    resultsGrid.innerHTML = results.map(result => `
        <div class="result-card">
            <div class="result-header">
                <div class="result-platform">
                    <i class="fas fa-database"></i>
                    ${result.platform}
                </div>
                <div class="result-status status-${result.status}">
                    ${formatStatus(result.status)}
                </div>
            </div>
            <div class="result-details">
                ${Object.entries(result.details).map(([key, value]) => `
                    <div class="result-detail">
                        <span class="detail-label">${key}:</span>
                        <span class="detail-value">${value}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function formatStatus(status) {
    const statusMap = {
        found: 'Found',
        breach: 'Breach Detected',
        'not-found': 'Not Found'
    };
    return statusMap[status] || status;
}

function exportResults(format) {
    if (!currentSearchData || currentSearchData.length === 0) {
        showNotification('No data to export', 'warning');
        return;
    }

    if (format === 'csv') {
        exportToCSV();
    } else if (format === 'pdf') {
        exportToPDF();
    }
}

function exportToCSV() {
    const headers = ['Platform', 'Status', 'Details'];
    const rows = currentSearchData.map(result => [
        result.platform,
        formatStatus(result.status),
        Object.entries(result.details).map(([k, v]) => `${k}: ${v}`).join('; ')
    ]);

    const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n');

    downloadFile(csvContent, 'osint-results.csv', 'text/csv');
    showNotification('CSV export completed', 'success');
}

function exportToPDF() {
    // Simple PDF-like text format for demonstration
    const content = currentSearchData.map(result => {
        const details = Object.entries(result.details)
            .map(([k, v]) => `  ${k}: ${v}`)
            .join('\n');
        return `Platform: ${result.platform}\nStatus: ${formatStatus(result.status)}\nDetails:\n${details}\n\n`;
    }).join('');

    const pdfContent = `OSINT Framework Portal - Search Results\n\nGenerated: ${new Date().toLocaleString()}\n\n${content}`;
    
    downloadFile(pdfContent, 'osint-results.txt', 'text/plain');
    showNotification('PDF export completed (as text file)', 'success');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: var(--${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'}-color);
        color: white;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        z-index: 1001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Animate out and remove
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add some interactive enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to cards
    document.addEventListener('mouseover', function(e) {
        if (e.target.closest('.feature-card, .result-card, .about-section')) {
            e.target.closest('.feature-card, .result-card, .about-section').style.transform = 'translateY(-5px)';
        }
    });

    document.addEventListener('mouseout', function(e) {
        if (e.target.closest('.feature-card, .result-card, .about-section')) {
            e.target.closest('.feature-card, .result-card, .about-section').style.transform = 'translateY(0)';
        }
    });
});
