# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Vedic Astrology (Jyotish) Research Platform built in Python for astronomical calculations and astrological analysis. The project uses placeholder ephemeris data currently but is designed to integrate with Swiss Ephemeris for production use.

## Commands

### Development Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r jyotish-requirements.txt

# Run setup script to create folder structure
python setup_jyotish_structure.py
```

### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=CoreLibrary

# Generate HTML coverage report
pytest --cov=CoreLibrary --cov-report=html
```

### Code Quality
```bash
# Format code with Black
black .
black --check .  # Check without modifying

# Lint with flake8
flake8 .
flake8 CoreLibrary/  # Specific directory

# Type checking with mypy
mypy .
mypy CoreLibrary/
```

### Documentation
```bash
# Build HTML documentation
sphinx-build -b html docs/ docs/_build/
```

## Architecture

### Core Structure
```
JyotishResearch/
├── CentralData/         # Static reference data (JSON)
├── CoreLibrary/         # Main calculation modules
├── ResearchProjects/    # Research implementations
│   ├── FlightAccidents/ # Example project
│   └── _template/       # Template for new projects
├── Config/              # Configuration files
└── Examples/            # Example scripts
```

### Key Modules in CoreLibrary/

**Core Calculation Modules (✅ Implemented):**
1. **chart.py** - Complete birth chart generation and analysis
2. **graha.py** - Planet model with characteristics, dignity, and natural relationships
3. **rasi.py** - Zodiac sign model with Parashara's rasi drishti (sign aspects)
4. **bhava.py** - House model with traditional significations and strength calculations
5. **aspects.py** - Planetary aspects (drishti) with traditional rules and orb calculations
6. **bhava_analysis.py** - Comprehensive house analysis with lord placement and yoga detection
7. **conversions.py** - Astronomical coordinate transformations and ayanamsa calculations
8. **calculations_helper.py** - Utility functions for nakshatra, navamsa, and general calculations

**Additional Modules (⏳ In Development):**
9. **graha_positions.py** - Planetary position calculations (methods need completion)
10. **panchanga.py** - Five-fold almanac calculations (methods need completion)
11. **lordships.py** - House lordship and functional benefic/malefic determination (methods need completion)
12. **combustion.py** - Planetary combustion detection (methods need completion)
13. **dignity.py** - Panchadha Maitri calculations (to be implemented)
14. **rasi_drishti.py** - Additional sign-based aspects (to be implemented)
15. **strengths.py** - Shadbala calculations (to be implemented)

### Configuration Files

- `settings.json` - Default calculation settings (ayanamsa, location, precision)
- `ayanamsa_config.json` - Ayanamsa system configurations
- `location_defaults.json` - Default location settings

### Data Structure

Core reference data is in `CentralData/` with:
- `bhava_significations.json` - House significations
- `graha_characteristics.json` - Planetary characteristics
- `nakshatra_tables.json` - Lunar mansion data
- `panchanga_data.json` - Almanac data
- `planetary_positions.json` - Placeholder ephemeris data
- `rasi_data.json` - Zodiac sign data

## Development Patterns

### Interactive Usage

For interactive chart calculation, use the main script:
```bash
python3 main.py
```

**New Features:**
- **Smart Location Lookup**: Enter city names (e.g., "mumbai", "new york") for automatic coordinate and timezone detection
- **Comprehensive Timezone Support**: Accepts both UTC offsets (UTC+05:30) and IANA timezones (Asia/Kolkata)
- **Large City Database**: 200+ major cities worldwide with coordinates and timezones

**Input Examples:**
```
# Location input examples
Enter city name: mumbai          -> Mumbai, India (19.0760°, 72.8777°)
Enter city name: new york        -> New York, USA (40.7128°, -74.0060°)

# Timezone examples  
UTC+05:30                        -> India Standard Time
+05:30                          -> Short format for UTC+05:30
Asia/Kolkata                    -> IANA timezone name
America/New_York                -> US Eastern timezone
```

This provides a menu-driven interface to:
- Input birth details (date, time, location) 
- **City-based location lookup** with automatic timezone detection
- View chart summary and planetary positions  
- Analyze house placements and strength
- Identify major yogas
- Save charts to JSON files

For usage examples and location demos, run:
```bash
python3 sample_input_demo.py      # See sample inputs and city lookup demo
python3 example_usage.py          # Programmatic usage examples
```

### Basic Chart Calculation
```python
from datetime import datetime
from CoreLibrary.chart import Chart

# Method 1: Using birth datetime
birth_datetime = datetime(1990, 5, 15, 14, 30)
chart = Chart(
    birth_datetime=birth_datetime,
    latitude=28.6139,      # Delhi coordinates
    longitude=77.2090,
    timezone_str='Asia/Kolkata',
    ayanamsa='Lahiri',
    house_system='Equal'
)

# Method 2: Using individual components
chart = Chart.from_birth_details(
    year=1990, month=5, day=15, 
    hour=14, minute=30,
    latitude=28.6139, longitude=77.2090,
    timezone_str='Asia/Kolkata'
)

# Get chart data
ascendant = chart.get_ascendant()
grahas = chart.get_graha_positions()
bhavas = chart.get_bhavas()
aspects = chart.get_aspects()
summary = chart.get_chart_summary()

# Export to JSON
json_data = chart.to_json('chart_output.json')
```

### Using Individual Modules
```python
from CoreLibrary.graha import Graha
from CoreLibrary.rasi import Rasi
from CoreLibrary.bhava import Bhava
from CoreLibrary.aspects import Aspects

# Create individual objects
sun = Graha('Sun', longitude=15.5)
aries = Rasi('Aries')
first_house = Bhava(1, cusp_degree=0.0, rasi='Aries')

# Calculate aspects between grahas
graha_dict = {'Sun': sun, 'Moon': Graha('Moon', longitude=95.2)}
aspects_calc = Aspects(graha_dict)
all_aspects = aspects_calc.get_all_graha_aspects()
```

### Creating New Research Projects
```bash
# Copy template
cp -r ResearchProjects/_template ResearchProjects/YourProject
```

Project structure:
- `data/` - Raw data and charts
- `analysis/` - Analysis scripts
- `reports/` - Findings and visualizations

## Important Notes

1. **Ephemeris Data**: Currently uses placeholder data. For production, integrate Swiss Ephemeris:
   ```python
   import swisseph as swe
   swe.set_ephe_path('/path/to/ephemeris/data')
   ```

2. **Timezone Handling**: Always use timezone-aware datetime objects

3. **Ayanamsa Systems**: Supports Lahiri (default), Raman, and Krishnamurti

4. **Test Files**: `test_calculations.py` and `test_models.py` exist but are currently empty stubs

5. **No Build Process**: Pure Python project, no compilation needed

6. **Batch Processing**: Supports concurrent processing using ProcessPoolExecutor for research projects

7. **Data Models**: All calculations return dictionaries with standardized keys for easy data processing

8. **Current Status**: 
   - ✅ **8 core modules fully implemented** (chart.py, graha.py, rasi.py, bhava.py, aspects.py, bhava_analysis.py, conversions.py, calculations_helper.py)
   - ⏳ **4 modules need method completion** (graha_positions.py, panchanga.py, lordships.py, combustion.py)
   - 📝 **3 modules to be implemented** (dignity.py, rasi_drishti.py, strengths.py)

9. **Placeholder Data**: Currently uses sample planetary positions. For production accuracy, integrate Swiss Ephemeris

10. **Usage**: Run `python main.py` for interactive chart calculation, or use the Chart class directly in your code