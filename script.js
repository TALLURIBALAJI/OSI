// Global variables
let currentSearchData = [];
const API_BASE_URL = 'http://localhost:5000';

// DOM elements
const searchForm = document.getElementById('searchForm');
const searchType = document.getElementById('searchType');
const searchInput = document.getElementById('searchInput');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const exportPDF = document.getElementById('exportPDF');
const exportCSV = document.getElementById('exportCSV');

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }

    if (searchType) {
        searchType.addEventListener('change', updatePlaceholder);
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
});

// Update input placeholder based on search type
function updatePlaceholder() {
    const type = searchType.value;
    const placeholders = {
        email: 'Enter an email (example@gmail.com)',
        phone: 'Enter a phone number (+1 202 555 0147)',
        ip: 'Enter an IP address (192.168.1.1 or 8.8.8.8)',
        name: 'Enter a full name (John Doe)',
        username: 'Enter a username/handle (@username)',
        domain: 'Enter a domain (example.com)'
    };
    
    searchInput.placeholder = placeholders[type];
    searchInput.value = '';
}

// Handle search form submission
async function handleSearch(e) {
    e.preventDefault();
    
    const type = searchType.value;
    const query = searchInput.value.trim();
    
    if (!query) {
        showNotification('Please enter a search query', 'warning');
        return;
    }

    // Show loading state
    showLoadingState();
    
    try {
        const results = await performSearch(type, query);
        displayResults(results, type, query);
        currentSearchData = results;
        showNotification('Search completed successfully!', 'success');
    } catch (error) {
        hideLoadingState();
        showNotification('Search failed: ' + error.message, 'error');
        console.error('Search error:', error);
    }
}

// Perform actual search via Flask API
async function performSearch(type, query) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: type,
                query: query
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Search request failed');
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.results;
        } else {
            throw new Error(data.error || 'Search failed');
        }
        
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Unable to connect to the server. Please ensure the Flask backend is running on http://localhost:5000');
        }
        throw error;
    }
}

