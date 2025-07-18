# Requirements for Vedic Astrology Research Platform

## 1. North Indian Chart Visualization

### Chart Layout Requirements
- **Format**: Diamond-shaped chart with 12 houses
- **House Numbering**: Anti-clockwise from top center (House 1)
- **Fixed Houses**: House positions remain constant
- **Moving Signs**: Zodiac signs rotate based on Lagna position
- **Visual Elements**:
  - Clear house boundaries with black lines
  - House numbers displayed prominently
  - Zodiac sign indicators (1-12 or sign glyphs)
  - Planet positions with proper symbols/abbreviations
  - Special marking for Lagna (ascendant)

### Technical Requirements
- **Implementation**: SVG-based for precise rendering
- **Responsive**: Scale appropriately for different screen sizes
- **Interactive**: Hover effects to show planet details
- **Export**: Ability to save as PNG/SVG

## 2. Research Interface

### CSV Upload Functionality
- **Accepted Formats**: CSV, Excel (.xlsx)
- **Required Columns**:
  - name (string)
  - date (YYYY-MM-DD)
  - time (HH:MM:SS)
  - latitude (decimal degrees)
  - longitude (decimal degrees)
  - timezone (IANA format or UTC offset)
- **Optional Columns**:
  - gender
  - place_name
  - notes

### JHD File Support (NEW)
- **Accepted Formats**: 
  - Individual .jhd files
  - Multiple .jhd files simultaneously
  - ZIP archives containing .jhd files
- **JHD Format Compatibility**:
  - Jagannatha Hora native format
  - 17+ line format with birth details
  - Geographic coordinates and timezone data
  - Place name and country information
- **Bidirectional Conversion**:
  - JHD to CSV conversion
  - CSV to JHD conversion
  - Batch processing capabilities

### Batch Processing
- **Capacity**: Handle 100+ charts efficiently
- **Progress Indicator**: Show processing status
- **Error Handling**: 
  - Skip invalid rows with error logging
  - Provide downloadable error report
- **Caching**: Store processed charts for quick access

### Display Features
- **Layout Options**:
  - Grid view (2-3 charts per row)
  - List view with expandable details
  - Comparison view (side-by-side)
- **Pagination**: 10, 20, or 50 charts per page
- **Filtering**:
  - By date range
  - By specific planetary positions
  - By yoga presence
- **Sorting**:
  - By name
  - By date/time
  - By specific planetary positions

## 3. Divisional Charts

### Initial Implementation (Phase 1)
- **D1**: Rasi Chart (Birth Chart)
- **D9**: Navamsa Chart (Marriage & Dharma)

### Full Implementation (Phase 2)
Following Parashara's system:
- **D2**: Hora Chart (Wealth)
- **D3**: Drekkana Chart (Siblings, Courage)
- **D4**: Chaturthamsa Chart (Property, Home)
- **D5**: Panchamsa Chart (Progeny)
- **D7**: Saptamsa Chart (Children)
- **D10**: Dasamsa Chart (Career, Status)
- **D12**: Dwadasamsa Chart (Parents, Lineage)
- **D16**: Shodasamsa Chart (Vehicles, Comforts)
- **D20**: Vimsamsa Chart (Spiritual Progress)
- **D24**: Chaturvimsamsa Chart (Education, Learning)
- **D30**: Trimsamsa Chart (Evils, Misfortunes)
- **D40**: Khavedamsa Chart (Maternal Legacy)
- **D45**: Akshavedamsa Chart (Paternal Legacy)
- **D60**: Shastiamsa Chart (Past Karma)

### Calculation Requirements
- **Accuracy**: Follow traditional Parashara methods
- **Validation**: Cross-verify with established software
- **Performance**: Calculate all divisionals in < 1 second

## 4. Export Functionality

### Supported Formats
- **PDF**: Professional report with charts and analysis
- **Excel**: Tabular data with multiple sheets
- **JSON**: Complete chart data for further processing
- **PNG/SVG**: Individual chart images
- **CSV**: Standardized birth data format
- **JHD**: Individual files or ZIP archives (NEW)

### Export Options
- **Single Chart**: Full detailed report
- **Batch Export**: Multiple charts in one file
- **Custom Selection**: Choose specific data points
- **Format Conversion**: 
  - Convert loaded data between CSV and JHD formats
  - Maintain data integrity across formats
  - Preserve timezone and coordinate information

### Export Data Integrity Requirements (PENDING FIXES)
- **CSV Export Completeness**: 
  - MUST include latitude/longitude coordinates for all charts
  - MUST preserve original birth location data
  - MUST maintain timezone information accuracy
- **Planetary Data Accuracy**:
  - MUST include proper dignity calculations (exaltation, own sign, debilitation)
  - MUST display correct planetary strengths and classifications
  - MUST match dignity calculations from main application interface

## 5. Analysis Tools

### Statistical Analysis
- **Planetary Distribution**: Across signs/houses
- **Yoga Frequency**: Common combinations
- **Pattern Detection**: Recurring themes
- **Time-based Analysis**: Trends by birth periods

### Research Features
- **Correlation Tools**: Find common patterns
- **Group Analysis**: Compare cohorts
- **Custom Queries**: SQL-like filtering
- **Visualization**: Charts and graphs

## 6. Performance Requirements

### Speed
- **Single Chart**: < 100ms calculation
- **Batch Processing**: 100 charts in < 10 seconds
- **Page Load**: < 2 seconds
- **Export Generation**: < 5 seconds for 100 charts

### Scalability
- **Concurrent Users**: Support 10+ simultaneous users
- **Data Storage**: Efficient caching system
- **Memory Usage**: Optimize for Streamlit Cloud limits

## 7. User Interface

### Design Principles
- **Clean**: Minimal, distraction-free interface
- **Intuitive**: Easy navigation for non-technical users
- **Responsive**: Works on desktop and tablet
- **Accessible**: Follow WCAG guidelines

### Key Features
- **Dark Mode**: Optional dark theme
- **Keyboard Shortcuts**: Quick navigation
- **Help System**: Contextual tooltips
- **Save Preferences**: Remember user settings

## 8. Future Enhancements

### Advanced Features
- **Dasha Systems**: Vimshottari, Yogini, etc.
- **Transit Analysis**: Current planetary positions
- **Muhurta**: Auspicious timing calculator
- **Compatibility**: Relationship matching

### Integration
- **API Access**: RESTful API for external tools
- **Plugin System**: Extensible architecture
- **Cloud Storage**: Save charts to cloud
- **Mobile App**: Companion mobile application