# Match Card Expansion Functionality - Manual Testing Guide

This document outlines how to manually test the match card expansion toggle functionality.

## Prerequisites

- A browser with JavaScript enabled
- Access to a page displaying match cards (e.g., a user's match history)

## Test Cases

### Test Case 1: Basic Expansion and Collapse

1. **Setup**: Load a page with match cards
2. **Action**: Click on the chevron button of any match card
3. **Expected Result**:
   - The match card should smoothly expand to a height of 200px
   - The chevron icon should rotate 180 degrees
4. **Action**: Click on the same chevron button again
5. **Expected Result**:
   - The match card should smoothly collapse back to its original height
   - The chevron icon should rotate back to its original position

### Test Case 2: Multiple Card Independence

1. **Setup**: Load a page with multiple match cards
2. **Action**: Click on the chevron button of the first match card
3. **Expected Result**: The first match card expands while others remain collapsed
4. **Action**: Click on the chevron button of the second match card
5. **Expected Result**: Both the first and second match cards are now expanded
6. **Action**: Click on the chevron button of the first match card again
7. **Expected Result**: The first match card collapses while the second remains expanded

### Test Case 3: State Persistence

1. **Setup**: Load a page with match cards
2. **Action**: Expand several match cards
3. **Expected Result**: The expanded state of each card persists until explicitly changed
4. **Action**: Scroll the page up and down
5. **Expected Result**: The expanded cards remain expanded after scrolling

### Test Case 4: Animation Smoothness

1. **Setup**: Load a page with match cards
2. **Action**: Click on a match card's chevron button
3. **Expected Result**: The expansion/collapse animation should be smooth and take approximately 0.3 seconds

## Troubleshooting

If the functionality doesn't work as expected, check the following:

1. Open the browser's developer console (F12) and look for any JavaScript errors
2. Verify that the match-card-expansion.js file is being loaded correctly
3. Check that the CSS classes and data attributes are properly applied to the match cards and buttons