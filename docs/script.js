/**
 * CODEYWOOD Documentation Site
 * Pixel art aesthetic with parallax scrolling
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components
    initStarfield();
    initBackgroundDarken();
    initNavigation();
    initScrollAnimations();
    initTypewriter();
});

/**
 * Starfield Background
 * Creates twinkling stars in the background
 */
function initStarfield() {
    const starfield = document.getElementById('starfield');
    if (!starfield) return;

    const starCount = 150;

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.className = 'star';

        // Random position
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;

        // Random size (1-3px)
        const size = Math.random() * 2 + 1;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;

        // Random twinkle timing
        star.style.setProperty('--twinkle-duration', `${Math.random() * 3 + 2}s`);
        star.style.setProperty('--star-opacity', `${Math.random() * 0.5 + 0.2}`);
        star.style.animationDelay = `${Math.random() * 3}s`;

        starfield.appendChild(star);
    }
}

/**
 * Background Darkening on Scroll
 * Fades the background image to dark as user scrolls past hero
 */
function initBackgroundDarken() {
    const overlay = document.getElementById('hero-bg-overlay');
    const hero = document.getElementById('hero');
    if (!overlay || !hero) return;

    let ticking = false;

    function updateOverlay() {
        const scrollY = window.pageYOffset;
        const heroHeight = hero.offsetHeight;

        // Calculate opacity: 0 at top, max 0.5 when scrolled past hero
        // This dims the background but keeps it visible through transparent sections
        const startDarken = heroHeight * 0.3;
        const endDarken = heroHeight;
        const maxDarkness = 0.5; // Only darken to 50%

        let opacity = 0;
        if (scrollY > startDarken) {
            opacity = Math.min((scrollY - startDarken) / (endDarken - startDarken), 1) * maxDarkness;
        }

        overlay.style.opacity = opacity;
        ticking = false;
    }

    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(updateOverlay);
            ticking = true;
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });

    // Initial update
    updateOverlay();
}

/**
 * Navigation
 * Handles mobile menu and scroll-based visibility
 */
function initNavigation() {
    const nav = document.querySelector('.pixel-nav');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (!nav) return;

    // Mobile menu toggle
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });

        // Close menu when clicking a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                mobileMenuBtn.classList.remove('active');
            });
        });
    }

    // Hide/show nav on scroll
    let lastScrollY = 0;
    let ticking = false;

    function updateNav() {
        const currentScrollY = window.pageYOffset;

        if (currentScrollY > lastScrollY && currentScrollY > 100) {
            // Scrolling down - hide nav
            nav.classList.add('hidden');
        } else {
            // Scrolling up - show nav
            nav.classList.remove('hidden');
        }

        lastScrollY = currentScrollY;
        ticking = false;
    }

    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(updateNav);
            ticking = true;
        }
    }, { passive: true });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const navHeight = nav.offsetHeight;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Scroll Animations
 * Simple AOS-like reveal animations
 */
function initScrollAnimations() {
    const elements = document.querySelectorAll('[data-aos]');
    if (elements.length === 0) return;

    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -10% 0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add delay if specified
                const delay = entry.target.dataset.aosDelay || 0;
                setTimeout(() => {
                    entry.target.classList.add('aos-animate');
                }, delay);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    elements.forEach(element => observer.observe(element));

    // Also animate section titles as they come into view
    const sectionTitles = document.querySelectorAll('.section-title');
    const titleObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                titleObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    sectionTitles.forEach(title => titleObserver.observe(title));
}

/**
 * Typewriter Effect
 * Re-triggers typewriter animation on scroll into view
 */
function initTypewriter() {
    const typewriter = document.querySelector('.typewriter');
    if (!typewriter) return;

    // The CSS handles the initial animation
    // This could be extended to re-trigger or add more complex typing effects
}

/**
 * Utility: Debounce function
 */
function debounce(func, wait = 10, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}

/**
 * Utility: Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Add CSS animation keyframes dynamically
 */
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pixelFadeIn {
        0% {
            opacity: 0;
            filter: blur(4px);
        }
        50% {
            opacity: 0.5;
            filter: blur(2px);
        }
        100% {
            opacity: 1;
            filter: blur(0);
        }
    }
`;
document.head.appendChild(styleSheet);

/**
 * Console Easter Egg
 */
console.log(`
%c ██████╗ ██████╗ ██████╗ ███████╗██╗   ██╗██╗    ██╗ ██████╗  ██████╗ ██████╗
%c██╔════╝██╔═══██╗██╔══██╗██╔════╝╚██╗ ██╔╝██║    ██║██╔═══██╗██╔═══██╗██╔══██╗
%c██║     ██║   ██║██║  ██║█████╗   ╚████╔╝ ██║ █╗ ██║██║   ██║██║   ██║██║  ██║
%c██║     ██║   ██║██║  ██║██╔══╝    ╚██╔╝  ██║███╗██║██║   ██║██║   ██║██║  ██║
%c╚██████╗╚██████╔╝██████╔╝███████╗   ██║   ╚███╔███╔╝╚██████╔╝╚██████╔╝██████╔╝
%c ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝    ╚══╝╚══╝  ╚═════╝  ╚═════╝ ╚═════╝

%cAI Video Story Generation System
%cBuilt with Claude Code

%cWant to contribute? https://github.com/kaigani/codeywood
`,
'color: #f4d03f',
'color: #f4d03f',
'color: #f4d03f',
'color: #c9a81f',
'color: #c9a81f',
'color: #c9a81f',
'color: #4ecdc4; font-size: 14px; font-weight: bold',
'color: #a0a0c0; font-size: 12px',
'color: #606080; font-size: 11px'
);
