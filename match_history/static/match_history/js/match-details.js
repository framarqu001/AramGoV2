/**
 * Match Details Expansion - Handles lazy loading of expanded match details
 * 
 * Features:
 * - Lazy loading of expanded match details via AJAX
 * - Client-side caching to avoid redundant requests
 * - Loading indicators for async content
 * - Optimized image loading
 */

document.addEventListener('DOMContentLoaded', function() {
    // Cache for storing already fetched match details
    const matchDetailsCache = {};
    
    // Add click event listeners to all match buttons
    document.querySelectorAll('.match-btn').forEach(button => {
        button.addEventListener('click', function() {
            const matchCard = this.closest('.match-card');
            const matchId = matchCard.dataset.matchId;
            const expandedContent = matchCard.querySelector('.expanded-content');
            const expandedDetails = matchCard.querySelector('.expanded-match-details');
            
            // Toggle expanded state
            if (expandedContent.style.display === 'none') {
                // Show the expanded content
                expandedContent.style.display = 'block';
                matchCard.classList.add('expanded');
                button.classList.add('expanded');
                
                // Check if we already have the data in cache
                if (matchDetailsCache[matchId]) {
                    expandedDetails.innerHTML = matchDetailsCache[matchId];
                    initLazyLoadImages(expandedDetails);
                } else {
                    // Show loading indicator
                    matchCard.querySelector('.loading-indicator').style.display = 'flex';
                    
                    // Fetch match details via AJAX
                    fetchMatchDetails(matchId)
                        .then(data => {
                            // Hide loading indicator
                            matchCard.querySelector('.loading-indicator').style.display = 'none';
                            
                            // Render match details
                            const renderedHtml = renderMatchDetails(data.match_details, matchId);
                            expandedDetails.innerHTML = renderedHtml;
                            
                            // Cache the rendered HTML
                            matchDetailsCache[matchId] = renderedHtml;
                            
                            // Initialize lazy loading for images
                            initLazyLoadImages(expandedDetails);
                        })
                        .catch(error => {
                            console.error('Error fetching match details:', error);
                            matchCard.querySelector('.loading-indicator').style.display = 'none';
                            expandedDetails.innerHTML = '<p class="error-message">Failed to load match details. Please try again.</p>';
                        });
                }
            } else {
                // Hide the expanded content
                expandedContent.style.display = 'none';
                matchCard.classList.remove('expanded');
                button.classList.remove('expanded');
            }
        });
    });
    
    /**
     * Fetches match details from the server
     * @param {string} matchId - The ID of the match to fetch details for
     * @returns {Promise} - A promise that resolves with the match details
     */
    function fetchMatchDetails(matchId) {
        return new Promise((resolve, reject) => {
            fetch(`/match_history/match/${matchId}/details/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => resolve(data))
                .catch(error => reject(error));
        });
    }
    
    /**
     * Renders match details HTML
     * @param {Object} matchDetails - The match details object
     * @param {string} matchId - The ID of the match
     * @returns {string} - The rendered HTML
     */
    function renderMatchDetails(matchDetails, matchId) {
        const blueTeam = matchDetails.blue_team;
        const redTeam = matchDetails.red_team;
        
        let html = `
            <div class="match-details-container">
                <h3>Match Details</h3>
                <div class="match-info-summary">
                    <p>Game Duration: ${matchDetails.game_duration_formatted}</p>
                    <p>Game Mode: ${matchDetails.game_mode}</p>
                    <p>Patch: ${matchDetails.patch}</p>
                </div>
                <table class="detailed-stats-table">
                    <thead>
                        <tr>
                            <th>Player</th>
                            <th>Champion</th>
                            <th>KDA</th>
                            <th>CS</th>
                            <th>Items</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="5" class="team-header blue-team-header">Blue Team ${matchDetails.winner === 100 ? '(Victory)' : '(Defeat)'}</td>
                        </tr>
        `;
        
        // Add blue team players
        blueTeam.forEach(player => {
            html += renderPlayerRow(player);
        });
        
        html += `
                        <tr>
                            <td colspan="5" class="team-header red-team-header">Red Team ${matchDetails.winner === 200 ? '(Victory)' : '(Defeat)'}</td>
                        </tr>
        `;
        
        // Add red team players
        redTeam.forEach(player => {
            html += renderPlayerRow(player);
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        return html;
    }
    
    /**
     * Renders a player row for the detailed stats table
     * @param {Object} player - The player object
     * @returns {string} - The rendered HTML
     */
    function renderPlayerRow(player) {
        const kda = `${player.kills}/${player.deaths}/${player.assists}`;
        
        let itemsHtml = '';
        player.items.forEach(item => {
            if (item) {
                itemsHtml += `<img class="lazy-load" data-src="${item}" alt="Item" width="22" height="22">`;
            }
        });
        
        return `
            <tr class="player-row">
                <td>
                    <a href="${player.summoner_url}">${player.summoner_name}</a>
                </td>
                <td>
                    <img class="lazy-load detailed-champion-img" data-src="${player.champion_image}" alt="${player.champion_name}">
                    ${player.champion_name}
                </td>
                <td>${kda}</td>
                <td>${player.creep_score}</td>
                <td class="items-cell">${itemsHtml}</td>
            </tr>
        `;
    }
    
    /**
     * Initializes lazy loading for images
     * @param {HTMLElement} container - The container element
     */
    function initLazyLoadImages(container) {
        const lazyImages = container.querySelectorAll('.lazy-load');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for browsers that don't support IntersectionObserver
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
                img.classList.add('loaded');
            });
        }
    }
});