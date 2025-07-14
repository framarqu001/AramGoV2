/**
 * Match Details Interaction
 * 
 * This script handles the click interaction and animation for expanding/collapsing match cards.
 * It adds event listeners to match buttons and toggles the expanded state of match cards.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize match card click handlers
    initMatchCardHandlers();

    // Re-initialize handlers when new content is loaded via AJAX
    // This is needed for infinite scrolling functionality
    observeMatchListChanges();
});

/**
 * Initialize click handlers for all match cards
 */
function initMatchCardHandlers() {
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach(button => {
        // Only add event listener if it doesn't already have one
        if (!button.hasAttribute('data-handler-initialized')) {
            button.setAttribute('data-handler-initialized', 'true');
            
            button.addEventListener('click', function(event) {
                // Prevent event from bubbling up
                event.preventDefault();
                event.stopPropagation();
                
                // Find the parent match card
                const matchCard = this.closest('.match-card');
                
                // Toggle expanded state
                toggleMatchCardExpansion(matchCard);
            });
        }
    });
}

/**
 * Toggle the expanded state of a match card
 * @param {HTMLElement} matchCard - The match card element to toggle
 */
function toggleMatchCardExpansion(matchCard) {
    // Get match ID for potential future use (e.g., loading additional data)
    const matchId = matchCard.getAttribute('data-match-id');
    
    // Toggle expanded class
    matchCard.classList.toggle('expanded');
    
    // Log for debugging
    console.log(`Match ${matchId} expansion toggled`);
}

/**
 * Observe changes to the match list for infinite scrolling support
 */
function observeMatchListChanges() {
    // Check if the match list exists
    const matchList = document.getElementById('match-list');
    if (!matchList) return;
    
    // Create a MutationObserver to watch for new match cards being added
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // New content was added, reinitialize handlers
                initMatchCardHandlers();
            }
        });
    });
    
    // Start observing the match list for changes
    observer.observe(matchList, { childList: true });
}