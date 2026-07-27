/**
 * Tests for match-card.js functionality
 * 
 * This file contains tests to verify the match card expansion toggle functionality.
 */

// Mock DOM elements for testing
function setupTestDOM() {
    // Create a match card element
    document.body.innerHTML = `
        <div id="match-list">
            <div class="match-card match-win">
                <div class="match-section-container">
                    <!-- Match card content -->
                </div>
                <button class="match-btn match-win">
                    <svg class="drop" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <title>chevron-down</title>
                        <path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" fill="white" />
                    </svg>
                </button>
            </div>
        </div>
    `;
}

// Test initialization of match cards
function testInitMatchCards() {
    setupTestDOM();
    
    // Call the initialization function
    initMatchCards();
    
    // Check if the button has been initialized
    const button = document.querySelector('.match-btn');
    if (!button.dataset.initialized) {
        console.error('Test failed: Button was not initialized');
        return false;
    }
    
    console.log('Test passed: Match cards initialized successfully');
    return true;
}

// Test toggle functionality
function testToggleMatchCard() {
    setupTestDOM();
    
    // Initialize the match card
    initMatchCards();
    
    // Get the button and trigger a click
    const button = document.querySelector('.match-btn');
    button.click();
    
    // Check if the match card has been expanded
    const matchCard = document.querySelector('.match-card');
    if (!matchCard.classList.contains('expanded')) {
        console.error('Test failed: Match card was not expanded');
        return false;
    }
    
    // Check if the chevron has been rotated
    const chevron = document.querySelector('.drop');
    if (chevron.style.transform !== 'rotate(180deg)') {
        console.error('Test failed: Chevron was not rotated');
        return false;
    }
    
    // Click again to collapse
    button.click();
    
    // Check if the match card has been collapsed
    if (matchCard.classList.contains('expanded')) {
        console.error('Test failed: Match card was not collapsed');
        return false;
    }
    
    // Check if the chevron has been rotated back
    if (chevron.style.transform !== 'rotate(0deg)') {
        console.error('Test failed: Chevron was not rotated back');
        return false;
    }
    
    console.log('Test passed: Toggle functionality works correctly');
    return true;
}

// Test local storage functionality
function testLocalStorage() {
    setupTestDOM();
    
    // Clear any existing data
    localStorage.clear();
    
    // Initialize the match card
    initMatchCards();
    
    // Get the button and trigger a click
    const button = document.querySelector('.match-btn');
    button.click();
    
    // Check if the expanded state was stored in local storage
    const expandedMatches = JSON.parse(localStorage.getItem('expandedMatches'));
    if (!expandedMatches || !expandedMatches.includes('0')) {
        console.error('Test failed: Expanded state was not stored in local storage');
        return false;
    }
    
    // Click again to collapse
    button.click();
    
    // Check if the expanded state was removed from local storage
    const updatedExpandedMatches = JSON.parse(localStorage.getItem('expandedMatches'));
    if (updatedExpandedMatches && updatedExpandedMatches.includes('0')) {
        console.error('Test failed: Expanded state was not removed from local storage');
        return false;
    }
    
    console.log('Test passed: Local storage functionality works correctly');
    return true;
}

// Run all tests
function runTests() {
    console.log('Running tests for match-card.js...');
    
    let allTestsPassed = true;
    
    // Run each test
    allTestsPassed = testInitMatchCards() && allTestsPassed;
    allTestsPassed = testToggleMatchCard() && allTestsPassed;
    allTestsPassed = testLocalStorage() && allTestsPassed;
    
    // Report overall result
    if (allTestsPassed) {
        console.log('All tests passed!');
    } else {
        console.error('Some tests failed.');
    }
}

// Run tests when the script is loaded in a test environment
if (typeof jest !== 'undefined') {
    runTests();
}