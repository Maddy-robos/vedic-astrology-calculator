# Jyotish Research Platform

A comprehensive Python-based platform for Vedic Astrology (Jyotish) research and analysis.

## 🌟 Features

### Core Calculation Modules

1. **Graha Positions** (`graha_positions.py`)
   - Calculate planetary positions in rasis with degrees
   - Tropical to sidereal conversions
   - Support for multiple ayanamsa systems
   - Ascendant and house cusp calculations

2. **Panchanga** (`panchanga.py`)
   - Vara (weekday) and lord
   - Tithi (lunar day) and lord
   - Nakshatra (constellation) and lord
   - Yoga (Sun-Moon combination) and lord
   - Karana (half-tithi) and lord

3. **Lordships** (`lordships.py`)
   - House lordship calculations
   - Functional benefic/malefic determination
   - Yoga Karaka identification
   - Special house group analysis (Kendra, Trikona, Dusthana, Upachaya)

4. **Bhava Analysis** (`bhava_analysis.py`)
   - Grahas in specific bhavas
   - Bhava from graha calculations
   - House strength analysis
   - Special house occupancy (Kendras, Trikonas, etc.)

5. **Dignity with Panchadha Maitri** (`dignity.py`)
   - Exaltation, debilitation, mooltrikona, own sign
   - 5-fold friendship calculation
   - Natural + temporary friendship
   - Dignity scoring system (1-9 scale)

6. **Combustion** (`combustion.py`)
   - Check if grahas are combust
   - Check if house lords are combust
   - Distance from Sun calculations
   - Combustion analysis and effects

7. **Rasi Drishti** (`rasi_drishti.py`)
   - Sign-based aspects
   - Dual signs → all other dual signs
   - Cardinal signs → fixed signs (except next)
   - Fixed signs → cardinal signs (except next)

## 📁 Project Structure

```
JyotishResearch/
├── CentralData/
│   ├── ephemeris/          # Planetary position data
│   ├── panchanga/          # Panchanga tables
│   ├── reference/          # Core reference data
│   └── modifications/      # Modified data versions
├── CoreLibrary/
│   ├── calculations/       # All calculation modules
│   ├── models/            # Data models
│   ├── utils/             # Helper functions
│   └── tests/             # Unit tests
├── ResearchProjects/
│   ├── FlightAccidents/   # Example research project
│   └── _template/         # Template for new projects
├── Documentation/         # API docs, methodology
├── Config/               # Configuration files
└── Examples/             # Example scripts
```

## 🚀 Getting Started

### 1. Installation

```bash
# Clone or download the project
cd JyotishResearch

# Create virtual environment
python -m venv venv
source venv/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Setup Script

```bash
python setup_jyotish_structure.py
```

This creates the complete folder structure and template files.

### 3. Basic Usage

```python
from datetime import datetime
from graha_positions import GrahaPositions
from lordships import Lordships
from dignity import Dignity
from combustion import Combustion

# Define birth details
birth_time = datetime(1990, 5, 15, 14, 30)
location = {
    'latitude': 28.6139,    # Delhi
    'longitude': 77.2090,
    'timezone': 'Asia/Kolkata'
}

# Calculate positions
graha_calc = GrahaPositions(birth_time, location)
positions = graha_calc.get_simplified_positions()
ascendant = graha_calc.calculate_ascendant()['rasi']

# Analyze lordships
lord_calc = Lordships(ascendant)
print(f"7th Lord: {lord_calc.get_house_lord(7)}")

# Check dignity
dignity_calc = Dignity(positions)
sun_dignity = dignity_calc.get_panchadha_maitri('Sun')
print(f"Sun Dignity: {sun_dignity['dignity']}")

