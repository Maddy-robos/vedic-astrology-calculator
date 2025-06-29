#!/usr/bin/env python3
"""
example_usage.py - Example of using the Chart class programmatically

This demonstrates how to create charts and access chart data without the interactive interface.
"""

import sys
import os
from datetime import datetime

# Add CoreLibrary to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'CoreLibrary'))

from chart import Chart
from location_helper import LocationHelper


def demonstrate_location_features():
    """Demonstrate the location lookup features"""
    
    print("LOCATION LOOKUP DEMONSTRATION:")
    print("=" * 50)
    
    # Search for cities
    cities_to_search = ['mumbai', 'delhi', 'new york', 'london', 'tokyo']
    
    for city_query in cities_to_search:
        matches = LocationHelper.search_location(city_query)
        if matches:
            top_match = matches[0]
            print(f"'{city_query}' -> {top_match['name']}, {top_match['country']}")
            print(f"  Coordinates: {top_match['latitude']:.4f}°, {top_match['longitude']:.4f}°")
            print(f"  Timezone: {top_match['timezone']}")
            print()
    
    # Timezone parsing examples
    print("TIMEZONE PARSING EXAMPLES:")
    print("-" * 30)
    timezone_inputs = [
        'UTC+05:30',
        '+05:30',
        'UTC-08:00',
        'Asia/Kolkata',
        'America/New_York',
        'Europe/London'
    ]
    
    for tz_input in timezone_inputs:
        parsed = LocationHelper.parse_timezone_offset(tz_input)
        print(f"  {tz_input:<20} -> {parsed}")
    
    print()


def example_chart_calculation():
    """Example of creating and analyzing a chart programmatically"""
    
    print("Creating example birth chart...")
    print("=" * 50)
    
    # Example birth details
    birth_datetime = datetime(1990, 5, 15, 14, 30)  # May 15, 1990, 2:30 PM
    latitude = 28.6139  # New Delhi, India
    longitude = 77.2090
    timezone_str = 'Asia/Kolkata'
    
    # Create chart
    chart = Chart(
        birth_datetime=birth_datetime,
        latitude=latitude,
        longitude=longitude,
        timezone_str=timezone_str,
        ayanamsa='Lahiri',
        house_system='Equal'
    )
    
    print(f"Chart created for: {birth_datetime}")
    print(f"Location: {latitude}°N, {longitude}°E")
    print(f"Timezone: {timezone_str}")
    print()
    
    # Get basic chart information
    summary = chart.get_chart_summary()
    print("CHART SUMMARY:")
    print("-" * 30)
    print(f"Ascendant: {summary['ascendant']['rasi']} {summary['ascendant']['degrees']}")
    print(f"Nakshatra: {summary['ascendant']['nakshatra']}")
    print(f"Chart Strength: {summary['chart_strength']}")
    print()
    
    # Show planetary positions
    print("PLANETARY POSITIONS:")
    print("-" * 30)
    positions = chart.get_graha_positions()
    for planet, data in positions.items():
        print(f"{planet:10}: {data['rasi']:12} {data['degrees_in_rasi']:6.2f}° ({data['nakshatra']} {data['pada']})")
    print()
    
    # Show house lords
    print("HOUSE LORDS:")
    print("-" * 30)
    bhava_analysis = chart.get_bhava_analysis()
    for i in range(1, 13):
        bhava_data = bhava_analysis['all_bhavas'][i]
        lord = bhava_data.get('bhava_lord', 'Unknown')
        rasi = chart.get_bhava(i)['rasi']
        print(f"House {i:2} ({rasi:12}): {lord}")
    print()
    
    # Show strongest houses
    strongest = bhava_analysis.get('strongest_bhavas', [])
    print("STRONGEST HOUSES:")
    print("-" * 30)
    for bhava_num, strength in strongest:
        bhava_info = chart.get_bhava(bhava_num)
        print(f"House {bhava_num}: {bhava_info['name']} (Strength: {strength:.2f})")
    print()
    
    # Show aspects summary
    aspects = chart.get_aspects()
    aspect_summary = aspects.get('summary', {})
    print("ASPECTS SUMMARY:")
    print("-" * 30)
    print(f"Total Aspects: {aspect_summary.get('total_aspects', 0)}")
    print(f"Conjunctions: {aspect_summary.get('total_conjunctions', 0)}")
    print(f"Strong Aspects: {aspect_summary.get('strong_aspects_count', 0)}")
    print(f"Most Aspected Planet: {aspect_summary.get('most_aspected_graha', 'None')}")
    print()
    
    # Show some yogas
    yogas = chart.find_yogas()
    print("IDENTIFIED YOGAS:")
    print("-" * 30)
    total_yogas = sum(len(yoga_list) for yoga_list in yogas.values())
    if total_yogas > 0:
        for yoga_type, yoga_list in yogas.items():
            if yoga_list:
                print(f"{yoga_type.replace('_', ' ').title()}: {len(yoga_list)} found")
    else:
        print("No major yogas identified in basic analysis")
    print()
    
    # Save to JSON
    print("SAVING CHART:")
    print("-" * 30)
    json_filename = "example_chart.json"
    chart.to_json(json_filename)
    print(f"Chart saved to {json_filename}")
    print()
    
    return chart


