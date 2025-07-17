/**
 * Match Card Optimizer
 * 
 * This script implements performance optimizations for match cards:
 * - Intersection Observer for lazy loading
 * - Efficient card expansion/collapse
 * - Memory management for expanded cards
 * - Progressive loading indicators
 */

class MatchCardOptimizer {
    constructor() {
        // Configuration
        this.config = {
            cardSelector: '.match-card',
            buttonSelector: '.match-btn',
            detailsContainerSelector: '.match-details-container',
            detailsContentSelector: '.match-details-content',
            loadingSelector: '.match-details-loading',
            expandedClass: 'expanded',
            observedClass: 'observed',
            maxExpandedCards: 3, // Maximum number of expanded cards at once
        };

        // State
        this.expandedCards = new Map(); // Map of expanded cards with match ID as key
        this.observer = null;
        this.initialized = false;
    }

    /**
     * Initialize the optimizer
     */
    init() {
        if (this.initialized) return;
        
        this.setupIntersectionObserver();
        this.attachEventListeners();
        this.initialized = true;
        
        console.log('Match Card Optimizer initialized');
    }

    /**
     * Set up the Intersection Observer for lazy loading
     */
    setupIntersectionObserver() {
        const options = {
            root: null, // viewport
            rootMargin: '100px', // start loading when cards are 100px from viewport
            threshold: 0.1 // trigger when 10% of the card is visible
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const card = entry.target;
                    card.classList.add(this.config.observedClass);
                    
                    // Once the card is observed, we don't need to observe it anymore
                    this.observer.unobserve(card);
                }
            });
        }, options);

        // Start observing all cards
        document.querySelectorAll(this.config.cardSelector).forEach(card => {
            this.observer.observe(card);
        });
    }

    /**
     * Attach event listeners to match cards
     */
    attachEventListeners() {
        document.querySelectorAll(this.config.buttonSelector).forEach(button => {
            button.addEventListener('click', (event) => {
                const card = event.currentTarget.closest(this.config.cardSelector);
                this.toggleCardExpansion(card);
            });
        });

        // Handle new cards added by infinite scrolling
        const matchList = document.getElementById('match-list');
        if (matchList) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach(mutation => {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        mutation.addedNodes.forEach(node => {
                            if (node.nodeType === 1 && node.matches(this.config.cardSelector)) {
                                // New card added, observe it and attach event listener
                                this.observer.observe(node);
                                const button = node.querySelector(this.config.buttonSelector);
                                if (button) {
                                    button.addEventListener('click', (event) => {
                                        this.toggleCardExpansion(node);
                                    });
                                }
                            }
                        });
                    }
                });
            });

            observer.observe(matchList, { childList: true });
        }
    }

    /**
     * Toggle card expansion state
     * @param {HTMLElement} card - The card element to toggle
     */
    toggleCardExpansion(card) {
        const matchId = card.dataset.matchId;
        const button = card.querySelector(this.config.buttonSelector);
        const detailsContainer = card.querySelector(this.config.detailsContainerSelector);
        
        if (!matchId || !button || !detailsContainer) {
            console.error('Missing required elements for card expansion');
            return;
        }

        // If card is already expanded, collapse it
        if (button.classList.contains(this.config.expandedClass)) {
            this.collapseCard(card, button, detailsContainer);
        } else {
            this.expandCard(card, button, detailsContainer, matchId);
        }
    }

    /**
     * Expand a card and load its details
     */
    expandCard(card, button, detailsContainer, matchId) {
        // Check if we need to collapse other cards first (memory management)
        if (this.expandedCards.size >= this.config.maxExpandedCards) {
            // Get the oldest expanded card and collapse it
            const oldestCardId = this.expandedCards.keys().next().value;
            const oldestCard = document.querySelector(`${this.config.cardSelector}[data-match-id="${oldestCardId}"]`);
            if (oldestCard) {
                const oldButton = oldestCard.querySelector(this.config.buttonSelector);
                const oldDetailsContainer = oldestCard.querySelector(this.config.detailsContainerSelector);
                this.collapseCard(oldestCard, oldButton, oldDetailsContainer);
            }
        }

        // Mark as expanded
        button.classList.add(this.config.expandedClass);
        detailsContainer.style.display = 'block';
        
        // Add to expanded cards map with timestamp
        this.expandedCards.set(matchId, Date.now());

        // Load details if not already loaded
        const detailsContent = detailsContainer.querySelector(this.config.detailsContentSelector);
        if (!detailsContent.innerHTML.trim()) {
            this.loadCardDetails(matchId, detailsContainer);
        }
    }

    /**
     * Collapse a card
     */
    collapseCard(card, button, detailsContainer) {
        button.classList.remove(this.config.expandedClass);
        detailsContainer.style.display = 'none';
        
        // Remove from expanded cards map
        const matchId = card.dataset.matchId;
        this.expandedCards.delete(matchId);
    }

    /**
     * Load card details via AJAX
     */
    loadCardDetails(matchId, detailsContainer) {
        const loadingElement = detailsContainer.querySelector(this.config.loadingSelector);
        const contentElement = detailsContainer.querySelector(this.config.detailsContentSelector);
        
        if (loadingElement) loadingElement.style.display = 'flex';
        if (contentElement) contentElement.innerHTML = '';

        fetch(`/match/${matchId}/details/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (loadingElement) loadingElement.style.display = 'none';
                this.renderCardDetails(data, contentElement);
            })
            .catch(error => {
                console.error('Error fetching match details:', error);
                if (loadingElement) {
                    loadingElement.innerHTML = '<p>Error loading details. Please try again.</p>';
                }
            });
    }

    /**
     * Render card details in the content element
     */
    renderCardDetails(data, contentElement) {
        // Create blue team section
        const blueTeamSection = document.createElement('div');
        blueTeamSection.className = 'match-details-team blue';
        
        const blueHeader = document.createElement('div');
        blueHeader.className = 'match-details-header';
        blueHeader.innerHTML = `
            <div>Blue Team ${data.blue_team_win ? '(Victory)' : '(Defeat)'}</div>
            <div>Kills: ${data.total_kills_blue} | Gold: ${(data.total_gold_blue / 1000).toFixed(1)}k</div>
        `;
        blueTeamSection.appendChild(blueHeader);

        // Add blue team players
        data.blue_team.forEach(player => {
            const playerDiv = document.createElement('div');
            playerDiv.className = 'match-details-player';
            playerDiv.innerHTML = `
                <img src="${player.champion_img}" alt="${player.champion_name}" width="24" height="24">
                <a href="${player.summoner_url || '#'}">${player.summoner_name}</a>
                <div class="match-details-stats">
                    <span>${player.kills}/${player.deaths}/${player.assists}</span>
                    <span>${player.damage_dealt.toLocaleString()} dmg</span>
                </div>
            `;
            blueTeamSection.appendChild(playerDiv);
        });

        // Create red team section
        const redTeamSection = document.createElement('div');
        redTeamSection.className = 'match-details-team red';
        
        const redHeader = document.createElement('div');
        redHeader.className = 'match-details-header';
        redHeader.innerHTML = `
            <div>Red Team ${!data.blue_team_win ? '(Victory)' : '(Defeat)'}</div>
            <div>Kills: ${data.total_kills_red} | Gold: ${(data.total_gold_red / 1000).toFixed(1)}k</div>
        `;
        redTeamSection.appendChild(redHeader);

        // Add red team players
        data.red_team.forEach(player => {
            const playerDiv = document.createElement('div');
            playerDiv.className = 'match-details-player';
            playerDiv.innerHTML = `
                <img src="${player.champion_img}" alt="${player.champion_name}" width="24" height="24">
                <a href="${player.summoner_url || '#'}">${player.summoner_name}</a>
                <div class="match-details-stats">
                    <span>${player.kills}/${player.deaths}/${player.assists}</span>
                    <span>${player.damage_dealt.toLocaleString()} dmg</span>
                </div>
            `;
            redTeamSection.appendChild(playerDiv);
        });

        // Add both sections to the content element
        contentElement.appendChild(blueTeamSection);
        contentElement.appendChild(redTeamSection);
    }

    /**
     * Clean up resources when the optimizer is no longer needed
     */
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        // Remove event listeners
        document.querySelectorAll(this.config.buttonSelector).forEach(button => {
            button.removeEventListener('click');
        });
        
        this.expandedCards.clear();
        this.initialized = false;
    }
}

// Initialize the optimizer when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.matchCardOptimizer = new MatchCardOptimizer();
    window.matchCardOptimizer.init();
});