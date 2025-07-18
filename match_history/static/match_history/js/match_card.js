/**
 * Match Card Expansion Toggle Functionality
 * 
 * This script handles the expansion and collapse of match cards
 * when clicking on the chevron button.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Select all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Add click event listener to each button
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the parent match card
            const matchCard = this.closest('.match-card');
            
            // Toggle the expansion
            toggleExpansion(matchCard, this);
        });
        
        // Initialize data-expanded attribute to track state
        button.closest('.match-card').setAttribute('data-expanded', 'false');
    });
    
    // Function to handle match card expansion/collapse
    function toggleExpansion(card, button) {
        // Get current expansion state
        const isExpanded = card.getAttribute('data-expanded') === 'true';
        
        // Toggle the expansion state
        card.setAttribute('data-expanded', !isExpanded);
        
        // Get the chevron icon
        const chevron = button.querySelector('svg.drop');
        
        if (isExpanded) {
            // Collapse the card
            card.style.height = '100px'; // Default height from CSS
            
            // Rotate chevron back to original position
            chevron.style.transform = 'rotate(0deg)';
        } else {
            // Expand the card - calculate appropriate height based on content
            const sectionContainer = card.querySelector('.match-section-container');
            const expandedHeight = Math.max(300, sectionContainer.scrollHeight + 20); // Add some padding
            card.style.height = expandedHeight + 'px';
            
            // Rotate chevron 180 degrees
            chevron.style.transform = 'rotate(180deg)';
        }
    }
    
    // Handle dynamically loaded match cards (for infinite scrolling)
    const matchList = document.getElementById('match-list');
    if (matchList) {
        // Create a MutationObserver to watch for new match cards
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Find new match buttons in added nodes
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            const newButtons = node.querySelectorAll('.match-btn');
                            
                            // Add event listeners to new buttons
                            newButtons.forEach(button => {
                                button.addEventListener('click', function() {
                                    const matchCard = this.closest('.match-card');
                                    toggleExpansion(matchCard, this);
                                });
                                
                                // Initialize data-expanded attribute
                                button.closest('.match-card').setAttribute('data-expanded', 'false');
                            });
                        }
                    });
                }
            });
        });
        
        // Start observing the match list for added nodes
        observer.observe(matchList, { childList: true });
    }
});