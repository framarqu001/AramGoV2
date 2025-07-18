/**
 * Match Card Expansion Toggle Functionality
 * 
 * This script adds functionality to toggle match card expansion state when clicking the chevron button.
 * 
 * Features:
 * - Adds click event listener to .match-btn elements
 * - Implements toggleExpansion() function to handle expansion state
 * - Updates data-expanded attribute to track card state
 * - Works with CSS to provide smooth height transition and chevron rotation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Add click event listener to each button
    matchButtons.forEach(button => {
        button.addEventListener('click', toggleExpansion);
    });
    
    /**
     * Toggle expansion state of match card
     * @param {Event} event - The click event
     */
    function toggleExpansion(event) {
        const button = event.currentTarget;
        const matchCard = button.closest('.match-card');
        
        // Get current expansion state
        const isExpanded = button.getAttribute('data-expanded') === 'true';
        
        // Toggle expansion state
        button.setAttribute('data-expanded', !isExpanded);
        matchCard.setAttribute('data-expanded', !isExpanded);
    }
});