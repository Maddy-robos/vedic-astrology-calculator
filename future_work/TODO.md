# TODO List for Vedic Astrology Research Platform

## Phase 1: Foundation (High Priority)

### Chart Visualization
- [x] Create `CoreLibrary/chart_visualization.py` module
  - [x] Implement `NorthIndianChart` class
  - [x] Create SVG generation method with proper coordinates
  - [x] Add anti-clockwise house numbering (1 at top, 2 to left, etc.)
  - [x] Implement text placement for planets and signs
  - [x] Add Lagna (ascendant) special marking
  - [x] Create responsive scaling logic
  - [x] Add export to PNG/SVG functionality

### Project Structure
- [x] Create `future_work` folder
- [x] Create `REQUIREMENTS.md` file
- [x] Create `TODO.md` file
- [x] Create `pages` folder for multipage app
- [x] Create `1_🔬_Research.py` page
- [x] Create `2_📊_Batch_Analysis.py` page

### Core Integration
- [x] Integrate chart visualization with existing `Chart` class
- [x] Add visualization method to streamlit_app.py
- [x] Create toggle between table view and visual chart

## Phase 2: Research Interface (High Priority)

### CSV Upload Feature
- [x] Implement file upload widget in Research page
- [x] Create CSV validation function
  - [x] Check required columns (name, date, time, lat, lon, timezone)
  - [x] Validate date/time formats
  - [x] Validate coordinate ranges
- [x] Add error handling and reporting
- [x] Create progress bar for batch processing

### Batch Display
- [x] Implement grid layout for multiple charts
  - [x] 2 charts per row on desktop
  - [ ] 1 chart per row on mobile
- [x] Add pagination controls
  - [x] Page size selector (10, 20, 50)
  - [x] Previous/Next buttons
  - [ ] Jump to page input
- [ ] Create chart selection for comparison view

### Divisional Chart Support
- [x] Add dropdown for divisional chart selection
- [x] Implement D1 (Rasi) display (already exists)
- [x] Implement D9 (Navamsa) display
- [ ] Create placeholder for future divisionals

## Phase 3: Divisional Charts (Medium Priority)

### Calculation Methods
- [x] Extend `calculations_helper.py` with new methods:
  - [x] `get_hora_rasi()` - D2
  - [x] `get_drekkana_rasi()` - D3
  - [ ] `get_chaturthamsa_chart()` - D4
  - [ ] `get_panchamsa_chart()` - D5
  - [ ] `get_saptamsa_chart()` - D7
  - [x] `get_dasamsa_rasi()` - D10
  - [ ] `get_dwadasamsa_chart()` - D12
  - [ ] `get_shodasamsa_chart()` - D16
  - [ ] `get_vimsamsa_chart()` - D20
  - [ ] `get_chaturvimsamsa_chart()` - D24
  - [ ] `get_trimsamsa_chart()` - D30
  - [ ] `get_khavedamsa_chart()` - D40
  - [ ] `get_akshavedamsa_chart()` - D45
  - [ ] `get_shastiamsa_chart()` - D60
- [x] Add unified `get_divisional_house_placements()` method

### Divisional Chart Class
- [ ] Create `CoreLibrary/divisional_charts.py`
- [ ] Implement `DivisionalChart` base class
- [ ] Add specific classes for each divisional
- [ ] Create unified interface for all charts

## Phase 4: Export & Analysis (Medium Priority)

### Export Functionality
- [x] Add export dropdown in Research page
- [ ] Implement PDF export
  - [ ] Use reportlab or similar library
  - [ ] Create professional layout template
  - [ ] Include chart images and data tables
- [x] Implement Excel export
  - [x] Use openpyxl or pandas
  - [x] Create multiple sheets (overview, planets, houses, etc.)
- [x] Implement JSON export
  - [x] Full chart data structure
  - [x] Include calculated values

### Analysis Tools
- [ ] Create statistical summary section
  - [ ] Planet distribution across signs
  - [ ] House occupation statistics
  - [ ] Common yoga frequencies
- [ ] Add filtering capabilities
  - [ ] By date range
  - [ ] By planetary positions
  - [ ] By yoga presence
- [ ] Implement search functionality

## Phase 5: Enhancements (Low Priority)

### Performance Optimization
- [ ] Implement caching for calculated charts
- [ ] Add database backend for large datasets
- [ ] Optimize SVG rendering for multiple charts
- [ ] Add lazy loading for pagination

### User Experience
- [ ] Add dark mode toggle
- [ ] Create keyboard shortcuts
- [ ] Implement help tooltips
- [ ] Add user preferences storage
- [ ] Create onboarding tutorial

### Advanced Features
- [ ] Add animation for chart transitions
- [ ] Implement chart comparison overlay
- [ ] Create custom query builder
- [ ] Add API endpoint for external access

## Testing & Documentation

### Testing
- [ ] Unit tests for chart visualization
- [ ] Unit tests for divisional calculations
- [ ] Integration tests for CSV processing
- [ ] Performance benchmarks
- [ ] Cross-browser testing for SVG

### Documentation
- [ ] API documentation for new modules
- [ ] User guide for Research interface
- [ ] Developer guide for extending divisionals
- [ ] Example notebooks for analysis

## Bug Fixes & Issues

### Known Issues
- [ ] None yet - to be discovered during development

### Improvements
- [ ] Optimize existing chart calculations
- [ ] Improve error messages
- [ ] Add logging for debugging

---

## Completed Tasks
- [x] Create future_work folder structure
- [x] Define requirements specification
- [x] Create comprehensive TODO list

---

**Note**: Strike through completed items using `[x]` checkbox or ~~strikethrough~~ syntax.