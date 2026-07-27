/**
 * Match Card Expansion JavaScript
 * 
 * This script handles the expansion and collapse of match cards in the match history view.
 * It provides functionality to:
 * - Toggle card expansion on button click
 * - Maintain expansion state during infinite scroll pagination
 * - Handle multiple card expansions simultaneously
 */

// Store expanded card IDs to maintain state during pagination
const expandedCards = new Set();

/**
 * Toggle the expanded state of a match card
 * @param {HTMLElement} card - The match card element to toggle
 * @param {HTMLElement} button - The button that was clicked
 */
function toggleExpanded(card, button) {
    // Get the current expansion state
    const isExpanded = card.getAttribute('data-expanded') === 'true';
    
    // Toggle the expansion state
    if (isExpanded) {
        // Collapse the card
        card.setAttribute('data-expanded', 'false');
        card.style.height = '100px'; // Reset to original height
        button.querySelector('svg').style.transform = 'rotate(0deg)'; // Reset rotation
        
        // Remove from expanded cards set
        const cardId = card.getAttribute('data-match-id');
        if (cardId) {
            expandedCards.delete(cardId);
        }
    } else {
        // Expand the card
        card.setAttribute('data-expanded', 'true');
        card.style.height = '300px'; // Expanded height
        button.querySelector('svg').style.transform = 'rotate(180deg)'; // Rotate chevron
        
        // Add to expanded cards set
        const cardId = card.getAttribute('data-match-id');
        if (cardId) {
            expandedCards.add(cardId);
        }
    }
}

/**
 * Initialize match card expansion functionality
 * This function attaches event listeners to all match buttons
 */
function initMatchCardExpansion() {
    // Select all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Attach click event handlers to each button
    matchButtons.forEach(button => {
        // Skip if already initialized
        if (button.hasAttribute('data-initialized')) {
            return;
        }
        
        button.setAttribute('data-initialized', 'true');
        
        button.addEventListener('click', function(event) {
            // Prevent default button behavior
            event.preventDefault();
            
            // Get the parent match card
            const matchCard = this.closest('.match-card');
            
            if (matchCard) {
                // Toggle the expanded state
                toggleExpanded(matchCard, this);
            }
        });
    });
    
    // Restore expansion state for cards that were previously expanded
    document.querySelectorAll('.match-card').forEach(card => {
        const cardId = card.getAttribute('data-match-id');
        if (cardId && expandedCards.has(cardId)) {
            const button = card.querySelector('.match-btn');
            if (button) {
                toggleExpanded(card, button);
            }
        }
    });
}

/**
 * Initialize the script when the DOM is fully loaded
 */
$(document).ready(function() {
    // Initialize match card expansion
    initMatchCardExpansion();
    
    // Set up a mutation observer to detect when new match cards are added (for infinite scroll)
    const matchList = document.getElementById('match-list');
    
    if (matchList) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // New cards were added, initialize them
                    initMatchCardExpansion();
                }
            });
        });
        
        // Start observing the match list for added nodes
        observer.observe(matchList, { childList: true });
    }
    
    // Also initialize when new content is loaded via AJAX
    $(document).ajaxSuccess(function() {
        // Initialize any new match cards that were loaded
        setTimeout(initMatchCardExpansion, 100);
    });
});