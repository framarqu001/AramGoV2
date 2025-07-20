/**
 * Tests for match_card.js
 * 
 * This file contains tests to verify the functionality of the match card expansion toggle.
 * These tests can be run using a JavaScript testing framework like Jest.
 */

// Mock DOM elements for testing
document.body.innerHTML = `
  <div id="match-list">
    <div class="match-card">
      <div class="match-section-container"></div>
      <button class="match-btn" aria-expanded="false">
        <svg class="drop"></svg>
      </button>
    </div>
  </div>
`;

// Import the functionality (in a real test environment)
// require('../match_card.js');

describe('Match Card Expansion', () => {
  // Test that clicking a match button toggles the expanded state
  test('clicking match button toggles expanded state', () => {
    // Trigger DOMContentLoaded event
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    const matchCard = document.querySelector('.match-card');
    const matchBtn = document.querySelector('.match-btn');
    const chevron = document.querySelector('.drop');
    
    // Initial state
    expect(matchCard.classList.contains('expanded')).toBe(false);
    expect(matchBtn.getAttribute('aria-expanded')).toBe('false');
    expect(chevron.classList.contains('rotated')).toBe(false);
    
    // Click to expand
    matchBtn.click();
    
    // Expanded state
    expect(matchCard.classList.contains('expanded')).toBe(true);
    expect(matchBtn.getAttribute('aria-expanded')).toBe('true');
    expect(chevron.classList.contains('rotated')).toBe(true);
    
    // Click to collapse
    matchBtn.click();
    
    // Back to collapsed state
    expect(matchCard.classList.contains('expanded')).toBe(false);
    expect(matchBtn.getAttribute('aria-expanded')).toBe('false');
    expect(chevron.classList.contains('rotated')).toBe(false);
  });
  
  // Test that dynamically added match cards work with event delegation
  test('dynamically added match cards work with event delegation', () => {
    // Trigger DOMContentLoaded event
    document.dispatchEvent(new Event('DOMContentLoaded'));
    
    // Add a new match card dynamically
    const matchList = document.getElementById('match-list');
    matchList.innerHTML += `
      <div class="match-card new-card">
        <div class="match-section-container"></div>
        <button class="match-btn" aria-expanded="false">
          <svg class="drop"></svg>
        </button>
      </div>
    `;
    
    const newMatchCard = document.querySelector('.new-card');
    const newMatchBtn = newMatchCard.querySelector('.match-btn');
    const newChevron = newMatchCard.querySelector('.drop');
    
    // Initial state
    expect(newMatchCard.classList.contains('expanded')).toBe(false);
    expect(newMatchBtn.getAttribute('aria-expanded')).toBe('false');
    
    // Simulate click event on the new button
    const clickEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true,
      view: window
    });
    newMatchBtn.dispatchEvent(clickEvent);
    
    // Expanded state
    expect(newMatchCard.classList.contains('expanded')).toBe(true);
    expect(newMatchBtn.getAttribute('aria-expanded')).toBe('true');
    expect(newChevron.classList.contains('rotated')).toBe(true);
  });
});