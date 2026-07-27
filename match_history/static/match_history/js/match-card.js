/**
 * Match Card Expansion Functionality
 * Handles the expanding and collapsing of match cards
 */
document.addEventListener('DOMContentLoaded', function() {
    // Find all match card buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Add click event listener to each button
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the parent match card
            const matchCard = this.closest('.match-card');
            
            // Toggle the expanded class on the match card
            matchCard.classList.toggle('expanded');
            
            // Toggle the active class on the button
            this.classList.toggle('active');
            
            // Store the expanded state in localStorage to persist between page loads
            const matchId = matchCard.dataset.matchId;
            if (matchId) {
                if (matchCard.classList.contains('expanded')) {
                    localStorage.setItem(`match-${matchId}-expanded`, 'true');
                } else {
                    localStorage.removeItem(`match-${matchId}-expanded`);
                }
            }
        });
    });
    
    // Restore expanded state from localStorage on page load
    const matchCards = document.querySelectorAll('.match-card');
    matchCards.forEach(card => {
        const matchId = card.dataset.matchId;
        if (matchId && localStorage.getItem(`match-${matchId}-expanded`) === 'true') {
            card.classList.add('expanded');
            const button = card.querySelector('.match-btn');
            if (button) {
                button.classList.add('active');
            }
        }
    });
});