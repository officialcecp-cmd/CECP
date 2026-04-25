// CHANGELOG: Added initAboutPage() for IntersectionObserver counter animations, and hash-based URL routing on DOMContentLoaded.
// =============================================================================
// CECP Club Website — Main JavaScript (Tab-Based Navigation)
// =============================================================================
// Handles: tab switching, mobile menu, scroll animations within tabs.
// =============================================================================

// =========================================================================
// 1. TAB NAVIGATION — Core Tab Switching Logic
// =========================================================================

/**
 * Switches the active tab. Hides all tab content, shows the selected one,
 * and updates the active state on navbar links.
 * @param {string} tabName - The tab identifier (home, about, initiatives, projects, team)
 */
function switchTab(tabName) {
    // Prevent default link behavior
    event && event.preventDefault && event.preventDefault();

    // --- Hide all tab content ---
    const allTabs = document.querySelectorAll('.tab-content');
    allTabs.forEach(tab => {
        tab.classList.remove('active-tab');
    });

    // --- Show the selected tab ---
    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) {
        targetTab.classList.add('active-tab');
        // Scroll the tab content to top
        targetTab.scrollTop = 0;
    }

    // --- Update navbar active states ---
    const allLinks = document.querySelectorAll('.tab-link');
    allLinks.forEach(link => {
        link.classList.remove('active');
        if (link.dataset.tab === tabName) {
            link.classList.add('active');
        }
    });

    // --- Update URL hash ---
    if (history.replaceState) {
        history.replaceState(null, null, `#${tabName}`);
    }

    // --- Close mobile menu if open ---
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');
    if (hamburger && mobileMenu) {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
    }

    // --- Re-trigger scroll animations for the new tab ---
    setTimeout(() => {
        initScrollAnimations(targetTab);
    }, 100);
}


// =========================================================================
// 2. SCROLL ANIMATIONS (Intersection Observer) — Per Tab
// =========================================================================

function initScrollAnimations(container) {
    if (!container) return;

    const elements = container.querySelectorAll('.animate-on-scroll');
    
    const observerOptions = {
        root: container.classList.contains('tab-content') ? container : null,
        rootMargin: '0px 0px -60px 0px',
        threshold: 0.1,
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    elements.forEach(el => observer.observe(el));
}


// =========================================================================
// 3. DOM READY — Initialize Everything
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {

    // --- Check URL Hash for direct navigation ---
    const hash = window.location.hash.substring(1);
    if (hash && document.getElementById(`tab-${hash}`)) {
        switchTab(hash);
    } else {
        // --- Initialize scroll animations for the home tab ---
        const homeTab = document.getElementById('tab-home');
        if (homeTab) {
            initScrollAnimations(homeTab);
        }
    }

    // --- Initialize specific logic for About Page ---
    initAboutPage();

    // --- Mobile Menu Toggle ---
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');

    if (hamburger && mobileMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            document.body.style.overflow = mobileMenu.classList.contains('active') 
                ? 'hidden' 
                : '';
        });
    }

    // --- Console Easter Egg ---
    console.log(
        '%c⚡ CECP — Centre for Electronics & Coding Projects',
        'color: #06b6d4; font-size: 16px; font-weight: bold;'
    );
    console.log(
        '%cRoorkee Institute of Technology | Electronics Club',
        'color: #94a3b8; font-size: 12px;'
    );
});

// =========================================================================
// 4. ABOUT PAGE SPECIFIC LOGIC
// =========================================================================

let aboutInitialized = false;

function initAboutPage() {
    if (aboutInitialized) return;
    aboutInitialized = true;

    // Intersection Observer for .animate-in
    const observerOptions = { root: null, rootMargin: '0px', threshold: 0.1 };
    const elementsToAnimate = document.querySelectorAll('.animate-in');
    
    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Check if it has a stat counter
                const counters = entry.target.querySelectorAll('.counter');
                counters.forEach(counter => {
                    animateCounter(counter);
                });
                obs.unobserve(entry.target);
            }
        });
    }, observerOptions);

    elementsToAnimate.forEach(el => observer.observe(el));
    
    function animateCounter(counterElement) {
        const target = +counterElement.getAttribute('data-target');
        const duration = 2000; // 2 seconds
        let startTime = null;
        
        function updateCount(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            
            // easeOutQuart
            const easeProgress = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(easeProgress * target);
            
            counterElement.innerText = current;
            
            if (progress < 1) {
                requestAnimationFrame(updateCount);
            } else {
                counterElement.innerText = target;
            }
        }
        requestAnimationFrame(updateCount);
    }
}


