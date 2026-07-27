document.addEventListener('DOMContentLoaded', function() {
    // Get all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Add click event listener to each button
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Toggle aria-expanded attribute
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
            
            // Get the details panel associated with this button
            const detailsId = this.getAttribute('aria-controls');
            const detailsPanel = document.getElementById(detailsId);
            
            // Toggle the expanded class to show/hide the panel
            if (isExpanded) {
                detailsPanel.classList.remove('expanded');
            } else {
                detailsPanel.classList.add('expanded');
            }
        });
    });
    
    // Function to handle new match cards added via AJAX
    function initNewMatchCards() {
        const newButtons = document.querySelectorAll('.match-btn:not([data-initialized])');
        
        newButtons.forEach(button => {
            button.setAttribute('data-initialized', 'true');
            button.addEventListener('click', function() {
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                this.setAttribute('aria-expanded', !isExpanded);
                
                const detailsId = this.getAttribute('aria-controls');
                const detailsPanel = document.getElementById(detailsId);
                
                if (isExpanded) {
                    detailsPanel.classList.remove('expanded');
                } else {
                    detailsPanel.classList.add('expanded');
                }
            });
        });
    }
    
    // Create a MutationObserver to watch for new match cards
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                initNewMatchCards();
            }
        });
    });
    
    // Start observing the match list container
    const matchList = document.getElementById('match-list');
    if (matchList) {
        observer.observe(matchList, { childList: true, subtree: true });
    }
});