/**
 * Match Card Expansion Toggle Functionality
 * 
 * This script handles the expansion and collapse of match cards when clicking the chevron button.
 * It includes smooth height transition animations for the match card and rotation animations for the chevron icon.
 * The expanded state is persisted during page scroll and pagination.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize match cards
    initMatchCards();
    
    // Re-initialize after AJAX content is loaded (for pagination)
    observeMatchListChanges();
});

/**
 * Initialize click handlers for all match cards
 */
function initMatchCards() {
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach(button => {
        // Skip if already initialized
        if (button.dataset.initialized) return;
        
        button.dataset.initialized = 'true';
        button.addEventListener('click', toggleMatchCard);
    });
}

/**
 * Toggle match card expansion state
 * @param {Event} event - Click event
 */
function toggleMatchCard(event) {
    const button = event.currentTarget;
    const matchCard = button.closest('.match-card');
    const chevron = button.querySelector('.drop');
    
    // Toggle expanded state
    const isExpanded = matchCard.classList.toggle('expanded');
    
    // Store expanded state in local storage
    const matchId = getMatchIdFromCard(matchCard);
    if (matchId) {
        if (isExpanded) {
            storeExpandedState(matchId);
        } else {
            removeExpandedState(matchId);
        }
    }
    
    // Animate chevron rotation
    if (isExpanded) {
        chevron.style.transform = 'rotate(180deg)';
    } else {
        chevron.style.transform = 'rotate(0deg)';
    }
    
    // Animate card height
    animateCardHeight(matchCard, isExpanded);
}

/**
 * Animate the height of the match card
 * @param {HTMLElement} card - The match card element
 * @param {boolean} expand - Whether to expand or collapse
 */
function animateCardHeight(card, expand) {
    // Get the current height of the card
    const currentHeight = card.offsetHeight;
    
    // Set the initial height explicitly to enable smooth transition
    card.style.height = currentHeight + 'px';
    
    // Force a reflow to ensure the initial height is applied
    card.offsetHeight;
    
    if (expand) {
        // Calculate expanded height (original height + additional content)
        // Set a larger height for expanded state - adjust as needed
        card.style.height = '300px';
    } else {
        // Return to original height
        card.style.height = '100px';
    }
}

/**
 * Extract match ID from the match card element
 * This assumes there's a way to identify unique matches
 * @param {HTMLElement} card - The match card element
 * @returns {string|null} - Match ID or null if not found
 */
function getMatchIdFromCard(card) {
    // This implementation depends on how match IDs are stored in the HTML
    // For now, we'll use the index of the card as a simple identifier
    const allCards = Array.from(document.querySelectorAll('.match-card'));
    return allCards.indexOf(card).toString();
}

/**
 * Store expanded state in local storage
 * @param {string} matchId - Match identifier
 */
function storeExpandedState(matchId) {
    const expandedMatches = getExpandedMatches();
    if (!expandedMatches.includes(matchId)) {
        expandedMatches.push(matchId);
        localStorage.setItem('expandedMatches', JSON.stringify(expandedMatches));
    }
}

/**
 * Remove expanded state from local storage
 * @param {string} matchId - Match identifier
 */
function removeExpandedState(matchId) {
    const expandedMatches = getExpandedMatches();
    const index = expandedMatches.indexOf(matchId);
    if (index !== -1) {
        expandedMatches.splice(index, 1);
        localStorage.setItem('expandedMatches', JSON.stringify(expandedMatches));
    }
}

/**
 * Get expanded matches from local storage
 * @returns {Array} - Array of match IDs
 */
function getExpandedMatches() {
    const stored = localStorage.getItem('expandedMatches');
    return stored ? JSON.parse(stored) : [];
}

/**
 * Restore expanded state for all match cards
 */
function restoreExpandedState() {
    const expandedMatches = getExpandedMatches();
    const allCards = document.querySelectorAll('.match-card');
    
    allCards.forEach((card, index) => {
        const matchId = index.toString();
        if (expandedMatches.includes(matchId)) {
            card.classList.add('expanded');
            const chevron = card.querySelector('.drop');
            if (chevron) {
                chevron.style.transform = 'rotate(180deg)';
            }
            card.style.height = '300px';
        }
    });
}

/**
 * Observe changes to the match list for pagination
 */
function observeMatchListChanges() {
    const matchList = document.getElementById('match-list');
    if (!matchList) return;
    
    // Create a MutationObserver to watch for new match cards
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Initialize new match cards
                initMatchCards();
                // Restore expanded state for newly added cards
                restoreExpandedState();
            }
        });
    });
    
    // Start observing the match list for changes
    observer.observe(matchList, { childList: true });
    
    // Also handle scroll events to maintain expanded state
    window.addEventListener('scroll', function() {
        // Debounce the scroll event to improve performance
        clearTimeout(window.scrollTimeout);
        window.scrollTimeout = setTimeout(function() {
            restoreExpandedState();
        }, 100);
    });
}

// Initialize when the script loads
initMatchCards();
restoreExpandedState();