// =========================================================================
// 5. PROJECT FILTERING — Cyberpunk Command Bar
// =========================================================================

/**
 * Filters project cards by level (Beginner, Intermediate, Pro)
 * or by category slug (cat-iot, cat-robotics, etc.).
 * Works with both .project-showcase-card and .holo-card selectors.
 */
function filterProjects(filterValue) {
    // Update active state on filter buttons (both old and new)
    const buttons = document.querySelectorAll('.project-filter-btn, .filter-chip');
    buttons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filterValue);
    });

    // Get all project cards (both old and new class names)
    const cards = document.querySelectorAll('.project-showcase-card, .holo-card');

    cards.forEach(card => {
        const level = card.dataset.level;
        const category = card.dataset.category;
        let show = false;

        if (filterValue === 'all') {
            show = true;
        } else if (filterValue.startsWith('cat-')) {
            show = category === filterValue;
        } else {
            show = level === filterValue;
        }

        if (show) {
            card.style.display = '';
            card.classList.remove('filtered-out');
            card.classList.add('filtered-in');
        } else {
            card.classList.remove('filtered-in');
            card.classList.add('filtered-out');
            setTimeout(() => {
                if (card.classList.contains('filtered-out')) {
                    card.style.display = 'none';
                }
            }, 400);
        }
    });

    // Show/hide section headers based on whether they have visible cards
    setTimeout(() => {
        ['completed-grid', 'ongoing-grid'].forEach(gridId => {
            const grid = document.getElementById(gridId);
            if (!grid) return;
            const visibleCards = grid.querySelectorAll('.project-showcase-card:not(.filtered-out), .holo-card:not(.filtered-out)');
            const section = grid.closest('#completed-section, #ongoing-section');
            if (section) {
                section.style.display = visibleCards.length > 0 ? '' : 'none';
            }
        });
    }, 450);
}


// =========================================================================
// 6. CYBERPUNK PARTICLE CANVAS — Projects Section Background
// =========================================================================

function initProjectsParticles() {
    const canvas = document.getElementById('projectsParticleCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;
    const MAX_PARTICLES = 60;

    function resize() {
        const container = canvas.parentElement;
        if (!container) return;
        canvas.width = container.offsetWidth;
        canvas.height = container.offsetHeight;
    }

    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.3,
            radius: Math.random() * 1.5 + 0.5,
            opacity: Math.random() * 0.4 + 0.1,
            color: Math.random() > 0.5 ? '6, 182, 212' : '99, 102, 241'
        };
    }

    function init() {
        resize();
        particles = [];
        for (let i = 0; i < MAX_PARTICLES; i++) {
            particles.push(createParticle());
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw connecting lines
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 150) {
                    const opacity = (1 - dist / 150) * 0.08;
                    ctx.strokeStyle = `rgba(6, 182, 212, ${opacity})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }

        // Draw particles
        particles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${p.color}, ${p.opacity})`;
            ctx.fill();

            // Move
            p.x += p.vx;
            p.y += p.vy;

            // Bounce
            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        });

        animationId = requestAnimationFrame(draw);
    }

    // Only run when visible
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                if (!animationId) draw();
            } else {
                if (animationId) {
                    cancelAnimationFrame(animationId);
                    animationId = null;
                }
            }
        });
    });

    observer.observe(canvas.parentElement);
    window.addEventListener('resize', resize);
    init();
}


// =========================================================================
// 7. HUD ANIMATED STAT COUNTERS
// =========================================================================

function initHUDCounters() {
    const counters = document.querySelectorAll('.hud-stat-value[data-count]');
    if (!counters.length) return;

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.dataset.count, 10) || 0;
                animateCounter(el, target);
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(c => observer.observe(c));
}

function animateCounter(el, target) {
    const duration = 2000;
    const start = performance.now();

    function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 4); // easeOutQuart
        const current = Math.floor(eased * target);
        el.textContent = current + '+';
        if (progress < 1) requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
}


// =========================================================================
// 8. INJECT MONOSPACE FONT
// =========================================================================

(function injectFonts() {
    if (!document.querySelector('link[href*="JetBrains+Mono"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&display=swap';
        document.head.appendChild(link);
    }
})();


// =========================================================================
// INIT — Boot all project-section systems
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {
    initProjectsParticles();
    initHUDCounters();
});
