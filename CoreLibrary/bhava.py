"""
bhava.py - Bhava (house) model and characteristics

This module provides:
- Bhava class representing a house with its properties and significations
- Methods to access bhava characteristics and meanings
- House strength calculations
- Cusp calculations for different house systems
"""

from typing import Dict, List, Optional, Union, Tuple
import json
import os
try:
    from .calculations_helper import CalculationsHelper
except ImportError:
    from calculations_helper import CalculationsHelper


class Bhava:
    """Class representing a bhava (house) with its characteristics and significations"""
    
    # Bhava significations according to traditional Jyotish
    BHAVA_SIGNIFICATIONS = {
        1: {
            'name': 'Lagna/Tanu Bhava',
            'sanskrit': 'Tanu Bhava',
            'primary_significations': [
                'Self', 'Personality', 'Physical body', 'Health', 'Appearance',
                'Character', 'Temperament', 'Identity', 'Birth', 'Beginning'
            ],
            'secondary_significations': [
                'Fame', 'Honor', 'Dignity', 'Head region', 'Overall vitality',
                'Complexion', 'Form', 'Disposition', 'Nature'
            ],
            'body_parts': ['Head', 'Brain', 'Face', 'Skull'],
            'element': 'Fire',
            'nature': 'Kendra',
            'strength': 'Very Strong',
            'karaka': 'Sun',
            'upachaya': False
        },
        2: {
            'name': 'Dhana Bhava',
            'sanskrit': 'Dhana Bhava',
            'primary_significations': [
                'Wealth', 'Money', 'Possessions', 'Family', 'Speech',
                'Food', 'Face', 'Right eye', 'Accumulated wealth'
            ],
            'secondary_significations': [
                'Tongue', 'Teeth', 'Nails', 'Precious metals', 'Gems',
                'Learning', 'Education', 'Family traditions', 'Values'
            ],
            'body_parts': ['Face', 'Right eye', 'Throat', 'Neck', 'Tongue'],
            'element': 'Earth',
            'nature': 'Maraka',
            'strength': 'Moderate',
            'karaka': 'Jupiter',
            'upachaya': False
        },
        3: {
            'name': 'Sahaja/Parakrama Bhava',
            'sanskrit': 'Sahaja Bhava',
            'primary_significations': [
                'Siblings', 'Courage', 'Efforts', 'Short journeys', 'Communication',
                'Skills', 'Talents', 'Arms', 'Right ear', 'Neighbors'
            ],
            'secondary_significations': [
                'Writing', 'Arts', 'Dance', 'Music', 'Heroism', 'Enterprise',
                'Signing documents', 'Agreements', 'Prowess'
            ],
            'body_parts': ['Arms', 'Hands', 'Shoulders', 'Right ear', 'Throat'],
            'element': 'Air',
            'nature': 'Upachaya',
            'strength': 'Weak initially, grows with time',
            'karaka': 'Mars',
            'upachaya': True
        },
        4: {
            'name': 'Sukha/Matru Bhava',
            'sanskrit': 'Sukha Bhava',
            'primary_significations': [
                'Mother', 'Home', 'Property', 'Land', 'Vehicles',
                'Happiness', 'Comforts', 'Education', 'Heart', 'Chest'
            ],
            'secondary_significations': [
                'Emotions', 'Mind', 'Gardens', 'Wells', 'Buildings',
                'Homeland', 'Academic degrees', 'Private life'
            ],
            'body_parts': ['Heart', 'Chest', 'Lungs', 'Ribs'],
            'element': 'Water',
            'nature': 'Kendra',
            'strength': 'Very Strong',
            'karaka': 'Moon',
            'upachaya': False
        },
        5: {
            'name': 'Putra/Vidya Bhava',
            'sanskrit': 'Putra Bhava',
            'primary_significations': [
                'Children', 'Creativity', 'Intelligence', 'Education', 'Romance',
                'Speculation', 'Investments', 'Purva punya', 'Stomach'
            ],
            'secondary_significations': [
                'Mantras', 'Spiritual practices', 'Authorship', 'Sports',
                'Entertainment', 'Love affairs', 'Pregnancy'
            ],
            'body_parts': ['Stomach', 'Upper abdomen', 'Liver', 'Gall bladder'],
            'element': 'Fire',
            'nature': 'Trikona',
            'strength': 'Very Strong',
            'karaka': 'Jupiter',
            'upachaya': False
        },
        6: {
            'name': 'Ari/Roga Bhava',
            'sanskrit': 'Ari Bhava',
            'primary_significations': [
                'Enemies', 'Diseases', 'Debts', 'Service', 'Employees',
                'Obstacles', 'Litigation', 'Competition', 'Lower abdomen'
            ],
            'secondary_significations': [
                'Immune system', 'Daily work', 'Routine', 'Pets',
                'Uncle/Aunt (maternal)', 'Step-mother', 'Theft'
            ],
            'body_parts': ['Lower abdomen', 'Kidneys', 'Small intestine'],
            'element': 'Earth',
            'nature': 'Upachaya',
            'strength': 'Weak initially, grows with time',
            'karaka': 'Mars/Saturn',
            'upachaya': True
        },
        7: {
            'name': 'Kalatra/Jaya Bhava',
            'sanskrit': 'Kalatra Bhava',
            'primary_significations': [
                'Spouse', 'Marriage', 'Business partnerships', 'Public life',
                'Travel', 'Trade', 'Death', 'Sexual organs'
            ],
            'secondary_significations': [
                'Passion', 'Desires', 'Public image', 'Cooperation',
                'Diplomacy', 'Balance', 'Open enemies'
            ],
            'body_parts': ['Sexual organs', 'Kidneys', 'Lower back'],
            'element': 'Air',
            'nature': 'Kendra/Maraka',
            'strength': 'Very Strong but can cause death',
            'karaka': 'Venus',
            'upachaya': False
        },
        8: {
            'name': 'Ayu/Mrityu Bhava',
            'sanskrit': 'Ayu Bhava',
            'primary_significations': [
                'Longevity', 'Death', 'Occult', 'Mysteries', 'Transformation',
                'Inheritance', 'Insurance', 'Hidden wealth', 'Excretory organs'
            ],
            'secondary_significations': [
                'Accidents', 'Surgery', 'Research', 'Investigation',
                'Spouse\'s wealth', 'Chronic diseases', 'Disgrace'
            ],
            'body_parts': ['Excretory organs', 'Reproductive system', 'Colon'],
            'element': 'Water',
            'nature': 'Dusthana',
            'strength': 'Very Weak',
            'karaka': 'Saturn',
            'upachaya': False
        },
        9: {
            'name': 'Bhagya/Dharma Bhava',
            'sanskrit': 'Bhagya Bhava',
            'primary_significations': [
                'Fortune', 'Religion', 'Philosophy', 'Higher learning',
                'Father', 'Teacher', 'Long journeys', 'Pilgrimage', 'Hips'
            ],
            'secondary_significations': [
                'Spirituality', 'Wisdom', 'Publishing', 'Foreign connections',
                'Grandchildren', 'Dreams', 'Intuition'
            ],
            'body_parts': ['Hips', 'Thighs', 'Buttocks'],
            'element': 'Fire',
            'nature': 'Trikona',
            'strength': 'Very Strong',
            'karaka': 'Jupiter/Sun',
            'upachaya': False
        },
        10: {
            'name': 'Karma/Rajya Bhava',
            'sanskrit': 'Karma Bhava',
            'primary_significations': [
                'Career', 'Profession', 'Status', 'Reputation', 'Government',
                'Authority', 'Father', 'Honor', 'Knees'
            ],
            'secondary_significations': [
                'Power', 'Command', 'Respect', 'Public recognition',
                'Activities', 'Deeds', 'Fame'
            ],
            'body_parts': ['Knees', 'Joints', 'Bones'],
            'element': 'Earth',
            'nature': 'Kendra',
            'strength': 'Very Strong',
            'karaka': 'Sun/Mercury/Jupiter/Saturn',
            'upachaya': False
        },
        11: {
            'name': 'Labha/Aya Bhava',
            'sanskrit': 'Labha Bhava',
            'primary_significations': [
                'Gains', 'Income', 'Friends', 'Elder siblings', 'Hopes',
                'Wishes', 'Left ear', 'Profits', 'Recovery from illness'
            ],
            'secondary_significations': [
                'Social circles', 'Organizations', 'Daughter-in-law',
                'Ankle', 'Large intestine'
            ],
            'body_parts': ['Calves', 'Left ear', 'Ankles', 'Shins'],
            'element': 'Air',
            'nature': 'Upachaya',
            'strength': 'Grows with time',
            'karaka': 'Jupiter',
            'upachaya': True
        },
        12: {
            'name': 'Vyaya/Moksha Bhava',
            'sanskrit': 'Vyaya Bhava',
            'primary_significations': [
                'Losses', 'Expenses', 'Foreign lands', 'Spirituality',
                'Liberation', 'Hospitals', 'Prisons', 'Sleep', 'Feet', 'Left eye'
            ],
            'secondary_significations': [
                'Charity', 'Donations', 'Meditation', 'Isolation',
                'Secret enemies', 'Bed comforts', 'Dreams'
            ],
            'body_parts': ['Feet', 'Toes', 'Left eye'],
            'element': 'Water',
            'nature': 'Dusthana',
            'strength': 'Weak',
            'karaka': 'Saturn',
            'upachaya': False
        }
    }
    
    # House nature classifications
    KENDRA_HOUSES = [1, 4, 7, 10]  # Angular houses
    TRIKONA_HOUSES = [1, 5, 9]     # Trine houses  
    UPACHAYA_HOUSES = [3, 6, 10, 11]  # Growing houses
    DUSTHANA_HOUSES = [6, 8, 12]   # Evil houses
    MARAKA_HOUSES = [2, 7]         # Death-dealing houses
    
    def __init__(self, number: int, cusp_degree: float = 0.0, 
                 rasi: Optional[str] = None, house_system: str = 'Placidus'):
        """
        Initialize a Bhava object
        
        Args:
            number: House number (1-12)
            cusp_degree: Degree of the house cusp (0-360)
            rasi: Rasi where the cusp falls
            house_system: House system used for calculations
        """
        if not 1 <= number <= 12:
            raise ValueError("Bhava number must be between 1 and 12")
            
        self.number = number
        self.cusp_degree = CalculationsHelper.normalize_degrees(cusp_degree)
        self.house_system = house_system
        
        # Calculate rasi if not provided
        if rasi is None and cusp_degree > 0:
            rasi_data = CalculationsHelper.degrees_to_rasi(self.cusp_degree)
            self.rasi = rasi_data['rasi']
            self.degrees_in_rasi = rasi_data['degrees']
        else:
            self.rasi = rasi
            self.degrees_in_rasi = 0.0
        
        # Load characteristics
        self.characteristics = self.BHAVA_SIGNIFICATIONS[number].copy()
        
    def get_name(self) -> str:
        """Get the name of the bhava"""
        return self.characteristics.get('name', f'House {self.number}')
    
    def get_sanskrit_name(self) -> str:
        """Get the Sanskrit name of the bhava"""
        return self.characteristics.get('sanskrit', f'Bhava {self.number}')
    
    def get_primary_significations(self) -> List[str]:
        """Get primary significations of this bhava"""
        return self.characteristics.get('primary_significations', [])
    
    def get_secondary_significations(self) -> List[str]:
        """Get secondary significations of this bhava"""
        return self.characteristics.get('secondary_significations', [])
    
    def get_all_significations(self) -> List[str]:
        """Get all significations (primary + secondary) of this bhava"""
        primary = self.get_primary_significations()
        secondary = self.get_secondary_significations()
        return primary + secondary
    
    def get_body_parts(self) -> List[str]:
        """Get body parts ruled by this bhava"""
        return self.characteristics.get('body_parts', [])
    
    def get_element(self) -> str:
        """Get the element associated with this bhava"""
        return self.characteristics.get('element', 'Unknown')
    
    def get_nature(self) -> str:
        """Get the nature classification of this bhava"""
        return self.characteristics.get('nature', 'Unknown')
    
    def get_karaka(self) -> str:
        """Get the natural karaka (significator) of this bhava"""
        return self.characteristics.get('karaka', 'None')
    
    def is_kendra(self) -> bool:
        """Check if this is a kendra (angular) house"""
        return self.number in self.KENDRA_HOUSES
    
    def is_trikona(self) -> bool:
        """Check if this is a trikona (trine) house"""
        return self.number in self.TRIKONA_HOUSES
    
    def is_upachaya(self) -> bool:
        """Check if this is an upachaya (growing) house"""
        return self.number in self.UPACHAYA_HOUSES
    
    def is_dusthana(self) -> bool:
        """Check if this is a dusthana (evil) house"""
        return self.number in self.DUSTHANA_HOUSES
    
    def is_maraka(self) -> bool:
        """Check if this is a maraka (death-dealing) house"""
        return self.number in self.MARAKA_HOUSES
    
    def get_opposite_bhava(self) -> int:
        """Get the number of the opposite bhava (7th from this bhava)"""
        return ((self.number + 5) % 12) + 1
    
    def get_trikona_bhavas(self) -> List[int]:
        """Get the trikona bhava numbers from this bhava"""
        # 1st, 5th, and 9th bhavas form a trikona
        trikona_numbers = [
            self.number,
            ((self.number + 3) % 12) + 1,  # 5th
            ((self.number + 7) % 12) + 1   # 9th
        ]
        return sorted(trikona_numbers)
    
    def get_kendra_bhavas(self) -> List[int]:
        """Get the kendra bhava numbers from this bhava"""
        # 1st, 4th, 7th, and 10th bhavas form kendras
        kendra_numbers = [
            self.number,
            ((self.number + 2) % 12) + 1,  # 4th
            ((self.number + 5) % 12) + 1,  # 7th
            ((self.number + 8) % 12) + 1   # 10th
        ]
        return sorted(kendra_numbers)
    
    def get_strength_category(self) -> str:
        """
        Get the strength category of this bhava
        
        Returns:
            'Very Strong', 'Strong', 'Moderate', 'Weak', or 'Very Weak'
        """
        if self.is_kendra() and self.is_trikona():  # 1st house
            return 'Very Strong'
        elif self.is_kendra() or self.is_trikona():
            return 'Very Strong'
        elif self.is_upachaya():
            return self.characteristics.get('strength', 'Grows with time')
        elif self.is_dusthana():
            return 'Weak'
        else:
            return 'Moderate'
    
    def calculate_bhava_madhya(self, next_cusp_degree: float) -> float:
        """
        Calculate bhava madhya (middle of the house)
        
        Args:
            next_cusp_degree: Degree of the next house cusp
            
        Returns:
            Bhava madhya degree
        """
        # Calculate the middle point between this cusp and next cusp
        next_cusp = CalculationsHelper.normalize_degrees(next_cusp_degree)
        
        # Handle crossing 0 degrees
        if next_cusp < self.cusp_degree:
            next_cusp += 360
            
        madhya = (self.cusp_degree + next_cusp) / 2
        
        return CalculationsHelper.normalize_degrees(madhya)
    
    def calculate_bhava_sandhi(self, next_cusp_degree: float) -> Tuple[float, float]:
        """
        Calculate bhava sandhi (junction points) - areas of weakness
        
        Args:
            next_cusp_degree: Degree of the next house cusp
            
        Returns:
            Tuple of (start_sandhi, end_sandhi) degrees
        """
        next_cusp = CalculationsHelper.normalize_degrees(next_cusp_degree)
        
        # Sandhi is typically 2 degrees before and after cusp
        start_sandhi = CalculationsHelper.normalize_degrees(self.cusp_degree - 2)
        end_sandhi = CalculationsHelper.normalize_degrees(self.cusp_degree + 2)
        
        return start_sandhi, end_sandhi
    
    def is_in_bhava_sandhi(self, degree: float, next_cusp_degree: float) -> bool:
        """
        Check if a degree falls in bhava sandhi (junction)
        
        Args:
            degree: Degree to check
            next_cusp_degree: Degree of next house cusp
            
        Returns:
            True if in sandhi, False otherwise
        """
        start_sandhi, end_sandhi = self.calculate_bhava_sandhi(next_cusp_degree)
        
        degree = CalculationsHelper.normalize_degrees(degree)
        
        # Handle crossing 0 degrees
        if end_sandhi < start_sandhi:
            return degree >= start_sandhi or degree <= end_sandhi
        else:
            return start_sandhi <= degree <= end_sandhi
    
    def get_bhava_span(self, next_cusp_degree: float) -> float:
        """
        Calculate the span of this bhava in degrees
        
        Args:
            next_cusp_degree: Degree of the next house cusp
            
        Returns:
            Span in degrees
        """
        next_cusp = CalculationsHelper.normalize_degrees(next_cusp_degree)
        
        if next_cusp < self.cusp_degree:
            next_cusp += 360
            
        return next_cusp - self.cusp_degree
    
    def contains_degree(self, degree: float, next_cusp_degree: float) -> bool:
        """
        Check if a degree falls within this bhava
        
        Args:
            degree: Degree to check
            next_cusp_degree: Degree of next house cusp
            
        Returns:
            True if degree is in this bhava, False otherwise
        """
        degree = CalculationsHelper.normalize_degrees(degree)
        next_cusp = CalculationsHelper.normalize_degrees(next_cusp_degree)
        
        # Handle crossing 0 degrees
        if next_cusp < self.cusp_degree:
            return degree >= self.cusp_degree or degree < next_cusp
        else:
            return self.cusp_degree <= degree < next_cusp
    
    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List]]:
        """
        Convert bhava object to dictionary representation
        
        Returns:
            Dictionary with bhava data
        """
        return {
            'number': self.number,
            'name': self.get_name(),
            'sanskrit_name': self.get_sanskrit_name(),
            'cusp_degree': self.cusp_degree,
            'rasi': self.rasi,
            'degrees_in_rasi': self.degrees_in_rasi,
            'element': self.get_element(),
            'nature': self.get_nature(),
            'karaka': self.get_karaka(),
            'is_kendra': self.is_kendra(),
            'is_trikona': self.is_trikona(),
            'is_upachaya': self.is_upachaya(),
            'is_dusthana': self.is_dusthana(),
            'is_maraka': self.is_maraka(),
            'strength_category': self.get_strength_category(),
            'primary_significations': self.get_primary_significations(),
            'secondary_significations': self.get_secondary_significations(),
            'body_parts': self.get_body_parts(),
            'opposite_bhava': self.get_opposite_bhava(),
            'trikona_bhavas': self.get_trikona_bhavas(),
            'kendra_bhavas': self.get_kendra_bhavas()
        }
    
    def __str__(self) -> str:
        """String representation of the bhava"""
        return f"Bhava {self.number} ({self.get_name()}) at {self.rasi} {self.degrees_in_rasi:.2f}°"
    
    def __repr__(self) -> str:
        """Detailed representation of the bhava"""
        return (f"Bhava(number={self.number}, cusp='{self.rasi} {self.degrees_in_rasi:.2f}°', "
                f"raw_longitude={self.cusp_degree:.2f}°, nature='{self.get_nature()}')")
    
    @classmethod
    def get_all_bhavas(cls, ascendant_degree: float, house_system: str = 'Equal') -> List['Bhava']:
        """
        Create all 12 bhava objects based on ascendant
        
        Args:
            ascendant_degree: Ascendant degree
            house_system: House system to use
            
        Returns:
            List of all 12 Bhava objects
        """
        bhavas = []
        
        for i in range(1, 13):
            if house_system == 'Equal':
                # Each house is 30 degrees
                cusp_degree = CalculationsHelper.normalize_degrees(
                    ascendant_degree + (i - 1) * 30
                )
            else:
                # For now, default to equal house
                # TODO: Implement Placidus, Campanus, etc.
                cusp_degree = CalculationsHelper.normalize_degrees(
                    ascendant_degree + (i - 1) * 30
                )
                
            bhava = cls(i, cusp_degree, house_system=house_system)
            bhavas.append(bhava)
            
        return bhavas
    
    @classmethod
    def load_significations_from_json(cls, filename: str = 'bhava_significations.json') -> Dict:
        """
        Load bhava significations from JSON file
        
        Args:
            filename: Name of JSON file to load
            
        Returns:
            Dictionary with bhava significations
        """
        try:
            data = CalculationsHelper.load_json_data(filename)
            if data and 'placeholder' not in data:
                return data
        except Exception as e:
            print(f"Could not load {filename}: {e}")
        
        # Return default significations if file not found or empty
        return cls.BHAVA_SIGNIFICATIONS
