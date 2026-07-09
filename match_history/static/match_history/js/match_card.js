/**
 * Match Card Expansion Toggle Functionality
 * 
 * This script handles the expansion and collapse of match cards when clicking
 * the chevron button. It includes animations for smooth transitions.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Select all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Add click event listener to each button
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the parent match card
            const matchCard = this.closest('.match-card');
            
            // Toggle expansion
            toggleExpansion(matchCard);
        });
    });
});

/**
 * Toggles the expansion state of a match card
 * @param {HTMLElement} matchCard - The match card element to toggle
 */
function toggleExpansion(matchCard) {
    // Get current expansion state or default to 'false'
    const isExpanded = matchCard.getAttribute('data-expanded') === 'true';
    
    // Get the chevron button and icon
    const button = matchCard.querySelector('.match-btn');
    const chevron = button.querySelector('.drop');
    
    // Store the original height for collapse animation
    const originalHeight = matchCard.offsetHeight;
    
    if (!isExpanded) {
        // Expand the card
        
        // Set data attribute for state tracking
        matchCard.setAttribute('data-expanded', 'true');
        
        // Rotate chevron icon
        chevron.style.transform = 'rotate(180deg)';
        
        // Set height to auto for expansion
        // First set a specific height, then transition to auto
        matchCard.style.height = originalHeight + 'px';
        
        // Force browser to recognize the height before changing it
        setTimeout(() => {
            // Remove any height restriction to allow content to show
            matchCard.style.height = '250px'; // Expanded height
            
            // Add transition for smooth animation
            matchCard.style.transition = 'height 0.3s ease';
        }, 10);
    } else {
        // Collapse the card
        
        // Set data attribute for state tracking
        matchCard.setAttribute('data-expanded', 'false');
        
        // Reset chevron rotation
        chevron.style.transform = 'rotate(0deg)';
        
        // Set a specific height before transitioning
        matchCard.style.height = matchCard.offsetHeight + 'px';
        
        // Force browser to recognize the height before changing it
        setTimeout(() => {
            // Add transition for smooth animation
            matchCard.style.transition = 'height 0.3s ease';
            
            // Collapse to original height
            matchCard.style.height = '100px'; // Original height from CSS
        }, 10);
    }
}