# Check combustion
combust_calc = Combustion(positions, ascendant)
is_7th_lord_combust = combust_calc.is_combust('7th Lord')
print(f"7th Lord Combust: {is_7th_lord_combust['is_combust']}")
```

## 📊 Research Projects

### Creating a New Research Project

1. Copy the `_template` folder in `ResearchProjects/`
2. Rename to your project name
3. Structure:
   ```
   YourProject/
   ├── data/          # Raw data, charts
   ├── analysis/      # Analysis scripts
   └── reports/       # Findings, visualizations
   ```

### Example: Flight Accidents Research

```python
# Load flight accident data
import pandas as pd
from main_example import analyze_chart

# Read accident data
accidents = pd.read_csv('ResearchProjects/FlightAccidents/data/raw_data.csv')

# Analyze each chart
results = []
for _, accident in accidents.iterrows():
    dt = pd.to_datetime(accident['datetime'])
    location = {
        'latitude': accident['latitude'],
        'longitude': accident['longitude'],
        'timezone': accident['timezone']
    }
    
    chart_analysis = analyze_chart(dt, location, accident['flight_id'])
    results.append(chart_analysis)

# Look for patterns...
```

## 🔧 Advanced Features

### Custom Calculations

```python
# Example: Find all charts where 8th lord is combust
def find_8th_lord_combust(chart_database):
    combust_8th_lords = []
    
    for chart in chart_database:
        positions = chart['positions']
        ascendant = chart['ascendant']
        
        combust = Combustion(positions, ascendant)
        if combust.is_combust('8th Lord')['is_combust']:
            combust_8th_lords.append(chart)
    
    return combust_8th_lords
```

### Batch Analysis

```python
# Analyze multiple charts
from concurrent.futures import ProcessPoolExecutor

def analyze_batch(chart_list):
    with ProcessPoolExecutor() as executor:
        results = executor.map(analyze_single_chart, chart_list)
    return list(results)
```

## 📚 Module Reference

### Core Data (`core_data.py`)
- `GRAHAS`: List of all grahas
- `RASIS`: List of all rasis
- `RASI_DATA`: Rasi characteristics
- `GRAHA_DIGNITIES`: Exaltation, debilitation, etc.
- `NATURAL_FRIENDSHIP`: Graha relationships
- `PANCHANGA_LORDS`: Lords for all panchanga elements

### Key Functions

#### Lordships
- `get_house_lord(house_number)`: Get lord of a house
- `get_houses_owned_by(graha)`: Get houses owned by graha
- `is_kendra_lord(graha)`: Check if graha rules kendra
- `get_yoga_karaka()`: Find yoga karaka graha

#### Dignity
- `get_panchadha_maitri(graha)`: Full dignity analysis
- `is_dignified(graha, min_score)`: Check if dignified
- `get_all_dignities()`: Dignity for all grahas

#### Combustion
- `is_combust(graha_or_lord)`: Check combustion
- `get_all_combust_grahas()`: List all combust grahas
- `get_combust_lords()`: List combust house lords

## ⚠️ Important Notes

1. **Ephemeris Data**: The current `graha_positions.py` uses placeholder data. For accurate calculations, integrate Swiss Ephemeris:
   ```python
   import swisseph as swe
   swe.set_ephe_path('/path/to/ephemeris/data')
   ```

2. **Ayanamsa**: Different ayanamsa values will give different results. The platform supports:
   - Lahiri (default)
   - Raman
   - Krishnamurti

3. **Time Zones**: Always use proper timezone-aware datetime objects for accuracy.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📖 Additional Resources

- [Swiss Ephemeris Documentation](https://www.astro.com/swisseph/)
- [Vedic Astrology Calculations](https://www.astro.com/astrology/)
- Research papers in `Documentation/papers/`

## 📝 License

This project is for educational and research purposes. Please respect traditional knowledge and use responsibly.

## 🙏 Acknowledgments

- Traditional Jyotish texts and teachers
- Swiss Ephemeris team
- Open source astronomy libraries

---

For questions or support, please open an issue or contact the maintainers.