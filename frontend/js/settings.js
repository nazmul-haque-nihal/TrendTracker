// frontend/js/settings.js
console.log("Settings page loaded");

// Use localhost for local development, Render API URL for production
// Replace 'https://trendtracker-046o.onrender.com' with YOUR actual Render API URL
const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'https://trendtracker-046o.onrender.com';

// DOM Elements
const platformConfigContainer = document.getElementById('platform-config');
const apiKeysForm = document.getElementById('api-keys-form');
const testYouTubeBtn = document.getElementById('test-youtube-btn');
const testRedditBtn = document.getElementById('test-reddit-btn');

// Load initial configuration
document.addEventListener('DOMContentLoaded', loadConfiguration);

async function loadConfiguration() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/config`);
        const config = await response.json();

        displayPlatformConfig(config.platforms);
        // Note: API keys are usually not returned by the backend for security
        // You would need a separate endpoint to get masked keys or manage them locally
        // For now, we'll leave the input fields empty
    } catch (error) {
        console.error("Error loading configuration:", error);
        showNotification("Error loading configuration.", 'error');
    }
}

function displayPlatformConfig(platforms) {
    let html = '<div class="platform-options">';
    for (const [platformName, platformConfig] of Object.entries(platforms)) {
        html += `
            <div class="platform-option">
                <label>
                    <input type="checkbox"
                           id="platform-${platformName}"
                           name="platforms"
                           value="${platformName}"
                           ${platformConfig.enabled ? 'checked' : ''}>
                    ${platformName.charAt(0).toUpperCase() + platformName.slice(1)}
                </label>
            </div>
        `;
    }
    html += '</div>';
    platformConfigContainer.innerHTML = html;
}

apiKeysForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(apiKeysForm);
    const configData = Object.fromEntries(formData.entries());

    // In a real app, you would send this data to a backend endpoint
    // that can securely store it (e.g., in environment variables or a secure database)
    // For this example, we'll just show a notification
    console.log("Saving configuration:", configData);

    // Simulate saving (replace with actual API call)
    try {
        // Example API call (you need to implement this endpoint)
        /*
        const response = await fetch(`${API_BASE_URL}/api/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(configData)
        });

        if (!response.ok) {
            throw new Error('Failed to save configuration');
        }
        */

        showNotification("Configuration saved successfully!");
        // Reload configuration to reflect changes
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    } catch (error) {
        console.error("Error saving configuration:", error);
        showNotification("Error saving configuration.", 'error');
    }
});

// Test API Connection Buttons
testYouTubeBtn.addEventListener('click', async () => {
    console.log("Testing YouTube API connection...");
    try {
        const response = await fetch(`${API_BASE_URL}/api/config/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ platform: 'youtube' })
        });

        const data = await response.json();
        if (response.ok) {
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        console.error("Error testing YouTube API:", error);
        showNotification(`Error testing YouTube API: ${error.message}`, 'error');
    }
});

testRedditBtn.addEventListener('click', async () => {
    console.log("Testing Reddit API connection...");
    try {
        const response = await fetch(`${API_BASE_URL}/api/config/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ platform: 'reddit' })
        });

        const data = await response.json();
        if (response.ok) {
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error, 'error');
        }
    } catch (error) {
        console.error("Error testing Reddit API:", error);
        showNotification(`Error testing Reddit API: ${error.message}`, 'error');
    }
});

// Re-use the showNotification function from components.js or define it here
function showNotification(message, type = 'success') {
    // Simple notification for settings page
    alert(`${type.toUpperCase()}: ${message}`);
    // Or implement a more sophisticated notification system similar to app.js
}