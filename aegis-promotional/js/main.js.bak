// Aegis OS Promotional Website - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            // Skip empty or just '#' hrefs
            if (href && href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Add active class to current page nav button
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-btn').forEach(btn => {
        // Check if onclick attribute exists and contains the current page
        const onclickAttr = btn.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes(currentPage)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Add animation on scroll for feature boxes
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Initially hide elements for animation
    document.querySelectorAll('.feature-box, .version-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // Console easter egg
    console.log('%cAegis OS', 'font-size: 24px; font-weight: bold; color: #0078d4;');
    console.log('%cThe gold standard for gamers, AI developers, and servers', 'font-size: 14px; color: #666;');
    console.log('%cInterested in our API? Visit /api/docs', 'font-size: 12px; color: #00ff88;');
});