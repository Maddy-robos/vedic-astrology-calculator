# main_example.py - Example of using all Jyotish modules together

from datetime import datetime
from graha_positions import GrahaPositions
from panchanga import Panchanga
from lordships import Lordships
from bhava_analysis import BhavaAnalysis
from dignity import Dignity
from combustion import Combustion
from rasi_drishti import RasiDrishti

def analyze_chart(birth_datetime, location, name="Native"):
    """Complete chart analysis using all modules"""
    
    print(f"\nJYOTISH CHART ANALYSIS")
    print(f"Name: {name}")
    print(f"Birth: {birth_datetime.strftime('%B %d, %Y at %I:%M %p')}")
    print(f"Location: {location['latitude']}°N, {location['longitude']}°E")
    print("=" * 80)
    
    # Step 1: Calculate Graha Positions
    print("\n1. CALCULATING POSITIONS...")
    graha_calc = GrahaPositions(birth_datetime, location)
    positions = graha_calc.get_simplified_positions()
    ascendant_data = graha_calc.calculate_ascendant()
    ascendant = ascendant_data['rasi']
    
    print(f"Ascendant: {ascendant}")
    
    # Step 2: Calculate Panchanga
    print("\n2. PANCHANGA AT BIRTH...")
    # Get Sun and Moon positions for Panchanga
    sun_pos = graha_calc.sidereal_positions.get('Sun', 0)
    moon_pos = graha_calc.sidereal_positions.get('Moon', 0)
    
    panchanga = Panchanga(birth_datetime, moon_pos, sun_pos)
    panchanga_lords = panchanga.get_panchanga_lords()
    
    print(f"Vara: {panchanga.vara['name']} (Lord: {panchanga.vara['lord']})")
    print(f"Tithi: {panchanga.tithi['name']} (Lord: {panchanga.tithi['lord']})")
    print(f"Nakshatra: {panchanga.nakshatra['name']} (Lord: {panchanga.nakshatra['lord']})")
    print(f"Yoga: {panchanga.yoga['name']} (Lord: {panchanga.yoga['lord']})")
    print(f"Karana: {panchanga.karana['name']} (Lord: {panchanga.karana['lord']})")
    
    # Step 3: Lordship Analysis
    print("\n3. LORDSHIP ANALYSIS...")
    lordships = Lordships(ascendant)
    
    print("\nFunctional Nature of Grahas:")
    for graha in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        houses = lordships.get_houses_owned_by(graha)
        if houses:
            nature = lordships.get_lordship_nature(graha)
            print(f"{graha}: Lord of {houses} - {nature['functional_nature']}")
    
    yoga_karaka = lordships.get_yoga_karaka()
    if yoga_karaka:
        print(f"\nYoga Karaka: {yoga_karaka}")
    
    # Step 4: Bhava Analysis
    print("\n4. BHAVA OCCUPANCY...")
    bhava_analysis = BhavaAnalysis(ascendant, positions)
    
    for bhava in range(1, 13):
        occupants = bhava_analysis.get_grahas_in_bhava(bhava)
        if occupants:
            print(f"House {bhava}: {', '.join(occupants)}")
    
    # Step 5: Dignity Analysis
    print("\n5. DIGNITY ANALYSIS (Panchadha Maitri)...")
    dignity_calc = Dignity(positions)
    
    for graha in positions:
        result = dignity_calc.get_panchadha_maitri(graha)
        print(f"{graha}: {result['dignity']} (Score: {result['score']}/9)")
    
    # Step 6: Combustion Analysis
    print("\n6. COMBUSTION ANALYSIS...")
    combustion_calc = Combustion(positions, ascendant)
    combust_grahas = combustion_calc.get_all_combust_grahas()
    
    if combust_grahas:
        print("Combust Grahas:")
        for cg in combust_grahas:
            print(f"- {cg['graha']} ({cg['distance_from_sun']:.1f}° from Sun)")
    else:
        print("No grahas are combust")
    
    # Step 7: Rasi Drishti Analysis
    print("\n7. RASI DRISHTI (Sign Aspects)...")
    rasi_drishti = RasiDrishti()
    
    # Find mutual aspects
    mutual_aspects = rasi_drishti.get_mutual_rasi_aspects(positions)
    if mutual_aspects:
        print("Mutual Rasi Aspects:")
        for ma in mutual_aspects:
            print(f"- {ma['graha1']} ↔ {ma['graha2']}")
    
    # Step 8: Special Combinations
    print("\n8. SPECIAL OBSERVATIONS...")
    
    # Check if any Panchanga lord is combust
    print("\nPanchanga Lord Status:")
    for limb, lord in panchanga_lords.items():
        if lord in ['Rahu', 'Ketu']:
            continue
        combust_check = combustion_calc.is_combust(lord)
        if combust_check.get('is_combust'):
            print(f"- {limb.replace('_', ' ').title()} ({lord}) is COMBUST!")
    
    # Check dignities of house lords
    print("\nKey House Lord Dignities:")
    for house in [1, 4, 7, 10]:  # Kendra lords
        lord = lordships.get_house_lord(house)
        if lord in positions:
            dignity_result = dignity_calc.get_panchadha_maitri(lord)
            print(f"- {house}H Lord ({lord}): {dignity_result['dignity']}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"- Ascendant: {ascendant}")
    print(f"- Moon Nakshatra: {panchanga.nakshatra['name']} ruled by {panchanga.nakshatra['lord']}")
    print(f"- Combust Grahas: {len(combust_grahas)}")
    print(f"- Yoga Karaka: {yoga_karaka if yoga_karaka else 'None'}")
    
    return {
        'positions': positions,
        'ascendant': ascendant,
        'panchanga': panchanga.get_panchanga_summary(),
        'lordships': lordships.get_all_lordships(),
        'dignities': dignity_calc.get_all_dignities(),
        'combustion': combustion_calc.analyze_combustion_effects()
    }


# Example usage
if __name__ == "__main__":
    # Example 1: Current time analysis
    current_time = datetime.now()
    location = {
        'latitude': 13.0827,   # Chennai
        'longitude': 80.2707,
        'timezone': 'Asia/Kolkata'
    }
    
    print("CURRENT PLANETARY POSITIONS")
    analyze_chart(current_time, location, "Current Moment")
    
    # Example 2: Birth chart analysis
    birth_time = datetime(1990, 5, 15, 14, 30)  # May 15, 1990, 2:30 PM
    
    print("\n" + "="*80)
    print("\nBIRTH CHART ANALYSIS")
    chart_data = analyze_chart(birth_time, location, "Example Native")
    
    # You can save the chart_data for research projects
    # import json
    # with open('chart_analysis.json', 'w') as f:
    #     # Convert datetime objects to strings for JSON serialization
    #     json.dump(chart_data, f, indent=2, default=str)