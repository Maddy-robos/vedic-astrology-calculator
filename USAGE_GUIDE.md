# Jyotish Chart Calculator - Usage Guide

## Quick Start

### 1. Interactive Chart Calculator
```bash
python3 main.py
```

### 2. See Sample Inputs
```bash
python3 sample_input_demo.py
```

### 3. Programmatic Examples
```bash
python3 example_usage.py
```

## Input Examples

### Birth Date & Time
```
Year: 1990
Month: 5
Day: 15
Hour: 14  (2 PM in 24-hour format)
Minute: 30
```

### Location Input

#### Option 1: City Lookup (Recommended)
```
Enter '1' for city lookup
Enter city name: mumbai

Results:
1. Mumbai, India
   Coordinates: 19.0760°, 72.8777°
   Timezone: Asia/Kolkata

2. Navi Mumbai, India
   Coordinates: 19.0330°, 73.0297°
   Timezone: Asia/Kolkata

Select city (1-2): 1
```

**Popular Cities Supported:**
- **India**: Mumbai, Delhi, Bangalore, Chennai, Kolkata, Hyderabad, Pune, Ahmedabad, Jaipur, Lucknow, etc.
- **USA**: New York, Los Angeles, Chicago, Houston, Philadelphia, Phoenix, San Antonio, San Diego, etc.
- **Global**: London, Tokyo, Singapore, Dubai, Hong Kong, Sydney, Toronto, Vancouver, etc.

#### Option 2: Manual Coordinates
```
Enter '2' for manual coordinates
Latitude: 19.0760  (positive for North)
Longitude: 72.8777 (positive for East)
```

### Timezone Input

#### Format 1: UTC Offset
```
UTC+05:30  (India Standard Time)
UTC-05:00  (US Eastern Standard Time)
UTC+08:00  (China/Singapore)
+05:30     (Short format)
-08:00     (Short format)
```

#### Format 2: IANA Timezone Names
```
Asia/Kolkata       (India)
America/New_York   (US Eastern)
Europe/London      (UK/GMT)
Asia/Tokyo         (Japan)
Asia/Dubai         (UAE)
Australia/Sydney   (Australia)
```

#### Common Timezone Examples
| Input | Description |
|-------|-------------|
| `UTC+05:30` | India, Sri Lanka |
| `UTC+08:00` | China, Singapore, Malaysia |
| `UTC+09:00` | Japan, South Korea |
| `UTC+04:00` | UAE, Oman |
| `UTC+06:00` | Bangladesh |
| `UTC+05:00` | Pakistan |
| `UTC-05:00` | US Eastern |
| `UTC-08:00` | US Pacific |
| `UTC+00:00` | UK, GMT |
| `UTC+01:00` | Central Europe |

### Ayanamsa & House System
```
Ayanamsa (default Lahiri): [Just press Enter for default]
House System (default Equal): [Just press Enter for default]
```

**Ayanamsa Options:**
- Lahiri (default) - Most commonly used
- Raman - Alternative system
- Krishnamurti - KP astrology system

**House System Options:**
- Equal (default) - 30° houses
- Placidus - Unequal houses (planned)

## Complete Sample Session

```
============================================================
           JYOTISH CHART CALCULATOR
============================================================

Enter Birth Date:
Year (YYYY): 1990
Month (1-12): 5
Day (1-31): 15

Enter Birth Time:
Hour (0-23): 14
Minute (0-59): 30

Enter Birth Location:
You can either:
1. Enter city name for automatic lookup
2. Enter coordinates manually

Enter '1' for city lookup or '2' for manual coordinates (default 1): 1
Enter city name: mumbai

Found 2 matching cities:
------------------------------------------------------------
 1. Mumbai, India
    Coordinates: 19.0760°, 72.8777°
    Timezone: Asia/Kolkata

 2. Navi Mumbai, India
    Coordinates: 19.0330°, 73.0297°
    Timezone: Asia/Kolkata

Select city (1-2) or 's' to search again: 1

Selected: Mumbai, India

Selected location: Mumbai, India
Timezone: Asia/Kolkata

Ayanamsa (default Lahiri): 
House System (default Equal): 

Calculating chart...
Chart calculation complete!

============================================================
                    MENU
============================================================
1. Chart Summary
2. Planetary Positions
3. House Analysis
4. Major Yogas
5. Save Chart to File
6. Calculate New Chart
7. Exit
------------------------------------------------------------
Enter your choice (1-7): 1
```

## Output Features

### 1. Chart Summary
- Birth details with location name
- Ascendant placement (rasi, degrees, nakshatra)
- Overall chart strength assessment
- Strongest planets and houses
- Aspect summary

### 2. Planetary Positions
- All 9 planetary positions
- Rasi placement
- Degrees within rasi
- Nakshatra and pada
- Retrograde status

### 3. House Analysis
- All 12 house details
- House lords and their placements
- House strength calculations
- Kendra/Trikona/Upachaya classifications

### 4. Yoga Detection
- Raj Yogas (Kendra-Trikona connections)
- Dhana Yogas (wealth combinations)
- Exchange Yogas (Parivartana)
- Conjunction analysis

### 5. JSON Export
- Complete chart data export
- Reusable for analysis
- Timestamp-based filename

## Quick Tips

1. **City Search**: Try partial names (e.g., "mumba" finds Mumbai)
2. **Multiple Results**: Cities are sorted by relevance
3. **Timezone Auto-Detection**: City lookup automatically sets timezone
4. **Manual Override**: Choose option 2 for precise coordinates
5. **Flexible Timezone**: Both UTC+05:30 and Asia/Kolkata work
6. **Default Options**: Press Enter to use defaults (Lahiri ayanamsa, Equal houses)

## Supported Locations

The system includes **200+ major cities** worldwide including:

- **All major Indian cities** (Mumbai, Delhi, Bangalore, Chennai, etc.)
- **US cities** (New York, Los Angeles, Chicago, Houston, etc.)
- **European cities** (London, Paris, Berlin, Rome, etc.)
- **Asian cities** (Tokyo, Singapore, Hong Kong, Dubai, etc.)
- **Other major global cities**

If your city isn't found, use manual coordinates (option 2).

## Error Handling

- Invalid dates/times are caught and explained
- Unknown cities prompt for retry or manual entry
- Invalid timezones are parsed or defaulted to UTC
- Chart calculation errors show helpful messages
- All inputs have validation and examples

## Need Help?

- Run `python3 sample_input_demo.py` for detailed examples
- Run `python3 sample_input_demo.py --interactive` for city lookup practice
- Check CLAUDE.md for technical documentation
- All functions include comprehensive help text

---

**Note**: Currently using placeholder planetary positions. For production accuracy, integrate with Swiss Ephemeris.