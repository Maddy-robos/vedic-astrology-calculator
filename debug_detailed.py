#!/usr/bin/env python3
"""
Detailed debug script for chart calculations
"""

import sys
import os
from datetime import datetime

# Add CoreLibrary to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'CoreLibrary'))

from swiss_ephemeris import SwissEphemeris
import swisseph as swe

def debug_detailed():
    """Detailed debugging of Swiss Ephemeris calculations"""
    print("=== DETAILED SWISS EPHEMERIS DEBUG ===")
    print("Date: 1993 Dec 10, 20:25 Tirupati")
    print("Expected Sun: ~255° (Sagittarius)")
    print("Expected Ascendant: Cancer")
    print()
    
    # Test date in different formats
    birth_datetime = datetime(1993, 12, 10, 20, 25)
    print(f"Local Birth Time: {birth_datetime}")
    
    # Convert to UTC (India is UTC+5:30)
    from datetime import timezone, timedelta
    ist = timezone(timedelta(hours=5, minutes=30))
    birth_local = birth_datetime.replace(tzinfo=ist)
    birth_utc = birth_local.astimezone(timezone.utc)
    
    print(f"UTC Birth Time: {birth_utc}")
    print()
    
    # Swiss Ephemeris direct test
    se = SwissEphemeris('Lahiri')
    jd = se.julian_day_from_datetime(birth_utc)
    
    print(f"Julian Day: {jd}")
    print()
    
    # Check ayanamsa
    ayanamsa = swe.get_ayanamsa_ut(jd)
    print(f"Ayanamsa (Lahiri): {ayanamsa:.6f}°")
    print()
    
    # Test Sun position step by step
    print("=== SUN POSITION ANALYSIS ===")
    sun_result, sun_flag = swe.calc_ut(jd, swe.SUN)
    
    if sun_flag >= 0:
        tropical_sun = sun_result[0]
        print(f"Tropical Sun longitude: {tropical_sun:.6f}°")
        
        sidereal_sun = (tropical_sun - ayanamsa) % 360
        print(f"Sidereal Sun longitude: {sidereal_sun:.6f}°")
        
        # Check which sign this is
        sun_sign_num = int(sidereal_sun // 30)
        sun_degrees_in_sign = sidereal_sun % 30
        
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        print(f"Sun in: {signs[sun_sign_num]} {sun_degrees_in_sign:.2f}°")
        print()
        
        # Expected for December 10
        print("Expected for December 10:")
        print("- Tropical Sun: ~258° (mid Sagittarius)")
        print("- With Lahiri ayanamsa ~24°: Sidereal ~234° (early Scorpio)")
        print("- But traditionally Sun enters Sagittarius around December 15-16")
        print()
        
        if sun_sign_num == 7:  # Scorpio
            print("✅ Sun in Scorpio is CORRECT for December 10, 1993!")
            print("   Sun doesn't enter Sagittarius until mid-December")
        else:
            print(f"❌ Unexpected: Sun in {signs[sun_sign_num]}")
    
    print()
    print("=== ASCENDANT VERIFICATION ===")
    asc_data = se.calculate_ascendant(jd, 13.6288, 79.4192)
    if asc_data:
        asc_lon = asc_data['longitude']
        asc_sign_num = int(asc_lon // 30)
        asc_degrees = asc_lon % 30
        
        print(f"Ascendant: {signs[asc_sign_num]} {asc_degrees:.2f}°")
        
        if asc_sign_num == 3:  # Cancer
            print("✅ Cancer Ascendant is CORRECT!")
        else:
            print(f"❌ Unexpected: {signs[asc_sign_num]} Ascendant")
    
    se.close()

if __name__ == "__main__":
    debug_detailed()