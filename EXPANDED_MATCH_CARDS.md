# Expanded Match Card UI Components

This document describes the implementation of expanded match card UI components that display detailed participant statistics.

## Overview

The expanded match card functionality allows users to view comprehensive statistics for all participants in a match by clicking the expand button on each match card. This provides a detailed breakdown of each player's performance, including KDA, CS, items, spells, and runes.

## Features

### 1. Collapsible Participant Stats Section
- **Location**: Below the existing match card content
- **Trigger**: Click the chevron button at the bottom of each match card
- **Animation**: Smooth expand/collapse with 300ms transition
- **State**: Initially collapsed, expands to show detailed participant information

### 2. Detailed Participant Information
Each participant entry displays:
- **Champion**: Champion icon and name
- **Player**: Summoner name (linked to their profile)
- **Build**: Summoner spells and runes
- **Items**: All 6 item slots with empty slot indicators
- **Statistics**: KDA ratio and CS per minute

### 3. Team Organization
- **Blue Team**: Displayed first with victory/defeat status
- **Red Team**: Displayed second with victory/defeat status
- **Main Player**: Highlighted with special styling and border
- **Team Colors**: Win/loss color coding for team headers

### 4. Responsive Design
- **Desktop (1024px+)**: Full grid layout with all information visible
- **Tablet (768px)**: Adjusted grid with smaller icons
- **Mobile (480px)**: Stacked layout with centered content

## Implementation Details

### Files Modified

#### 1. `match_history/templates/match_history/match_list.html`
- Added collapsible participant stats section
- Updated match button with toggle functionality
- Implemented detailed participant information display
- Added proper ARIA attributes for accessibility

#### 2. `match_history/static/match_history/css/details.css`
- Added CSS classes for expanded participant stats
- Implemented smooth animations and transitions
- Added responsive breakpoints
- Enhanced hover states for interactive elements

#### 3. `match_history/static/match_history/js/match_details.js`
- Created JavaScript functionality for expand/collapse behavior
- Added keyboard accessibility support
- Implemented smooth scrolling for expanded content
- Added support for dynamically loaded content (AJAX)

#### 4. `match_history/templates/match_history/details.html`
- Added JavaScript file reference
- Integrated with existing AJAX functionality

#### 5. `match_history/tests.py`
- Added comprehensive test suite for expanded match card functionality
- Tests template rendering, button attributes, and data display

### CSS Classes Added

#### Layout Classes
- `.participant-stats-expanded`: Main container for expanded content
- `.participant-stats-container`: Inner container with team organization
- `.team-stats`: Container for each team's participants
- `.team-header`: Team label with victory/defeat status
- `.participant-detailed-entry`: Individual participant row

#### Component Classes
- `.participant-champion`: Champion icon and name section
- `.participant-build`: Spells and runes section
- `.participant-items`: Item build display
- `.participant-stats`: KDA and CS statistics
- `.champion-icon-expanded`: Larger champion icons for expanded view
- `.item-empty`: Empty item slot styling

#### State Classes
- `.expanded`: Applied when content is expanded
- `.main-participant`: Highlights the main player
- `.team-win` / `.team-lose`: Color coding for team status

### JavaScript Functions

#### Core Functions
- `toggleMatchDetails(button)`: Main function to expand/collapse match details
- `initializeNewMatchCards()`: Initialize functionality for dynamically loaded cards

#### Event Handlers
- Click handlers for expand/collapse
- Keyboard accessibility (Enter/Space keys)
- AJAX completion handlers for dynamic content

## Usage

### For Users
1. Navigate to any summoner's match history page
2. Click the chevron button (▼) at the bottom of any match card
3. View detailed statistics for all participants in the match
4. Click the button again (now ▲) to collapse the details

### For Developers
The expanded match card functionality is automatically initialized when the page loads. For dynamically loaded content (via AJAX), call `initializeNewMatchCards()` after new match cards are added to the DOM.

```javascript
// After loading new match cards via AJAX
$('#match-list').append(newMatchCardsHTML);
initializeNewMatchCards();
```

## Accessibility Features

- **ARIA Labels**: Proper labeling for screen readers
- **Keyboard Navigation**: Support for Enter and Space key activation
- **Focus Management**: Proper focus handling during expand/collapse
- **Semantic HTML**: Proper heading structure and content organization

## Browser Compatibility

- **Modern Browsers**: Full support for all features
- **CSS Grid**: Used for layout (IE11+ support)
- **CSS Transitions**: Smooth animations (IE10+ support)
- **JavaScript**: ES6 features used (modern browser support)

## Performance Considerations

- **CSS Transitions**: Hardware-accelerated animations
- **Lazy Loading**: Content is hidden by default to improve initial render
- **Event Delegation**: Efficient event handling for multiple match cards
- **Mutation Observer**: Minimal DOM observation for smooth scrolling

## Testing

Run the test suite to verify functionality:

```bash
python manage.py test match_history.tests.ExpandedMatchCardTest
```

The test suite covers:
- Template rendering with expanded sections
- Button attributes and functionality
- Participant statistics display
- Team victory/defeat status
- Main participant highlighting

## Future Enhancements

Potential improvements for future versions:
- **Performance Metrics**: Additional statistics like damage dealt, healing, etc.
- **Champion Mastery**: Display mastery levels for each participant
- **Rank Information**: Show current rank for each player
- **Match Timeline**: Add timeline events and key moments
- **Export Functionality**: Allow users to export match details