#!/usr/bin/env python3
"""
Debug script for chart calculations
"""

import sys
import os
from datetime import datetime

# Add CoreLibrary to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'CoreLibrary'))

from chart import Chart

def debug_chart():
    """Debug the problematic chart calculation"""
    print("=== DEBUGGING CHART CALCULATION ===")
    print("Date: 1993 Dec 10, 20:25 Tirupati")
    print("Expected: Cancer Ascendant, Punarvasu Nakshatra")
    print("Actual: Showing wrong positions")
    print()
    
    # Test the problematic date: 1993 Dec 10, 20:25 Tirupati
    birth_datetime = datetime(1993, 12, 10, 20, 25)
    
    try:
        chart = Chart(
            birth_datetime=birth_datetime,
            latitude=13.6288,      # Tirupati coordinates
            longitude=79.4192,
            timezone_str='Asia/Kolkata',
            ayanamsa='Lahiri',
            house_system='Equal'
        )
        
        print('=== CHART DEBUG INFO ===')
        print(f'Birth Date: {birth_datetime}')
        print(f'Location: Tirupati (13.6288°N, 79.4192°E)')
        print(f'Timezone: Asia/Kolkata')
        print()
        
        # Get chart data
        ascendant = chart.get_ascendant()
        grahas = chart.get_graha_positions()
        
        print('=== ASCENDANT ===')
        print(f'Ascendant: {ascendant}')
        print()
        
        print('=== GRAHA POSITIONS ===')
        for graha_name, graha_data in grahas.items():
            print(f'{graha_name}: {graha_data["longitude"]:.2f}° in {graha_data["rasi"]}')
        
        print()
        print('=== ISSUES TO CHECK ===')
        print('1. Is Sun in correct sign for December? (Should be Sagittarius/Dhanus)')
        print('2. Is Moon position reasonable?')
        print('3. Is Ascendant calculation correct for given time/location?')
        print('4. Are we using correct ephemeris data?')
        print('5. Is timezone conversion working properly?')
        
        # Check raw astronomical data
        print()
        print('=== RAW ASTRONOMICAL DATA ===')
        print('This will help us see if the problem is in:')
        print('- Ephemeris data (planetary positions)')
        print('- Coordinate calculations')
        print('- Timezone handling')
        print('- Sidereal time calculations')
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chart()