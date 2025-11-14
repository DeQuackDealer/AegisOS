// Aegis OS Promotional Website - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = 48;
                const targetPosition = target.offsetTop - offset;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add active class to current page nav button
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-btn').forEach(btn => {
        const btnHref = btn.getAttribute('onclick');
        if (btnHref && btnHref.includes(currentPage)) {
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
