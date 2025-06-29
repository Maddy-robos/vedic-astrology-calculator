#!/usr/bin/env python3
"""
sample_input_demo.py - Demonstration of sample inputs for the chart calculator

This script shows examples of how to provide input to the main.py calculator.
"""

import sys
import os

# Add CoreLibrary to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'CoreLibrary'))

from location_helper import LocationHelper


def show_sample_inputs():
    """Display sample input examples for users"""
    
    print("=" * 70)
    print("         JYOTISH CHART CALCULATOR - SAMPLE INPUTS")
    print("=" * 70)
    print()
    
    print("When you run 'python3 main.py', here are examples of inputs you can provide:")
    print()
    
    # Sample birth details
    print("1. BIRTH DATE & TIME EXAMPLES:")
    print("-" * 35)
    print("   Year: 1990")
    print("   Month: 5")
    print("   Day: 15")
    print("   Hour: 14  (2 PM in 24-hour format)")
    print("   Minute: 30")
    print()
    
    # Location examples
    print("2. LOCATION INPUT EXAMPLES:")
    print("-" * 35)
    print("   Option 1 - City Name Lookup (Recommended):")
    print("   > Enter '1' for city lookup")
    print("   > Enter city name: mumbai")
    print("   > Select from search results")
    print()
    print("   Popular Indian Cities:")
    indian_cities = LocationHelper.get_popular_cities('India', 15)
    for i, city in enumerate(indian_cities):
        if i < 10:  # Show first 10
            print(f"     • {city['name']}")
    print("     ... and many more")
    print()
    
    print("   Option 2 - Manual Coordinates:")
    print("   > Enter '2' for manual coordinates")
    print("   > Latitude: 19.0760  (Mumbai)")
    print("   > Longitude: 72.8777 (Mumbai)")
    print()
    
    # Timezone examples
    print("3. TIMEZONE INPUT EXAMPLES:")
    print("-" * 35)
    print("   Format 1 - UTC Offset:")
    print("     UTC+05:30  (India Standard Time)")
    print("     UTC-05:00  (US Eastern Time)")
    print("     UTC+08:00  (China/Singapore)")
    print("     +05:30     (Short format)")
    print()
    print("   Format 2 - IANA Timezone Names:")
    print("     Asia/Kolkata       (India)")
    print("     America/New_York   (US Eastern)")
    print("     Europe/London      (UK/GMT)")
    print("     Asia/Tokyo         (Japan)")
    print("     Asia/Dubai         (UAE)")
    print()
    
    # Common timezone table
    print("   Common UTC Offsets:")
    timezones = [
        ("UTC+05:30", "India, Sri Lanka"),
        ("UTC+08:00", "China, Singapore, Malaysia"),
        ("UTC+09:00", "Japan, South Korea"),
        ("UTC+04:00", "UAE, Oman"),
        ("UTC+06:00", "Bangladesh"),
        ("UTC+05:00", "Pakistan"),
        ("UTC-05:00", "US Eastern"),
        ("UTC-08:00", "US Pacific"),
        ("UTC+00:00", "UK, GMT"),
        ("UTC+01:00", "Central Europe"),
    ]
    
    for tz, location in timezones:
        print(f"     {tz:<10} = {location}")
    print()
    
    # Ayanamsa examples
    print("4. AYANAMSA OPTIONS:")
    print("-" * 25)
    print("   • Lahiri (default) - Most commonly used")
    print("   • Raman - Alternative system")
    print("   • Krishnamurti - KP astrology system")
    print("   • Just press Enter for default (Lahiri)")
    print()
    
    # House system examples
    print("5. HOUSE SYSTEM OPTIONS:")
    print("-" * 30)
    print("   • Equal (default) - 30° houses")
    print("   • Placidus - Unequal houses (planned)")
    print("   • Just press Enter for default (Equal)")
    print()
    
    # Complete example
    print("6. COMPLETE SAMPLE SESSION:")
    print("-" * 35)
    sample_session = """
    Year (YYYY): 1990
    Month (1-12): 5
    Day (1-31): 15
    Hour (0-23): 14
    Minute (0-59): 30
    
    Enter Birth Location:
    You can either:
    1. Enter city name for automatic lookup
    2. Enter coordinates manually
    
    Enter '1' for city lookup or '2' for manual coordinates (default 1): 1
    Enter city name: mumbai
    
    Found 2 matching cities:
    1. Mumbai, India
       Coordinates: 19.0760°, 72.8777°
       Timezone: Asia/Kolkata
    
    2. Navi Mumbai, India
       Coordinates: 19.0330°, 73.0297°
       Timezone: Asia/Kolkata
    
    Select city (1-2) or 's' to search again: 1
    
    Selected: Mumbai, India
    Timezone: Asia/Kolkata
    
    Ayanamsa (default Lahiri): [Enter]
    House System (default Equal): [Enter]
    """
    print(sample_session)
    
    print("7. QUICK CITY LOOKUP DEMO:")
    print("-" * 35)
    print("Try searching for these cities:")
    demo_cities = ['delhi', 'new york', 'london', 'tokyo', 'dubai', 'singapore']
    for city in demo_cities:
        matches = LocationHelper.search_location(city)
        if matches:
            print(f"   '{city}' -> {matches[0]['name']}, {matches[0]['country']}")
    print()
    
    print("8. TIMEZONE PARSING EXAMPLES:")
    print("-" * 40)
    timezone_examples = [
        'UTC+05:30',
        '+05:30', 
        'Asia/Kolkata',
        'UTC-05:00',
        'America/New_York',
        'Europe/London'
    ]
    
    for tz_input in timezone_examples:
        parsed = LocationHelper.parse_timezone_offset(tz_input)
        if parsed:
            print(f"   Input: '{tz_input}' -> Parsed: '{parsed}'")
        else:
            print(f"   Input: '{tz_input}' -> Valid IANA timezone")
    print()
    
    print("=" * 70)
    print("Ready to try? Run: python3 main.py")
    print("=" * 70)


def interactive_location_demo():
    """Interactive demonstration of location lookup"""
    print("\n" + "=" * 50)
    print("         INTERACTIVE LOCATION DEMO")
    print("=" * 50)
    
    while True:
        city_name = input("\nEnter a city name to search (or 'quit' to exit): ").strip()
        
        if city_name.lower() in ['quit', 'exit', 'q']:
            break
        
        if not city_name:
            continue
        
        matches = LocationHelper.search_location(city_name)
        
        if matches:
            print(f"\nFound {len(matches)} matches for '{city_name}':")
            print("-" * 50)
            
            for i, city in enumerate(matches[:5], 1):  # Show top 5
                print(f"{i}. {city['name']}, {city['country']}")
                print(f"   Coordinates: {city['latitude']:.4f}°, {city['longitude']:.4f}°")
                print(f"   Timezone: {city['timezone']}")
                print()
                
            if len(matches) > 5:
                print(f"   ... and {len(matches) - 5} more matches")
        else:
            print(f"No cities found matching '{city_name}'")
        
        print("-" * 50)


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_location_demo()
    else:
        show_sample_inputs()
        
        # Ask if user wants interactive demo
        try:
            demo = input("\nWould you like to try the interactive city lookup demo? (y/n): ").strip().lower()
            if demo == 'y':
                interactive_location_demo()
        except KeyboardInterrupt:
            print("\nGoodbye!")


if __name__ == "__main__":
    main()