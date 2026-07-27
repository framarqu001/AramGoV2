/**
 * Match Details JavaScript
 * Handles the match card expansion/collapse functionality and tooltips
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Find the parent match card
            const matchCard = this.closest('.match-card');
            
            // Toggle the expanded class
            matchCard.classList.toggle('expanded');
        });
    });
    
    // Initialize tooltips for champion damage types
    const championItems = document.querySelectorAll('.champion-item');
    
    championItems.forEach(item => {
        // Tooltip is already handled by CSS :hover
        // This is just a placeholder for any additional tooltip functionality
    });
    
    // Handle dynamically loaded match cards (from pagination)
    document.addEventListener('DOMNodeInserted', function(e) {
        if (e.target.classList && e.target.classList.contains('match-card')) {
            // Add click event listener to the new match card's button
            const newButton = e.target.querySelector('.match-btn');
            if (newButton) {
                newButton.addEventListener('click', function() {
                    const matchCard = this.closest('.match-card');
                    matchCard.classList.toggle('expanded');
                });
            }
        }
    });
});