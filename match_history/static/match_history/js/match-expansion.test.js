/**
 * Match Card Expansion Tests
 * 
 * This file contains tests for the match card expansion functionality.
 * These tests can be run in a browser console to verify the functionality.
 */

// Test function to verify match card expansion functionality
function testMatchCardExpansion() {
    console.log('Running match card expansion tests...');
    
    // Test 1: Check if all match cards have the required data attributes
    const matchCards = document.querySelectorAll('.match-card');
    let allCardsHaveAttributes = true;
    
    matchCards.forEach(card => {
        if (!card.hasAttribute('data-match-id') || !card.hasAttribute('data-expanded')) {
            allCardsHaveAttributes = false;
            console.error('Test 1 failed: Found card without required data attributes', card);
        }
    });
    
    if (allCardsHaveAttributes) {
        console.log('Test 1 passed: All match cards have required data attributes');
    }
    
    // Test 2: Check if all match buttons have event listeners
    const matchButtons = document.querySelectorAll('.match-btn');
    let allButtonsInitialized = true;
    
    matchButtons.forEach(button => {
        if (!button.hasAttribute('data-initialized')) {
            allButtonsInitialized = false;
            console.error('Test 2 failed: Found button without initialization', button);
        }
    });
    
    if (allButtonsInitialized) {
        console.log('Test 2 passed: All match buttons are initialized');
    }
    
    // Test 3: Test expansion functionality on a sample card
    if (matchCards.length > 0) {
        const testCard = matchCards[0];
        const testButton = testCard.querySelector('.match-btn');
        
        if (testButton) {
            // Get initial state
            const initialState = testCard.getAttribute('data-expanded');
            
            // Trigger click
            testButton.click();
            
            // Check if state changed
            const newState = testCard.getAttribute('data-expanded');
            
            if (initialState !== newState) {
                console.log('Test 3 passed: Card expansion state changes on button click');
            } else {
                console.error('Test 3 failed: Card expansion state did not change on button click');
            }
            
            // Reset state
            if (initialState !== newState) {
                testButton.click();
            }
        } else {
            console.error('Test 3 skipped: No button found in test card');
        }
    } else {
        console.error('Test 3 skipped: No match cards found');
    }
    
    console.log('Match card expansion tests completed');
}

// Function to test expansion state persistence during pagination
function testExpansionStatePersistence() {
    console.log('Testing expansion state persistence...');
    
    // Expand a card
    const firstCard = document.querySelector('.match-card');
    if (firstCard) {
        const firstCardId = firstCard.getAttribute('data-match-id');
        const firstButton = firstCard.querySelector('.match-btn');
        
        if (firstButton && firstCardId) {
            // Expand the card
            if (firstCard.getAttribute('data-expanded') !== 'true') {
                firstButton.click();
            }
            
            console.log(`Card ${firstCardId} expanded. Scroll down to trigger pagination.`);
            console.log('After pagination, check if the expandedCards set still contains this ID:', firstCardId);
            console.log('expandedCards set:', expandedCards);
        }
    }
}

// Add to window for easy access in browser console
window.testMatchCardExpansion = testMatchCardExpansion;
window.testExpansionStatePersistence = testExpansionStatePersistence;

// Run tests when the page is fully loaded
$(document).ready(function() {
    // Wait a bit for all initializations to complete
    setTimeout(function() {
        console.log('Match card expansion tests are available.');
        console.log('Run tests by calling window.testMatchCardExpansion() in the console.');
        console.log('Test pagination by calling window.testExpansionStatePersistence() in the console.');
    }, 1000);
});