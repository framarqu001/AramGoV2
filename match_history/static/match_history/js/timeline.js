/**
 * Match Timeline Visualization
 * 
 * This script handles the visualization of match timelines, including:
 * - Expanding/collapsing timeline sections
 * - Rendering timeline events and gold/exp differences
 * - Handling event tooltips and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all match timelines
    initializeMatchTimelines();
    
    // Add event listeners to expand/collapse buttons
    setupTimelineToggleButtons();
});

/**
 * Initialize all match timelines on the page
 */
function initializeMatchTimelines() {
    const timelineContainers = document.querySelectorAll('.match-timeline-container');
    
    timelineContainers.forEach(container => {
        const timelineData = JSON.parse(container.dataset.timelineData || '{}');
        if (Object.keys(timelineData).length > 0) {
            renderTimeline(container, timelineData);
        }
    });
}

/**
 * Setup event listeners for timeline toggle buttons
 */
function setupTimelineToggleButtons() {
    const matchButtons = document.querySelectorAll('.match-btn');
    
    matchButtons.forEach(button => {
        button.addEventListener('click', function() {
            const matchCard = this.closest('.match-card');
            const timelineSection = matchCard.querySelector('.timeline-section');
            
            // Toggle timeline visibility
            if (timelineSection) {
                if (timelineSection.classList.contains('timeline-expanded')) {
                    // Collapse timeline
                    timelineSection.classList.remove('timeline-expanded');
                    timelineSection.classList.add('timeline-collapsed');
                    
                    // Rotate button icon
                    this.querySelector('.drop').classList.remove('rotated');
                } else {
                    // Expand timeline
                    timelineSection.classList.remove('timeline-collapsed');
                    timelineSection.classList.add('timeline-expanded');
                    
                    // Rotate button icon
                    this.querySelector('.drop').classList.add('rotated');
                    
                    // Render timeline if not already rendered
                    const timelineContainer = timelineSection.querySelector('.match-timeline-container');
                    if (timelineContainer && !timelineContainer.classList.contains('rendered')) {
                        const timelineData = JSON.parse(timelineContainer.dataset.timelineData || '{}');
                        if (Object.keys(timelineData).length > 0) {
                            renderTimeline(timelineContainer, timelineData);
                            timelineContainer.classList.add('rendered');
                        }
                    }
                }
            }
        });
    });
}

/**
 * Render the timeline visualization
 * @param {HTMLElement} container - The container element for the timeline
 * @param {Object} timelineData - The timeline data to visualize
 */
function renderTimeline(container, timelineData) {
    // Clear any existing content
    container.innerHTML = '';
    
    // Create timeline elements
    const timelineWrapper = document.createElement('div');
    timelineWrapper.className = 'timeline-wrapper';
    
    // Create timeline axis
    const timelineAxis = createTimelineAxis(timelineData.gameDuration);
    timelineWrapper.appendChild(timelineAxis);
    
    // Create events section
    const eventsSection = createEventsSection(timelineData.events);
    timelineWrapper.appendChild(eventsSection);
    
    // Create gold/exp difference graph
    const differenceGraph = createDifferenceGraph(timelineData.goldDiff, timelineData.expDiff);
    timelineWrapper.appendChild(differenceGraph);
    
    // Add the timeline to the container
    container.appendChild(timelineWrapper);
}

/**
 * Create the timeline axis with time markers
 * @param {number} gameDuration - The duration of the game in seconds
 * @returns {HTMLElement} - The timeline axis element
 */
function createTimelineAxis(gameDuration) {
    const axisElement = document.createElement('div');
    axisElement.className = 'timeline-axis';
    
    // Create time markers every 5 minutes
    const intervalMinutes = 5;
    const gameMinutes = Math.ceil(gameDuration / 60);
    const intervals = Math.ceil(gameMinutes / intervalMinutes);
    
    for (let i = 0; i <= intervals; i++) {
        const minute = i * intervalMinutes;
        if (minute <= gameMinutes) {
            const marker = document.createElement('div');
            marker.className = 'time-marker';
            marker.style.left = `${(minute / gameMinutes) * 100}%`;
            
            const label = document.createElement('span');
            label.className = 'time-label';
            label.textContent = `${minute}m`;
            
            marker.appendChild(label);
            axisElement.appendChild(marker);
        }
    }
    
    return axisElement;
}

/**
 * Create the events section with event markers
 * @param {Array} events - The events data
 * @returns {HTMLElement} - The events section element
 */
function createEventsSection(events) {
    const eventsElement = document.createElement('div');
    eventsElement.className = 'timeline-events';
    
    if (!events || events.length === 0) {
        return eventsElement;
    }
    
    const gameDuration = events[events.length - 1].timestamp / 1000 / 60; // Convert to minutes
    
    events.forEach(event => {
        const eventMinute = event.timestamp / 1000 / 60; // Convert to minutes
        const position = (eventMinute / gameDuration) * 100;
        
        const eventMarker = document.createElement('div');
        eventMarker.className = `event-marker event-type-${event.type}`;
        eventMarker.style.left = `${position}%`;
        
        // Create tooltip
        const tooltip = document.createElement('div');
        tooltip.className = 'event-tooltip';
        tooltip.innerHTML = createEventTooltipContent(event);
        
        eventMarker.appendChild(tooltip);
        eventsElement.appendChild(eventMarker);
        
        // Add event listeners for tooltip
        eventMarker.addEventListener('mouseenter', function() {
            tooltip.classList.add('visible');
        });
        
        eventMarker.addEventListener('mouseleave', function() {
            tooltip.classList.remove('visible');
        });
    });
    
    return eventsElement;
}

