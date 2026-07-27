/**
 * Match Card Expansion Logic
 * 
 * This script handles the expansion and collapse of match cards in the match history section.
 * It includes functionality for:
 * - Expanding/collapsing match cards on button click
 * - Smooth scrolling when cards expand/collapse
 * - Persisting expansion state during page navigation
 * - Ensuring compatibility with infinite scroll
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the expansion functionality
    initMatchCardExpansion();
});

/**
 * Initialize match card expansion functionality
 */
function initMatchCardExpansion() {
    // Add event listeners to existing match cards
    addMatchCardEventListeners();
    
    // Restore expansion state from session storage
    restoreExpansionState();
    
    // Set up a mutation observer to handle dynamically loaded cards (infinite scroll)
    observeNewMatchCards();
}

/**
 * Add event listeners to match card expansion buttons
 */
function addMatchCardEventListeners() {
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach(button => {
        // Skip if already initialized
        if (button.dataset.initialized) return;
        
        button.dataset.initialized = 'true';
        button.addEventListener('click', function() {
            expandMatchCard(this);
        });
    });
}

/**
 * Expand or collapse a match card
 * @param {HTMLElement} button - The button that was clicked
 */
function expandMatchCard(button) {
    const matchCard = button.closest('.match-card');
    const matchId = getMatchIdFromCard(matchCard);
    const isExpanded = matchCard.classList.contains('expanded');
    
    // Get the current position of the card relative to the viewport
    const cardRect = matchCard.getBoundingClientRect();
    const cardTopPosition = cardRect.top;
    
    // Toggle expanded state
    if (isExpanded) {
        // Collapse the card
        matchCard.classList.remove('expanded');
        matchCard.style.height = '100px'; // Reset to original height
        
        // Rotate the chevron back
        const chevron = button.querySelector('svg');
        chevron.style.transform = '';
        
        // Remove from session storage
        removeExpandedCardFromStorage(matchId);
    } else {
        // Expand the card
        matchCard.classList.add('expanded');
        matchCard.style.height = '300px'; // Expanded height
        
        // Rotate the chevron
        const chevron = button.querySelector('svg');
        chevron.style.transform = 'rotate(180deg)';
        
        // Save to session storage
        saveExpandedCardToStorage(matchId);
    }
    
    // Adjust scroll position to keep the card in the same relative position
    adjustScrollPosition(matchCard, cardTopPosition);
}

/**
 * Adjust scroll position to maintain the card's position in the viewport
 * @param {HTMLElement} card - The card element
 * @param {number} originalTopPosition - The original top position of the card
 */
function adjustScrollPosition(card, originalTopPosition) {
    // Get the new position of the card
    const newRect = card.getBoundingClientRect();
    const newTopPosition = newRect.top;
    
    // Calculate the difference in position
    const positionDifference = newTopPosition - originalTopPosition;
    
    // Adjust the scroll position if there's a significant change
    if (Math.abs(positionDifference) > 5) {
        window.scrollBy({
            top: positionDifference,
            behavior: 'smooth'
        });
    }
}

/**
 * Extract a unique identifier for the match card
 * @param {HTMLElement} card - The match card element
 * @returns {string} - A unique identifier for the card
 */
function getMatchIdFromCard(card) {
    // Use the data-match-id attribute if available
    if (card.dataset.matchId) {
        return `match-${card.dataset.matchId}`;
    }
    
    // Fallback to using the card's position in the list
    const allCards = Array.from(document.querySelectorAll('.match-card'));
    const index = allCards.indexOf(card);
    
    return `match-${index}`;
}

/**
 * Save expanded card state to session storage
 * @param {string} matchId - The match identifier
 */
function saveExpandedCardToStorage(matchId) {
    // Get current expanded cards from storage
    const expandedCards = getExpandedCardsFromStorage();
    
    // Add this card if not already present
    if (!expandedCards.includes(matchId)) {
        expandedCards.push(matchId);
        
        // Save back to storage
        sessionStorage.setItem('expandedMatchCards', JSON.stringify(expandedCards));
    }
}

/**
 * Remove expanded card state from session storage
 * @param {string} matchId - The match identifier
 */
function removeExpandedCardFromStorage(matchId) {
    // Get current expanded cards from storage
    const expandedCards = getExpandedCardsFromStorage();
    
    // Remove this card if present
    const updatedCards = expandedCards.filter(id => id !== matchId);
    
    // Save back to storage
    sessionStorage.setItem('expandedMatchCards', JSON.stringify(updatedCards));
}

/**
 * Get expanded cards from session storage
 * @returns {Array} - Array of expanded card IDs
 */
function getExpandedCardsFromStorage() {
    const storedCards = sessionStorage.getItem('expandedMatchCards');
    return storedCards ? JSON.parse(storedCards) : [];
}

/**
 * Restore expansion state from session storage
 */
function restoreExpansionState() {
    const expandedCards = getExpandedCardsFromStorage();
    
    // Find all match cards
    const allCards = document.querySelectorAll('.match-card');
    
    // Expand cards that were previously expanded
    allCards.forEach((card, index) => {
        const matchId = `match-${index}`;
        
        if (expandedCards.includes(matchId)) {
            // Find the button in this card
            const button = card.querySelector('.match-btn');
            if (button) {
                // Expand the card without scrolling adjustment
                card.classList.add('expanded');
                card.style.height = '300px';
                
                // Rotate the chevron
                const chevron = button.querySelector('svg');
                if (chevron) {
                    chevron.style.transform = 'rotate(180deg)';
                }
            }
        }
    });
}

/**
 * Set up a mutation observer to handle dynamically loaded cards (infinite scroll)
 */
function observeNewMatchCards() {
    // Create a new observer
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            // Check if new nodes were added
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                // Check each added node
                mutation.addedNodes.forEach(function(node) {
                    // If it's an element node
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // If it's a match card itself
                        if (node.classList && node.classList.contains('match-card')) {
                            initializeNewCard(node);
                        }
                        
                        // Or if it contains match cards
                        const newCards = node.querySelectorAll('.match-card');
                        if (newCards.length > 0) {
                            newCards.forEach(card => initializeNewCard(card));
                        }
                    }
                });
            }
        });
    });
    
    // Start observing the match list container
    const matchList = document.getElementById('match-list');
    if (matchList) {
        observer.observe(matchList, { childList: true, subtree: true });
    }
}

/**
 * Initialize a newly added match card
 * @param {HTMLElement} card - The new match card element
 */
function initializeNewCard(card) {
    const button = card.querySelector('.match-btn');
    if (button && !button.dataset.initialized) {
        button.dataset.initialized = 'true';
        button.addEventListener('click', function() {
            expandMatchCard(this);
        });
    }
}