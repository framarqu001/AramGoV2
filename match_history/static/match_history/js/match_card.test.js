/**
 * Tests for match_card.js functionality
 * 
 * This file contains tests to verify the match card expansion toggle functionality.
 */

// Mock document and DOM elements for testing
const mockMatchCard = {
    getAttribute: jest.fn(),
    setAttribute: jest.fn(),
    querySelector: jest.fn(),
    style: {},
    offsetHeight: 100
};

const mockChevron = {
    style: {}
};

const mockButton = {
    querySelector: jest.fn().mockReturnValue(mockChevron)
};

// Import the function to test
// Note: In a real test environment, you would use a module system
// Here we're assuming the function is globally available
// const { toggleExpansion } = require('./match_card.js');

describe('Match Card Expansion', () => {
    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
        mockMatchCard.getAttribute.mockReturnValue('false');
        mockMatchCard.querySelector.mockReturnValue(mockButton);
        mockMatchCard.style = {};
        mockChevron.style = {};
    });

    test('toggleExpansion should expand a collapsed card', () => {
        // Setup
        mockMatchCard.getAttribute.mockReturnValue('false');
        
        // Execute
        toggleExpansion(mockMatchCard);
        
        // Verify
        expect(mockMatchCard.setAttribute).toHaveBeenCalledWith('data-expanded', 'true');
        expect(mockChevron.style.transform).toBe('rotate(180deg)');
        
        // Simulate setTimeout callback
        jest.runAllTimers();
        
        expect(mockMatchCard.style.height).toBe('250px');
        expect(mockMatchCard.style.transition).toBe('height 0.3s ease');
    });

    test('toggleExpansion should collapse an expanded card', () => {
        // Setup
        mockMatchCard.getAttribute.mockReturnValue('true');
        
        // Execute
        toggleExpansion(mockMatchCard);
        
        // Verify
        expect(mockMatchCard.setAttribute).toHaveBeenCalledWith('data-expanded', 'false');
        expect(mockChevron.style.transform).toBe('rotate(0deg)');
        
        // Simulate setTimeout callback
        jest.runAllTimers();
        
        expect(mockMatchCard.style.height).toBe('100px');
        expect(mockMatchCard.style.transition).toBe('height 0.3s ease');
    });
});