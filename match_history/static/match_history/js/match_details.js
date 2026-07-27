document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all stats toggle buttons
    document.querySelectorAll('.stats-toggle-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            // Find the parent match card
            const matchCard = this.closest('.match-card');
            
            // Find the detailed stats section within this match card
            const detailedStats = matchCard.querySelector('.detailed-stats-section');
            
            // Toggle the display of the detailed stats section
            if (detailedStats.style.display === 'none' || !detailedStats.style.display) {
                detailedStats.style.display = 'block';
                this.textContent = 'Hide Details';
                
                // Adjust the match card height to accommodate the detailed stats
                matchCard.style.height = 'auto';
            } else {
                detailedStats.style.display = 'none';
                this.textContent = 'Show Details';
                
                // Reset the match card height
                matchCard.style.height = '100px';
            }
        });
    });
});