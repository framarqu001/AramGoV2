/**
 * Match Card Expansion Toggle Functionality
 * 
 * This script handles the expansion and collapse of match cards
 * when the user clicks on the match-btn element.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initial setup for all match cards
    setupMatchCards();

    // Setup for dynamically loaded match cards (pagination)
    document.addEventListener('matchCardsLoaded', setupMatchCards);
});

/**
 * Sets up click event listeners for all match buttons
 */
function setupMatchCards() {
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach(button => {
        // Only add event listener if it hasn't been added before
        if (!button.hasAttribute('data-listener-added')) {
            button.addEventListener('click', toggleExpansion);
            button.setAttribute('data-listener-added', 'true');
        }
    });
}

/**
 * Toggles the expansion state of a match card
 * @param {Event} event - The click event
 */
function toggleExpansion(event) {
    const button = event.currentTarget;
    const matchCard = button.closest('.match-card');
    
    if (!matchCard) return;
    
    // Toggle expanded state
    if (matchCard.classList.contains('expanded')) {
        // Collapse the card
        matchCard.classList.add('collapsing');
        matchCard.classList.remove('expanded');
        
        // Rotate the button icon back
        button.querySelector('.drop').classList.remove('rotated');
        
        // Remove the collapsing class after animation completes
        setTimeout(() => {
            matchCard.classList.remove('collapsing');
        }, 300); // Match this with CSS transition duration
    } else {
        // Expand the card
        matchCard.classList.add('expanding');
        
        // Rotate the button icon
        button.querySelector('.drop').classList.add('rotated');
        
        // Set expanded class after animation starts
        setTimeout(() => {
            matchCard.classList.add('expanded');
            matchCard.classList.remove('expanding');
        }, 300); // Match this with CSS transition duration
    }
}