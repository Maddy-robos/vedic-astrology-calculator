#!/usr/bin/env python3
"""
Debug aspect calculation to understand the house counting
"""

import sys
import os
from datetime import datetime

# Add CoreLibrary to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'CoreLibrary'))

from chart import Chart
from aspects import Aspects

def debug_aspect_calculation():
    """Debug the aspect calculation logic"""
    print("=== DEBUGGING ASPECT CALCULATIONS ===")
    print()
    
    # Show Mars' special aspects
    mars_aspects = Aspects.GRAHA_SPECIAL_ASPECTS['Mars']
    print(f"Mars special aspects (degrees): {mars_aspects}")
    print()
    
    # Convert to house positions
    print("Converting degrees to house positions:")
    for angle in mars_aspects:
        houses = angle / 30
        print(f"{angle}° = {houses} houses away")
    print()
    
    # Test with actual chart
    birth_datetime = datetime(1993, 12, 10, 20, 25)
    chart = Chart(
        birth_datetime=birth_datetime,
        latitude=13.6288,
        longitude=79.4192,
        timezone_str='Asia/Kolkata',
        ayanamsa='Lahiri',
        house_system='Equal'
    )
    
    # Get Mars position
    grahas = chart.get_graha_positions()
    mars_data = grahas['Mars']
    print(f"Mars position: {mars_data['rasi']} {mars_data['degrees_in_rasi']:.2f}°")
    
    # Calculate which rasis Mars aspects
    rasi_list = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    mars_rasi_num = rasi_list.index(mars_data['rasi'])
    print(f"Mars is in rasi number: {mars_rasi_num} (0-based)")
    print()
    
    print("Mars aspects the following rasis:")
    for angle in mars_aspects:
        houses_away = int(angle / 30)
        # Fix: Need to subtract 1 because counting is inclusive
        # 4th aspect means 3 houses away (counting from next house)
        aspected_rasi_num = (mars_rasi_num + houses_away) % 12
        aspected_rasi = rasi_list[aspected_rasi_num]
        print(f"- {angle}° aspect ({houses_away} houses) -> {aspected_rasi}")
    
    print()
    print("Bhava 1 (Lagna) is in:", chart.get_bhavas()[1]['rasi'])
    print()
    
    # Check the actual calculation
    print("ISSUE FOUND:")
    print("210° / 30 = 7, but this is the 8th aspect (counting from the planet itself)")
    print("The traditional counting is:")
    print("- 4th aspect = 3 houses away from next sign")
    print("- 7th aspect = 6 houses away from next sign (opposite)")  
    print("- 8th aspect = 7 houses away from next sign")
    
    chart.close()

if __name__ == "__main__":
    debug_aspect_calculation()