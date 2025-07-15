document.addEventListener('DOMContentLoaded', function() {
    // Initial setup for existing buttons
    setupMatchButtons();
    
    // Setup for dynamically loaded content via AJAX
    // Using event delegation on the match-list container
    document.getElementById('match-list').addEventListener('click', function(event) {
        // Check if the clicked element or its parent is a match button
        const button = event.target.closest('.match-btn');
        if (button) {
            toggleMatchDetails(button);
        }
    });
});

// Function to set up match buttons
function setupMatchButtons() {
    // Get all match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    // Add click event listener to each button
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            toggleMatchDetails(this);
        });
    });
}

// Function to toggle match details
function toggleMatchDetails(button) {
    // Toggle active class on the button
    button.classList.toggle('active');
    
    // Get the parent match card
    const matchCard = button.closest('.match-card');
    
    // Get the next element which should be the details table container
    const detailsContainer = matchCard.nextElementSibling;
    
    if (detailsContainer && detailsContainer.classList.contains('match-details-table-container')) {
        // Toggle active class on the details container
        detailsContainer.classList.toggle('active');
        
        // Toggle display style
        if (detailsContainer.style.display === 'none' || detailsContainer.style.display === '') {
            detailsContainer.style.display = 'block';
        } else {
            // We use setTimeout to allow the animation to complete before hiding
            setTimeout(() => {
                if (!detailsContainer.classList.contains('active')) {
                    detailsContainer.style.display = 'none';
                }
            }, 500); // Match the transition duration in CSS
        }
    }
}

// Handle dynamically loaded content
$(document).ajaxSuccess(function() {
    // Setup newly loaded match buttons
    setupMatchButtons();
});