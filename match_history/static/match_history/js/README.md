# Match Card Expansion Toggle Functionality

This directory contains JavaScript files for the match card expansion toggle functionality in the AramGoV2 application.

## Files

- `match-card.js`: Main implementation of the match card expansion toggle functionality
- `match-card.test.js`: Tests for the match card expansion toggle functionality

## Functionality

The match card expansion toggle functionality allows users to expand and collapse match cards by clicking on the chevron button. Key features include:

1. **Smooth Animation**: Match cards expand and collapse with a smooth height transition animation
2. **Chevron Rotation**: The chevron icon rotates 180 degrees during toggle animation
3. **Persistent State**: Expanded state is maintained during page scroll and pagination
4. **Consistent Behavior**: Expansion works consistently across all match cards

## Implementation Details

### Event Handling

- Click events are attached to all `.match-btn` elements
- New match cards added through pagination are automatically initialized

### Animation

- CSS transitions are used for smooth height changes and chevron rotation
- The match card height transitions between 100px (collapsed) and 300px (expanded)

### State Persistence

- Local storage is used to persist the expanded state of match cards
- A MutationObserver watches for new match cards added through pagination
- Expanded state is restored after scrolling and pagination

## Usage

The functionality is automatically initialized when the page loads. No additional configuration is required.

## Testing

To test the functionality:

1. Load a page with match cards
2. Click on the chevron button of a match card
3. Verify that the card expands smoothly and the chevron rotates
4. Click again to collapse
5. Scroll down to trigger pagination and verify that the expanded state is maintained

## Future Improvements

- Add support for keyboard navigation
- Implement animation speed customization
- Add option to expand/collapse all match cards at once