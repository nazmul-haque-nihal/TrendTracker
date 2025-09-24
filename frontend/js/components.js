// frontend/js/components.js

class PlatformFilter {
    constructor(containerId, onFilterChange) {
        this.container = document.getElementById(containerId);
        this.onFilterChange = onFilterChange;
        this.platforms = [
            { name: 'youtube', label: 'YouTube', enabled: true },
            { name: 'reddit', label: 'Reddit', enabled: true },
            { name: 'twitter', label: 'Twitter', enabled: false },
            { name: 'tiktok', label: 'TikTok', enabled: false },
        ];
        this.selectedPlatforms = this.platforms.filter(p => p.enabled).map(p => p.name);
        this.render();
    }

    render() {
        const html = `
            <div class="filter-section">
                <h3>Filter by Platform</h3>
                <div class="filter-options">
                    ${this.platforms.map(platform => `
                        <label class="filter-option">
                            <input type="checkbox" value="${platform.name}"
                                   ${this.selectedPlatforms.includes(platform.name) ? 'checked' : ''}>
                            <span>${platform.label}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
        this.container.innerHTML = html;

        // Add event listeners
        const checkboxes = this.container.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const platform = e.target.value;
                if (e.target.checked) {
                    if (!this.selectedPlatforms.includes(platform)) {
                        this.selectedPlatforms.push(platform);
                    }
                } else {
                    this.selectedPlatforms = this.selectedPlatforms.filter(p => p !== platform);
                }
                this.onFilterChange({ platforms: this.selectedPlatforms });
            });
        });
    }
}

class CategoryFilter {
    constructor(containerId, onFilterChange) {
        this.container = document.getElementById(containerId);
        this.onFilterChange = onFilterChange;
        // Define your categories
        this.categories = [
            'funny', 'sad', 'emotional', 'anime', 'movie clips',
            'viral music', 'viral dance', 'technology'
        ];
        this.selectedCategory = '';
        this.render();
    }

    render() {
        const html = `
            <div class="filter-section">
                <h3>Filter by Category</h3>
                <div class="filter-options">
                    <label class="filter-option">
                        <input type="radio" name="category" value="" checked>
                        <span>All</span>
                    </label>
                    ${this.categories.map(category => `
                        <label class="filter-option">
                            <input type="radio" name="category" value="${category}">
                            <span>${category.charAt(0).toUpperCase() + category.slice(1)}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `;
        this.container.innerHTML = html;

        // Add event listeners
        const radios = this.container.querySelectorAll('input[name="category"]');
        radios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedCategory = e.target.value;
                    this.onFilterChange({ category: this.selectedCategory });
                }
            });
        });
    }
}

// Utility function for notifications
function showNotification(message, type = 'success') {
    // Remove any existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 1000;
        transform: translateX(120%);
        transition: transform 0.3s ease-out;
        background-color: ${type === 'success' ? '#4caf50' : '#f44336'};
    `;
    document.body.appendChild(notification);

    // Trigger reflow to ensure the transition works
    notification.offsetHeight;
    notification.classList.add('show');

    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}