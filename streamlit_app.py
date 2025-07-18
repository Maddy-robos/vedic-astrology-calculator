import streamlit as st
import pandas as pd
from datetime import datetime, time
import json
import os
import sys
from pathlib import Path
import requests
from time import sleep

# Add project root and CoreLibrary to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'CoreLibrary'))

from chart import Chart
from calculations_helper import CalculationsHelper
from graha import Graha
from aspect_analysis import AspectAnalysis
from chart_visualization import NorthIndianChart
from chara_karaka import CharaKaraka

# Set page config
st.set_page_config(
    page_title="Vedic Astrology Calculator",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #FF6B6B;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF5252;
        transform: translateY(-2px);
    }
    .info-box {
        background-color: #F7F9FC;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
        margin: 1rem 0;
    }
    .planet-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 3px solid #4ECDC4;
    }
    .house-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 3px solid #95E1D3;
    }
    .aspect-card {
        background-color: #FFF5F5;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        border-left: 3px solid #F38181;
    }
    .yoga-card {
        background-color: #FFF9E6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #FFD93D;
    }
    h1 {
        color: #2C3E50;
        text-align: center;
        margin-bottom: 2rem;
    }
    h2 {
        color: #34495E;
        margin-top: 2rem;
    }
    h3 {
        color: #555;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px;
        background-color: #F0F0F0;
        border-radius: 5px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6B6B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Load city data
@st.cache_data
def load_city_data():
    """Load city database from JSON file"""
    city_file = Path(__file__).parent / "CentralData" / "city_coordinates.json"
    if city_file.exists():
        with open(city_file, 'r') as f:
            data = json.load(f)
            # Convert list to dictionary for easier lookup
            city_dict = {}
            for city in data:
                # Create multiple keys for flexible matching
                city_name_lower = city['name'].lower()
                city_dict[city_name_lower] = city
                # Also add just the city name without country
                city_only = city_name_lower.split(',')[0].strip()
                city_dict[city_only] = city
            return city_dict
    return {}

# Initialize session state
if 'chart' not in st.session_state:
    st.session_state.chart = None
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False
if 'stored_charts' not in st.session_state:
    st.session_state.stored_charts = []
if 'show_admin_download' not in st.session_state:
    st.session_state.show_admin_download = False

def lookup_city(city_name, city_data):
    """Look up city coordinates and timezone from local database"""
    city_lower = city_name.lower().strip()
    
    # Direct match
    if city_lower in city_data:
        return {
            'name': city_data[city_lower]['name'],
            'latitude': city_data[city_lower]['latitude'],
            'longitude': city_data[city_lower]['longitude'],
            'timezone': city_data[city_lower]['timezone']
        }
    
    # Partial match - check if search term is in any key
    matches = []
    for key, value in city_data.items():
        # Check if search term is part of the key
        if city_lower in key:
            matches.append(value)
    
    if matches:
        return {
            'name': matches[0]['name'],
            'latitude': matches[0]['latitude'],
            'longitude': matches[0]['longitude'],
            'timezone': matches[0]['timezone']
        }
    
    return None

def find_city_matches(search_term, city_data, limit=5):
    """Find all cities matching the search term"""
    search_lower = search_term.lower().strip()
    matches = []
    
    # First pass: exact start matches
    for key, value in city_data.items():
        if key.startswith(search_lower):
            matches.append({
                'name': value['name'],
                'coords': f"{value['latitude']:.2f}, {value['longitude']:.2f}",
                'data': value,
                'source': 'local',
                'match_type': 'start'
            })
    
    # Second pass: contains matches (if we need more)
    if len(matches) < limit:
        for key, value in city_data.items():
            if search_lower in key and not key.startswith(search_lower):
                matches.append({
                    'name': value['name'],
                    'coords': f"{value['latitude']:.2f}, {value['longitude']:.2f}",
                    'data': value,
                    'source': 'local',
                    'match_type': 'contains'
                })
                if len(matches) >= limit:
                    break
    
    # Sort by match type (start matches first) and limit
    matches.sort(key=lambda x: (x['match_type'] != 'start', x['name']))
    return matches[:limit]

def save_new_location(city_data):
    """Save new location to the city database and deduplicate"""
    city_file = Path(__file__).parent / "CentralData" / "city_coordinates.json"
    
    try:
        # Load existing data
        if city_file.exists():
            with open(city_file, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        # Check if location already exists (to avoid duplicates)
        city_key = city_data['name'].lower()
        
        exists = False
        for existing_city in existing_data:
            if existing_city['name'].lower() == city_key:
                exists = True
                break
        
        if not exists:
            # Add new location
            new_entry = {
                'name': city_data['name'],
                'latitude': city_data['latitude'],
                'longitude': city_data['longitude'],
                'timezone': city_data['timezone']
            }
            existing_data.append(new_entry)
            
            # Sort by name for better organization
            existing_data.sort(key=lambda x: x['name'])
            
            # Save back to file
            with open(city_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return True
    except Exception as e:
        st.error(f"Error saving location: {str(e)}")
    
    return False

def deduplicate_cities():
    """Remove duplicate cities from the database"""
    city_file = Path(__file__).parent / "CentralData" / "city_coordinates.json"
    
    try:
        if not city_file.exists():
            return
        
        with open(city_file, 'r') as f:
            data = json.load(f)
        
        # Use a set to track unique city names (case-insensitive)
        seen_names = set()
        unique_cities = []
        
        for city in data:
            city_key = city['name'].lower()
            if city_key not in seen_names:
                seen_names.add(city_key)
                unique_cities.append(city)
        
        # Sort by name
        unique_cities.sort(key=lambda x: x['name'])
        
        # Save deduplicated data
        with open(city_file, 'w') as f:
            json.dump(unique_cities, f, indent=2)
        
        removed_count = len(data) - len(unique_cities)
        if removed_count > 0:
            st.success(f"Removed {removed_count} duplicate cities from database")
        
    except Exception as e:
        st.error(f"Error deduplicating cities: {str(e)}")

@st.cache_data
def geocode_city(city_name):
    """Use Nominatim API to geocode a city name"""
    try:
        # Add delay to respect Nominatim's usage policy
        sleep(1)
        
        # Nominatim API endpoint
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': city_name,
            'format': 'json',
            'limit': 5,
            'extratags': 1,
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'VedicAstrologyCalculator/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        if results:
            # Get the first result
            result = results[0]
            
            # Extract location info
            lat = float(result['lat'])
            lon = float(result['lon'])
            display_name = result['display_name']
            
            # Try to determine timezone from coordinates
            # This is a simplified approach - for production, use a proper timezone API
            timezone = guess_timezone(lat, lon)
            
            new_location = {
                'name': display_name.split(',')[0] + ', ' + display_name.split(',')[-1].strip(),
                'latitude': lat,
                'longitude': lon,
                'timezone': timezone,
                'source': 'Nominatim'
            }
            
            # Save the new location to database
            save_new_location(new_location)
            
            return new_location
    except Exception as e:
        st.error(f"Geocoding error: {str(e)}")
    
    return None

def guess_timezone(lat, lon):
    """Guess timezone based on coordinates (simplified)"""
    # This is a very basic approximation
    # For production, use a proper timezone API like timezonefinder
    
    # Rough timezone estimation based on longitude
    if lon >= -12 and lon <= 0:
        return "Europe/London"
    elif lon > 0 and lon <= 15:
        return "Europe/Paris"
    elif lon > 15 and lon <= 30:
        return "Europe/Athens"
    elif lon > 30 and lon <= 45:
        return "Asia/Dubai"
    elif lon > 45 and lon <= 60:
        return "Asia/Karachi"
    elif lon > 60 and lon <= 82.5:
        return "Asia/Kolkata"
    elif lon > 82.5 and lon <= 97.5:
        return "Asia/Dhaka"
    elif lon > 97.5 and lon <= 112.5:
        return "Asia/Bangkok"
    elif lon > 112.5 and lon <= 127.5:
        return "Asia/Shanghai"
    elif lon > 127.5 and lon <= 142.5:
        return "Asia/Tokyo"
    elif lon > 142.5 and lon <= 157.5:
        return "Australia/Sydney"
    elif lon > 157.5 or lon < -157.5:
        return "Pacific/Auckland"
    elif lon >= -157.5 and lon < -142.5:
        return "Pacific/Honolulu"
    elif lon >= -142.5 and lon < -127.5:
        return "America/Los_Angeles"
    elif lon >= -127.5 and lon < -112.5:
        return "America/Denver"
    elif lon >= -112.5 and lon < -97.5:
        return "America/Chicago"
    elif lon >= -97.5 and lon < -82.5:
        return "America/New_York"
    elif lon >= -82.5 and lon < -67.5:
        return "America/New_York"
    elif lon >= -67.5 and lon < -52.5:
        return "America/Sao_Paulo"
    else:
        return "UTC"

def format_timezone(tz_str):
    """Format timezone string for display"""
    if tz_str.startswith('UTC'):
        return tz_str
    elif tz_str.startswith(('+', '-')):
        return f"UTC{tz_str}"
    else:
        return tz_str

# Title
st.markdown("<h1>🪐 Vedic Astrology Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-bottom: 2rem;'>Calculate your birth chart using traditional Vedic astrology</p>", unsafe_allow_html=True)

# Sidebar for input
with st.sidebar:
    st.markdown("## Birth Details")
    
    # Date and Time inputs
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input(
            "Birth Date",
            value=datetime(1990, 1, 1).date(),
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.now().date()
        )
    
    with col2:
        birth_time_str = st.text_input(
            "Birth Time",
            value="12:00:00",
            help="Enter time as HH:MM:SS (e.g., 14:30:25 or 08:15:00)",
            placeholder="14:30:25"
        )
    
    st.markdown("### Location")
    
    # City lookup with autocomplete
    city_data = load_city_data()
    
    # Add deduplicate button in expander
    with st.expander("🔧 Database Management"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Remove Duplicates", help="Clean up duplicate cities in database"):
                deduplicate_cities()
                st.rerun()
        with col2:
            st.caption(f"Total cities: {len(city_data)}")
    
    # City autocomplete input with real-time suggestions
    # Search input with real-time autocomplete
    city_input = st.text_input(
        "City Name",
        placeholder="Start typing city name (e.g., Mumbai, New York, London)",
        help="Autocomplete suggestions appear as you type",
        key="city_search_input"
    )
        
    # Show autocomplete suggestions as you type
    if city_input and len(city_input.strip()) >= 2:
        search_term = city_input.strip()
        
        # Find local matches
        local_matches = find_city_matches(search_term, city_data, limit=5)
        
        if local_matches:
            st.markdown("**🏙️ Select from suggestions:**")
            
            # Display matches as selectable options
            for i, match in enumerate(local_matches):
                if st.button(
                    f"📍 {match['name']} ({match['coords']})", 
                    key=f"match_{i}_{hash(search_term)}",
                    use_container_width=True
                ):
                    st.session_state.selected_city = match['data']
                    st.rerun()
        
        # Online search for 4+ characters
        elif len(search_term) >= 4:
            if st.button(
                f"🔍 Search '{search_term}' online", 
                key=f"online_{hash(search_term)}",
                use_container_width=True
            ):
                with st.spinner(f"Searching for '{search_term}'..."):
                    online_result = geocode_city(search_term)
                    if online_result:
                        st.session_state.selected_city = online_result
                        st.success(f"✅ Found: {online_result['name']}")
                        st.rerun()
                    else:
                        st.warning(f"❌ No results found for '{search_term}'")
    
    # Show popular cities when no input
    elif not city_input:
        st.markdown("**🌟 Popular Cities:**")
        popular_cities = ['mumbai', 'delhi', 'bangalore', 'chennai', 'new york', 'london', 'tokyo']
        
        cols = st.columns(3)
        for i, city_key in enumerate(popular_cities):
            if city_key in city_data:
                col = cols[i % 3]
                with col:
                    if st.button(
                        f"🏙️ {city_data[city_key]['name']}", 
                        key=f"popular_{city_key}",
                        use_container_width=True
                    ):
                        st.session_state.selected_city = city_data[city_key]
                        st.rerun()
    
    # Check if a city was selected
    city_info = None
    if 'selected_city' in st.session_state:
        city_info = st.session_state.selected_city
        
        # Display selected city info
        if city_info:
            st.success(f"✓ Selected: {city_info['name']}")
            st.caption(f"📍 Lat: {city_info['latitude']:.4f}, Lon: {city_info['longitude']:.4f}")
            st.caption(f"🕐 Timezone: {format_timezone(city_info['timezone'])}")
            
            # Add clear button
            if st.button("❌ Clear selection", key="clear_city"):
                del st.session_state.selected_city
                st.rerun()
    
    # Manual coordinate input
    st.markdown("#### Manual Coordinates")
    col1, col2 = st.columns(2)
    
    with col1:
        if city_info:
            latitude = st.number_input(
                "Latitude",
                value=city_info['latitude'],
                min_value=-90.0,
                max_value=90.0,
                format="%.4f"
            )
        else:
            latitude = st.number_input(
                "Latitude",
                value=28.6139,
                min_value=-90.0,
                max_value=90.0,
                format="%.4f",
                help="Delhi: 28.6139"
            )
    
    with col2:
        if city_info:
            longitude = st.number_input(
                "Longitude",
                value=city_info['longitude'],
                min_value=-180.0,
                max_value=180.0,
                format="%.4f"
            )
        else:
            longitude = st.number_input(
                "Longitude",
                value=77.2090,
                min_value=-180.0,
                max_value=180.0,
                format="%.4f",
                help="Delhi: 77.2090"
            )
    
    # Timezone
    if city_info:
        timezone_str = st.text_input(
            "Timezone",
            value=city_info['timezone'],
            help="e.g., Asia/Kolkata, UTC+05:30"
        )
    else:
        timezone_str = st.text_input(
            "Timezone",
            value="Asia/Kolkata",
            help="e.g., Asia/Kolkata, UTC+05:30"
        )
    
    # Settings button
    st.markdown("---")
    if st.button("⚙️ Advanced Settings"):
        st.session_state.show_settings = not st.session_state.show_settings
    
    # Settings section (hidden by default)
    if st.session_state.show_settings:
        st.markdown("### Advanced Settings")
        
        # House system
        house_system = st.selectbox(
            "House System",
            options=["Placidus", "Equal", "Whole Sign"],
            index=0,  # Placidus as default
            help="Select the house system for calculations"
        )
        
        # Ayanamsa
        ayanamsa = st.selectbox(
            "Ayanamsa",
            options=["Lahiri", "Raman", "Krishnamurti"],
            index=0,
            help="Select the ayanamsa for sidereal calculations"
        )
    else:
        # Default values when settings are hidden
        house_system = "Placidus"
        ayanamsa = "Lahiri"
    
    st.markdown("---")
    
    # Calculate button
    calculate_button = st.button("🔮 Calculate Chart", type="primary", use_container_width=True)

def parse_time_input(time_str):
    """Parse time input in various formats"""
    try:
        # Remove any extra spaces
        time_str = time_str.strip()
        
        # Handle different formats
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:  # HH:MM
                hour, minute = int(parts[0]), int(parts[1])
                return time(hour, minute, 0)
            elif len(parts) == 3:  # HH:MM:SS
                hour, minute, second = int(parts[0]), int(parts[1]), int(parts[2])
                return time(hour, minute, second)
        else:
            # Assume just hour
            hour = int(time_str)
            return time(hour, 0, 0)
            
    except (ValueError, IndexError):
        raise ValueError(f"Invalid time format: '{time_str}'. Use HH:MM or HH:MM:SS format.")
    
    raise ValueError(f"Invalid time format: '{time_str}'. Use HH:MM or HH:MM:SS format.")

def store_chart_data(chart, city_info):
    """Store chart data for admin download"""
    try:
        birth_info = chart.chart_data['birth_info']
        chart_record = {
            'timestamp': datetime.now().isoformat(),
            'birth_datetime': birth_info['birth_datetime'].isoformat() if hasattr(birth_info['birth_datetime'], 'isoformat') else str(birth_info['birth_datetime']),
            'birth_place': city_info['name'] if city_info else 'Manual Entry',
            'latitude': birth_info['latitude'],
            'longitude': birth_info['longitude'],
            'timezone': birth_info['timezone'],
            'ayanamsa': birth_info['ayanamsa'],
            'house_system': birth_info['house_system']
        }
        
        # Add to stored charts
        st.session_state.stored_charts.append(chart_record)
        
        # Keep only last 100 entries to prevent memory issues
        if len(st.session_state.stored_charts) > 100:
            st.session_state.stored_charts = st.session_state.stored_charts[-100:]
            
    except Exception as e:
        # Silently fail to not interfere with chart calculation
        pass

# Main content area
if calculate_button:
    try:
        # Parse time input
        birth_time = parse_time_input(birth_time_str)
        
        # Combine date and time
        birth_datetime = datetime.combine(birth_date, birth_time)
        
        # Create chart
        with st.spinner("Calculating your birth chart..."):
            chart = Chart(
                birth_datetime=birth_datetime,
                latitude=latitude,
                longitude=longitude,
                timezone_str=timezone_str,
                ayanamsa=ayanamsa,
                house_system=house_system
            )
            st.session_state.chart = chart
            
            # Store chart data for admin download
            store_chart_data(chart, city_info)
        
        st.success("✨ Chart calculated successfully!")
        
    except ValueError as e:
        st.error(f"❌ Time format error: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error calculating chart: {str(e)}")
        st.stop()

# Display chart if available
if st.session_state.chart:
    chart = st.session_state.chart
    
    # Chart Summary
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    summary = chart.get_chart_summary()
    grahas = chart.get_graha_positions()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Lagna (Ascendant):** {summary['ascendant']['rasi']} {summary['ascendant']['degrees']}")
        moon_sign = grahas.get('Moon', {}).get('rasi', 'Unknown')
        st.markdown(f"**Rasi (Moon Sign):** {moon_sign}")
    with col2:
        sun_sign = grahas.get('Sun', {}).get('rasi', 'Unknown')
        st.markdown(f"**Sun Sign:** {sun_sign}")
        moon_nakshatra = grahas.get('Moon', {}).get('nakshatra', {})
        if isinstance(moon_nakshatra, dict):
            st.markdown(f"**Nakshatra:** {moon_nakshatra.get('name', 'Unknown')}")
        else:
            st.markdown(f"**Nakshatra:** {moon_nakshatra}")
    with col3:
        st.markdown(f"**Ayanamsa:** {chart.ayanamsa}")
        st.markdown(f"**House System:** {chart.house_system}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["📊 Chart", "🪐 Planets", "🏠 Houses", "👁️ Bhava Aspects", "👑 Chara Karakas", "📅 Panchanga", "☌ Conjunctions", "🎯 Yogas", "💾 Export"])
    
    with tab1:
        st.markdown("## Birth Chart Visualization")
        
        # Chart type selector
        col1, col2 = st.columns([2, 1])
        with col1:
            chart_type = st.selectbox(
                "Select Chart Type",
                options=[
                    "D1 - Rasi Chart", 
                    "D2 - Hora Chart", 
                    "D3 - Drekkana Chart",
                    "D9 - Navamsa Chart",
                    "D10 - Dasamsa Chart"
                ],
                help="Choose which divisional chart to display"
            )
        with col2:
            chart_size = st.slider(
                "Chart Size",
                min_value=400,
                max_value=700,
                value=600,
                step=50,
                help="Adjust chart size"
            )
        
        # Get chart data
        ascendant = chart.get_ascendant()
        ascendant_deg = ascendant['longitude']
        grahas = chart.get_graha_positions()
        
        if "D1" in chart_type:
            # D1 Chart - Display North Indian chart using rasi-based placement
            summary = chart.get_chart_summary()
            lagna_sign = summary['ascendant']['rasi']
            
            # Use rasi-based placement (traditional Vedic method)
            # Planets are placed based on their rasi, not degree-based bhava positions
            house_planets = CalculationsHelper.get_rasi_based_house_placements(
                lagna_sign, grahas
            )
            
            # Chart title
            chart_title = "Birth Chart (Rasi - D1)"
            info_text = f"**Lagna**: {lagna_sign}"
            
        else:
            # Divisional charts (D2, D3, D9, D10)
            if "D2" in chart_type:
                div_type = "D2"
                div_name = "Hora"
            elif "D3" in chart_type:
                div_type = "D3"
                div_name = "Drekkana"
            elif "D9" in chart_type:
                div_type = "D9"
                div_name = "Navamsa"
            elif "D10" in chart_type:
                div_type = "D10"
                div_name = "Dasamsa"
            
            # Get divisional house placements using unified method
            house_planets = CalculationsHelper.get_divisional_house_placements(
                div_type, ascendant_deg, grahas
            )
            
            # Get divisional ascendant
            if div_type == "D2":
                lagna_sign = CalculationsHelper.get_hora_rasi(ascendant_deg)
            elif div_type == "D3":
                lagna_sign = CalculationsHelper.get_drekkana_rasi(ascendant_deg)
            elif div_type == "D9":
                lagna_sign = CalculationsHelper.get_navamsa_rasi(ascendant_deg)
            elif div_type == "D10":
                lagna_sign = CalculationsHelper.get_dasamsa_rasi(ascendant_deg)
            
            # Chart title and info
            chart_title = f"{div_name} Chart ({div_type})"
            info_text = f"**{div_name} Lagna**: {lagna_sign}"
        
        # Create and display North Indian chart
        ni_chart = NorthIndianChart(width=chart_size, height=chart_size)
        svg_string = ni_chart.generate_chart(
            lagna_sign=lagna_sign,
            house_planets=house_planets,
            chart_title=chart_title,
            graha_positions=grahas
        )
        
        # Center the chart
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown(svg_string, unsafe_allow_html=True)
        
        # Show chart summary below
        st.markdown("### Chart Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(info_text)
        with col2:
            if "D1" in chart_type:
                moon_sign = grahas.get('Moon', {}).get('rasi', 'Unknown')
                st.markdown(f"**Moon Sign:** {moon_sign}")
            else:
                total_planets = sum(len(planets) for planets in house_planets.values())
                st.markdown(f"**Planets Placed:** {total_planets}")
        with col3:
            if "D1" in chart_type:
                sun_sign = grahas.get('Sun', {}).get('rasi', 'Unknown')
                st.markdown(f"**Sun Sign:** {sun_sign}")
            else:
                occupied_houses = len([h for h, p in house_planets.items() if p])
                st.markdown(f"**Houses Occupied:** {occupied_houses}")
        with col4:
            st.markdown(f"**Chart Type:** {chart_type.split(' - ')[0]}")

    with tab2:
        st.markdown("## Detailed Planetary Positions")
        
        # Get planet positions and house placements
        planets = chart.get_graha_positions()
        bhava_analysis = chart.get_bhava_analysis()
        graha_placements = bhava_analysis.get('graha_placements', {})
        
        # Create reverse mapping of planet to house
        planet_houses = {}
        for house_num, planets_in_house in graha_placements.items():
            for planet in planets_in_house:
                planet_houses[planet] = house_num
        
        # Create comprehensive planetary data table
        planetary_data = []
        for name, data in planets.items():
            # Calculate degrees within sign
            degrees_in_sign = data['longitude'] % 30
            
            # Get house number
            house_num = planet_houses.get(name, 'N/A')
            
            # Get dignity
            graha = Graha(name, data['longitude'])
            graha.rasi = data['rasi']
            dignity = graha.get_dignity()
            
            # Get nakshatra name
            nakshatra_info = data.get('nakshatra', 'Unknown')
            if isinstance(nakshatra_info, dict):
                nakshatra_name = nakshatra_info.get('name', 'Unknown')
            else:
                nakshatra_name = str(nakshatra_info)
            
            # Retrograde status
            retrograde = "Yes" if data.get('is_retrograde', False) else "No"
            
            planetary_data.append({
                'Planet': name,
                'Sign': data['rasi'],
                'Degrees': f"{degrees_in_sign:.2f}°",
                'Nakshatra': nakshatra_name,
                'House': house_num,
                'Dignity': dignity if dignity else 'Normal',
                'Retrograde': retrograde
            })
        
        # Display as sortable table
        import pandas as pd
        df = pd.DataFrame(planetary_data)
        
        # Add sorting options
        col1, col2 = st.columns([1, 3])
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                options=['Planet', 'Sign', 'House', 'Dignity', 'Retrograde'],
                help="Choose column to sort by"
            )
        
        # Sort dataframe
        if sort_by == 'House':
            # Convert house to numeric for proper sorting
            df['House_Numeric'] = pd.to_numeric(df['House'], errors='coerce')
            df_sorted = df.sort_values('House_Numeric').drop('House_Numeric', axis=1)
        else:
            df_sorted = df.sort_values(sort_by)
        
        # Display table
        st.dataframe(
            df_sorted,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Planet': st.column_config.TextColumn('🪐 Planet', width='medium'),
                'Sign': st.column_config.TextColumn('♈ Sign', width='medium'),
                'Degrees': st.column_config.TextColumn('📐 Degrees', width='small'),
                'Nakshatra': st.column_config.TextColumn('⭐ Nakshatra', width='medium'),
                'House': st.column_config.TextColumn('🏠 House', width='small'),
                'Dignity': st.column_config.TextColumn('👑 Dignity', width='medium'),
                'Retrograde': st.column_config.TextColumn('↩️ Retrograde', width='small')
            }
        )
        
        # Additional planetary analysis
        st.markdown("### Planetary Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Strong planets
            strong_planets = [row['Planet'] for row in planetary_data 
                            if 'Exalted' in row['Dignity'] or 'Own' in row['Dignity']]
            if strong_planets:
                st.success(f"**Strong Planets**: {', '.join(strong_planets)}")
            
        with col2:
            # Retrograde planets
            retrograde_planets = [row['Planet'] for row in planetary_data if row['Retrograde'] == 'Yes']
            if retrograde_planets:
                st.warning(f"**Retrograde Planets**: {', '.join(retrograde_planets)}")
            
        with col3:
            # Debilitated planets
            weak_planets = [row['Planet'] for row in planetary_data 
                          if 'Debilitated' in row['Dignity']]
            if weak_planets:
                st.error(f"**Debilitated Planets**: {', '.join(weak_planets)}")

    with tab3:
        
        # Get house data and analysis
        houses = chart.get_bhavas()
        bhava_analysis = chart.get_bhava_analysis()
        all_bhavas = bhava_analysis.get('all_bhavas', {})
        graha_placements = bhava_analysis.get('graha_placements', {})
        
        # Display houses in grid
        col1, col2 = st.columns(2)
        
        for i, (bhava_num, bhava_data) in enumerate(houses.items()):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                st.markdown(f"<div class='house-card'>", unsafe_allow_html=True)
                st.markdown(f"### House {bhava_num}")
                
                # Get lord from bhava analysis
                analysis = all_bhavas.get(bhava_num, {})
                lord = analysis.get('bhava_lord', 'Unknown')
                st.markdown(f"**Sign:** {bhava_data['rasi']} | **Lord:** {lord}")
                # Calculate degrees within sign (0-30)
                cusp_in_sign = bhava_data['cusp_degree'] % 30
                st.markdown(f"**Cusp:** {bhava_data['rasi']} {cusp_in_sign:.1f}°")
                
                # Planets in house from graha_placements
                planets_in_house = graha_placements.get(str(bhava_num), [])
                if planets_in_house:
                    st.markdown(f"**Planets:** {', '.join(planets_in_house)}")
                
                # House strength from analysis
                strength_data = analysis.get('strength_analysis', {})
                if strength_data:
                    strength = strength_data.get('total_strength', 0) * 100
                    strength_category = strength_data.get('strength_category', 'Unknown')
                    st.progress(strength / 100, text=f"{strength_category} ({strength:.0f}/100)")
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("## Bhava Aspects (Drishti to Houses)")
        
        # Create aspect analyzer (always rasi-based)
        aspect_analyzer = AspectAnalysis(chart.chart_data, aspect_mode='rasi')
        
        # Display mode info and house selection
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("🎯 **Traditional Rasi-based Aspects**: Planets aspect complete signs (rasis), counting forward for normal planets and backward for retrograde planets.")
        
        # House selection
        with col2:
            house_options = ['All'] + list(range(1, 13))
            selected_option = st.selectbox(
                "Select House",
                options=house_options,
                format_func=lambda x: "All Houses" if x == 'All' else f"House {x}",
                help="Choose which house to analyze aspects to"
            )
        
        if selected_option == 'All':
            # Display all houses in a compact grid format
            st.markdown("### All House Aspects Overview")
            
            try:
                # Get aspects for all houses
                all_house_data = []
                for bhava_num in range(1, 13):
                    analysis = aspect_analyzer.get_bhava_aspects_analysis(bhava_num)
                    all_house_data.append((bhava_num, analysis))
                
                # Display in 3 columns
                col1, col2, col3 = st.columns(3)
                columns = [col1, col2, col3]
                
                for i, (bhava_num, bhava_analysis) in enumerate(all_house_data):
                    col = columns[i % 3]
                    
                    with col:
                        # Compact house card
                        st.markdown(f"""
                        <div class='house-card' style='margin-bottom: 1rem; padding: 0.8rem;'>
                            <h4 style='margin: 0 0 0.5rem 0; color: #2C3E50;'>🏠 House {bhava_num}</h4>
                            <div style='font-size: 0.9em; margin-bottom: 0.5rem;'>
                                <strong>{bhava_analysis.get('bhava_name', f'House {bhava_num}')}</strong><br>
                                {bhava_analysis.get('bhava_rasi', 'Unknown')} {bhava_analysis.get('bhava_degrees', 0):.1f}°
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if bhava_analysis and 'aspects' in bhava_analysis and bhava_analysis['aspects']:
                            aspects = bhava_analysis['aspects']
                            summary = bhava_analysis.get('summary', {})
                            
                            # Compact metrics
                            total = summary.get('total_aspects', 0)
                            benefic = summary.get('benefic_aspects', 0)
                            malefic = summary.get('malefic_aspects', 0)
                            
                            # Color-coded metrics
                            if malefic > benefic:
                                color = "#FF6B6B"  # Red for malefic
                                icon = "🔴"
                            elif benefic > malefic:
                                color = "#4ECDC4"  # Green for benefic
                                icon = "🟢"
                            else:
                                color = "#FFD93D"  # Yellow for neutral
                                icon = "⚪"
                            
                            st.markdown(f"""
                                <div style='background: {color}20; padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem;'>
                                    {icon} <strong>{total}</strong> aspects<br>
                                    <small>🟢 {benefic} | 🔴 {malefic}</small>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Compact aspect list
                            for aspect in aspects[:3]:  # Show only top 3 aspects
                                graha = aspect['graha']
                                aspect_type = aspect['aspect_type'].replace(' Aspect', '')
                                nature_emoji = "🟢" if aspect['benefic_nature'] == 'Benefic' else "🔴"
                                
                                st.markdown(f"""
                                    <div style='font-size: 0.8em; padding: 0.3rem; margin: 0.2rem 0; 
                                         background: #F8F9FA; border-radius: 4px; border-left: 3px solid {color};'>
                                        {nature_emoji} <strong>{graha}</strong> {aspect_type}<br>
                                        <small>{aspect['drishti_effect']}</small>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            if len(aspects) > 3:
                                st.markdown(f"<small style='color: #666;'>... and {len(aspects) - 3} more</small>", 
                                          unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div style='padding: 0.5rem; background: #F0F0F0; border-radius: 5px; text-align: center;'>
                                    <small style='color: #666;'>No aspects</small>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Overall summary
                st.markdown("### Overall Summary")
                total_aspects_all = sum(len(data[1].get('aspects', [])) for data in all_house_data)
                total_benefic_all = sum(data[1].get('summary', {}).get('benefic_aspects', 0) for data in all_house_data)
                total_malefic_all = sum(data[1].get('summary', {}).get('malefic_aspects', 0) for data in all_house_data)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Aspects", total_aspects_all)
                with col2:
                    st.metric("🟢 Benefic", total_benefic_all)
                with col3:
                    st.metric("🔴 Malefic", total_malefic_all)
                with col4:
                    benefic_ratio = (total_benefic_all / total_aspects_all * 100) if total_aspects_all > 0 else 0
                    st.metric("🟢 Benefic %", f"{benefic_ratio:.1f}%")
                    
            except Exception as e:
                st.error(f"Error analyzing all house aspects: {str(e)}")
        
        elif selected_option and selected_option != 'All':
            # Single house detailed view
            selected_bhava = selected_option
            try:
                # Get aspects analysis for selected bhava
                bhava_analysis = aspect_analyzer.get_bhava_aspects_analysis(selected_bhava)
                
                if bhava_analysis and 'aspects' in bhava_analysis and bhava_analysis['aspects']:
                    st.markdown(f"### 🏠 House {selected_bhava}: {bhava_analysis['bhava_name']}")
                    
                    # Compact header with key info
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Sign:** {bhava_analysis['bhava_rasi']} {bhava_analysis['bhava_degrees']:.1f}°")
                    with col2:
                        summary = bhava_analysis.get('summary', {})
                        if 'overall_influence' in summary:
                            influence = summary['overall_influence']
                            if 'Auspicious' in influence:
                                st.success(f"🟢 {influence}")
                            elif 'Inauspicious' in influence:
                                st.error(f"🔴 {influence}")
                            else:
                                st.info(f"⚪ {influence}")
                    
                    # Compact aspect display in 2 columns
                    aspects = bhava_analysis['aspects']
                    col1, col2 = st.columns(2)
                    
                    for i, aspect in enumerate(aspects):
                        col = col1 if i % 2 == 0 else col2
                        
                        with col:
                            nature_color = "#4ECDC4" if aspect['benefic_nature'] == 'Benefic' else "#FF6B6B"
                            nature_emoji = "🟢" if aspect['benefic_nature'] == 'Benefic' else "🔴"
                            
                            st.markdown(f"""
                            <div style='background: {nature_color}15; padding: 0.8rem; margin: 0.5rem 0; 
                                 border-radius: 8px; border-left: 4px solid {nature_color};'>
                                <div style='font-weight: bold; margin-bottom: 0.3rem;'>
                                    {nature_emoji} {aspect['graha']} → H{selected_bhava}
                                </div>
                                <div style='font-size: 0.9em; color: #666; margin-bottom: 0.3rem;'>
                                    {aspect['aspect_type']} ({aspect['aspect_angle']}°)
                                </div>
                                <div style='font-size: 0.85em;'>
                                    <div>From: {aspect['graha_position']['rasi']} {aspect['graha_position']['degrees']:.1f}°</div>
                                    <div>Dignity: {aspect['dignity']}</div>
                                    <div>Effect: {aspect['drishti_effect']}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Compact summary
                    if 'summary' in bhava_analysis:
                        summary = bhava_analysis['summary']
                        st.markdown("#### Quick Summary")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🎯 Total", summary.get('total_aspects', 0))
                        with col2:
                            st.metric("🟢 Benefic", summary.get('benefic_aspects', 0))
                        with col3:
                            st.metric("🔴 Malefic", summary.get('malefic_aspects', 0))
                
                else:
                    st.info(f"🔍 No significant aspects found to House {selected_bhava}")
                    
            except Exception as e:
                st.error(f"Error analyzing aspects to House {selected_bhava}: {str(e)}")
    
    with tab5:
        st.markdown("## 👑 Chara Karakas (Variable Significators)")
        
        # Get Chara Karakas
        chara_karakas = chart.get_chara_karakas()
        
        if chara_karakas:
            # Display standard calculation
            st.markdown("### Standard Method (By Degrees in Sign)")
            st.markdown("*Planets sorted by their degrees in their respective signs*")
            
            standard_data = []
            for result in chara_karakas['standard']:
                karaka_info = CharaKaraka.KARAKA_NAMES.get(result.karaka, result.karaka)
                standard_data.append({
                    'Karaka': f"{result.karaka} - {karaka_info}",
                    'Planet': result.planet,
                    'Degrees': f"{result.degrees:.2f}°"
                })
            
            if standard_data:
                df_standard = pd.DataFrame(standard_data)
                st.dataframe(df_standard, use_container_width=True, hide_index=True)
            
            # Display advanced calculation
            st.markdown("### Advanced Method (By Total Degrees Traveled)")
            st.markdown("*Considers retrograde motion and total distance traveled in current sign*")
            
            advanced_data = []
            for result in chara_karakas['advanced']:
                karaka_info = CharaKaraka.KARAKA_NAMES.get(result.karaka, result.karaka)
                advanced_data.append({
                    'Karaka': f"{result.karaka} - {karaka_info}",
                    'Planet': result.planet,
                    'Total Degrees': f"{result.degrees:.2f}°"
                })
            
            if advanced_data:
                df_advanced = pd.DataFrame(advanced_data)
                st.dataframe(df_advanced, use_container_width=True, hide_index=True)
                
                # Display detailed retrograde motion information
                if 'retrograde_data' in chara_karakas:
                    st.markdown("### 🔍 Planetary Motion Details")
                    st.markdown("*Click on any planet below to see its detailed motion history*")
                    
                    retrograde_data = chara_karakas['retrograde_data']
                    
                    # Create expanders for each planet
                    for result in chara_karakas['advanced']:
                        planet_name = result.planet
                        
                        if planet_name in retrograde_data and retrograde_data[planet_name]:
                            motion_data = retrograde_data[planet_name]
                            
                            # Determine if planet is currently retrograde or has retrograded
                            is_retro = motion_data.get('is_retrograde', False)
                            has_retrograded = motion_data['max_forward'] > motion_data['current_position']
                            
                            # Create emoji based on motion status
                            status_emoji = "🔴" if is_retro else ("🟡" if has_retrograded else "🟢")
                            
                            with st.expander(f"{status_emoji} {planet_name} Motion Timeline"):
                                # Display motion timeline
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.markdown("**Entry into Sign**")
                                    if motion_data.get('entry_date'):
                                        st.write(f"📅 {motion_data['entry_date'].strftime('%Y-%m-%d %H:%M')}")
                                    st.write(f"📐 {motion_data['entry_point']:.2f}°")
                                
                                with col2:
                                    st.markdown("**Maximum Forward**")
                                    if motion_data.get('max_forward_date'):
                                        st.write(f"📅 {motion_data['max_forward_date'].strftime('%Y-%m-%d %H:%M')}")
                                    st.write(f"📐 {motion_data['max_forward']:.2f}°")
                                
                                with col3:
                                    st.markdown("**Current Position**")
                                    st.write(f"📐 {motion_data['current_position']:.2f}°")
                                    status = "Retrograde" if is_retro else ("Direct" if not has_retrograded else "Direct (was retrograde)")
                                    st.write(f"🔄 {status}")
                                
                                # Show retrograde dates if available
                                if motion_data.get('retrograde_start_date'):
                                    st.markdown("**Retrograde Period**")
                                    st.write(f"Started: {motion_data['retrograde_start_date'].strftime('%Y-%m-%d %H:%M')}")
                                
                                # Visual progress bar
                                st.markdown("**Motion Progress**")
                                
                                # Calculate percentages for visualization
                                total_range = 30.0  # Full sign is 30 degrees
                                entry_pct = (motion_data['entry_point'] / total_range) * 100
                                current_pct = (motion_data['current_position'] / total_range) * 100
                                max_pct = (motion_data['max_forward'] / total_range) * 100
                                
                                # Visual timeline using Streamlit components
                                # Create progress bars to show motion
                                progress_col1, progress_col2 = st.columns([1, 1])
                                
                                with progress_col1:
                                    # Forward motion progress
                                    forward_progress = (motion_data['max_forward'] - motion_data['entry_point']) / 30.0
                                    st.progress(forward_progress, text=f"Forward: {motion_data['entry_point']:.1f}° → {motion_data['max_forward']:.1f}°")
                                
                                with progress_col2:
                                    if has_retrograded:
                                        # Retrograde motion progress
                                        retro_progress = (motion_data['max_forward'] - motion_data['current_position']) / 30.0
                                        st.progress(retro_progress, text=f"Retrograde: {motion_data['max_forward']:.1f}° → {motion_data['current_position']:.1f}°")
                                    else:
                                        st.info("No retrograde motion")
                                
                                # Alternative visual representation using metrics
                                st.markdown("**Degree Positions**")
                                position_col1, position_col2, position_col3 = st.columns(3)
                                
                                with position_col1:
                                    st.metric("Entry", f"{motion_data['entry_point']:.2f}°", delta=None)
                                
                                with position_col2:
                                    delta_from_entry = motion_data['max_forward'] - motion_data['entry_point']
                                    st.metric("Maximum", f"{motion_data['max_forward']:.2f}°", delta=f"+{delta_from_entry:.2f}°")
                                
                                with position_col3:
                                    delta_from_max = motion_data['current_position'] - motion_data['max_forward']
                                    st.metric("Current", f"{motion_data['current_position']:.2f}°", delta=f"{delta_from_max:.2f}°")
                                
                                # Summary statistics
                                st.markdown("**Motion Summary**")
                                total_travel = motion_data.get('total_travel', 0)
                                forward_travel = motion_data['max_forward'] - motion_data['entry_point']
                                backward_travel = motion_data['max_forward'] - motion_data['current_position'] if has_retrograded else 0
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Travel", f"{total_travel:.2f}°")
                                with col2:
                                    st.metric("Forward", f"{forward_travel:.2f}°")
                                with col3:
                                    st.metric("Backward", f"{backward_travel:.2f}°")
            
            # Karaka significations
            st.markdown("### Karaka Significations")
            col1, col2 = st.columns(2)
            
            karaka_meanings = {
                'AK': ('Atma Karaka', 'Soul, Self, Life purpose'),
                'AmK': ('Amatya Karaka', 'Career, Profession, Authority'),
                'BK': ('Bhratri Karaka', 'Siblings, Courage, Communication'),
                'MK': ('Matri Karaka', 'Mother, Emotions, Home'),
                'PiK': ('Pitru Karaka', 'Father, Ancestors, Dharma'),
                'PK': ('Putra Karaka', 'Children, Creativity, Intelligence'),
                'GK': ('Gnati Karaka', 'Enemies, Obstacles, Competition'),
                'DK': ('Dara Karaka', 'Spouse, Marriage, Partnerships')
            }
            
            for i, (karaka, (full_name, signifies)) in enumerate(karaka_meanings.items()):
                col = col1 if i % 2 == 0 else col2
                with col:
                    st.markdown(f"**{karaka} - {full_name}**")
                    st.markdown(f"*{signifies}*")
        else:
            st.info("Unable to calculate Chara Karakas")
    
    with tab6:
        st.markdown("## 📅 Panchanga (Five Limbs of Time)")
        
        # Get Panchanga
        panchanga = chart.get_panchanga()
        
        if panchanga:
            # Display all 5 limbs in a structured way
            for limb_name, limb_data in panchanga.items():
                if limb_name == 'vara':
                    st.markdown(f"### 🌅 Vara (Weekday)")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Day", limb_data['name'])
                    with col2:
                        st.metric("Lord", limb_data['lord'])
                
                elif limb_name == 'tithi':
                    st.markdown(f"### 🌙 Tithi (Lunar Day)")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tithi", f"{limb_data['number']} - {limb_data['name']}")
                    with col2:
                        st.metric("Lord", limb_data['lord'])
                    with col3:
                        st.metric("Progress", f"{limb_data['percentage_complete']:.1f}%")
                
                elif limb_name == 'nakshatra':
                    st.markdown(f"### ⭐ Nakshatra (Lunar Mansion)")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Nakshatra", f"{limb_data['number']} - {limb_data['name']}")
                    with col2:
                        st.metric("Lord", limb_data['lord'])
                    with col3:
                        st.metric("Pada", limb_data['pada'])
                    with col4:
                        st.metric("Progress", f"{limb_data['percentage_complete']:.1f}%")
                
                elif limb_name == 'yoga':
                    st.markdown(f"### 🔗 Yoga (Sun-Moon Combination)")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Yoga", f"{limb_data['number']} - {limb_data['name']}")
                    with col2:
                        nature = "Benefic" if limb_data['benefic'] else "Malefic"
                        if limb_data['benefic']:
                            st.success(f"🟢 {nature}")
                        else:
                            st.error(f"🔴 {nature}")
                    with col3:
                        st.metric("Progress", f"{limb_data['percentage_complete']:.1f}%")
                
                elif limb_name == 'karana':
                    st.markdown(f"### 🌗 Karana (Half Tithi)")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Karana", f"{limb_data['number']} - {limb_data['name']}")
                    with col2:
                        st.metric("Type", limb_data['type'])
                    with col3:
                        nature = "Benefic" if limb_data['benefic'] else "Malefic"
                        if limb_data['benefic']:
                            st.success(f"🟢 {nature}")
                        else:
                            st.error(f"🔴 {nature}")
                    with col4:
                        st.metric("Progress", f"{limb_data['percentage_complete']:.1f}%")
            
            # Summary table
            st.markdown("### 📋 Panchanga Summary")
            summary_data = {
                'Element': ['Vara', 'Tithi', 'Nakshatra', 'Yoga', 'Karana'],
                'Value': [
                    panchanga['vara']['name'],
                    panchanga['tithi']['name'],
                    f"{panchanga['nakshatra']['name']} Pada {panchanga['nakshatra']['pada']}",
                    panchanga['yoga']['name'],
                    panchanga['karana']['name']
                ],
                'Lord/Nature': [
                    panchanga['vara']['lord'],
                    panchanga['tithi']['lord'],
                    panchanga['nakshatra']['lord'],
                    '🟢 Benefic' if panchanga['yoga']['benefic'] else '🔴 Malefic',
                    '🟢 Benefic' if panchanga['karana']['benefic'] else '🔴 Malefic'
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
        else:
            st.info("Unable to calculate Panchanga")
    
    with tab7:
        st.markdown("## Conjunctions & Mutual Aspects")
        
        # Get aspects data
        aspects_data = chart.get_aspects()
        
        if aspects_data and 'patterns' in aspects_data:
            patterns = aspects_data['patterns']
            
            # Display conjunctions
            if patterns.get('conjunctions'):
                st.markdown("### Conjunctions")
                for conj in patterns['conjunctions']:
                    st.markdown(f"<div class='aspect-card'>", unsafe_allow_html=True)
                    st.markdown(f"**{conj['graha1']} ☌ {conj['graha2']}**")
                    st.markdown(f"Separation: {conj['angular_distance']:.1f}° | Strength: {conj['strength']}")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Display mutual aspects
            if patterns.get('mutual_aspects'):
                st.markdown("### Mutual Aspects")
                for mutual in patterns['mutual_aspects']:
                    st.markdown(f"<div class='aspect-card'>", unsafe_allow_html=True)
                    st.markdown(f"**{mutual['graha1']} ↔ {mutual['graha2']}**")
                    st.markdown(f"Angular distance: {mutual['angular_distance']:.1f}°")
                    st.markdown(f"Combined strength: {mutual['combined_strength']:.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Display strong aspects
            if patterns.get('strong_aspects'):
                st.markdown("### Strong Aspects")
                for aspect in patterns['strong_aspects']:
                    aspect_info = aspect['aspect_info']
                    st.markdown(f"<div class='aspect-card'>", unsafe_allow_html=True)
                    st.markdown(f"**{aspect['aspecting_graha']} → {aspect['aspected_graha']}**")
                    if 'strongest_aspect' in aspect_info:
                        strongest = aspect_info['strongest_aspect']
                        st.markdown(f"Aspect angle: {strongest['angle']}° | Orb: {strongest['exact_orb']:.1f}°")
                        st.markdown(f"Strength: {strongest['strength']:.2f} ({strongest['orb_category']})")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Display summary
            if 'summary' in aspects_data:
                summary = aspects_data['summary']
                st.markdown("### Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Aspects", summary.get('total_aspects', 0))
                with col2:
                    st.metric("Conjunctions", summary.get('total_conjunctions', 0))
                with col3:
                    st.metric("Average Strength", f"{summary.get('average_strength', 0):.2f}")
        else:
            st.info("No significant aspects found in the chart.")
    
    with tab8:
        st.markdown("## Yogas (Planetary Combinations)")
        
        # Get yogas
        yogas = chart.find_yogas()
        
        # Check if any yogas exist
        has_yogas = any(len(yoga_list) > 0 for yoga_list in yogas.values())
        
        if has_yogas:
            # Display yogas by category
            if yogas.get('raj_yogas'):
                st.markdown("### Raj Yogas (Power & Authority)")
                for yoga in yogas['raj_yogas']:
                    st.markdown(f"<div class='yoga-card'>", unsafe_allow_html=True)
                    if isinstance(yoga, dict):
                        st.markdown(f"**{yoga.get('name', 'Raj Yoga')}**")
                        st.markdown(f"*{yoga.get('description', 'Royal combination present')}*")
                        if 'formed_by' in yoga:
                            st.markdown(f"Formed by: {yoga['formed_by']}")
                    else:
                        st.markdown(f"**Raj Yoga**: {yoga}")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            if yogas.get('dhana_yogas'):
                st.markdown("### Dhana Yogas (Wealth)")
                for yoga in yogas['dhana_yogas']:
                    st.markdown(f"<div class='yoga-card'>", unsafe_allow_html=True)
                    if isinstance(yoga, dict):
                        st.markdown(f"**{yoga.get('type', 'Dhana Yoga')}**")
                        if 'lords' in yoga:
                            st.markdown(f"Formed by lords: {', '.join(yoga['lords'])}")
                    else:
                        st.markdown(f"**Dhana Yoga**: {yoga}")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            if yogas.get('spiritual_yogas'):
                st.markdown("### Spiritual Yogas")
                for yoga in yogas['spiritual_yogas']:
                    st.markdown(f"<div class='yoga-card'>", unsafe_allow_html=True)
                    st.markdown(f"**Spiritual Yoga**: {yoga}")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            if yogas.get('challenging_yogas'):
                st.markdown("### Challenging Yogas")
                for yoga in yogas['challenging_yogas']:
                    st.markdown(f"<div class='yoga-card'>", unsafe_allow_html=True)
                    st.markdown(f"**Challenging Yoga**: {yoga}")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No significant yogas found in the chart.")
    
    with tab9:
        st.markdown("## Export Chart Data")
        
        # Get full chart data
        birth_datetime = chart.chart_data['birth_info']['birth_datetime']
        chart_data = {
            'birth_details': {
                'datetime': birth_datetime.isoformat() if hasattr(birth_datetime, 'isoformat') else str(birth_datetime),
                'latitude': chart.chart_data['birth_info']['latitude'],
                'longitude': chart.chart_data['birth_info']['longitude'],
                'timezone': chart.chart_data['birth_info']['timezone'],
                'ayanamsa': chart.ayanamsa,
                'house_system': chart.house_system
            },
            'summary': chart.get_chart_summary(),
            'planets': chart.get_graha_positions(),
            'houses': chart.get_bhavas(),
            'aspects': chart.get_aspects(),
            'yogas': chart.find_yogas()
        }
        
        # Custom JSON encoder to handle datetime objects
        def json_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return str(obj)
            else:
                return str(obj)
        
        # Convert to JSON with custom encoder
        json_str = json.dumps(chart_data, indent=2, default=json_encoder)
        
        # Download button
        # Create safe filename
        if isinstance(birth_datetime, datetime):
            filename_date = birth_datetime.strftime('%Y%m%d_%H%M')
        else:
            filename_date = "chart"
        
        st.download_button(
            label="📥 Download Chart as JSON",
            data=json_str,
            file_name=f"vedic_chart_{filename_date}.json",
            mime="application/json"
        )
        
        # Display preview
        with st.expander("Preview JSON Data"):
            # Parse the JSON string to ensure it's properly formatted
            try:
                preview_data = json.loads(json_str)
                st.json(preview_data)
            except Exception as e:
                st.error(f"Error displaying preview: {str(e)}")
                st.code(json_str[:1000] + "..." if len(json_str) > 1000 else json_str)

else:
    # Welcome message when no chart is calculated
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown("### 🙏 Welcome to the Vedic Astrology Calculator")
    st.markdown("""
    This application calculates your Vedic (Jyotish) birth chart using traditional methods.
    
    **How to use:**
    1. Enter your birth date and exact time in the sidebar
    2. Enter your birth city or manual coordinates
    3. Click 'Calculate Chart' to generate your chart
    4. Explore different tabs to view planets, houses, aspects, and yogas
    
    **Features:**
    - 🌍 Automatic city lookup with timezone detection
    - 🏠 Multiple house systems (Placidus default)
    - 🪐 Detailed planetary positions with dignities
    - 👁️ Traditional aspect calculations
    - 🎯 Yoga detection
    - 💾 Export chart data as JSON
    
    **New!** Check out the Research Interface in the sidebar for batch chart processing and analysis!
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Hidden admin download section (activate via browser console)
# To show: Run in browser console: sessionStorage.setItem('show_admin', 'true'); location.reload();
if st.session_state.get('show_admin_download', False) or (hasattr(st, 'query_params') and 'admin' in st.query_params):
    st.markdown("---")
    st.markdown("## 🔒 Admin Panel")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Stored Charts", len(st.session_state.stored_charts))
    with col2:
        if st.button("🗑️ Clear All Data"):
            st.session_state.stored_charts = []
            st.success("All stored data cleared!")
    with col3:
        if st.session_state.stored_charts:
            # Prepare download data
            download_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_charts': len(st.session_state.stored_charts),
                'charts': st.session_state.stored_charts
            }
            
            json_str = json.dumps(download_data, indent=2)
            
            st.download_button(
                label="📥 Download All Data",
                data=json_str,
                file_name=f"astrology_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Show recent charts
    if st.session_state.stored_charts:
        st.markdown("### Recent Charts")
        df = pd.DataFrame(st.session_state.stored_charts[-10:])  # Show last 10
        st.dataframe(df, use_container_width=True)

# JavaScript to enable admin panel
st.markdown("""
<script>
// Check if admin mode should be enabled
if (sessionStorage.getItem('show_admin') === 'true') {
    // This will be checked on next rerun
    fetch('/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({admin: true})
    });
}

// Add console command helper
console.log('🔮 Vedic Astrology Calculator');
console.log('To enable admin panel, run: sessionStorage.setItem("show_admin", "true"); location.reload();');
console.log('To disable admin panel, run: sessionStorage.removeItem("show_admin"); location.reload();');
</script>
""", unsafe_allow_html=True)

# Check for admin mode via URL or session
try:
    if 'admin' in st.query_params:
        st.session_state.show_admin_download = True
except:
    pass

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>Built with ❤️ using Vedic Astrology principles</p>", unsafe_allow_html=True)