/**
 * Create the gold/exp difference graph
 * @param {Array} goldDiff - The gold difference data points
 * @param {Array} expDiff - The experience difference data points
 * @returns {HTMLElement} - The difference graph element
 */
function createDifferenceGraph(goldDiff, expDiff) {
    const graphElement = document.createElement('div');
    graphElement.className = 'difference-graph';
    
    if (!goldDiff || goldDiff.length === 0) {
        return graphElement;
    }
    
    // Create SVG element for the graph
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    svg.setAttribute("viewBox", "0 0 100 100");
    svg.setAttribute("preserveAspectRatio", "none");
    
    // Create gold difference line
    const goldLine = document.createElementNS(svgNS, "polyline");
    goldLine.setAttribute("class", "gold-line");
    goldLine.setAttribute("points", createLinePoints(goldDiff));
    
    // Create exp difference line
    const expLine = document.createElementNS(svgNS, "polyline");
    expLine.setAttribute("class", "exp-line");
    expLine.setAttribute("points", createLinePoints(expDiff));
    
    // Create zero line
    const zeroLine = document.createElementNS(svgNS, "line");
    zeroLine.setAttribute("class", "zero-line");
    zeroLine.setAttribute("x1", "0");
    zeroLine.setAttribute("y1", "50");
    zeroLine.setAttribute("x2", "100");
    zeroLine.setAttribute("y2", "50");
    
    // Add elements to SVG
    svg.appendChild(zeroLine);
    svg.appendChild(goldLine);
    svg.appendChild(expLine);
    
    // Add legend
    const legend = document.createElement('div');
    legend.className = 'graph-legend';
    
    const goldLegend = document.createElement('div');
    goldLegend.className = 'legend-item gold';
    goldLegend.innerHTML = '<span class="legend-color"></span> Gold Difference';
    
    const expLegend = document.createElement('div');
    expLegend.className = 'legend-item exp';
    expLegend.innerHTML = '<span class="legend-color"></span> Exp Difference';
    
    legend.appendChild(goldLegend);
    legend.appendChild(expLegend);
    
    // Add SVG and legend to graph element
    graphElement.appendChild(svg);
    graphElement.appendChild(legend);
    
    return graphElement;
}

/**
 * Create SVG line points from data points
 * @param {Array} dataPoints - The data points for the line
 * @returns {string} - The points attribute value for the polyline
 */
function createLinePoints(dataPoints) {
    if (!dataPoints || dataPoints.length === 0) {
        return "";
    }
    
    // Find max absolute value for scaling
    const maxValue = Math.max(...dataPoints.map(point => Math.abs(point.value)));
    
    // Create points string
    return dataPoints.map((point, index) => {
        const x = (index / (dataPoints.length - 1)) * 100;
        // Scale value to -50 to 50 range and invert (negative is up in SVG)
        const y = 50 - ((point.value / maxValue) * 40);
        return `${x},${y}`;
    }).join(" ");
}

/**
 * Create HTML content for event tooltip
 * @param {Object} event - The event data
 * @returns {string} - HTML content for the tooltip
 */
function createEventTooltipContent(event) {
    const timeStr = formatTimestamp(event.timestamp);
    let content = `<div class="tooltip-time">${timeStr}</div>`;
    
    switch (event.type) {
        case 'kill':
            content += `
                <div class="tooltip-title">Champion Kill</div>
                <div class="tooltip-content">
                    <img src="${event.killerChampionIcon}" class="tooltip-icon" alt="Killer">
                    <span class="tooltip-text">${event.killerName} killed ${event.victimName}</span>
                    <img src="${event.victimChampionIcon}" class="tooltip-icon" alt="Victim">
                </div>
            `;
            break;
        case 'objective':
            content += `
                <div class="tooltip-title">${event.objectiveName}</div>
                <div class="tooltip-content">
                    <img src="${event.objectiveIcon}" class="tooltip-icon" alt="Objective">
                    <span class="tooltip-text">${event.teamName} secured ${event.objectiveName}</span>
                </div>
            `;
            break;
        case 'structure':
            content += `
                <div class="tooltip-title">Structure Destroyed</div>
                <div class="tooltip-content">
                    <img src="${event.structureIcon}" class="tooltip-icon" alt="Structure">
                    <span class="tooltip-text">${event.teamName} destroyed ${event.structureName}</span>
                </div>
            `;
            break;
        default:
            content += `
                <div class="tooltip-title">Game Event</div>
                <div class="tooltip-content">
                    <span class="tooltip-text">${event.description}</span>
                </div>
            `;
    }
    
    return content;
}

/**
 * Format timestamp to minutes:seconds
 * @param {number} timestamp - The timestamp in milliseconds
 * @returns {string} - Formatted time string
 */
function formatTimestamp(timestamp) {
    const totalSeconds = Math.floor(timestamp / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}