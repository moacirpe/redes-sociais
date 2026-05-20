// Utility Functions for Espaço Laika Website

/**
 * Debounce function to limit the rate of function execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
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

/**
 * Throttle function to limit function calls to once per interval
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Check if element is in viewport
 * @param {Element} element - DOM element to check
 * @param {number} threshold - Visibility threshold (0-1)
 * @returns {boolean} Whether element is visible
 */
function isInViewport(element, threshold = 0) {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    const windowWidth = window.innerWidth || document.documentElement.clientWidth;

    const vertInView = (rect.top <= windowHeight - (threshold * rect.height)) &&
                      (rect.bottom >= threshold * rect.height);
    const horInView = (rect.left <= windowWidth - (threshold * rect.width)) &&
                     (rect.right >= threshold * rect.width);

    return vertInView && horInView;
}

/**
 * Smooth scroll to element
 * @param {Element|string} target - Target element or selector
 * @param {number} offset - Offset from top in pixels
 */
function smoothScrollTo(target, offset = 0) {
    const element = typeof target === 'string' ? document.querySelector(target) : target;
    if (!element) return;

    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        } catch (fallbackErr) {
            document.body.removeChild(textArea);
            return false;
        }
    }
}

/**
 * Format phone number as user types
 * @param {string} value - Phone number value
 * @returns {string} Formatted phone number
 */
function formatPhoneNumber(value) {
    // Remove all non-numeric characters
    const phoneNumber = value.replace(/\D/g, '');

    // Apply Brazilian phone number format
    if (phoneNumber.length <= 2) {
        return phoneNumber;
    } else if (phoneNumber.length <= 6) {
        return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2)}`;
    } else if (phoneNumber.length <= 10) {
        return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2, 6)}-${phoneNumber.slice(6)}`;
    } else {
        return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2, 7)}-${phoneNumber.slice(7, 11)}`;
    }
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Whether email is valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Format currency in Brazilian Real
 * @param {number} value - Numeric value
 * @returns {string} Formatted currency string
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

/**
 * Get URL parameters
 * @param {string} name - Parameter name
 * @returns {string|null} Parameter value or null
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Set URL parameter without page reload
 * @param {string} key - Parameter key
 * @param {string} value - Parameter value
 */
function setUrlParameter(key, value) {
    const url = new URL(window.location);
    url.searchParams.set(key, value);
    window.history.pushState({}, '', url);
}

/**
 * Lazy load images
 * @param {NodeList} images - Images to lazy load
 */
function lazyLoadImages(images) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

/**
 * Create and show toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, error, info, warning)
 * @param {number} duration - Duration in milliseconds
 */
function showToast(message, type = 'info', duration = 3000) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="toast-icon fas ${getToastIcon(type)}"></i>
            <span class="toast-message">${message}</span>
        </div>
        <button class="toast-close" aria-label="Fechar notificação">&times;</button>
    `;

    // Add styles
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: 'Inter', sans-serif;
        animation: slideInFromRight 0.3s ease-out;
    `;

    // Set colors based on type
    const colors = {
        success: '#27ae60',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db'
    };

    toast.style.backgroundColor = colors[type] || colors.info;
    toast.style.color = 'white';

    // Add to page
    document.body.appendChild(toast);

    // Close button functionality
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });

    // Auto remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideOutToRight 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

function getToastIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

/**
 * Detect if user prefers reduced motion
 * @returns {boolean} Whether user prefers reduced motion
 */
function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Get computed CSS custom property value
 * @param {string} property - CSS property name
 * @param {Element} element - Element to get property from (default: document.documentElement)
 * @returns {string} Property value
 */
function getCssCustomProperty(property, element = document.documentElement) {
    return getComputedStyle(element).getPropertyValue(property).trim();
}

/**
 * Set CSS custom property value
 * @param {string} property - CSS property name
 * @param {string} value - Property value
 * @param {Element} element - Element to set property on (default: document.documentElement)
 */
function setCssCustomProperty(property, value, element = document.documentElement) {
    element.style.setProperty(property, value);
}

/**
 * Check if browser supports WebP images
 * @returns {Promise<boolean>} Whether WebP is supported
 */
function supportsWebP() {
    return new Promise(resolve => {
        const webP = new Image();
        webP.onload = webP.onerror = () => {
            resolve(webP.height === 2);
        };
        webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
    });
}

/**
 * Generate random ID
 * @param {number} length - ID length
 * @returns {string} Random ID
 */
function generateId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Deep clone an object
 * @param {any} obj - Object to clone
 * @returns {any} Cloned object
 */
function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (typeof obj === 'object') {
        const clonedObj = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = deepClone(obj[key]);
            }
        }
        return clonedObj;
    }
}

/**
 * Format date in Brazilian Portuguese
 * @param {Date|string} date - Date to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date
 */
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        ...options
    };

    return new Intl.DateTimeFormat('pt-BR', defaultOptions).format(new Date(date));
}

/**
 * Calculate age from birth date
 * @param {Date|string} birthDate - Birth date
 * @returns {number} Age in years
 */
function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }

    return age;
}

/**
 * Capitalize first letter of each word
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
function capitalizeWords(str) {
    return str.replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Truncate text with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}

/**
 * Check if device is mobile
 * @returns {boolean} Whether device is mobile
 */
function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Get browser information
 * @returns {object} Browser info
 */
function getBrowserInfo() {
    const ua = navigator.userAgent;
    let browser = 'Unknown';
    let version = 'Unknown';

    // Detect browser
    if (ua.indexOf('Chrome') > -1) {
        browser = 'Chrome';
        version = ua.match(/Chrome\/(\d+)/)[1];
    } else if (ua.indexOf('Firefox') > -1) {
        browser = 'Firefox';
        version = ua.match(/Firefox\/(\d+)/)[1];
    } else if (ua.indexOf('Safari') > -1) {
        browser = 'Safari';
        version = ua.match(/Safari\/(\d+)/)[1];
    } else if (ua.indexOf('Edge') > -1) {
        browser = 'Edge';
        version = ua.match(/Edge\/(\d+)/)[1];
    }

    return {
        browser,
        version,
        isMobile: isMobile(),
        userAgent: ua
    };
}

// Export functions for module use (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        debounce,
        throttle,
        isInViewport,
        smoothScrollTo,
        copyToClipboard,
        formatPhoneNumber,
        isValidEmail,
        formatCurrency,
        getUrlParameter,
        setUrlParameter,
        lazyLoadImages,
        showToast,
        prefersReducedMotion,
        getCssCustomProperty,
        setCssCustomProperty,
        supportsWebP,
        generateId,
        deepClone,
        formatDate,
        calculateAge,
        capitalizeWords,
        truncateText,
        isMobile,
        getBrowserInfo
    };
}