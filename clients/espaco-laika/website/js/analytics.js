// Analytics and Tracking Configuration

class AnalyticsController {
    constructor() {
        this.init();
    }

    init() {
        this.setupGoogleAnalytics();
        this.setupPerformanceMonitoring();
        this.setupUserTracking();
        this.setupEventTracking();
        this.setupErrorTracking();
    }

    // Google Analytics 4 Setup
    setupGoogleAnalytics() {
        // GA4 is loaded in the HTML, this handles additional configuration
        if (typeof gtag !== 'undefined') {
            // Set custom dimensions
            gtag('config', 'GA_MEASUREMENT_ID', {
                'custom_map': {
                    'dimension1': 'user_type',
                    'dimension2': 'page_theme',
                    'dimension3': 'device_type'
                },
                'send_page_view': true
            });

            // Track PWA installs
            window.addEventListener('appinstalled', () => {
                gtag('event', 'pwa_install', {
                    'event_category': 'engagement',
                    'event_label': 'pwa_install'
                });
            });
        }
    }

    // Performance Monitoring
    setupPerformanceMonitoring() {
        // Core Web Vitals tracking
        this.trackCoreWebVitals();

        // Page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                this.trackPagePerformance();
            }, 0);
        });

        // Resource loading tracking
        this.trackResourceLoading();
    }

    // Track Core Web Vitals
    trackCoreWebVitals() {
        // Use web-vitals library if available
        if ('web-vitals' in window) {
            import('https://unpkg.com/web-vitals@3?module')
                .then(({getCLS, getFID, getFCP, getLCP, getTTFB}) => {
                    getCLS(metric => this.sendToAnalytics('web_vitals', metric));
                    getFID(metric => this.sendToAnalytics('web_vitals', metric));
                    getFCP(metric => this.sendToAnalytics('web_vitals', metric));
                    getLCP(metric => this.sendToAnalytics('web_vitals', metric));
                    getTTFB(metric => this.sendToAnalytics('web_vitals', metric));
                })
                .catch(() => {
                    // Fallback: manual Core Web Vitals tracking
                    this.manualCoreWebVitalsTracking();
                });
        } else {
            this.manualCoreWebVitalsTracking();
        }
    }

    // Manual Core Web Vitals tracking (fallback)
    manualCoreWebVitalsTracking() {
        // LCP (Largest Contentful Paint)
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            this.sendToAnalytics('web_vitals', {
                name: 'LCP',
                value: lastEntry.startTime,
                id: 'v3-' + Date.now() + '-' + Math.floor(Math.random() * 1000)
            });
        }).observe({entryTypes: ['largest-contentful-paint']});

        // FID (First Input Delay)
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                this.sendToAnalytics('web_vitals', {
                    name: 'FID',
                    value: entry.processingStart - entry.startTime,
                    id: 'v3-' + Date.now() + '-' + Math.floor(Math.random() * 1000)
                });
            }
        }).observe({entryTypes: ['first-input']});

        // CLS (Cumulative Layout Shift)
        let clsValue = 0;
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                }
            }
        }).observe({entryTypes: ['layout-shift']});

        // Send CLS on page hide
        window.addEventListener('pagehide', () => {
            this.sendToAnalytics('web_vitals', {
                name: 'CLS',
                value: clsValue,
                id: 'v3-' + Date.now() + '-' + Math.floor(Math.random() * 1000)
            });
        });
    }

    // Track page performance metrics
    trackPagePerformance() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const paint = performance.getEntriesByType('paint');

        if (navigation) {
            const metrics = {
                'page_load_time': navigation.loadEventEnd - navigation.fetchStart,
                'dom_content_loaded': navigation.domContentLoadedEventEnd - navigation.fetchStart,
                'first_paint': paint.find(entry => entry.name === 'first-paint')?.startTime || 0,
                'first_contentful_paint': paint.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
            };

            Object.entries(metrics).forEach(([name, value]) => {
                if (value > 0) {
                    this.sendToAnalytics('performance', { name, value });
                }
            });
        }
    }

    // Track resource loading
    trackResourceLoading() {
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.duration > 1000) { // Only track slow resources
                    this.sendToAnalytics('resource_timing', {
                        name: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize,
                        type: entry.initiatorType
                    });
                }
            }
        }).observe({entryTypes: ['resource']});
    }

    // User tracking and behavior
    setupUserTracking() {
        // Track user engagement
        this.trackUserEngagement();

        // Track scroll depth
        this.trackScrollDepth();

        // Track time on page
        this.trackTimeOnPage();

        // Track user preferences
        this.trackUserPreferences();
    }

    // Track user engagement
    trackUserEngagement() {
        let engagementStartTime = Date.now();
        let hasEngaged = false;

        const engagementEvents = ['click', 'scroll', 'keydown', 'touchstart'];

        engagementEvents.forEach(event => {
            document.addEventListener(event, () => {
                if (!hasEngaged) {
                    hasEngaged = true;
                    const timeToEngage = Date.now() - engagementStartTime;
                    this.sendToAnalytics('engagement', {
                        action: 'first_engagement',
                        time_to_engage: timeToEngage
                    });
                }
            }, { once: true });
        });
    }

    // Track scroll depth
    trackScrollDepth() {
        const scrollDepths = [25, 50, 75, 90, 100];
        let maxScrollDepth = 0;

        window.addEventListener('scroll', debounce(() => {
            const scrollTop = window.pageYOffset;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = Math.round((scrollTop / docHeight) * 100);

            scrollDepths.forEach(depth => {
                if (scrollPercent >= depth && maxScrollDepth < depth) {
                    maxScrollDepth = depth;
                    this.sendToAnalytics('engagement', {
                        action: 'scroll_depth',
                        depth: depth
                    });
                }
            });
        }, 100));
    }

    // Track time on page
    trackTimeOnPage() {
        let startTime = Date.now();
        let timeSpent = 0;

        const trackInterval = setInterval(() => {
            timeSpent = Math.floor((Date.now() - startTime) / 1000);
        }, 1000);

        // Send time on page when user leaves
        const sendTimeOnPage = () => {
            clearInterval(trackInterval);
            if (timeSpent > 0) {
                this.sendToAnalytics('engagement', {
                    action: 'time_on_page',
                    time_spent: timeSpent
                });
            }
        };

        window.addEventListener('beforeunload', sendTimeOnPage);
        window.addEventListener('pagehide', sendTimeOnPage);

        // Also track when user becomes hidden (tab switch, minimize)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                sendTimeOnPage();
            } else {
                startTime = Date.now(); // Reset timer when user returns
            }
        });
    }

    // Track user preferences
    trackUserPreferences() {
        // Track theme preference
        const theme = localStorage.getItem('theme') || 'light';
        this.sendToAnalytics('preference', {
            type: 'theme',
            value: theme
        });

        // Track language
        this.sendToAnalytics('preference', {
            type: 'language',
            value: navigator.language
        });

        // Track screen size
        this.sendToAnalytics('technical', {
            screen_width: screen.width,
            screen_height: screen.height,
            viewport_width: window.innerWidth,
            viewport_height: window.innerHeight
        });
    }

    // Event tracking
    setupEventTracking() {
        // Track button clicks
        document.addEventListener('click', (e) => {
            const button = e.target.closest('button, .btn, [role="button"]');
            if (button) {
                this.trackButtonClick(button, e);
            }
        });

        // Track form submissions
        document.addEventListener('submit', (e) => {
            this.trackFormSubmission(e.target);
        });

        // Track link clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link && link.href) {
                this.trackLinkClick(link, e);
            }
        });

        // Track social media interactions
        this.trackSocialInteractions();
    }

    // Track button clicks
    trackButtonClick(button, event) {
        const buttonText = button.textContent?.trim() || button.getAttribute('aria-label') || 'Unknown';
        const buttonId = button.id || button.className;

        this.sendToAnalytics('interaction', {
            type: 'button_click',
            button_text: buttonText,
            button_id: buttonId,
            page_location: window.location.pathname
        });
    }

    // Track form submissions
    trackFormSubmission(form) {
        const formId = form.id || form.className || 'unknown_form';

        this.sendToAnalytics('interaction', {
            type: 'form_submission',
            form_id: formId,
            page_location: window.location.pathname
        });
    }

    // Track link clicks
    trackLinkClick(link, event) {
        const linkText = link.textContent?.trim() || link.getAttribute('aria-label') || 'Unknown';
        const href = link.href;
        const isExternal = href && !href.startsWith(window.location.origin);

        this.sendToAnalytics('interaction', {
            type: 'link_click',
            link_text: linkText,
            href: href,
            is_external: isExternal,
            page_location: window.location.pathname
        });
    }

    // Track social media interactions
    trackSocialInteractions() {
        const socialLinks = document.querySelectorAll('.social-link, a[href*="instagram"], a[href*="facebook"], a[href*="twitter"], a[href*="tiktok"], a[href*="youtube"]');

        socialLinks.forEach(link => {
            link.addEventListener('click', () => {
                const platform = this.getSocialPlatform(link.href);
                this.sendToAnalytics('social', {
                    platform: platform,
                    action: 'click',
                    page_location: window.location.pathname
                });
            });
        });
    }

    // Get social platform from URL
    getSocialPlatform(url) {
        if (url.includes('instagram')) return 'instagram';
        if (url.includes('facebook')) return 'facebook';
        if (url.includes('twitter') || url.includes('x.com')) return 'twitter';
        if (url.includes('tiktok')) return 'tiktok';
        if (url.includes('youtube')) return 'youtube';
        if (url.includes('linkedin')) return 'linkedin';
        return 'unknown';
    }

    // Error tracking
    setupErrorTracking() {
        // JavaScript errors
        window.addEventListener('error', (event) => {
            this.trackJavaScriptError(event.error, event.message, event.filename, event.lineno, event.colno);
        });

        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.trackUnhandledRejection(event.reason);
        });

        // Network errors
        window.addEventListener('offline', () => {
            this.sendToAnalytics('error', {
                type: 'network',
                message: 'User went offline'
            });
        });
    }

    // Track JavaScript errors
    trackJavaScriptError(error, message, filename, lineno, colno) {
        this.sendToAnalytics('error', {
            type: 'javascript',
            message: message,
            filename: filename,
            line: lineno,
            column: colno,
            stack: error?.stack,
            user_agent: navigator.userAgent
        });
    }

    // Track unhandled promise rejections
    trackUnhandledRejection(reason) {
        this.sendToAnalytics('error', {
            type: 'promise_rejection',
            reason: reason?.toString(),
            stack: reason?.stack,
            user_agent: navigator.userAgent
        });
    }

    // Send data to analytics
    sendToAnalytics(category, data) {
        // Google Analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', category, {
                ...data,
                event_category: category,
                non_interaction: data.non_interaction || false
            });
        }

        // Custom analytics endpoint (optional)
        if (window.ANALYTICS_ENDPOINT) {
            fetch(window.ANALYTICS_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    category,
                    data,
                    timestamp: new Date().toISOString(),
                    url: window.location.href,
                    userAgent: navigator.userAgent
                })
            }).catch(() => {
                // Silently fail if analytics endpoint is unavailable
            });
        }

        // Console logging in development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log(`[Analytics] ${category}:`, data);
        }
    }

    // Privacy and consent management
    setupPrivacyControls() {
        // Check for cookie consent
        this.checkCookieConsent();

        // Setup consent management
        this.setupConsentManagement();
    }

    // Check cookie consent
    checkCookieConsent() {
        const consent = localStorage.getItem('cookie_consent');
        if (!consent) {
            this.showCookieConsentBanner();
        }
    }

    // Show cookie consent banner
    showCookieConsentBanner() {
        const banner = document.createElement('div');
        banner.className = 'cookie-consent-banner';
        banner.innerHTML = `
            <div class="cookie-consent-content">
                <p>Utilizamos cookies para melhorar sua experiência. Ao continuar navegando, você concorda com nossa <a href="/privacidade">Política de Privacidade</a>.</p>
                <div class="cookie-consent-actions">
                    <button class="btn btn-sm btn-outline" onclick="this.closest('.cookie-consent-banner').remove()">Recusar</button>
                    <button class="btn btn-sm btn-primary" onclick="analyticsController.acceptCookies()">Aceitar</button>
                </div>
            </div>
        `;

        banner.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--bg-color);
            border-top: 1px solid var(--border-color);
            padding: 16px;
            z-index: 10000;
            box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
        `;

        document.body.appendChild(banner);
    }

    // Accept cookies
    acceptCookies() {
        localStorage.setItem('cookie_consent', 'accepted');
        document.querySelector('.cookie-consent-banner')?.remove();

        // Enable analytics
        this.sendToAnalytics('consent', {
            action: 'accept_cookies',
            non_interaction: true
        });
    }

    // Setup consent management
    setupConsentManagement() {
        // Listen for consent changes
        window.addEventListener('consent_changed', (event) => {
            const consent = event.detail;
            if (consent.analytics) {
                // Re-enable analytics
                this.init();
            }
        });
    }
}

// Initialize analytics when DOM is ready
let analyticsController;
document.addEventListener('DOMContentLoaded', () => {
    analyticsController = new AnalyticsController();
});

// Export for global access
window.AnalyticsController = AnalyticsController;
window.analyticsController = analyticsController;