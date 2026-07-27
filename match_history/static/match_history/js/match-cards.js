/**
 * Match Cards Expansion Functionality
 * Handles the expand/collapse interaction for match cards
 */
document.addEventListener('DOMContentLoaded', function() {
    // Function to initialize match card expansion
    function initMatchCardExpansion() {
        const matchButtons = document.querySelectorAll('.match-btn');
        
        matchButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Get the parent match card
                const matchCard = this.closest('.match-card');
                
                // Toggle expanded class on the match card
                matchCard.classList.toggle('expanded');
                
                // Toggle expanded class on the button for chevron rotation
                this.classList.toggle('expanded');
                
                // Accessibility
                const isExpanded = matchCard.classList.contains('expanded');
                this.setAttribute('aria-expanded', isExpanded);
            });
        });
    }
    
    // Initialize match card expansion
    initMatchCardExpansion();
    
    // Re-initialize when new content is loaded (for pagination)
    // This handles dynamically loaded match cards
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                initMatchCardExpansion();
            }
        });
    });
    
    // Observe the match list container for changes
    const matchList = document.getElementById('match-list');
    if (matchList) {
        observer.observe(matchList, { childList: true });
    }
});