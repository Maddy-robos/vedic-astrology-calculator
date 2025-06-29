"""
graha.py - Graha (planet) model and characteristics

This module provides:
- Graha class representing a planet with its properties
- Methods to access graha characteristics
- Natural relationships between grahas
- Exaltation/debilitation positions
"""

from typing import Dict, List, Optional, Union, Tuple
import json
import os
try:
    from .calculations_helper import CalculationsHelper
except ImportError:
    from calculations_helper import CalculationsHelper


class Graha:
    """Class representing a graha (planet) with its characteristics and state"""
    
    # Natural relationships between grahas (Naisargika Maitri)
    NATURAL_FRIENDSHIPS = {
        'Sun': {
            'friends': ['Moon', 'Mars', 'Jupiter'],
            'neutrals': ['Mercury'],
            'enemies': ['Venus', 'Saturn', 'Rahu', 'Ketu']
        },
        'Moon': {
            'friends': ['Sun', 'Mercury'],
            'neutrals': ['Mars', 'Jupiter', 'Venus', 'Saturn'],
            'enemies': ['Rahu', 'Ketu']
        },
        'Mars': {
            'friends': ['Sun', 'Moon', 'Jupiter'],
            'neutrals': ['Venus', 'Saturn'],
            'enemies': ['Mercury', 'Rahu', 'Ketu']
        },
        'Mercury': {
            'friends': ['Sun', 'Venus'],
            'neutrals': ['Mars', 'Jupiter', 'Saturn'],
            'enemies': ['Moon', 'Rahu', 'Ketu']
        },
        'Jupiter': {
            'friends': ['Sun', 'Moon', 'Mars'],
            'neutrals': ['Saturn'],
            'enemies': ['Mercury', 'Venus', 'Rahu', 'Ketu']
        },
        'Venus': {
            'friends': ['Mercury', 'Saturn'],
            'neutrals': ['Mars', 'Jupiter'],
            'enemies': ['Sun', 'Moon', 'Rahu', 'Ketu']
        },
        'Saturn': {
            'friends': ['Mercury', 'Venus'],
            'neutrals': ['Jupiter'],
            'enemies': ['Sun', 'Moon', 'Mars', 'Rahu', 'Ketu']
        },
        'Rahu': {
            'friends': ['Mercury', 'Venus', 'Saturn'],
            'neutrals': [],
            'enemies': ['Sun', 'Moon', 'Mars', 'Jupiter']
        },
        'Ketu': {
            'friends': ['Mars', 'Venus', 'Saturn'],
            'neutrals': [],
            'enemies': ['Sun', 'Moon', 'Mercury', 'Jupiter']
        }
    }
    
    # Graha characteristics
    GRAHA_CHARACTERISTICS = {
        'Sun': {
            'sanskrit': 'Surya',
            'gender': 'Male',
            'nature': 'Malefic',
            'element': 'Fire',
            'guna': 'Sattva',
            'owns': ['Leo'],
            'moolatrikona': {'sign': 'Leo', 'degrees': (0, 20)},
            'exaltation': {'sign': 'Aries', 'degree': 10},
            'debilitation': {'sign': 'Libra', 'degree': 10},
            'karakatva': ['Soul', 'Father', 'Government', 'Authority', 'Health'],
            'direction': 'East',
            'color': 'Red',
            'metal': 'Gold',
            'gemstone': 'Ruby',
            'day': 'Sunday'
        },
        'Moon': {
            'sanskrit': 'Chandra',
            'gender': 'Female',
            'nature': 'Benefic when waxing, Malefic when waning',
            'element': 'Water',
            'guna': 'Sattva',
            'owns': ['Cancer'],
            'moolatrikona': {'sign': 'Taurus', 'degrees': (4, 30)},
            'exaltation': {'sign': 'Taurus', 'degree': 3},
            'debilitation': {'sign': 'Scorpio', 'degree': 3},
            'karakatva': ['Mind', 'Mother', 'Emotions', 'Public', 'Liquids'],
            'direction': 'Northwest',
            'color': 'White',
            'metal': 'Silver',
            'gemstone': 'Pearl',
            'day': 'Monday'
        },
        'Mars': {
            'sanskrit': 'Mangala/Kuja',
            'gender': 'Male',
            'nature': 'Malefic',
            'element': 'Fire',
            'guna': 'Tamas',
            'owns': ['Aries', 'Scorpio'],
            'moolatrikona': {'sign': 'Aries', 'degrees': (0, 12)},
            'exaltation': {'sign': 'Capricorn', 'degree': 28},
            'debilitation': {'sign': 'Cancer', 'degree': 28},
            'karakatva': ['Energy', 'Siblings', 'Property', 'Courage', 'Conflicts'],
            'direction': 'South',
            'color': 'Red',
            'metal': 'Copper',
            'gemstone': 'Red Coral',
            'day': 'Tuesday'
        },
        'Mercury': {
            'sanskrit': 'Budha',
            'gender': 'Neutral',
            'nature': 'Benefic if alone or with benefics, Malefic with malefics',
            'element': 'Earth',
            'guna': 'Rajas',
            'owns': ['Gemini', 'Virgo'],
            'moolatrikona': {'sign': 'Virgo', 'degrees': (16, 20)},
            'exaltation': {'sign': 'Virgo', 'degree': 15},
            'debilitation': {'sign': 'Pisces', 'degree': 15},
            'karakatva': ['Communication', 'Intelligence', 'Trade', 'Education', 'Friends'],
            'direction': 'North',
            'color': 'Green',
            'metal': 'Brass',
            'gemstone': 'Emerald',
            'day': 'Wednesday'
        },
        'Jupiter': {
            'sanskrit': 'Guru/Brihaspati',
            'gender': 'Male',
            'nature': 'Benefic',
            'element': 'Ether',
            'guna': 'Sattva',
            'owns': ['Sagittarius', 'Pisces'],
            'moolatrikona': {'sign': 'Sagittarius', 'degrees': (0, 10)},
            'exaltation': {'sign': 'Cancer', 'degree': 5},
            'debilitation': {'sign': 'Capricorn', 'degree': 5},
            'karakatva': ['Wisdom', 'Children', 'Wealth', 'Religion', 'Teachers'],
            'direction': 'Northeast',
            'color': 'Yellow',
            'metal': 'Gold',
            'gemstone': 'Yellow Sapphire',
            'day': 'Thursday'
        },
        'Venus': {
            'sanskrit': 'Shukra',
            'gender': 'Female',
            'nature': 'Benefic',
            'element': 'Water',
            'guna': 'Rajas',
            'owns': ['Taurus', 'Libra'],
            'moolatrikona': {'sign': 'Libra', 'degrees': (0, 15)},
            'exaltation': {'sign': 'Pisces', 'degree': 27},
            'debilitation': {'sign': 'Virgo', 'degree': 27},
            'karakatva': ['Marriage', 'Love', 'Arts', 'Luxury', 'Vehicles'],
            'direction': 'Southeast',
            'color': 'White',
            'metal': 'Silver',
            'gemstone': 'Diamond',
            'day': 'Friday'
        },
        'Saturn': {
            'sanskrit': 'Shani',
            'gender': 'Neutral',
            'nature': 'Malefic',
            'element': 'Air',
            'guna': 'Tamas',
            'owns': ['Capricorn', 'Aquarius'],
            'moolatrikona': {'sign': 'Aquarius', 'degrees': (0, 20)},
            'exaltation': {'sign': 'Libra', 'degree': 20},
            'debilitation': {'sign': 'Aries', 'degree': 20},
            'karakatva': ['Longevity', 'Sorrow', 'Discipline', 'Servants', 'Delays'],
            'direction': 'West',
            'color': 'Black/Blue',
            'metal': 'Iron',
            'gemstone': 'Blue Sapphire',
            'day': 'Saturday'
        },
        'Rahu': {
            'sanskrit': 'Rahu',
            'gender': 'Male',
            'nature': 'Malefic',
            'element': 'Air',
            'guna': 'Tamas',
            'owns': [],  # Shadowy planet, no ownership
            'moolatrikona': {'sign': 'Gemini', 'degrees': (0, 30)},  # Some consider
            'exaltation': {'sign': 'Gemini', 'degree': 15},  # Some say Taurus
            'debilitation': {'sign': 'Sagittarius', 'degree': 15},  # Some say Scorpio
            'karakatva': ['Illusion', 'Foreign', 'Technology', 'Obsession', 'Sudden events'],
            'direction': 'Southwest',
            'color': 'Smoky',
            'metal': 'Lead',
            'gemstone': 'Hessonite',
            'day': 'Saturday'  # Co-rules with Saturn
        },
        'Ketu': {
            'sanskrit': 'Ketu',
            'gender': 'Neutral',
            'nature': 'Malefic',
            'element': 'Fire',
            'guna': 'Tamas',
            'owns': [],  # Shadowy planet, no ownership
            'moolatrikona': {'sign': 'Sagittarius', 'degrees': (0, 30)},  # Some consider
            'exaltation': {'sign': 'Sagittarius', 'degree': 15},  # Some say Scorpio
            'debilitation': {'sign': 'Gemini', 'degree': 15},  # Some say Taurus
            'karakatva': ['Spirituality', 'Liberation', 'Past karma', 'Separation', 'Occult'],
            'direction': 'Northwest',
            'color': 'Multi-colored',
            'metal': 'Lead',
            'gemstone': 'Cat\'s Eye',
            'day': 'Tuesday'  # Co-rules with Mars
        }
    }
    
    def __init__(self, name: str, longitude: float = 0.0, latitude: float = 0.0, 
                 speed: float = 0.0, nakshatra: Optional[str] = None):
        """
        Initialize a Graha object
        
        Args:
            name: Name of the graha (e.g., 'Sun', 'Moon', etc.)
            longitude: Ecliptic longitude in degrees (0-360)
            latitude: Ecliptic latitude in degrees
            speed: Daily motion in degrees (negative if retrograde)
            nakshatra: Current nakshatra placement
        """
        if name not in self.GRAHA_CHARACTERISTICS:
            raise ValueError(f"Invalid graha name: {name}")
            
        self.name = name
        self.longitude = CalculationsHelper.normalize_degrees(longitude)
        self.latitude = latitude
        self.speed = speed
        self.is_retrograde = speed < 0
        
        # Calculate rasi and degrees
        rasi_data = CalculationsHelper.degrees_to_rasi(self.longitude)
        self.rasi = rasi_data['rasi']
        self.degrees_in_rasi = rasi_data['degrees']
        
        # Calculate nakshatra if not provided
        if nakshatra is None:
            nakshatra_data = CalculationsHelper.get_nakshatra_pada(self.longitude)
            self.nakshatra = nakshatra_data['nakshatra']
            self.pada = nakshatra_data['pada']
        else:
            self.nakshatra = nakshatra
            self.pada = CalculationsHelper.get_nakshatra_pada(self.longitude)['pada']
            
        # Load characteristics
        self.characteristics = self.GRAHA_CHARACTERISTICS[name].copy()
        self.natural_relationships = self.NATURAL_FRIENDSHIPS[name].copy()
        
    def get_dignity(self) -> str:
        """
        Get the dignity status of the graha in its current position
        
        Returns:
            'Exalted', 'Own Sign', 'Moolatrikona', 'Debilitated', or 'Neutral'
        """
        char = self.characteristics
        
        # Check exaltation
        if 'exaltation' in char and char['exaltation']['sign'] == self.rasi:
            # Check if within orb of exact degree (usually 1 degree orb)
            exact_degree = char['exaltation']['degree']
            if abs(self.degrees_in_rasi - exact_degree) <= 1:
                return 'Exalted (exact)'
            else:
                return 'Exalted'
                
        # Check debilitation
        if 'debilitation' in char and char['debilitation']['sign'] == self.rasi:
            exact_degree = char['debilitation']['degree']
            if abs(self.degrees_in_rasi - exact_degree) <= 1:
                return 'Debilitated (exact)'
            else:
                return 'Debilitated'
                
        # Check own sign
        if self.rasi in char.get('owns', []):
            # Check if in moolatrikona portion
            if 'moolatrikona' in char and char['moolatrikona']['sign'] == self.rasi:
                mt_degrees = char['moolatrikona']['degrees']
                if mt_degrees[0] <= self.degrees_in_rasi <= mt_degrees[1]:
                    return 'Moolatrikona'
            return 'Own Sign'
            
        return 'Neutral'
    
    def get_natural_relationship(self, other_graha: str) -> str:
        """
        Get natural relationship with another graha
        
        Args:
            other_graha: Name of the other graha
            
        Returns:
            'Friend', 'Neutral', or 'Enemy'
        """
        if other_graha in self.natural_relationships['friends']:
            return 'Friend'
        elif other_graha in self.natural_relationships['neutrals']:
            return 'Neutral'
        elif other_graha in self.natural_relationships['enemies']:
            return 'Enemy'
        else:
            return 'Unknown'
    
    def is_benefic(self) -> bool:
        """
        Check if graha is naturally benefic
        
        Returns:
            True if benefic, False if malefic
        """
        nature = self.characteristics.get('nature', '')
        
        if self.name == 'Moon':
            # Moon is benefic when waxing (needs additional calculation)
            # For now, return True as a placeholder
            return True
        elif self.name == 'Mercury':
            # Mercury's nature depends on associations (needs chart context)
            # For now, return True as a placeholder
            return True
        
        return 'Benefic' in nature
    
    def get_karaka_significations(self) -> List[str]:
        """
        Get the natural significations (karakatva) of the graha
        
        Returns:
            List of significations
        """
        return self.characteristics.get('karakatva', [])
    
    def get_owned_signs(self) -> List[str]:
        """
        Get the signs owned by this graha
        
        Returns:
            List of owned sign names
        """
        return self.characteristics.get('owns', [])
    
    def get_aspect_strength(self, target_longitude: float) -> float:
        """
        Calculate the strength of aspect to a target point
        
        Args:
            target_longitude: Target longitude in degrees
            
        Returns:
            Aspect strength (0.0 to 1.0)
        """
        distance = CalculationsHelper.get_angular_distance(self.longitude, target_longitude)
        
        # Full aspects (drishti) based on graha
        full_aspects = {
            'Mars': [90, 120, 210],      # 4th, 8th aspects
            'Jupiter': [120, 240],        # 5th, 9th aspects  
            'Saturn': [60, 90, 270],      # 3rd, 10th aspects
            'Rahu': [120, 240],           # 5th, 9th aspects
            'Ketu': [120, 240]            # 5th, 9th aspects
        }
        
        # All grahas have 7th aspect (180 degrees)
        if abs(distance - 180) <= 1:
            return 1.0
            
        # Check special aspects
        if self.name in full_aspects:
            for aspect_angle in full_aspects[self.name]:
                if abs(distance - aspect_angle) <= 1:
                    return 1.0
                    
        # Partial aspects (all grahas)
        partial_aspects = {
            30: 0.25,   # 2nd house
            60: 0.5,    # 3rd house
            90: 0.75,   # 4th house
            120: 0.5,   # 5th house
            150: 0.25,  # 6th house
            210: 0.25,  # 8th house
            240: 0.5,   # 9th house
            270: 0.75,  # 10th house
            300: 0.5,   # 11th house
            330: 0.25   # 12th house
        }
        
        for angle, strength in partial_aspects.items():
            if abs(distance - angle) <= 5:  # 5 degree orb for partial aspects
                return strength
                
        return 0.0
    
    def to_dict(self) -> Dict[str, Union[str, float, bool, List, Dict]]:
        """
        Convert graha object to dictionary representation
        
        Returns:
            Dictionary with graha data
        """
        return {
            'name': self.name,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'speed': self.speed,
            'is_retrograde': self.is_retrograde,
            'rasi': self.rasi,
            'degrees_in_rasi': self.degrees_in_rasi,
            'nakshatra': self.nakshatra,
            'pada': self.pada,
            'dignity': self.get_dignity(),
            'is_benefic': self.is_benefic(),
            'sanskrit_name': self.characteristics.get('sanskrit', ''),
            'element': self.characteristics.get('element', ''),
            'owns': self.get_owned_signs()
        }
    
    def __str__(self) -> str:
        """String representation of the graha"""
        return (f"{self.name} at {self.degrees_in_rasi:.2f}° {self.rasi} "
                f"({self.nakshatra} pada {self.pada})")
    
    def __repr__(self) -> str:
        """Detailed representation of the graha"""
        return (f"Graha(name='{self.name}', longitude={self.longitude:.2f}, "
                f"rasi='{self.rasi}', dignity='{self.get_dignity()}')")
