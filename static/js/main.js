/*
=============================================================================
EitaLearn - Main JavaScript
=============================================================================
PURPOSE: Shared JavaScript utilities used across all pages.
         Page-specific JS is in the {% block extra_js %} of each template.

CONTENTS:
  - General utility functions
  - Animation helpers
  - Common event listeners

TODO: Add service worker for offline support
TODO: Add real-time WebSocket connection for live updates
TODO: Add accessibility enhancements (keyboard navigation, screen reader support)
TODO: Add analytics tracking for student engagement metrics
=============================================================================
*/

/**
 * SCORE BAR ANIMATION
 * Animates score bars from 0 to their actual width when they
 * scroll into view. Makes the dashboard feel more dynamic.
 * 
 * WHY: Animated bars draw attention and make data more engaging.
 *      Students and teachers are more likely to notice important scores.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Animate score bars when they come into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const fill = entry.target;
                const width = fill.style.width;
                fill.style.width = '0%';
                // Small delay so the animation is visible
                setTimeout(() => {
                    fill.style.width = width;
                }, 100);
                observer.unobserve(fill);
            }
        });
    }, { threshold: 0.3 });

    // Observe all score bar fills on the page
    document.querySelectorAll('.score-bar-fill, .comp-bar-fill, .mini-bar-fill, .progress-fill').forEach(bar => {
        observer.observe(bar);
    });
});

/**
 * SMOOTH CARD HOVER EFFECTS
 * Adds a subtle tilt/depth effect to interactive cards.
 * 
 * WHY: Makes the UI feel more polished and professional.
 * TODO: Make this configurable or add a "reduce motion" setting
 */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.subject-card, .student-card, .flagged-card').forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
        });
    });
});

/**
 * NUMBER COUNTER ANIMATION
 * Animates numbers counting up from 0 to their final value.
 * Used on dashboard stat cards.
 * 
 * WHY: Animated numbers are more attention-grabbing than static ones.
 */
function animateCounter(element, targetValue, duration = 1000) {
    let startValue = 0;
    const startTime = performance.now();

    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out for smooth deceleration
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.round(startValue + (targetValue - startValue) * easedProgress);

        element.textContent = currentValue;

        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            // Ensure we end on exact target value
            element.textContent = targetValue;
        }
    }

    requestAnimationFrame(updateCounter);
}

// Animate stat numbers on the page
document.addEventListener('DOMContentLoaded', function () {
    const statNumbers = document.querySelectorAll('.stat-number, .eng-number');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const text = el.textContent.trim();

                // Only animate pure numbers (not percentages or text with units)
                const numMatch = text.match(/^(\d+)/);
                if (numMatch) {
                    const target = parseInt(numMatch[1]);
                    const suffix = text.replace(numMatch[1], '');

                    const originalText = el.textContent;
                    animateCounter({
                        set textContent(val) {
                            el.textContent = val + suffix;
                        }
                    }, target, 800);
                }

                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(el => observer.observe(el));
});

/**
 * PRINT FUNCTIONALITY
 * Allows students/teachers to print their reports.
 * 
 * TODO: Add proper print styles in CSS
 * TODO: Add PDF export option using a library like jsPDF
 */
function printReport() {
    window.print();
}

/**
 * TOOLTIP HELPER
 * Shows a tooltip on hover for elements with data-tooltip attribute.
 * 
 * WHY: Provides additional context without cluttering the UI.
 */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-tooltip]').forEach(el => {
        el.addEventListener('mouseenter', function (e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.cssText = `
                position: fixed;
                background: #1a1a2e;
                color: white;
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 0.8rem;
                z-index: 9999;
                pointer-events: none;
                max-width: 250px;
            `;
            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;

            this._tooltip = tooltip;
        });

        el.addEventListener('mouseleave', function () {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
});

/**
 * FLASH MESSAGE AUTO-DISMISS
 * Automatically hides alert/success messages after a few seconds.
 */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert-success').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

console.log('EitaLearn v1.0 - Mock Prototype Loaded');
