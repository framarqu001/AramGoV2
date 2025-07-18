document.addEventListener('DOMContentLoaded', function() {
    // Initialize timelines when match cards are expanded
    initializeMatchCardListeners();
});

function initializeMatchCardListeners() {
    // Add click event listeners to match buttons
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            const matchCard = this.closest('.match-card');
            
            // Toggle expanded class
            matchCard.classList.toggle('expanded');
            
            // Initialize timeline if it's not already initialized
            if (matchCard.classList.contains('expanded')) {
                const timelineContainer = matchCard.querySelector('.timeline-container');
                if (timelineContainer && !timelineContainer.dataset.initialized) {
                    initializeTimeline(timelineContainer);
                    timelineContainer.dataset.initialized = 'true';
                }
            }
        });
    });
}

function initializeTimeline(timelineContainer) {
    const matchDuration = parseInt(timelineContainer.dataset.duration);
    const matchId = timelineContainer.dataset.matchId;
    
    // Create time markers
    createTimeMarkers(timelineContainer, matchDuration);
    
    // Position events on the timeline
    positionTimelineEvents(timelineContainer, matchDuration);
    
    // Initialize event filters
    initializeEventFilters(timelineContainer);
}

function createTimeMarkers(timelineContainer, matchDuration) {
    const timelineTrack = timelineContainer.querySelector('.timeline-track');
    const timelineMarkers = timelineContainer.querySelector('.timeline-markers');
    
    // Clear existing markers
    timelineMarkers.innerHTML = '';
    
    // Calculate appropriate interval for markers based on match duration
    const intervalMinutes = calculateMarkerInterval(matchDuration);
    const intervalSeconds = intervalMinutes * 60;
    
    // Create markers
    for (let time = 0; time <= matchDuration; time += intervalSeconds) {
        if (time > matchDuration) break;
        
        const minutes = Math.floor(time / 60);
        const seconds = time % 60;
        const formattedTime = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Calculate position as percentage of total duration
        const position = (time / matchDuration) * 100;
        
        // Create marker element
        const marker = document.createElement('div');
        marker.className = 'time-marker';
        marker.style.left = `${position}%`;
        
        // Create label
        const label = document.createElement('div');
        label.className = 'time-marker-label';
        label.textContent = formattedTime;
        
        marker.appendChild(label);
        timelineMarkers.appendChild(marker);
    }
}

function calculateMarkerInterval(matchDuration) {
    // Convert duration from seconds to minutes
    const durationMinutes = matchDuration / 60;
    
    // Choose appropriate interval based on match duration
    if (durationMinutes <= 15) {
        return 1; // 1-minute intervals for short matches
    } else if (durationMinutes <= 25) {
        return 2; // 2-minute intervals for medium matches
    } else if (durationMinutes <= 40) {
        return 5; // 5-minute intervals for longer matches
    } else {
        return 10; // 10-minute intervals for very long matches
    }
}

function positionTimelineEvents(timelineContainer, matchDuration) {
    const timelineTrack = timelineContainer.querySelector('.timeline-track');
    const events = timelineContainer.querySelectorAll('.timeline-event');
    
    events.forEach(event => {
        const timestamp = parseInt(event.dataset.timestamp);
        
        // Calculate position as percentage of total duration
        const position = (timestamp / matchDuration) * 100;
        
        // Position the event on the timeline
        event.style.left = `${position}%`;
        event.style.top = '50%';
        
        // Add event type as class for styling
        const eventType = event.dataset.type.toLowerCase();
        if (!event.classList.contains(eventType)) {
            event.classList.add(eventType);
        }
    });
}

function initializeEventFilters(timelineContainer) {
    const filterButtons = timelineContainer.closest('.timeline-section').querySelectorAll('.timeline-filter');
    const events = timelineContainer.querySelectorAll('.timeline-event');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active state of filter buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filterType = this.dataset.filter;
            
            // Show/hide events based on filter
            events.forEach(event => {
                if (filterType === 'all') {
                    event.style.display = 'block';
                } else {
                    const eventType = event.dataset.type.toLowerCase();
                    event.style.display = (eventType === filterType) ? 'block' : 'none';
                }
            });
        });
    });
}

// Function to handle dynamic loading of match cards
function initializeNewMatchCards() {
    // This function can be called after new match cards are loaded via AJAX
    initializeMatchCardListeners();
}