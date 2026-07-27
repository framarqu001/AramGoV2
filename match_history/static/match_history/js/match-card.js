/**
 * Match Card Progressive Loading
 * 
 * This script handles the progressive loading of expanded match details
 * when a user clicks on a match card.
 */

(function() {
    // Cache object for storing loaded match details
    const matchCache = {
        // Check if browser supports localStorage
        supported: (function() {
            try {
                localStorage.setItem('test', 'test');
                localStorage.removeItem('test');
                return true;
            } catch (e) {
                return false;
            }
        })(),
        
        // Get match details from cache
        get: function(matchId) {
            if (!this.supported) return null;
            
            try {
                const cachedData = localStorage.getItem(`match_${matchId}`);
                if (cachedData) {
                    const parsedData = JSON.parse(cachedData);
                    // Check if cache is still valid (24 hours)
                    if (Date.now() - parsedData.timestamp < 24 * 60 * 60 * 1000) {
                        return parsedData.html;
                    } else {
                        // Remove expired cache
                        localStorage.removeItem(`match_${matchId}`);
                    }
                }
            } catch (e) {
                console.error('Error retrieving from cache:', e);
            }
            
            return null;
        },
        
        // Store match details in cache
        set: function(matchId, html) {
            if (!this.supported) return;
            
            try {
                const data = {
                    html: html,
                    timestamp: Date.now()
                };
                localStorage.setItem(`match_${matchId}`, JSON.stringify(data));
            } catch (e) {
                console.error('Error storing in cache:', e);
                // If storage is full, clear old items
                this.clearOldItems();
            }
        },
        
        // Clear old items from cache if storage is full
        clearOldItems: function() {
            if (!this.supported) return;
            
            try {
                const keys = [];
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key.startsWith('match_')) {
                        keys.push(key);
                    }
                }
                
                // Sort by timestamp (oldest first)
                keys.sort((a, b) => {
                    const aData = JSON.parse(localStorage.getItem(a));
                    const bData = JSON.parse(localStorage.getItem(b));
                    return aData.timestamp - bData.timestamp;
                });
                
                // Remove oldest 50% of items
                const removeCount = Math.ceil(keys.length / 2);
                for (let i = 0; i < removeCount; i++) {
                    localStorage.removeItem(keys[i]);
                }
            } catch (e) {
                console.error('Error clearing cache:', e);
                // If all else fails, clear everything
                localStorage.clear();
            }
        }
    };
    
    // Function to toggle match card expansion
    function toggleMatchCard(card, button) {
        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        const matchId = card.dataset.matchId;
        const expandedContainer = card.querySelector('.match-expanded-container');
        const expandedWrapper = card.querySelector('.match-expanded-wrapper');
        const loadingIndicator = card.querySelector('.match-loading-indicator');
        const errorMessage = card.querySelector('.match-error-message');
        
        // Toggle expanded state
        if (isExpanded) {
            // Collapse
            button.setAttribute('aria-expanded', 'false');
            card.classList.remove('expanded');
            expandedContainer.style.display = 'none';
        } else {
            // Expand
            button.setAttribute('aria-expanded', 'true');
            card.classList.add('expanded');
            expandedContainer.style.display = 'block';
            
            // Check if content is already loaded
            if (expandedWrapper.innerHTML.trim() === '') {
                // Show loading indicator
                loadingIndicator.style.display = 'flex';
                errorMessage.style.display = 'none';
                
                // Check cache first
                const cachedHtml = matchCache.get(matchId);
                if (cachedHtml) {
                    // Use cached content
                    expandedWrapper.innerHTML = cachedHtml;
                    loadingIndicator.style.display = 'none';
                } else {
                    // Load content via AJAX
                    loadMatchDetails(matchId, card);
                }
            }
        }
    }
    
    // Function to load match details via AJAX
    function loadMatchDetails(matchId, card) {
        const expandedWrapper = card.querySelector('.match-expanded-wrapper');
        const loadingIndicator = card.querySelector('.match-loading-indicator');
        const errorMessage = card.querySelector('.match-error-message');
        
        // Construct URL for the AJAX request
        const currentPath = window.location.pathname;
        const url = `${currentPath}/match/${matchId}/`;
        
        // Make AJAX request
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            // Insert content
            expandedWrapper.innerHTML = data.html;
            
            // Cache the content
            matchCache.set(matchId, data.html);
        })
        .catch(error => {
            console.error('Error loading match details:', error);
            
            // Hide loading indicator and show error message
            loadingIndicator.style.display = 'none';
            errorMessage.style.display = 'block';
        });
    }
    
    // Function to retry loading match details
    function retryLoadMatchDetails(event, matchId, card) {
        event.preventDefault();
        
        const expandedWrapper = card.querySelector('.match-expanded-wrapper');
        const loadingIndicator = card.querySelector('.match-loading-indicator');
        const errorMessage = card.querySelector('.match-error-message');
        
        // Show loading indicator and hide error message
        loadingIndicator.style.display = 'flex';
        errorMessage.style.display = 'none';
        expandedWrapper.innerHTML = '';
        
        // Load content via AJAX
        loadMatchDetails(matchId, card);
    }
    
    // Initialize match cards when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Add click event listeners to all match buttons
        document.querySelectorAll('.match-card').forEach(card => {
            const button = card.querySelector('.match-btn');
            const matchId = card.dataset.matchId;
            
            // Add click event listener to button
            button.addEventListener('click', function() {
                toggleMatchCard(card, button);
            });
            
            // Add click event listener to retry button
            const retryButton = card.querySelector('.retry-load');
            if (retryButton) {
                retryButton.addEventListener('click', function(event) {
                    retryLoadMatchDetails(event, matchId, card);
                });
            }
        });
        
        // Add event listener for dynamically added match cards (pagination)
        document.getElementById('match-list').addEventListener('DOMNodeInserted', function(event) {
            if (event.target.classList && event.target.classList.contains('match-card')) {
                const card = event.target;
                const button = card.querySelector('.match-btn');
                const matchId = card.dataset.matchId;
                
                // Add click event listener to button
                button.addEventListener('click', function() {
                    toggleMatchCard(card, button);
                });
                
                // Add click event listener to retry button
                const retryButton = card.querySelector('.retry-load');
                if (retryButton) {
                    retryButton.addEventListener('click', function(event) {
                        retryLoadMatchDetails(event, matchId, card);
                    });
                }
            }
        });
    });
})();