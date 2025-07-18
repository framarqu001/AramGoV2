/**
 * Match Card Expansion Toggle Functionality
 * 
 * This script handles the expand/collapse functionality for match cards.
 * It adds click event listeners to match-btn elements and toggles the expanded
 * state of the parent match-card element.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize toggle functionality for existing cards
    initMatchCardToggles();
    
    // Set up a MutationObserver to handle dynamically added cards (for infinite scroll)
    const matchListObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // New content was added, initialize toggles on new elements
                initMatchCardToggles();
            }
        });
    });
    
    // Start observing the match-list container for added nodes
    const matchList = document.getElementById('match-list');
    if (matchList) {
        matchListObserver.observe(matchList, { childList: true });
    }
});

/**
 * Initialize toggle functionality for all match cards
 */
function initMatchCardToggles() {
    const matchButtons = document.querySelectorAll('.match-btn:not(.initialized)');
    
    matchButtons.forEach(function(button) {
        // Mark this button as initialized to avoid duplicate event listeners
        button.classList.add('initialized');
        
        button.addEventListener('click', function() {
            const matchCard = this.closest('.match-card');
            
            // Toggle expanded state
            matchCard.classList.toggle('expanded');
            this.classList.toggle('expanded');
            
            // Accessibility
            const isExpanded = matchCard.classList.contains('expanded');
            this.setAttribute('aria-expanded', isExpanded);
            
            // Optional: scroll into view if expanding and not fully visible
            if (isExpanded) {
                const cardRect = matchCard.getBoundingClientRect();
                const viewportHeight = window.innerHeight;
                
                if (cardRect.bottom > viewportHeight) {
                    matchCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            }
        });
    });
}