def demonstrate_chart_methods():
    """Demonstrate various chart analysis methods"""
    
    print("DEMONSTRATING CHART METHODS:")
    print("=" * 50)
    
    # Create a simple chart
    chart = Chart.from_birth_details(
        year=1985, month=8, day=20, hour=10, minute=15,
        latitude=19.0760, longitude=72.8777,  # Mumbai
        timezone_str='Asia/Kolkata'
    )
    
    # Demonstrate individual graha position lookup
    print("Individual Planet Lookups:")
    print("-" * 30)
    sun_pos = chart.get_graha_position('Sun')
    moon_pos = chart.get_graha_position('Moon')
    print(f"Sun: {sun_pos['rasi']} {sun_pos['degrees_in_rasi']:.2f}°")
    print(f"Moon: {moon_pos['rasi']} {moon_pos['degrees_in_rasi']:.2f}°")
    print()
    
    # Demonstrate house lookup
    print("Individual House Lookups:")
    print("-" * 30)
    first_house = chart.get_bhava(1)
    tenth_house = chart.get_bhava(10)
    print(f"1st House: {first_house['name']} in {first_house['rasi']}")
    print(f"10th House: {tenth_house['name']} in {tenth_house['rasi']}")
    print()
    
    # Demonstrate ascendant details
    print("Ascendant Details:")
    print("-" * 30)
    ascendant = chart.get_ascendant()
    print(f"Longitude: {ascendant['longitude']:.4f}°")
    print(f"Rasi: {ascendant['rasi']}")
    print(f"Degrees in Rasi: {ascendant['degrees_in_rasi']:.2f}°")
    print(f"Nakshatra: {ascendant['nakshatra']} Pada {ascendant['pada']}")
    print()


def main():
    """Main function demonstrating chart usage"""
    
    print("JYOTISH CHART LIBRARY EXAMPLE")
    print("=" * 50)
    print("This example demonstrates programmatic usage of the Chart class")
    print("without the interactive interface.")
    print()
    
    try:
        # Demonstrate location features first
        demonstrate_location_features()
        
        print("\n" + "=" * 50)
        
        # Run example calculation
        chart1 = example_chart_calculation()
        
        print("\n" + "=" * 50)
        
        # Demonstrate methods
        demonstrate_chart_methods()
        
        print("\nExample completed successfully!")
        print("\nNote: Planetary positions are currently placeholders.")
        print("For production use, integrate with Swiss Ephemeris for accurate calculations.")
        
    except Exception as e:
        print(f"Error during example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()