"""
rasi.py - Rasi (zodiac sign) model and characteristics

This module provides:
- Rasi class representing a zodiac sign with its properties
- Methods to access rasi characteristics
- Element, quality, and rulership information
- Aspect patterns and relationships
"""

from typing import Dict, List, Optional, Union, Tuple
import json
import os
try:
    from .calculations_helper import CalculationsHelper
except ImportError:
    from calculations_helper import CalculationsHelper


class Rasi:
    """Class representing a rasi (zodiac sign) with its characteristics"""
    
    # Rasi characteristics
    RASI_CHARACTERISTICS = {
        'Aries': {
            'sanskrit': 'Mesha',
            'number': 1,
            'element': 'Fire',
            'quality': 'Cardinal',
            'gender': 'Male',
            'nature': 'Movable',
            'ruling_planet': 'Mars',
            'exaltation_planet': 'Sun',
            'debilitation_planet': 'Saturn',
            'moolatrikona_planet': 'Mars',
            'friendly_planets': ['Sun', 'Moon', 'Mars', 'Jupiter'],
            'enemy_planets': ['Mercury', 'Venus', 'Saturn'],
            'body_parts': ['Head', 'Brain', 'Eyes'],
            'direction': 'East',
            'symbol': 'Ram',
            'color': 'Red',
            'gemstone': 'Red Coral',
            'deity': 'Agni',
            'gana': 'Deva'
        },
        'Taurus': {
            'sanskrit': 'Vrishabha',
            'number': 2,
            'element': 'Earth',
            'quality': 'Fixed',
            'gender': 'Female',
            'nature': 'Fixed',
            'ruling_planet': 'Venus',
            'exaltation_planet': 'Moon',
            'debilitation_planet': 'none',
            'moolatrikona_planet': 'Venus',
            'friendly_planets': ['Mercury', 'Venus', 'Saturn'],
            'enemy_planets': ['Sun', 'Moon', 'Mars'],
            'body_parts': ['Face', 'Neck', 'Throat'],
            'direction': 'South',
            'symbol': 'Bull',
            'color': 'White',
            'gemstone': 'Diamond',
            'deity': 'Lakshmi',
            'gana': 'Manushya'
        },
        'Gemini': {
            'sanskrit': 'Mithuna',
            'number': 3,
            'element': 'Air',
            'quality': 'Mutable',
            'gender': 'Male',
            'nature': 'Dual',
            'ruling_planet': 'Mercury',
            'exaltation_planet': 'Rahu',
            'debilitation_planet': 'Ketu',
            'moolatrikona_planet': 'Mercury',
            'friendly_planets': ['Sun', 'Mercury', 'Venus'],
            'enemy_planets': ['Moon', 'Mars', 'Jupiter'],
            'body_parts': ['Arms', 'Shoulders', 'Lungs'],
            'direction': 'West',
            'symbol': 'Twins',
            'color': 'Green',
            'gemstone': 'Emerald',
            'deity': 'Vishnu',
            'gana': 'Manushya'
        },
        'Cancer': {
            'sanskrit': 'Karkat',
            'number': 4,
            'element': 'Water',
            'quality': 'Cardinal',
            'gender': 'Female',
            'nature': 'Movable',
            'ruling_planet': 'Moon',
            'exaltation_planet': 'Jupiter',
            'debilitation_planet': 'Mars',
            'moolatrikona_planet': 'Moon',
            'friendly_planets': ['Sun', 'Moon', 'Mars', 'Jupiter'],
            'enemy_planets': ['Mercury', 'Venus', 'Saturn'],
            'body_parts': ['Chest', 'Stomach', 'Breasts'],
            'direction': 'North',
            'symbol': 'Crab',
            'color': 'Pale Blue',
            'gemstone': 'Pearl',
            'deity': 'Varuna',
            'gana': 'Deva'
        },
        'Leo': {
            'sanskrit': 'Simha',
            'number': 5,
            'element': 'Fire',
            'quality': 'Fixed',
            'gender': 'Male',
            'nature': 'Fixed',
            'ruling_planet': 'Sun',
            'exaltation_planet': 'none',
            'debilitation_planet': 'none',
            'moolatrikona_planet': 'Sun',
            'friendly_planets': ['Sun', 'Moon', 'Mars', 'Jupiter'],
            'enemy_planets': ['Mercury', 'Venus', 'Saturn'],
            'body_parts': ['Heart', 'Upper Back', 'Spine'],
            'direction': 'East',
            'symbol': 'Lion',
            'color': 'Golden',
            'gemstone': 'Ruby',
            'deity': 'Shiva',
            'gana': 'Rakshasa'
        },
        'Virgo': {
            'sanskrit': 'Kanya',
            'number': 6,
            'element': 'Earth',
            'quality': 'Mutable',
            'gender': 'Female',
            'nature': 'Dual',
            'ruling_planet': 'Mercury',
            'exaltation_planet': 'Mercury',
            'debilitation_planet': 'Venus',
            'moolatrikona_planet': 'Mercury',
            'friendly_planets': ['Sun', 'Mercury', 'Venus'],
            'enemy_planets': ['Moon', 'Mars', 'Jupiter'],
            'body_parts': ['Abdomen', 'Intestines', 'Digestive system'],
            'direction': 'South',
            'symbol': 'Virgin',
            'color': 'Navy Blue',
            'gemstone': 'Emerald',
            'deity': 'Kali',
            'gana': 'Manushya'
        },
        'Libra': {
            'sanskrit': 'Tula',
            'number': 7,
            'element': 'Air',
            'quality': 'Cardinal',
            'gender': 'Male',
            'nature': 'Movable',
            'ruling_planet': 'Venus',
            'exaltation_planet': 'Saturn',
            'debilitation_planet': 'Sun',
            'moolatrikona_planet': 'Venus',
            'friendly_planets': ['Mercury', 'Venus', 'Saturn'],
            'enemy_planets': ['Sun', 'Moon', 'Mars'],
            'body_parts': ['Lower Back', 'Kidneys', 'Skin'],
            'direction': 'West',
            'symbol': 'Balance/Scales',
            'color': 'Bright Colors',
            'gemstone': 'Diamond',
            'deity': 'Indra',
            'gana': 'Rakshasa'
        },
        'Scorpio': {
            'sanskrit': 'Vrischik',
            'number': 8,
            'element': 'Water',
            'quality': 'Fixed',
            'gender': 'Female',
            'nature': 'Fixed',
            'ruling_planet': 'Mars',
            'exaltation_planet': 'Ketu',
            'debilitation_planet': 'Moon',
            'moolatrikona_planet': 'Mars',
            'friendly_planets': ['Sun', 'Moon', 'Mars', 'Jupiter'],
            'enemy_planets': ['Mercury', 'Venus', 'Saturn'],
            'body_parts': ['Reproductive organs', 'Bladder', 'Rectum'],
            'direction': 'North',
            'symbol': 'Scorpion',
            'color': 'Deep Red',
            'gemstone': 'Red Coral',
            'deity': 'Mangal',
            'gana': 'Deva'
        },
        'Sagittarius': {
            'sanskrit': 'Dhanu',
            'number': 9,
            'element': 'Fire',
            'quality': 'Mutable',
            'gender': 'Male',
            'nature': 'Dual',
            'ruling_planet': 'Jupiter',
            'exaltation_planet': 'Ketu',
            'debilitation_planet': 'Rahu',
            'moolatrikona_planet': 'Jupiter',
            'friendly_planets': ['Sun', 'Moon', 'Mars', 'Jupiter'],
            'enemy_planets': ['Mercury', 'Venus', 'Saturn'],
            'body_parts': ['Hips', 'Thighs', 'Liver'],
            'direction': 'East',
            'symbol': 'Archer/Bow',
            'color': 'Yellow',
            'gemstone': 'Yellow Sapphire',
            'deity': 'Indra',
            'gana': 'Deva'
        },
        'Capricorn': {
            'sanskrit': 'Makar',
            'number': 10,
            'element': 'Earth',
            'quality': 'Cardinal',
            'gender': 'Female',
            'nature': 'Movable',
            'ruling_planet': 'Saturn',
            'exaltation_planet': 'Mars',
            'debilitation_planet': 'Jupiter',
            'moolatrikona_planet': 'Saturn',
            'friendly_planets': ['Mercury', 'Venus', 'Saturn'],
            'enemy_planets': ['Sun', 'Moon', 'Mars'],
            'body_parts': ['Knees', 'Bones', 'Teeth'],
            'direction': 'South',
            'symbol': 'Crocodile/Sea-goat',
            'color': 'Black',
            'gemstone': 'Blue Sapphire',
            'deity': 'Varuna',
            'gana': 'Rakshasa'
        },
        'Aquarius': {
            'sanskrit': 'Kumbha',
            'number': 11,
            'element': 'Air',
            'quality': 'Fixed',
            'gender': 'Male',
            'nature': 'Fixed',
            'ruling_planet': 'Saturn',
            'exaltation_planet': 'none',
            'debilitation_planet': 'none',
            'moolatrikona_planet': 'Saturn',
            'friendly_planets': ['Mercury', 'Venus', 'Saturn'],
            'enemy_planets': ['Sun', 'Moon', 'Mars'],
            'body_parts': ['Calves', 'Ankles', 'Circulatory system'],
            'direction': 'West',
            'symbol': 'Water Bearer',
            'color': 'Blue',
            'gemstone': 'Blue Sapphire',
            'deity': 'Varuna',
            'gana': 'Manushya'
        },
        'Pisces': {
            'sanskrit': 'Meen',
            'number': 12,
            'element': 'Water',
            'quality': 'Mutable',
            'gender': 'Female',
            'nature': 'Dual',
            'ruling_planet': 'Jupiter',
            'exaltation_planet': 'Venus',
            'debilitation_planet': 'Mercury',
            'moolatrikona_planet': 'Jupiter',
            'friendly_planets': ['Sun', 'Moon', 'Mars', 'Jupiter'],
            'enemy_planets': ['Mercury', 'Venus', 'Saturn'],
            'body_parts': ['Feet', 'Toes', 'Lymphatic system'],
            'direction': 'North',
            'symbol': 'Fish',
            'color': 'Sea Green',
            'gemstone': 'Yellow Sapphire',
            'deity': 'Vishnu',
            'gana': 'Deva'
        }
    }
    
    # Rasi order for calculations
    RASI_ORDER = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    
    def __init__(self, name: str):
        """
        Initialize a Rasi object
        
        Args:
            name: Name of the rasi (e.g., 'Aries', 'Taurus', etc.)
        """
        if name not in self.RASI_CHARACTERISTICS:
            raise ValueError(f"Invalid rasi name: {name}")
            
        self.name = name
        self.characteristics = self.RASI_CHARACTERISTICS[name].copy()
        self.number = self.characteristics['number']
        
    def get_element(self) -> str:
        """Get the element of the rasi"""
        return self.characteristics.get('element', 'Unknown')
    
    def get_quality(self) -> str:
        """Get the quality/modality of the rasi"""
        return self.characteristics.get('quality', 'Unknown')
    
    def get_nature(self) -> str:
        """Get the nature of the rasi (Movable/Fixed/Dual)"""
        return self.characteristics.get('nature', 'Unknown')
    
    def get_ruling_planet(self) -> str:
        """Get the ruling planet of the rasi"""
        return self.characteristics.get('ruling_planet', 'Unknown')
    
    def get_exaltation_planet(self) -> str:
        """Get the planet that is exalted in this rasi"""
        return self.characteristics.get('exaltation_planet', 'none')
    
    def get_debilitation_planet(self) -> str:
        """Get the planet that is debilitated in this rasi"""
        return self.characteristics.get('debilitation_planet', 'none')
    
    def get_friendly_planets(self) -> List[str]:
        """Get list of planets friendly to this rasi"""
        return self.characteristics.get('friendly_planets', [])
    
    def get_enemy_planets(self) -> List[str]:
        """Get list of planets enemy to this rasi"""
        return self.characteristics.get('enemy_planets', [])
    
    def is_friend_of_planet(self, planet: str) -> bool:
        """Check if a planet is friend of this rasi"""
        return planet in self.get_friendly_planets()
    
    def is_enemy_of_planet(self, planet: str) -> bool:
        """Check if a planet is enemy of this rasi"""
        return planet in self.get_enemy_planets()
    
    def get_opposite_rasi(self) -> str:
        """Get the opposite rasi (7th from this rasi)"""
        opposite_index = (self.number + 5) % 12  # 7th rasi (0-indexed)
        return self.RASI_ORDER[opposite_index]
    
    def get_trikona_rasis(self) -> List[str]:
        """Get the trikona (trine) rasis from this rasi"""
        # 1st, 5th, and 9th rasis form a trikona
        trikona_indices = [
            (self.number - 1) % 12,      # 1st (self)
            (self.number + 3) % 12,      # 5th
            (self.number + 7) % 12       # 9th
        ]
        return [self.RASI_ORDER[i] for i in trikona_indices]
    
    def get_kendra_rasis(self) -> List[str]:
        """Get the kendra (angular) rasis from this rasi"""
        # 1st, 4th, 7th, and 10th rasis form kendras
        kendra_indices = [
            (self.number - 1) % 12,      # 1st (self)
            (self.number + 2) % 12,      # 4th
            (self.number + 5) % 12,      # 7th
            (self.number + 8) % 12       # 10th
        ]
        return [self.RASI_ORDER[i] for i in kendra_indices]
    
    def get_distance_to_rasi(self, other_rasi: str) -> int:
        """
        Get the distance (number of houses) to another rasi
        
        Args:
            other_rasi: Target rasi name
            
        Returns:
            Distance in houses (1-12)
        """
        if other_rasi not in self.RASI_ORDER:
            raise ValueError(f"Invalid rasi name: {other_rasi}")
            
        other_number = self.RASI_CHARACTERISTICS[other_rasi]['number']
        distance = other_number - self.number
        
        if distance <= 0:
            distance += 12
            
        return distance
    
    def get_rasi_aspects(self) -> List[str]:
        """
        Get the rasis aspected by this rasi according to Parashara's rules
        
        Returns:
            List of aspected rasi names
        """
        aspected_rasis = []
        
        # All rasis aspect the 7th rasi
        opposite = self.get_opposite_rasi()
        aspected_rasis.append(opposite)
        
        # Special aspects based on rasi nature
        nature = self.get_nature()
        
        if nature == 'Movable':  # Cardinal signs
            # Movable signs aspect fixed signs except adjacent ones
            for rasi in self.RASI_ORDER:
                rasi_nature = self.RASI_CHARACTERISTICS[rasi]['nature']
                if rasi_nature == 'Fixed':
                    distance = self.get_distance_to_rasi(rasi)
                    # Exclude adjacent rasis (2nd and 12th)
                    if distance not in [2, 12]:
                        aspected_rasis.append(rasi)
                        
        elif nature == 'Fixed':
            # Fixed signs aspect dual signs except adjacent ones
            for rasi in self.RASI_ORDER:
                rasi_nature = self.RASI_CHARACTERISTICS[rasi]['nature']
                if rasi_nature == 'Dual':
                    distance = self.get_distance_to_rasi(rasi)
                    # Exclude adjacent rasis (2nd and 12th)
                    if distance not in [2, 12]:
                        aspected_rasis.append(rasi)
                        
        elif nature == 'Dual':  # Mutable signs
            # Dual signs aspect movable signs except adjacent ones
            for rasi in self.RASI_ORDER:
                rasi_nature = self.RASI_CHARACTERISTICS[rasi]['nature']
                if rasi_nature == 'Movable':
                    distance = self.get_distance_to_rasi(rasi)
                    # Exclude adjacent rasis (2nd and 12th)
                    if distance not in [2, 12]:
                        aspected_rasis.append(rasi)
        
        # Remove duplicates and self
        aspected_rasis = list(set(aspected_rasis))
        if self.name in aspected_rasis:
            aspected_rasis.remove(self.name)
            
        return aspected_rasis
    
    def is_aspecting_rasi(self, target_rasi: str) -> bool:
        """
        Check if this rasi aspects the target rasi
        
        Args:
            target_rasi: Target rasi name
            
        Returns:
            True if aspecting, False otherwise
        """
        return target_rasi in self.get_rasi_aspects()
    
    def get_same_element_rasis(self) -> List[str]:
        """Get all rasis of the same element"""
        element = self.get_element()
        same_element = []
        
        for rasi in self.RASI_ORDER:
            if self.RASI_CHARACTERISTICS[rasi]['element'] == element:
                same_element.append(rasi)
                
        return same_element
    
    def get_same_quality_rasis(self) -> List[str]:
        """Get all rasis of the same quality/modality"""
        quality = self.get_quality()
        same_quality = []
        
        for rasi in self.RASI_ORDER:
            if self.RASI_CHARACTERISTICS[rasi]['quality'] == quality:
                same_quality.append(rasi)
                
        return same_quality
    
    def get_body_parts(self) -> List[str]:
        """Get body parts ruled by this rasi"""
        return self.characteristics.get('body_parts', [])
    
    def get_direction(self) -> str:
        """Get the cardinal direction associated with this rasi"""
        return self.characteristics.get('direction', 'Unknown')
    
    def get_color(self) -> str:
        """Get the color associated with this rasi"""
        return self.characteristics.get('color', 'Unknown')
    
    def get_symbol(self) -> str:
        """Get the symbol of this rasi"""
        return self.characteristics.get('symbol', 'Unknown')
    
    def get_deity(self) -> str:
        """Get the presiding deity of this rasi"""
        return self.characteristics.get('deity', 'Unknown')
    
    def get_gana(self) -> str:
        """Get the gana (nature) of this rasi"""
        return self.characteristics.get('gana', 'Unknown')
    
    def to_dict(self) -> Dict[str, Union[str, int, List, Dict]]:
        """
        Convert rasi object to dictionary representation
        
        Returns:
            Dictionary with rasi data
        """
        return {
            'name': self.name,
            'sanskrit': self.characteristics.get('sanskrit', ''),
            'number': self.number,
            'element': self.get_element(),
            'quality': self.get_quality(),
            'nature': self.get_nature(),
            'ruling_planet': self.get_ruling_planet(),
            'exaltation_planet': self.get_exaltation_planet(),
            'debilitation_planet': self.get_debilitation_planet(),
            'opposite_rasi': self.get_opposite_rasi(),
            'trikona_rasis': self.get_trikona_rasis(),
            'kendra_rasis': self.get_kendra_rasis(),
            'aspected_rasis': self.get_rasi_aspects(),
            'body_parts': self.get_body_parts(),
            'direction': self.get_direction(),
            'color': self.get_color(),
            'symbol': self.get_symbol(),
            'deity': self.get_deity(),
            'gana': self.get_gana()
        }
    
    def __str__(self) -> str:
        """String representation of the rasi"""
        return f"{self.name} ({self.characteristics.get('sanskrit', '')})"
    
    def __repr__(self) -> str:
        """Detailed representation of the rasi"""
        return (f"Rasi(name='{self.name}', number={self.number}, "
                f"element='{self.get_element()}', quality='{self.get_quality()}')")
    
    @classmethod
    def get_all_rasis(cls) -> List['Rasi']:
        """Get list of all Rasi objects"""
        return [cls(name) for name in cls.RASI_ORDER]
    
    @classmethod
    def get_rasi_by_number(cls, number: int) -> 'Rasi':
        """
        Get Rasi object by its number (1-12)
        
        Args:
            number: Rasi number (1-12)
            
        Returns:
            Rasi object
        """
        if not 1 <= number <= 12:
            raise ValueError("Rasi number must be between 1 and 12")
            
        rasi_name = cls.RASI_ORDER[number - 1]
        return cls(rasi_name)
