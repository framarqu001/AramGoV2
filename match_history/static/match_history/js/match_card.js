/**
 * Match Card Expansion Toggle Functionality
 * 
 * This script handles the expansion and collapse of match cards with smooth animation.
 * It adds click event listeners to match-btn elements and toggles the expansion state.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Select all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Add click event listener to each match button
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the parent match card
            const matchCard = this.closest('.match-card');
            
            // Toggle expanded state
            const isExpanded = matchCard.classList.contains('expanded');
            
            // Update aria-expanded attribute for accessibility
            this.setAttribute('aria-expanded', !isExpanded);
            
            if (isExpanded) {
                // Collapse the card
                collapseCard(matchCard, this);
            } else {
                // Expand the card
                expandCard(matchCard, this);
            }
        });
    });
    
    // Function to handle card expansion
    function expandCard(card, button) {
        // Add expanded class to the card
        card.classList.add('expanded');
        
        // Get the current height of the card
        const currentHeight = card.offsetHeight;
        
        // Set the height to auto temporarily to calculate the expanded height
        card.style.height = 'auto';
        const expandedHeight = card.offsetHeight;
        
        // Set back to the original height before animation
        card.style.height = currentHeight + 'px';
        
        // Trigger reflow
        card.offsetHeight;
        
        // Add transition class and set the target height
        card.classList.add('card-transition');
        card.style.height = expandedHeight + 'px';
        
        // Rotate the chevron icon
        const chevron = button.querySelector('.drop');
        chevron.classList.add('rotated');
        
        // Remove the fixed height after transition completes
        setTimeout(() => {
            card.style.height = 'auto';
        }, 300);
    }
    
    // Function to handle card collapse
    function collapseCard(card, button) {
        // Set a fixed height before collapsing to enable animation
        card.style.height = card.offsetHeight + 'px';
        
        // Trigger reflow
        card.offsetHeight;
        
        // Add transition class
        card.classList.add('card-transition');
        
        // Set the target height (original collapsed height)
        card.style.height = '100px'; // This should match the initial height in CSS
        
        // Rotate the chevron icon back
        const chevron = button.querySelector('.drop');
        chevron.classList.remove('rotated');
        
        // Remove expanded class and clean up after transition
        setTimeout(() => {
            card.classList.remove('expanded');
            card.classList.remove('card-transition');
            card.style.height = '';
        }, 300);
    }
    
    // Add event delegation for dynamically loaded match cards (for pagination)
    document.getElementById('match-list').addEventListener('click', function(event) {
        // Check if the clicked element or its parent is a match button
        const button = event.target.closest('.match-btn');
        if (button && !button.hasAttribute('listener')) {
            // Mark this button as having a listener to avoid duplicates
            button.setAttribute('listener', 'true');
            
            // Get the parent match card
            const matchCard = button.closest('.match-card');
            
            // Toggle expanded state
            const isExpanded = matchCard.classList.contains('expanded');
            
            // Update aria-expanded attribute for accessibility
            button.setAttribute('aria-expanded', !isExpanded);
            
            if (isExpanded) {
                // Collapse the card
                collapseCard(matchCard, button);
            } else {
                // Expand the card
                expandCard(matchCard, button);
            }
        }
    });
});