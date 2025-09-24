// frontend/js/app.js
console.log("TrendTracker app loaded");

// Use localhost for local development, Render URL for production
const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'https://your-render-app-name.onrender.com';

let currentFilters = {};

// DOM Elements
const trendsContainer = document.getElementById('trends-container');
const trendsList = document.getElementById('trends-list');
const loadingMessage = document.getElementById('loading-message');
const refreshBtn = document.getElementById('refreshBtn');
const scrapeBtn = document.getElementById('scrapeBtn');

// Initialize filters
document.addEventListener('DOMContentLoaded', () => {
    new PlatformFilter('filters-container', (filters) => {
        currentFilters.platforms = filters.platforms;
        loadTrends(currentFilters);
    });

    new CategoryFilter('filters-container', (filters) => {
        currentFilters.category = filters.category;
        loadTrends(currentFilters);
    });

    // Load initial trends
    loadTrends();

    // Event listeners
    refreshBtn.addEventListener('click', () => loadTrends(currentFilters));
    scrapeBtn.addEventListener('click', scrapeNewTrends);
});

async function loadTrends(filters = {}) {
    console.log("Loading trends with filters:", filters);

    loadingMessage.style.display = 'block';
    trendsList.innerHTML = ''; // Clear existing trends

    try {
        let queryString = new URLSearchParams(filters).toString();
        if (queryString) queryString = '?' + queryString;

        const response = await fetch(`${API_BASE_URL}/api/trends${queryString}`);
        console.log("API response status:", response.status);

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        const trends = await response.json();
        console.log("Received trends ", trends);

        displayTrends(trends);
    } catch (error) {
        console.error("Error loading trends:", error);
        loadingMessage.textContent = `Error loading trends: ${error.message}`;
        showNotification(`Error loading trends: ${error.message}`, 'error');
    }
}

function displayTrends(trends) {
    console.log(`Displaying ${trends.length} trends`);
    loadingMessage.style.display = 'none';

    if (trends.length === 0) {
        trendsList.innerHTML = '<p>No trends found.</p>';
        return;
    }

    trendsList.innerHTML = trends.map(trend => `
        <div class="trend-card" data-trend-id="${trend.id}" onclick="window.open('${trend.url}', '_blank')">
            <img
                src="${trend.thumbnail_url || 'image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23ddd"/><text x="50" y="55" font-size="40" text-anchor="middle" fill="%23888">▶️</text></svg>'}"
                alt="${trend.title}"
                class="trend-thumbnail"
                onerror="this.src='image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><rect width=\"100\" height=\"100\" fill=\"%23ddd\"/><text x=\"50\" y=\"55\" font-size=\"40\" text-anchor=\"middle\" fill=\"%23888\">❌</text></svg>'; this.onerror=null;"
            >
            <div class="trend-content">
                <h3 class="trend-title">${trend.title}</h3>
                <div class="trend-meta">
                    <span>${trend.author || 'Unknown Author'}</span>
                    <span>${new Date(trend.published_at).toLocaleDateString()}</span>
                </div>
                <div class="trend-stats">
                    <span class="stat">👁️ ${trend.view_count?.toLocaleString() || 'N/A'}</span>
                    <span class="stat">👍 ${trend.like_count?.toLocaleString() || 'N/A'}</span>
                    <span class="stat">💬 ${trend.comment_count?.toLocaleString() || 'N/A'}</span>
                </div>
                <div class="trend-platform-category">
                    <span class="platform-tag">${trend.platform}</span>
                    ${trend.category ? `<span class="category-tag">${trend.category}</span>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

async function scrapeNewTrends() {
    console.log("Scraping new trends...");
    scrapeBtn.disabled = true;
    scrapeBtn.textContent = '🕷️ Scraping...';

    try {
        const configResponse = await fetch(`${API_BASE_URL}/api/config`);
        const config = await configResponse.json();
        const enabledPlatforms = Object.keys(config.platforms).filter(p => config.platforms[p].enabled);

        const response = await fetch(`${API_BASE_URL}/api/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                platforms: enabledPlatforms,
                limit_per_platform: 15 // Adjust as needed
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Scraping failed with status ${response.status}`);
        }

        const result = await response.json();
        console.log("Scrape result:", result);
        showNotification(result.message);

        // Reload trends after scraping
        loadTrends(currentFilters);
    } catch (error) {
        console.error("Error scraping trends:", error);
        showNotification(`Error scraping trends: ${error.message}`, 'error');
    } finally {
        scrapeBtn.disabled = false;
        scrapeBtn.textContent = '🕷️ Scrape New';
    }
}