// Display search results
function displayResults(results, type, query) {
    hideLoadingState();
    
    if (!results || results.length === 0) {
        resultsGrid.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>No Results Found</h3>
                <p>No information found for "${query}" using ${type} search.</p>
            </div>
        `;
        resultsSection.style.display = 'block';
        return;
    }
    
    resultsGrid.innerHTML = '';
    
    results.forEach((result, index) => {
        const card = createResultCard(result, index);
        resultsGrid.appendChild(card);
    });
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Format values to make URLs clickable
function formatValueWithLinks(value) {
    if (!value || typeof value !== 'string') {
        return value;
    }
    
    // URL detection regex
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    
    // Check if the entire value is a URL
    if (urlRegex.test(value) && value.match(urlRegex)?.[0] === value) {
        return `<a href="${value}" target="_blank" rel="noopener noreferrer" class="result-link">
                    <i class="fas fa-external-link-alt"></i> Visit Link
                </a>`;
    }
    
    // Replace URLs within text with clickable links
    return value.replace(urlRegex, (url) => {
        // Extract domain for display
        try {
            const urlObj = new URL(url);
            const domain = urlObj.hostname.replace('www.', '');
            
            // Special handling for search URLs
            if (url.includes('google.com/search')) {
                const queryParam = urlObj.searchParams.get('q');
                if (queryParam) {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="result-link">
                                <i class="fas fa-search"></i> Search "${queryParam}" on Google
                            </a>`;
                }
            }
            
            if (url.includes('linkedin.com/search')) {
                const keywords = urlObj.searchParams.get('keywords');
                if (keywords) {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="result-link">
                                <i class="fab fa-linkedin"></i> Search "${decodeURIComponent(keywords)}" on LinkedIn
                            </a>`;
                }
            }
            
            if (url.includes('facebook.com/search')) {
                const query = urlObj.searchParams.get('q');
                if (query) {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="result-link">
                                <i class="fab fa-facebook"></i> Search "${decodeURIComponent(query)}" on Facebook
                            </a>`;
                }
            }
            
            if (url.includes('twitter.com/search')) {
                const query = urlObj.searchParams.get('q');
                if (query) {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="result-link">
                                <i class="fab fa-twitter"></i> Search "${query}" on Twitter
                            </a>`;
                }
            }
            
            return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="result-link">
                        <i class="fas fa-external-link-alt"></i> ${domain}
                    </a>`;
        } catch {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="result-link">
                        <i class="fas fa-external-link-alt"></i> Visit Link
                    </a>`;
        }
    });
}

// Create individual result card
function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    const statusClass = getStatusClass(result.status);
    const statusIcon = getStatusIcon(result.status);
    
    let detailsHtml = '';
    if (result.details && Object.keys(result.details).length > 0) {
        detailsHtml = Object.entries(result.details)
            .map(([key, value]) => {
                const formattedValue = formatValueWithLinks(value);
                return `
                    <div class="detail-item">
                        <span class="detail-key">${key}:</span>
                        <span class="detail-value">${formattedValue}</span>
                    </div>
                `;
            }).join('');
    }
    
    card.innerHTML = `
        <div class="result-header">
            <div class="result-title">
                <h3>${result.platform}</h3>
                <span class="result-status ${statusClass}">
                    <i class="${statusIcon}"></i>
                    ${result.status.replace('_', ' ').toUpperCase()}
                </span>
            </div>
        </div>
        <div class="result-details">
            ${detailsHtml || '<p class="no-details">No additional details available</p>'}
        </div>
    `;
    
    return card;
}

// Get CSS class for status
function getStatusClass(status) {
    const statusMap = {
        'found': 'status-found',
        'not_found': 'status-not-found',
        'error': 'status-error',
        'invalid': 'status-error',
        'clean': 'status-clean',
        'compromised': 'status-compromised',
        'breach': 'status-compromised',
        'info': 'status-info',
        'summary': 'status-info',
        'api_key_required': 'status-warning',
        'unknown': 'status-warning'
    };
    
    return statusMap[status] || 'status-unknown';
}

// Get icon for status
function getStatusIcon(status) {
    const iconMap = {
        'found': 'fas fa-check-circle',
        'not_found': 'fas fa-times-circle',
        'error': 'fas fa-exclamation-triangle',
        'invalid': 'fas fa-exclamation-triangle',
        'clean': 'fas fa-shield-alt',
        'compromised': 'fas fa-exclamation-triangle',
        'breach': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle',
        'summary': 'fas fa-list',
        'api_key_required': 'fas fa-key',
        'unknown': 'fas fa-question-circle'
    };
    
    return iconMap[status] || 'fas fa-question';
}

// Show loading state
function showLoadingState() {
    if (resultsGrid) {
        resultsGrid.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <h3>Searching...</h3>
                <p>Gathering information from multiple sources</p>
            </div>
        `;
        resultsSection.style.display = 'block';
    }
}

// Hide loading state
function hideLoadingState() {
    // Loading state will be replaced by actual results
}

// Export results
async function exportResults(format) {
    if (!currentSearchData || currentSearchData.length === 0) {
        showNotification('No data to export', 'warning');
        return;
    }
    
    try {
        const query = searchInput.value.trim();
        
        const response = await fetch(`${API_BASE_URL}/api/export/${format}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                results: currentSearchData,
                query: query
            })
        });
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.statusText}`);
        }
        
        // Create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `osint_report_${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification(`${format.toUpperCase()} export completed!`, 'success');
        
    } catch (error) {
        showNotification(`Export failed: ${error.message}`, 'error');
        console.error('Export error:', error);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    // Set background color based on type
    const colors = {
        'success': '#27ae60',
        'error': '#e74c3c',
        'warning': '#f39c12',
        'info': '#3498db'
    };
    notification.style.backgroundColor = colors[type] || colors['info'];
    
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
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Add hover effects to cards
document.addEventListener('mouseover', function(e) {
    if (e.target.closest('.feature-card, .result-card, .about-section')) {
        const element = e.target.closest('.feature-card, .result-card, .about-section');
        element.style.transform = 'translateY(-5px)';
        element.style.transition = 'transform 0.3s ease';
    }
});

document.addEventListener('mouseout', function(e) {
    if (e.target.closest('.feature-card, .result-card, .about-section')) {
        const element = e.target.closest('.feature-card, .result-card, .about-section');
        element.style.transform = 'translateY(0)';
    }
});

// Utility function for debouncing
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