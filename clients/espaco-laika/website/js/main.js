// Main JavaScript for Espaço Laika Website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initThemeToggle();
    initNavigation();
    initScrollEffects();
    initFormValidation();
    initGallery();
    initAnimations();
    initAccessibility();
    initPerformanceMonitoring();
});

// Theme Toggle Functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');

    if (themeToggle && themeIcon) {
        // Check for saved theme preference or default to light mode
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        updateThemeIcon(currentTheme);

        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);

            // Analytics event
            if (typeof gtag !== 'undefined') {
                gtag('event', 'theme_change', {
                    'event_category': 'engagement',
                    'event_label': newTheme
                });
            }
        });
    }
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Navigation Toggle for Mobile
function initNavigation() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !isExpanded);
            navMenu.classList.toggle('active');
        });

        // Close mobile menu when clicking on a link
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navToggle.setAttribute('aria-expanded', 'false');
                navMenu.classList.remove('active');
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                navToggle.setAttribute('aria-expanded', 'false');
                navMenu.classList.remove('active');
            }
        });
    }
}

// Scroll Effects
function initScrollEffects() {
    const header = document.querySelector('.header');
    const heroStats = document.querySelector('.hero-stats');

    // Header background on scroll
    window.addEventListener('scroll', debounce(function() {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }, 10));

    // Animate stats on scroll
    if (heroStats) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateStats();
                }
            });
        });

        observer.observe(heroStats);
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animate Statistics Numbers
function animateStats() {
    const stats = document.querySelectorAll('.stat-number');

    stats.forEach(stat => {
        const target = parseInt(stat.textContent.replace(/\D/g, ''));
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60fps
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                stat.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                stat.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    });
}

// Form Validation
function initFormValidation() {
    const contactForm = document.getElementById('contactForm');

    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            if (validateForm(this)) {
                submitForm(this);
            }
        });

        // Real-time validation
        const inputs = contactForm.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });

            input.addEventListener('input', debounce(function() {
                clearFieldError(this);
                if (this.value.trim()) {
                    this.closest('.form-group').classList.add('success');
                } else {
                    this.closest('.form-group').classList.remove('success');
                }
            }, 300));
        });
    }
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });

    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Clear previous error
    clearFieldError(field);

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo é obrigatório.';
    }

    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Por favor, insira um email válido.';
        }
    }

    // Phone validation (optional)
    if (field.type === 'tel' && value) {
        const phoneRegex = /^\(?(\d{2})\)?\s?9?\d{4}-?\d{4}$/;
        if (!phoneRegex.test(value.replace(/\D/g, ''))) {
            isValid = false;
            errorMessage = 'Por favor, insira um telefone válido.';
        }
    }

    if (!isValid) {
        showFieldError(field, errorMessage);
    }

    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('error');
    field.style.borderColor = '#e74c3c';

    let errorElement = field.parentNode.querySelector('.error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.style.color = '#e74c3c';
        errorElement.style.fontSize = '0.875rem';
        errorElement.style.marginTop = '0.25rem';
        field.parentNode.appendChild(errorElement);
    }
    errorElement.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('error');
    field.style.borderColor = '';

    const errorElement = field.parentNode.querySelector('.error-message');
    if (errorElement) {
        errorElement.remove();
    }
}

function submitForm(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    const originalText = btnText.textContent;

    // Show loading state
    submitBtn.disabled = true;
    btnText.style.opacity = '0';
    btnLoading.style.display = 'flex';

    // Simulate form submission (replace with actual submission logic)
    setTimeout(() => {
        // Success state
        btnLoading.innerHTML = '<i class="fas fa-check"></i> Mensagem Enviada!';
        submitBtn.style.background = '#27ae60';

        // Reset form
        setTimeout(() => {
            form.reset();
            submitBtn.disabled = false;
            btnText.style.opacity = '1';
            btnLoading.style.display = 'none';
            btnText.textContent = originalText;
            submitBtn.style.background = '';

            // Clear success states
            form.querySelectorAll('.form-group').forEach(group => {
                group.classList.remove('success');
            });
        }, 3000);
    }, 2000);
}

// Gallery Lightbox
function initGallery() {
    const galleryItems = document.querySelectorAll('.galeria-item');

    galleryItems.forEach(item => {
        item.addEventListener('click', function() {
            const img = this.querySelector('img');
            if (img) {
                openLightbox(img.src, img.alt);
            }
        });

        // Keyboard support
        item.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

function openLightbox(src, alt) {
    // Create lightbox elements
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-overlay"></div>
        <div class="lightbox-content">
            <img src="${src}" alt="${alt}">
            <button class="lightbox-close" aria-label="Fechar galeria">&times;</button>
        </div>
    `;

    // Add styles
    lightbox.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    const overlay = lightbox.querySelector('.lightbox-overlay');
    overlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
    `;

    const content = lightbox.querySelector('.lightbox-content');
    content.style.cssText = `
        position: relative;
        max-width: 90vw;
        max-height: 90vh;
        z-index: 10001;
    `;

    const img = lightbox.querySelector('img');
    img.style.cssText = `
        max-width: 100%;
        max-height: 100%;
        border-radius: 10px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    `;

    const closeBtn = lightbox.querySelector('.lightbox-close');
    closeBtn.style.cssText = `
        position: absolute;
        top: -15px;
        right: -15px;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: white;
        color: black;
        border: none;
        font-size: 20px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    // Add event listeners
    overlay.addEventListener('click', () => lightbox.remove());
    closeBtn.addEventListener('click', () => lightbox.remove());

    // Add keyboard support
    document.addEventListener('keydown', function closeOnEscape(e) {
        if (e.key === 'Escape') {
            lightbox.remove();
            document.removeEventListener('keydown', closeOnEscape);
        }
    });

    // Add to page
    document.body.appendChild(lightbox);
}

// Animations on Scroll
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe all sections
    document.querySelectorAll('.section').forEach(section => {
        observer.observe(section);
    });
}

// Accessibility Features
function initAccessibility() {
    // Add main content landmark
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.setAttribute('id', 'main-content');
    }

    // Focus management for mobile menu
    const navToggle = document.getElementById('nav-toggle');
    if (navToggle) {
        navToggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    }

    // Add ARIA labels where needed
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
        const icon = link.querySelector('i');
        if (icon) {
            const platform = icon.className.split(' ')[1].replace('fa-', '');
            link.setAttribute('aria-label', `Visite nosso ${platform}`);
        }
    });
}

// Performance Monitoring
function initPerformanceMonitoring() {
    // Monitor page load time
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Página carregada em ${loadTime.toFixed(2)}ms`);

        // Send to analytics if available
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_load_time', {
                value: Math.round(loadTime)
            });
        }
    });

    // Monitor Core Web Vitals (if available)
    if ('web-vitals' in window) {
        import('https://unpkg.com/web-vitals@3?module')
            .then(({getCLS, getFID, getFCP, getLCP, getTTFB}) => {
                getCLS(console.log);
                getFID(console.log);
                getFCP(console.log);
                getLCP(console.log);
                getTTFB(console.log);
            })
            .catch(() => {
                // Web Vitals not available, skip
            });
    }
}

// Utility Functions
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

// Newsletter subscription (placeholder)
function subscribeNewsletter(email) {
    // Simulate API call
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (email.includes('@')) {
                resolve('Inscrição realizada com sucesso!');
            } else {
                reject('Email inválido');
            }
        }, 1000);
    });
}