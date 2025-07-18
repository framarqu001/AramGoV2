document.addEventListener('DOMContentLoaded', function() {
    // Get all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Add click event listener to each button
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the parent match card
            const matchCard = this.closest('.match-card');
            
            // Get the details panel within this match card
            const detailsPanel = matchCard.querySelector('.match-details-panel');
            
            // Toggle expanded class on the button
            this.classList.toggle('expanded');
            
            // Toggle expanded class on the details panel
            detailsPanel.classList.toggle('expanded');
            
            // Store the expanded state in localStorage to persist it
            const matchId = matchCard.dataset.matchId || matchCard.id;
            if (matchId) {
                if (detailsPanel.classList.contains('expanded')) {
                    localStorage.setItem('match-expanded-' + matchId, 'true');
                } else {
                    localStorage.removeItem('match-expanded-' + matchId);
                }
            }
        });
    });
    
    // Restore expanded state from localStorage on page load
    document.querySelectorAll('.match-card').forEach(card => {
        const matchId = card.dataset.matchId || card.id;
        if (matchId && localStorage.getItem('match-expanded-' + matchId) === 'true') {
            const button = card.querySelector('.match-btn');
            const panel = card.querySelector('.match-details-panel');
            
            if (button && panel) {
                button.classList.add('expanded');
                panel.classList.add('expanded');
            }
        }
    });
});