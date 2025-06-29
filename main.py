#!/usr/bin/env python3
"""
main.py - Interactive Jyotish Chart Calculator

This is the main entry point for calculating and displaying birth charts.
Users can input birth details and get comprehensive chart information.
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Add CoreLibrary to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'CoreLibrary'))

from chart import Chart
from location_helper import LocationHelper
from aspect_analysis import AspectAnalysis


def get_location_input():
    """Get location input from user with city lookup option"""
    print("\nEnter Birth Location:")
    print("You can either:")
    print("1. Enter city name for automatic lookup")
    print("2. Enter coordinates manually")
    print()
    
    choice = input("Enter '1' for city lookup or '2' for manual coordinates (default 1): ").strip()
    
    if choice == '2':
        # Manual coordinate entry
        print("\nEnter coordinates manually:")
        latitude = float(input("Latitude (degrees, positive for North): "))
        longitude = float(input("Longitude (degrees, positive for East): "))
        
        # Ask for timezone
        print("\nEnter timezone:")
        LocationHelper.display_timezone_help()
        timezone_str = input("Timezone (e.g., UTC+05:30, Asia/Kolkata): ").strip()
        
        # Parse and validate timezone
        parsed_tz = LocationHelper.parse_timezone_offset(timezone_str)
        if parsed_tz:
            timezone_str = parsed_tz
        elif not timezone_str:
            timezone_str = 'UTC'
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'timezone_str': timezone_str,
            'location_name': f"({latitude:.4f}, {longitude:.4f})"
        }
    
    else:
        # City lookup
        while True:
            city_query = input("Enter city name: ").strip()
            if not city_query:
                print("Please enter a city name.")
                continue
            
            # Search for cities
            matches = LocationHelper.search_location(city_query)
            
            if not matches:
                print(f"No cities found matching '{city_query}'.")
                retry = input("Try another city name? (y/n): ").strip().lower()
                if retry != 'y':
                    return get_location_input()  # Fall back to manual entry
                continue
            
            # Display matches
            print(f"\nFound {len(matches)} matching cities:")
            print("-" * 60)
            for i, city in enumerate(matches[:10], 1):  # Show top 10 matches
                print(f"{i:2}. {city['name']}, {city['country']}")
                print(f"    Coordinates: {city['latitude']:.4f}°, {city['longitude']:.4f}°")
                print(f"    Timezone: {city['timezone']}")
                print()
            
            if len(matches) > 10:
                print(f"... and {len(matches) - 10} more matches")
                print()
            
            # Let user choose
            try:
                choice_num = input(f"Select city (1-{min(len(matches), 10)}) or 's' to search again: ").strip()
                
                if choice_num.lower() == 's':
                    continue
                
                choice_idx = int(choice_num) - 1
                if 0 <= choice_idx < min(len(matches), 10):
                    selected_city = matches[choice_idx]
                    print(f"\nSelected: {selected_city['name']}, {selected_city['country']}")
                    
                    return {
                        'latitude': selected_city['latitude'],
                        'longitude': selected_city['longitude'],
                        'timezone_str': selected_city['timezone'],
                        'location_name': f"{selected_city['name']}, {selected_city['country']}"
                    }
                else:
                    print("Invalid selection.")
                    
            except ValueError:
                print("Invalid input. Please enter a number or 's' to search again.")


def get_user_input():
    """Get birth details from user input"""
    print("=" * 60)
    print("           JYOTISH CHART CALCULATOR")
    print("=" * 60)
    print()
    
    try:
        # Get birth date
        print("Enter Birth Date:")
        year = int(input("Year (YYYY): "))
        month = int(input("Month (1-12): "))
        day = int(input("Day (1-31): "))
        
        # Get birth time
        print("\nEnter Birth Time:")
        hour = int(input("Hour (0-23): "))
        minute = int(input("Minute (0-59): "))
        
        # Get birth location using new helper
        location_data = get_location_input()
        if not location_data:
            return None
        
        # Get ayanamsa (optional)
        print(f"\nSelected location: {location_data['location_name']}")
        print(f"Timezone: {location_data['timezone_str']}")
        print()
        
        ayanamsa = input("Ayanamsa (default Lahiri): ").strip()
        if not ayanamsa:
            ayanamsa = 'Lahiri'
        
        # Get house system (optional)
        house_system = input("House System (default Equal): ").strip()
        if not house_system:
            house_system = 'Equal'
        
        return {
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute,
            'latitude': location_data['latitude'],
            'longitude': location_data['longitude'],
            'timezone_str': location_data['timezone_str'],
            'location_name': location_data['location_name'],
            'ayanamsa': ayanamsa,
            'house_system': house_system
        }
        
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return None


def display_chart_summary(chart: Chart):
    """Display a comprehensive chart summary"""
    summary = chart.get_chart_summary()
    
    print("\n" + "=" * 60)
    print("                BIRTH CHART SUMMARY")
    print("=" * 60)
    
    # Birth details
    birth = summary['birth_details']
    location_name = getattr(chart, 'location_name', 'Unknown Location')
    print(f"\nBirth Details:")
    print(f"  Date & Time: {birth['datetime']}")
    print(f"  Location: {location_name}")
    print(f"  Coordinates: {birth['location']}")
    print(f"  Timezone: {birth['timezone']}")
    
    # Ascendant
    asc = summary['ascendant']
    print(f"\nAscendant (Lagna):")
    print(f"  Rasi: {asc['rasi']}")
    print(f"  Degrees: {asc['degrees']}")
    print(f"  Nakshatra: {asc['nakshatra']}")
    
    # Chart strength
    print(f"\nOverall Chart Strength: {summary['chart_strength']}")
    
    # Strongest planets
    if summary['strongest_grahas']:
        print(f"\nStrongest Planets:")
        for graha in summary['strongest_grahas']:
            print(f"  • {graha}")
    
    print(f"\nAspects Summary:")
    print(f"  Total Aspects: {summary['total_aspects']}")
    print(f"  Conjunctions: {summary['conjunctions']}")


def display_planetary_positions(chart: Chart):
    """Display detailed planetary positions"""
    positions = chart.get_graha_positions()
    
    print("\n" + "=" * 60)
    print("              PLANETARY POSITIONS")
    print("=" * 60)
    print(f"{'Planet':<10} {'Rasi':<12} {'Degrees':<10} {'Nakshatra':<15} {'Pada':<5}")
    print("-" * 60)
    
    planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    for planet in planet_order:
        if planet in positions:
            pos = positions[planet]
            degrees_str = f"{pos['degrees_in_rasi']:.2f}°"
            nakshatra_str = f"{pos['nakshatra']}"
            pada_str = str(pos['pada'])
            
            print(f"{planet:<10} {pos['rasi']:<12} {degrees_str:<10} {nakshatra_str:<15} {pada_str:<5}")


def display_house_analysis(chart: Chart):
    """Display house analysis"""
    bhavas = chart.get_bhavas()
    bhava_analysis = chart.get_bhava_analysis()
    
    print("\n" + "=" * 60)
    print("                HOUSE ANALYSIS")
    print("=" * 60)
    
    for i in range(1, 13):
        bhava = bhavas[i]
        analysis = bhava_analysis['all_bhavas'][i]
        
        print(f"\n{i}. {bhava['name']} ({bhava['rasi']})")
        print(f"   Cusp: {bhava['rasi']} {bhava['degrees_in_rasi']:.2f}°")
        print(f"   Nature: {bhava['nature']}")
        print(f"   Lord: {analysis.get('bhava_lord', 'Unknown')}")
        
        # Show planets in house
        planets_in_house = analysis.get('grahas_placed', [])
        if planets_in_house:
            print(f"   Planets: {', '.join(planets_in_house)}")
        
        # Show strength
        strength = analysis.get('strength_analysis', {})
        strength_category = strength.get('strength_category', 'Unknown')
        total_strength = strength.get('total_strength', 0.0)
        print(f"   Strength: {strength_category} ({total_strength:.2f})")


def display_yogas(chart: Chart):
    """Display major yogas found in the chart"""
    yogas = chart.find_yogas()
    
    print("\n" + "=" * 60)
    print("                 MAJOR YOGAS")
    print("=" * 60)
    
    yoga_found = False
    
    for yoga_type, yoga_list in yogas.items():
        if yoga_list:
            yoga_found = True
            print(f"\n{yoga_type.replace('_', ' ').title()}:")
            for yoga in yoga_list:
                if isinstance(yoga, dict):
                    if 'type' in yoga:
                        print(f"  • {yoga['type']}")
                    else:
                        print(f"  • {yoga}")
                else:
                    print(f"  • {yoga}")
    
    if not yoga_found:
        print("\nNo major yogas detected with current analysis.")
        print("Note: This is a basic analysis. More detailed yoga detection")
        print("would require additional astrological rules implementation.")


def display_aspects_analysis(chart: Chart):
    """Display detailed aspects analysis for bhavas"""
    print("\n" + "=" * 60)
    print("              ASPECTS ANALYSIS")
    print("=" * 60)
    
    # Ask for aspect calculation mode
    print("\nSelect aspect calculation mode:")
    print("1. Rasi-based (Traditional Vedic - Default)")
    print("2. Degree-based (With orbs)")
    
    mode_choice = input("\nEnter choice (1 or 2, default is 1): ").strip()
    
    if mode_choice == '2':
        aspect_mode = 'degree'
        print("\nUsing degree-based aspects with orbs.")
    else:
        aspect_mode = 'rasi'
        print("\nUsing traditional rasi-based (sign-to-sign) aspects.")
    
    # Create aspect analysis object
    aspect_analyzer = AspectAnalysis(chart.chart_data, aspect_mode=aspect_mode)
    
    print("\nSelect a house (bhava) to analyze aspects:")
    print("Enter a number from 1-12, or 'all' for all houses, or 'back' to return to main menu")
    
    while True:
        try:
            choice = input("\nEnter bhava number (1-12), 'all', or 'back': ").strip().lower()
            
            if choice == 'back':
                return
            elif choice == 'all':
                print("\n" + "=" * 80)
                print("                     COMPLETE ASPECTS ANALYSIS")
                print("=" * 80)
                
                for bhava_num in range(1, 13):
                    try:
                        analysis = aspect_analyzer.get_bhava_aspects_analysis(bhava_num)
                        table = aspect_analyzer.format_aspects_table(analysis)
                        print(table)
                    except Exception as e:
                        print(f"Error analyzing Bhava {bhava_num}: {e}")
                
                print("\n" + "=" * 80)
                print("                  END OF COMPLETE ANALYSIS")
                print("=" * 80)
                return
                
            else:
                bhava_num = int(choice)
                if 1 <= bhava_num <= 12:
                    try:
                        analysis = aspect_analyzer.get_bhava_aspects_analysis(bhava_num)
                        table = aspect_analyzer.format_aspects_table(analysis)
                        print(table)
                        
                        # Ask if user wants to analyze another bhava
                        again = input("\nAnalyze another bhava? (y/n): ").strip().lower()
                        if again not in ['y', 'yes']:
                            return
                    except Exception as e:
                        print(f"Error analyzing Bhava {bhava_num}: {e}")
                else:
                    print("Please enter a number between 1 and 12.")
                    
        except ValueError:
            print("Invalid input. Please enter a number between 1-12, 'all', or 'back'.")
        except KeyboardInterrupt:
            return


def save_chart_to_file(chart: Chart, filename: Optional[str] = None):
    """Save chart data to JSON file"""
    if filename is None:
        birth_info = chart.chart_data['birth_info']
        dt = birth_info['birth_datetime']
        filename = f"chart_{dt.strftime('%Y%m%d_%H%M')}.json"
    
    try:
        json_data = chart.to_json(filename)
        print(f"\nChart saved to: {filename}")
        return True
    except Exception as e:
        print(f"Error saving chart: {e}")
        return False


def main_menu(chart: Chart):
    """Display main menu and handle user choices"""
    while True:
        print("\n" + "=" * 60)
        print("                    MENU")
        print("=" * 60)
        print("1. Chart Summary")
        print("2. Planetary Positions")
        print("3. House Analysis")
        print("4. Major Yogas")
        print("5. Aspects Analysis")
        print("6. Save Chart to File")
        print("7. Calculate New Chart")
        print("8. Exit")
        print("-" * 60)
        
        try:
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == '1':
                display_chart_summary(chart)
            elif choice == '2':
                display_planetary_positions(chart)
            elif choice == '3':
                display_house_analysis(chart)
            elif choice == '4':
                display_yogas(chart)
            elif choice == '5':
                display_aspects_analysis(chart)
            elif choice == '6':
                save_chart_to_file(chart)
            elif choice == '7':
                return True  # Signal to calculate new chart
            elif choice == '8':
                print("\nThank you for using Jyotish Chart Calculator!")
                return False  # Signal to exit
            else:
                print("Invalid choice. Please enter a number between 1-8.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return False


def main():
    """Main function"""
    print("Welcome to Jyotish Chart Calculator!")
    print("This tool calculates Vedic astrology birth charts.")
    print("\nNote: Currently using placeholder planetary positions.")
    print("For accurate calculations, integrate with Swiss Ephemeris.")
    
    while True:
        # Get user input
        birth_details = get_user_input()
        if birth_details is None:
            print("Exiting...")
            break
        
        try:
            # Create chart
            print("\nCalculating chart...")
            location_name = birth_details.pop('location_name', 'Unknown Location')
            chart = Chart.from_birth_details(**birth_details)
            
            # Store location name in chart for display
            chart.location_name = location_name
            print("Chart calculation complete!")
            
            # Show menu
            continue_calculating = main_menu(chart)
            if not continue_calculating:
                break
                
        except Exception as e:
            print(f"\nError calculating chart: {e}")
            print("Please check your input and try again.")
            
            retry = input("\nWould you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                break
    
    print("\nGoodbye!")


if __name__ == "__main__":
    main()