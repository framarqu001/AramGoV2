// Match card expand/collapse functionality
function toggleMatchDetails(button) {
    const matchCard = button.closest('.match-card');
    const expandedSection = matchCard.querySelector('.participant-stats-expanded');
    const isExpanded = button.getAttribute('aria-expanded') === 'true';
    
    if (isExpanded) {
        // Collapse
        expandedSection.classList.remove('expanded');
        matchCard.classList.remove('expanded');
        button.classList.remove('expanded');
        button.setAttribute('aria-expanded', 'false');
        button.setAttribute('aria-label', 'Toggle match details');
    } else {
        // Expand
        expandedSection.classList.add('expanded');
        matchCard.classList.add('expanded');
        button.classList.add('expanded');
        button.setAttribute('aria-expanded', 'true');
        button.setAttribute('aria-label', 'Hide match details');
    }
}

// Initialize match cards on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for keyboard accessibility
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach(button => {
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleMatchDetails(this);
            }
        });
    });
    
    // Add smooth scrolling when expanding cards
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const target = mutation.target;
                if (target.classList.contains('participant-stats-expanded') && 
                    target.classList.contains('expanded')) {
                    // Smooth scroll to keep the expanded content in view
                    setTimeout(() => {
                        target.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'nearest' 
                        });
                    }, 150);
                }
            }
        });
    });
    
    // Observe all expanded sections for class changes
    document.querySelectorAll('.participant-stats-expanded').forEach(section => {
        observer.observe(section, { attributes: true });
    });
});

// Handle dynamic content loading (for AJAX updates)
function initializeNewMatchCards() {
    const newButtons = document.querySelectorAll('.match-btn:not([data-initialized])');
    
    newButtons.forEach(button => {
        button.setAttribute('data-initialized', 'true');
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleMatchDetails(this);
            }
        });
    });
}

// Export for use in other scripts if needed
window.toggleMatchDetails = toggleMatchDetails;
window.initializeNewMatchCards = initializeNewMatchCards;