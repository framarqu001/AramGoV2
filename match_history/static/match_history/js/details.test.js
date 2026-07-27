/**
 * Test file for match card expansion functionality
 * 
 * This file contains tests for the match card expansion functionality.
 * It can be run in a browser console to verify that the functionality works correctly.
 */

// Test function to verify that the match card expansion functionality works
function testMatchCardExpansion() {
    console.log('Testing match card expansion functionality...');
    
    // Test 1: Check if the script is loaded
    if (typeof initMatchCardExpansion === 'function') {
        console.log('✅ Script loaded successfully');
    } else {
        console.error('❌ Script not loaded');
        return;
    }
    
    // Test 2: Check if match cards exist
    const matchCards = document.querySelectorAll('.match-card');
    if (matchCards.length > 0) {
        console.log(`✅ Found ${matchCards.length} match cards`);
    } else {
        console.error('❌ No match cards found');
        return;
    }
    
    // Test 3: Check if match buttons exist and have event listeners
    const matchButtons = document.querySelectorAll('.match-btn');
    if (matchButtons.length > 0) {
        console.log(`✅ Found ${matchButtons.length} match buttons`);
        
        // Check if buttons have the initialized attribute
        const initializedButtons = Array.from(matchButtons).filter(btn => btn.dataset.initialized === 'true');
        if (initializedButtons.length === matchButtons.length) {
            console.log('✅ All buttons are initialized with event listeners');
        } else {
            console.error(`❌ Only ${initializedButtons.length} out of ${matchButtons.length} buttons are initialized`);
        }
    } else {
        console.error('❌ No match buttons found');
        return;
    }
    
    // Test 4: Test expanding a card
    const firstButton = matchButtons[0];
    const firstCard = firstButton.closest('.match-card');
    
    console.log('Testing card expansion...');
    firstButton.click();
    
    if (firstCard.classList.contains('expanded')) {
        console.log('✅ Card expanded successfully');
        
        // Check if the height is updated
        if (firstCard.style.height === '300px') {
            console.log('✅ Card height updated correctly');
        } else {
            console.error(`❌ Card height not updated correctly: ${firstCard.style.height}`);
        }
        
        // Check if the chevron is rotated
        const chevron = firstButton.querySelector('svg');
        if (chevron.style.transform === 'rotate(180deg)') {
            console.log('✅ Chevron rotated correctly');
        } else {
            console.error(`❌ Chevron not rotated correctly: ${chevron.style.transform}`);
        }
    } else {
        console.error('❌ Card not expanded');
    }
    
    // Test 5: Test collapsing the card
    console.log('Testing card collapse...');
    firstButton.click();
    
    if (!firstCard.classList.contains('expanded')) {
        console.log('✅ Card collapsed successfully');
        
        // Check if the height is reset
        if (firstCard.style.height === '100px') {
            console.log('✅ Card height reset correctly');
        } else {
            console.error(`❌ Card height not reset correctly: ${firstCard.style.height}`);
        }
        
        // Check if the chevron is reset
        const chevron = firstButton.querySelector('svg');
        if (chevron.style.transform === '') {
            console.log('✅ Chevron reset correctly');
        } else {
            console.error(`❌ Chevron not reset correctly: ${chevron.style.transform}`);
        }
    } else {
        console.error('❌ Card not collapsed');
    }
    
    // Test 6: Test session storage
    console.log('Testing session storage...');
    
    // Expand the card again
    firstButton.click();
    
    // Check if the card ID is saved in session storage
    const expandedCards = JSON.parse(sessionStorage.getItem('expandedMatchCards') || '[]');
    const cardId = getMatchIdFromCard(firstCard);
    
    if (expandedCards.includes(cardId)) {
        console.log('✅ Card ID saved in session storage');
    } else {
        console.error(`❌ Card ID not saved in session storage: ${cardId} not in ${expandedCards}`);
    }
    
    // Collapse the card again
    firstButton.click();
    
    // Check if the card ID is removed from session storage
    const updatedExpandedCards = JSON.parse(sessionStorage.getItem('expandedMatchCards') || '[]');
    
    if (!updatedExpandedCards.includes(cardId)) {
        console.log('✅ Card ID removed from session storage');
    } else {
        console.error(`❌ Card ID not removed from session storage: ${cardId} still in ${updatedExpandedCards}`);
    }
    
    console.log('All tests completed!');
}

// Run the tests when the page is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit to ensure the main script has initialized
    setTimeout(testMatchCardExpansion, 1000);
});