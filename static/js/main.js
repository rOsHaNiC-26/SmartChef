/**
 * SmartChef - Main JavaScript
 * Handles theme toggle, notifications, user menu, language switching, and mobile navigation
 */

document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    initNotifications();
    initUserMenu();
    initBellIcon();
    initMobileNav();
    initLanguage();
});

// ==================== THEME TOGGLE ====================
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    // Get theme from HTML attribute or localStorage
    let currentTheme = document.documentElement.getAttribute('data-theme') ||
        localStorage.getItem('theme') || 'light';

    // Apply theme
    applyTheme(currentTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyTheme(currentTheme);
            localStorage.setItem('theme', currentTheme);

            // If user is logged in, save to server
            if (document.querySelector('.user-menu')) {
                updateThemeOnServer(currentTheme);
            }
        });
    }
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// updateThemeOnServer is defined later using updateSettingsOnServer

// ==================== NOTIFICATIONS ====================
function initNotifications() {
    // Auto-dismiss notifications after 5 seconds
    const notifications = document.querySelectorAll('.notification[data-auto-dismiss]');
    notifications.forEach(notification => {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    });
}

// Show notification dynamically
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${icons[type]}</span>
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(notification);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100px); }
    }
`;
document.head.appendChild(style);

// ==================== NOTIFICATION BELL ====================
function initBellIcon() {
    const bellBtn = document.getElementById('bellBtn');
    const bellContainer = document.querySelector('.notification-bell-container');

    if (bellBtn && bellContainer) {
        bellBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            // Close other dropdowns
            document.querySelector('.user-menu')?.classList.remove('open');
            bellContainer.classList.toggle('open');
        });
    }
}

// ==================== USER MENU ====================
function initUserMenu() {
    const userBtn = document.getElementById('userBtn');
    const userMenu = document.querySelector('.user-menu');

    if (userBtn && userMenu) {
        userBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            // Close other dropdowns
            document.querySelector('.notification-bell-container')?.classList.remove('open');
            userMenu.classList.toggle('open');
        });

        // Close all dropdowns on click outside
        document.addEventListener('click', function (e) {
            if (userMenu && !userMenu.contains(e.target)) {
                userMenu.classList.remove('open');
            }
            const bellContainer = document.querySelector('.notification-bell-container');
            if (bellContainer && !bellContainer.contains(e.target)) {
                bellContainer.classList.remove('open');
            }
        });
    }
}

// ==================== MOBILE NAVIGATION ====================
function initMobileNav() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('open');
            this.classList.toggle('active');
        });

        // Close on link click
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('open');
                navToggle.classList.remove('active');
            });
        });
    }
}

// ==================== LANGUAGE SWITCHING ====================
function initLanguage() {
    // Get current language from HTML
    const currentLang = document.documentElement.lang || 'en';
    updateLanguage(currentLang);
}

function changeLanguage(lang) {
    updateLanguage(lang);
    localStorage.setItem('language', lang);
    if (document.querySelector('.user-menu')) {
        updateSettingsOnServer({ language: lang });
    }
}

function updateLanguage(lang) {
    // Update all elements with data-en, data-hi, data-mr attributes
    const elements = document.querySelectorAll('[data-' + lang + ']'); // Optimize selector? No, data-en always exists usually
    const allElements = document.querySelectorAll('[data-en]'); // Get all translatable elements

    allElements.forEach(el => {
        const text = el.getAttribute(`data-${lang}`) || el.getAttribute('data-en');
        if (text) {
            el.textContent = text;
        }
    });

    // Update HTML lang attribute
    document.documentElement.lang = lang;
}

// ==================== SHARE APP ====================
function shareApp() {
    if (navigator.share) {
        navigator.share({
            title: 'SmartChef',
            text: 'Check out SmartChef - Cook, Share, Inspire!',
            url: window.location.origin
        }).catch(console.error);
    } else {
        copyToClipboard(window.location.origin);
        showNotification('App link copied to clipboard!', 'success');
    }
}

// ==================== SETTINGS UPDATER ====================
function updateSettingsOnServer(data) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    // Helper to get CSRF token from cookie if not in DOM
    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const token = csrfToken || getCookie('csrftoken');

    if (!token) return;

    const formData = new URLSearchParams();
    for (const key in data) {
        formData.append(key, data[key]);
    }
    formData.append('csrfmiddlewaretoken', token);

    fetch('/settings/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
            }
        })
        .catch(err => console.log('Settings update failed:', err));
}

// Update existing theme toggler to use new generic function
function updateThemeOnServer(theme) {
    updateSettingsOnServer({ theme: theme });
}

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

// Format number with K/M suffix
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Smooth scroll to element
function scrollToElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy', 'error');
    }
}

// ==================== RECIPE INTERACTIONS ====================

// Like button handler
document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        this.classList.toggle('liked');
        const icon = this.querySelector('i');
        if (icon) {
            icon.classList.toggle('fas');
            icon.classList.toggle('far');
        }
    });
});

// Ingredient checkbox animation
document.querySelectorAll('.ingredient-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function () {
        const item = this.closest('.ingredient-item');
        if (item) {
            item.classList.toggle('checked', this.checked);
        }
    });
});

// Print recipe
function printRecipe() {
    window.print();
}

// Share recipe
async function shareRecipe(title, url) {
    if (navigator.share) {
        try {
            await navigator.share({
                title: title,
                text: 'Check out this delicious recipe on SmartChef!',
                url: url || window.location.href
            });
        } catch (err) {
            if (err.name !== 'AbortError') {
                copyToClipboard(url || window.location.href);
            }
        }
    } else {
        copyToClipboard(url || window.location.href);
    }
}

// ==================== FORM ENHANCEMENTS ====================

// Auto-resize textarea
document.querySelectorAll('textarea').forEach(textarea => {
    textarea.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
});

// Image preview for file input
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (input.files && input.files[0] && preview) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Password matching validation
const regForm = document.querySelector('form[action*="register"]');
if (!regForm) {
    // Check if it's the current register page (might not have action set)
    if (window.location.pathname.includes('register')) {
        const password = document.getElementById('password');
        const confirm = document.getElementById('confirm_password');

        if (password && confirm) {
            const validatePass = () => {
                if (confirm.value === '') {
                    confirm.style.borderColor = '';
                } else if (password.value === confirm.value) {
                    confirm.style.borderColor = 'var(--success)';
                } else {
                    confirm.style.borderColor = 'var(--error)';
                }
            };

            password.addEventListener('input', validatePass);
            confirm.addEventListener('input', validatePass);
        }
    }
}

// ==================== SEARCH FUNCTIONALITY ====================

// Live search with debounce
const searchInput = document.querySelector('.search-input');
if (searchInput) {
    const debouncedSearch = debounce(function (value) {
        // Only submit if value has changed significantly
        if (value.length >= 2 || value.length === 0) {
            // Could add AJAX search here
            console.log('Searching for:', value);
        }
    }, 500);

    searchInput.addEventListener('input', function () {
        debouncedSearch(this.value);
    });
}

// ==================== LAZY LOADING IMAGES ====================

// Simple lazy loading for recipe images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
                observer.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// ==================== ACCESSIBILITY ====================

// Keyboard navigation for user menu
document.addEventListener('keydown', function (e) {
    // Close menus on Escape
    if (e.key === 'Escape') {
        document.querySelector('.user-menu')?.classList.remove('open');
        document.getElementById('navMenu')?.classList.remove('open');
    }
});

// Focus trap for modal-like elements
function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    element.addEventListener('keydown', function (e) {
        if (e.key === 'Tab') {
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    });
}

console.log('🍳 SmartChef loaded successfully!');
