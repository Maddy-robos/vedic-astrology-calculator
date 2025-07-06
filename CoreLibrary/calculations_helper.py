"""
calculations_helper.py - Helper functions for Jyotish calculations

This module provides utility functions used across various calculation modules:
- Distance calculations between grahas
- Nakshatra and pada calculations
- Navamsa calculations
- Bhava (house) calculations
- General mathematical utilities
"""

import math
from typing import Dict, List, Tuple, Optional, Union
import json
import os
from datetime import datetime


class CalculationsHelper:
    """Helper class containing utility functions for Jyotish calculations"""
    
    # Nakshatra data
    NAKSHATRAS = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 
        'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha',
        'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha',
        'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
        'Uttara Bhadrapada', 'Revati'
    ]
    
    # Rasi order
    RASIS = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    
    # Graha order
    GRAHAS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    @staticmethod
    def normalize_degrees(degrees: float) -> float:
        """
        Normalize degrees to 0-360 range
        
        Args:
            degrees: Degrees value (can be negative or > 360)
            
        Returns:
            Normalized degrees (0-360)
        """
        degrees = degrees % 360.0
        if degrees < 0:
            degrees += 360.0
        return degrees
    
    @staticmethod
    def get_angular_distance(deg1: float, deg2: float, forward_only: bool = False) -> float:
        """
        Calculate angular distance between two longitudes
        
        Args:
            deg1: First longitude in degrees
            deg2: Second longitude in degrees
            forward_only: If True, calculate only forward distance from deg1 to deg2
            
        Returns:
            Angular distance in degrees (0-180 if not forward_only, 0-360 if forward_only)
        """
        deg1 = CalculationsHelper.normalize_degrees(deg1)
        deg2 = CalculationsHelper.normalize_degrees(deg2)
        
        if forward_only:
            # Calculate forward distance from deg1 to deg2
            distance = deg2 - deg1
            if distance < 0:
                distance += 360.0
            return distance
        else:
            # Calculate shortest angular distance
            diff = abs(deg2 - deg1)
            if diff > 180:
                diff = 360 - diff
            return diff
    
    @staticmethod
    def get_nakshatra_pada(longitude: float) -> Dict[str, Union[str, int, float]]:
        """
        Calculate nakshatra and pada from longitude
        
        Args:
            longitude: Longitude in degrees (0-360)
            
        Returns:
            Dictionary with nakshatra name, pada (1-4), and degree in nakshatra
        """
        longitude = CalculationsHelper.normalize_degrees(longitude)
        
        # Each nakshatra is 13°20' (13.333... degrees)
        nakshatra_size = 360.0 / 27
        
        # Calculate nakshatra index (0-26)
        nakshatra_index = int(longitude / nakshatra_size)
        
        # Degrees within nakshatra
        degrees_in_nakshatra = longitude % nakshatra_size
        
        # Each pada is 3°20' (3.333... degrees)
        pada_size = nakshatra_size / 4
        pada = int(degrees_in_nakshatra / pada_size) + 1
        
        # Degrees within pada
        degrees_in_pada = degrees_in_nakshatra % pada_size
        
        return {
            'nakshatra': CalculationsHelper.NAKSHATRAS[nakshatra_index],
            'pada': pada,
            'degrees_in_nakshatra': degrees_in_nakshatra,
            'degrees_in_pada': degrees_in_pada
        }
    
    @staticmethod
    def get_navamsa_rasi(longitude: float) -> str:
        """
        Calculate navamsa (D9) rasi from longitude
        
        Args:
            longitude: Longitude in degrees (0-360)
            
        Returns:
            Navamsa rasi name
        """
        longitude = CalculationsHelper.normalize_degrees(longitude)
        
        # Get the rasi (0-11)
        rasi_index = int(longitude / 30)
        
        # Degrees within rasi
        degrees_in_rasi = longitude % 30
        
        # Each navamsa is 3°20' (3.333... degrees)
        navamsa_size = 30.0 / 9
        navamsa_index = int(degrees_in_rasi / navamsa_size)
        
        # Starting navamsa position based on rasi element
        # Fire signs (Aries, Leo, Sagittarius) - start from Aries
        # Earth signs (Taurus, Virgo, Capricorn) - start from Capricorn
        # Air signs (Gemini, Libra, Aquarius) - start from Libra
        # Water signs (Cancer, Scorpio, Pisces) - start from Cancer
        
        element_starts = {
            0: 0,   # Aries -> Aries
            1: 9,   # Taurus -> Capricorn
            2: 6,   # Gemini -> Libra
            3: 3,   # Cancer -> Cancer
            4: 0,   # Leo -> Aries
            5: 9,   # Virgo -> Capricorn
            6: 6,   # Libra -> Libra
            7: 3,   # Scorpio -> Cancer
            8: 0,   # Sagittarius -> Aries
            9: 9,   # Capricorn -> Capricorn
            10: 6,  # Aquarius -> Libra
            11: 3   # Pisces -> Cancer
        }
        
        start_index = element_starts[rasi_index]
        navamsa_rasi_index = (start_index + navamsa_index) % 12
        
        return CalculationsHelper.RASIS[navamsa_rasi_index]
    
    @staticmethod
    def get_navamsa_house_placements(d1_ascendant: float, 
                                   graha_positions: Dict[str, Dict]) -> Dict[int, List[str]]:
        """
        Calculate house placements for D9 Navamsa chart
        
        Args:
            d1_ascendant: D1 ascendant longitude in degrees
            graha_positions: Dictionary of graha positions from D1 chart
            
        Returns:
            Dictionary mapping house numbers to list of planets in that house
        """
        # Get D9 ascendant
        d9_asc_sign = CalculationsHelper.get_navamsa_rasi(d1_ascendant)
        d9_asc_index = CalculationsHelper.RASIS.index(d9_asc_sign)
        
        # Initialize house placements
        house_planets = {i: [] for i in range(1, 13)}
        
        # Calculate D9 positions for each planet
        for graha, data in graha_positions.items():
            if 'longitude' in data:
                # Get D9 sign for this planet
                d9_sign = CalculationsHelper.get_navamsa_rasi(data['longitude'])
                d9_sign_index = CalculationsHelper.RASIS.index(d9_sign)
                
                # Calculate house number (1-12)
                # House = (planet sign - ascendant sign) + 1
                house_num = ((d9_sign_index - d9_asc_index) % 12) + 1
                
                house_planets[house_num].append(graha)
        
        return house_planets
    
    @staticmethod
    def get_hora_rasi(longitude: float) -> str:
        """
        Calculate Hora (D2) rasi from longitude
        
        Args:
            longitude: Longitude in degrees (0-360)
            
        Returns:
            Hora rasi name (Leo or Cancer)
        """
        longitude = CalculationsHelper.normalize_degrees(longitude)
        
        # Get the rasi (0-11)
        rasi_index = int(longitude / 30)
        
        # Degrees within rasi
        degrees_in_rasi = longitude % 30
        
        # Each hora is 15 degrees
        hora_index = int(degrees_in_rasi / 15)  # 0 or 1
        
        # Odd signs: first hora = Sun (Leo), second hora = Moon (Cancer)
        # Even signs: first hora = Moon (Cancer), second hora = Sun (Leo)
        if rasi_index % 2 == 0:  # Even rasi (Aries=0, Gemini=2, etc.)
            return 'Leo' if hora_index == 0 else 'Cancer'
        else:  # Odd rasi (Taurus=1, Cancer=3, etc.)
            return 'Cancer' if hora_index == 0 else 'Leo'
    
    @staticmethod
    def get_drekkana_rasi(longitude: float) -> str:
        """
        Calculate Drekkana (D3) rasi from longitude
        
        Args:
            longitude: Longitude in degrees (0-360)
            
        Returns:
            Drekkana rasi name
        """
        longitude = CalculationsHelper.normalize_degrees(longitude)
        
        # Get the rasi (0-11)
        rasi_index = int(longitude / 30)
        
        # Degrees within rasi
        degrees_in_rasi = longitude % 30
        
        # Each drekkana is 10 degrees
        drekkana_index = int(degrees_in_rasi / 10)  # 0, 1, or 2
        
        # Drekkana calculation:
        # 1st drekkana = same sign
        # 2nd drekkana = 5th sign from current
        # 3rd drekkana = 9th sign from current
        if drekkana_index == 0:
            result_rasi = rasi_index
        elif drekkana_index == 1:
            result_rasi = (rasi_index + 4) % 12  # 5th sign (index + 4)
        else:  # drekkana_index == 2
            result_rasi = (rasi_index + 8) % 12  # 9th sign (index + 8)
        
        return CalculationsHelper.RASIS[result_rasi]
    
    @staticmethod
    def get_dasamsa_rasi(longitude: float) -> str:
        """
        Calculate Dasamsa (D10) rasi from longitude
        
        Args:
            longitude: Longitude in degrees (0-360)
            
        Returns:
            Dasamsa rasi name
        """
        longitude = CalculationsHelper.normalize_degrees(longitude)
        
        # Get the rasi (0-11)
        rasi_index = int(longitude / 30)
        
        # Degrees within rasi
        degrees_in_rasi = longitude % 30
        
        # Each dasamsa is 3 degrees
        dasamsa_index = int(degrees_in_rasi / 3)  # 0-9
        
        # Dasamsa calculation based on odd/even signs
        if rasi_index % 2 == 0:  # Odd signs (Aries, Gemini, Leo, etc.)
            # Start from same sign
            result_rasi = (rasi_index + dasamsa_index) % 12
        else:  # Even signs (Taurus, Cancer, Virgo, etc.)
            # Start from 9th sign
            start_rasi = (rasi_index + 8) % 12  # 9th from current
            result_rasi = (start_rasi + dasamsa_index) % 12
        
        return CalculationsHelper.RASIS[result_rasi]
    
    @staticmethod
    def get_divisional_house_placements(divisional_type: str,
                                      d1_ascendant: float, 
                                      graha_positions: Dict[str, Dict]) -> Dict[int, List[str]]:
        """
        Calculate house placements for any divisional chart
        
        Args:
            divisional_type: Type of divisional chart ('D2', 'D3', 'D9', 'D10')
            d1_ascendant: D1 ascendant longitude in degrees
            graha_positions: Dictionary of graha positions from D1 chart
            
        Returns:
            Dictionary mapping house numbers to list of planets in that house
        """
        # Get divisional ascendant
        if divisional_type == 'D2':
            div_asc_sign = CalculationsHelper.get_hora_rasi(d1_ascendant)
        elif divisional_type == 'D3':
            div_asc_sign = CalculationsHelper.get_drekkana_rasi(d1_ascendant)
        elif divisional_type == 'D9':
            div_asc_sign = CalculationsHelper.get_navamsa_rasi(d1_ascendant)
        elif divisional_type == 'D10':
            div_asc_sign = CalculationsHelper.get_dasamsa_rasi(d1_ascendant)
        else:
            raise ValueError(f"Unsupported divisional type: {divisional_type}")
        
        div_asc_index = CalculationsHelper.RASIS.index(div_asc_sign)
        
        # Initialize house placements
        house_planets = {i: [] for i in range(1, 13)}
        
        # Calculate divisional positions for each planet
        for graha, data in graha_positions.items():
            if 'longitude' in data:
                # Get divisional sign for this planet
                if divisional_type == 'D2':
                    div_sign = CalculationsHelper.get_hora_rasi(data['longitude'])
                elif divisional_type == 'D3':
                    div_sign = CalculationsHelper.get_drekkana_rasi(data['longitude'])
                elif divisional_type == 'D9':
                    div_sign = CalculationsHelper.get_navamsa_rasi(data['longitude'])
                elif divisional_type == 'D10':
                    div_sign = CalculationsHelper.get_dasamsa_rasi(data['longitude'])
                
                div_sign_index = CalculationsHelper.RASIS.index(div_sign)
                
                # Calculate house number (1-12)
                house_num = ((div_sign_index - div_asc_index) % 12) + 1
                
                house_planets[house_num].append(graha)
        
        return house_planets
    
    @staticmethod
    def calculate_bhava_madhya(ascendant: float, bhava_number: int, 
                              house_system: str = 'Placidus') -> float:
        """
        Calculate bhava madhya (house cusp) for given house number
        
        Args:
            ascendant: Ascendant degree (0-360)
            bhava_number: House number (1-12)
            house_system: House system to use (currently only supports equal house)
            
        Returns:
            Bhava madhya degree
        """
        if bhava_number < 1 or bhava_number > 12:
            raise ValueError("Bhava number must be between 1 and 12")
            
        ascendant = CalculationsHelper.normalize_degrees(ascendant)
        
        # For now, using equal house system
        # TODO: Implement Placidus and other house systems
        if house_system == 'Equal' or True:  # Default to equal for now
            # Each house is 30 degrees
            bhava_madhya = ascendant + (bhava_number - 1) * 30
            return CalculationsHelper.normalize_degrees(bhava_madhya)
    
    @staticmethod
    def get_bhava_from_degree(degree: float, ascendant: float, 
                            house_system: str = 'Equal') -> int:
        """
        Determine which bhava a given degree falls in
        
        Args:
            degree: Longitude degree to check
            ascendant: Ascendant degree
            house_system: House system to use
            
        Returns:
            Bhava number (1-12)
        """
        degree = CalculationsHelper.normalize_degrees(degree)
        ascendant = CalculationsHelper.normalize_degrees(ascendant)
        
        # For equal house system
        if house_system == 'Equal' or True:  # Default to equal for now
            # Calculate distance from ascendant
            distance = degree - ascendant
            if distance < 0:
                distance += 360
                
            # Each house is 30 degrees
            bhava = int(distance / 30) + 1
            
            return bhava
    
    @staticmethod
    def is_retrograde(speed: float) -> bool:
        """
        Check if a graha is retrograde based on its speed
        
        Args:
            speed: Daily motion speed in degrees
            
        Returns:
            True if retrograde, False otherwise
        """
        return speed < 0
    
    @staticmethod
    def get_rasi_element(rasi: str) -> str:
        """
        Get element of a rasi
        
        Args:
            rasi: Rasi name
            
        Returns:
            Element name (Fire, Earth, Air, Water)
        """
        elements = {
            'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
            'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
            'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
            'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'
        }
        return elements.get(rasi, 'Unknown')
    
    @staticmethod
    def get_rasi_quality(rasi: str) -> str:
        """
        Get quality/modality of a rasi
        
        Args:
            rasi: Rasi name
            
        Returns:
            Quality name (Cardinal/Movable, Fixed, Mutable/Dual)
        """
        qualities = {
            'Aries': 'Cardinal', 'Cancer': 'Cardinal', 
            'Libra': 'Cardinal', 'Capricorn': 'Cardinal',
            'Taurus': 'Fixed', 'Leo': 'Fixed', 
            'Scorpio': 'Fixed', 'Aquarius': 'Fixed',
            'Gemini': 'Mutable', 'Virgo': 'Mutable', 
            'Sagittarius': 'Mutable', 'Pisces': 'Mutable'
        }
        return qualities.get(rasi, 'Unknown')
    
    @staticmethod
    def get_functional_nature(graha: str, ascendant_rasi: str) -> str:
        """
        Get functional nature of graha based on ascendant
        
        Args:
            graha: Graha name
            ascendant_rasi: Ascendant rasi
            
        Returns:
            'Benefic', 'Malefic', 'Neutral', or 'Yoga Karaka'
        """
        # This is a simplified version
        # Full implementation would consider lordships
        
        # Natural benefics and malefics
        natural_benefics = ['Jupiter', 'Venus', 'Mercury', 'Moon']
        natural_malefics = ['Saturn', 'Mars', 'Sun', 'Rahu', 'Ketu']
        
        # Basic determination (should be enhanced with lordship rules)
        if graha in natural_benefics:
            return 'Benefic'
        elif graha in natural_malefics:
            return 'Malefic'
        else:
            return 'Neutral'
    
    @staticmethod
    def calculate_vargas(longitude: float) -> Dict[str, str]:
        """
        Calculate various divisional charts (vargas) positions
        
        Args:
            longitude: Planet longitude in degrees
            
        Returns:
            Dictionary with varga names and rasi positions
        """
        longitude = CalculationsHelper.normalize_degrees(longitude)
        
        vargas = {}
        
        # D1 - Rasi chart
        vargas['D1'] = CalculationsHelper.RASIS[int(longitude / 30)]
        
        # D2 - Hora chart
        rasi_index = int(longitude / 30)
        degrees_in_rasi = longitude % 30
        if degrees_in_rasi < 15:
            # First half - ruled by Moon (Cancer)
            vargas['D2'] = 'Cancer' if rasi_index % 2 == 0 else 'Leo'
        else:
            # Second half - ruled by Sun (Leo)
            vargas['D2'] = 'Leo' if rasi_index % 2 == 0 else 'Cancer'
        
        # D3 - Drekkana chart
        drekkana_part = int(degrees_in_rasi / 10)
        drekkana_starts = {
            'Fire': [0, 4, 8],    # Aries, Leo, Sagittarius
            'Earth': [1, 5, 9],   # Taurus, Virgo, Capricorn
            'Air': [2, 6, 10],    # Gemini, Libra, Aquarius
            'Water': [3, 7, 11]   # Cancer, Scorpio, Pisces
        }
        element = CalculationsHelper.get_rasi_element(CalculationsHelper.RASIS[rasi_index])
        element_key = element if element in drekkana_starts else 'Fire'
        drekkana_index = drekkana_starts[element_key][drekkana_part]
        vargas['D3'] = CalculationsHelper.RASIS[drekkana_index]
        
        # D9 - Navamsa chart (already implemented)
        vargas['D9'] = CalculationsHelper.get_navamsa_rasi(longitude)
        
        # D12 - Dwadasamsa chart
        dwadasamsa_part = int(degrees_in_rasi / 2.5)
        dwadasamsa_index = (rasi_index + dwadasamsa_part) % 12
        vargas['D12'] = CalculationsHelper.RASIS[dwadasamsa_index]
        
        return vargas
    
    @staticmethod
    def get_nakshatra_lord(nakshatra: str) -> str:
        """
        Get the lord of a nakshatra
        
        Args:
            nakshatra: Nakshatra name
            
        Returns:
            Lord graha name
        """
        # Vimshottari dasha system lords
        nakshatra_lords = {
            'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun',
            'Rohini': 'Moon', 'Mrigashira': 'Mars', 'Ardra': 'Rahu',
            'Punarvasu': 'Jupiter', 'Pushya': 'Saturn', 'Ashlesha': 'Mercury',
            'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
            'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu',
            'Vishakha': 'Jupiter', 'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury',
            'Mula': 'Ketu', 'Purva Ashadha': 'Venus', 'Uttara Ashadha': 'Sun',
            'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
            'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 
            'Revati': 'Mercury'
        }
        return nakshatra_lords.get(nakshatra, 'Unknown')
    
    @staticmethod
    def load_json_data(filename: str) -> Dict:
        """
        Load JSON data from CentralData directory
        
        Args:
            filename: Name of JSON file to load
            
        Returns:
            Loaded JSON data as dictionary
        """
        base_path = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_path, 'CentralData', filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found in CentralData directory")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Error parsing {filename}")
            return {}
    
    @staticmethod
    def get_timezone_offset(timezone_str: str, dt: datetime) -> float:
        """
        Get timezone offset in hours for a given timezone and datetime
        
        Args:
            timezone_str: Timezone string (e.g., 'Asia/Kolkata')
            dt: Datetime object
            
        Returns:
            Offset in hours from UTC
        """
        try:
            import pytz
            tz = pytz.timezone(timezone_str)
            
            # Make datetime timezone-aware if it isn't already
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            else:
                dt = dt.astimezone(tz)
                
            # Get UTC offset
            offset = dt.utcoffset().total_seconds() / 3600.0
            return offset
            
        except Exception as e:
            print(f"Error getting timezone offset: {e}")
            return 0.0
    
    @staticmethod
    def degrees_to_rasi(longitude: float) -> Dict[str, Union[str, float]]:
        """
        Convert longitude degrees to rasi and degrees within rasi
        
        Args:
            longitude: Longitude in degrees (0-360)
            
        Returns:
            Dictionary with rasi name and degrees within rasi
        """
        longitude = CalculationsHelper.normalize_degrees(longitude)
        
        # Each rasi is 30 degrees
        rasi_index = int(longitude / 30)
        degrees_in_rasi = longitude % 30
        
        return {
            'rasi': CalculationsHelper.RASIS[rasi_index],
            'degrees': degrees_in_rasi
        }
