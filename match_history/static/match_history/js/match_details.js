/**
 * Match Details Expansion/Collapse Functionality
 * 
 * This script handles the expansion and collapse of the match details section
 * when a user clicks on the dropdown button in a match card.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to initialize match detail buttons
    function initMatchDetailButtons() {
        const matchButtons = document.querySelectorAll('.match-btn');
        
        matchButtons.forEach(button => {
            button.addEventListener('click', function() {
                const matchId = this.getAttribute('data-match-id');
                const expandedDetails = document.getElementById(`expanded-${matchId}`);
                const chevronIcon = this.querySelector('.drop');
                
                // Toggle the expanded details visibility
                if (expandedDetails.style.display === 'none' || !expandedDetails.style.display) {
                    expandedDetails.style.display = 'block';
                    // Rotate chevron icon to point up
                    chevronIcon.style.transform = 'rotate(180deg)';
                } else {
                    expandedDetails.style.display = 'none';
                    // Reset chevron icon rotation
                    chevronIcon.style.transform = 'rotate(0deg)';
                }
            });
        });
    }
    
    // Initialize buttons on page load
    initMatchDetailButtons();
    
    // Re-initialize buttons when new content is loaded (for pagination)
    document.addEventListener('contentLoaded', function() {
        initMatchDetailButtons();
    });
    
    // Handle AJAX pagination
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Check if any of the added nodes are match cards
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && (node.classList.contains('match-card') || node.querySelector('.match-card'))) {
                        initMatchDetailButtons();
                    }
                });
            }
        });
    });
    
    // Start observing the match list container for DOM changes
    const matchListContainer = document.getElementById('match-list');
    if (matchListContainer) {
        observer.observe(matchListContainer, { childList: true, subtree: true });
    }
});