"""
Chara Karaka (Variable Significator) Calculations

This module implements the calculation of Chara Karakas - variable significators
that change based on planetary positions at birth. There are 8 Chara Karakas:
- AK (Atma Karaka) - Soul significator
- AmK (Amatya Karaka) - Career/profession significator  
- BK (Bhratri Karaka) - Sibling significator
- MK (Matri Karaka) - Mother significator
- PiK (Pitru Karaka) - Father significator
- PK (Putra Karaka) - Children significator
- GK (Gnati Karaka) - Enemies/obstacles significator
- DK (Dara Karaka) - Spouse significator

Two calculation methods are supported:
1. Standard Method - Based on degrees in sign (0-30°)
2. Advanced Method - Based on total degrees traveled in current sign
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CharaKarakaResult:
    """Result of Chara Karaka calculation"""
    planet: str
    karaka: str
    degrees: float
    method: str  # 'standard' or 'advanced'


class CharaKaraka:
    """Calculate Chara Karakas using standard and advanced methods"""
    
    # Order of Chara Karakas from highest to lowest degrees
    KARAKA_ORDER = ['AK', 'AmK', 'BK', 'MK', 'PiK', 'PK', 'GK', 'DK']
    
    # Full names of Karakas
    KARAKA_NAMES = {
        'AK': 'Atma Karaka',
        'AmK': 'Amatya Karaka',
        'BK': 'Bhratri Karaka',
        'MK': 'Matri Karaka',
        'PiK': 'Pitru Karaka',
        'PK': 'Putra Karaka',
        'GK': 'Gnati Karaka',
        'DK': 'Dara Karaka'
    }
    
    def __init__(self, graha_positions: Dict):
        """
        Initialize with graha positions
        
        Args:
            graha_positions: Dictionary with planet names as keys and position data as values
                            Each position should have 'longitude' and 'degrees_in_rasi'
        """
        self.graha_positions = graha_positions
        
    def calculate_standard(self) -> List[CharaKarakaResult]:
        """
        Calculate Chara Karakas using standard method (degrees in sign)
        
        Rules:
        - Use degrees in sign (0-30°) for all planets
        - For Rahu: use (30 - degrees)
        - Exclude Ketu completely
        - Assign karakas in descending order of degrees
        """
        degrees_dict = {}
        
        for graha_name, graha_data in self.graha_positions.items():
            # Skip Ketu
            if graha_name == 'Ketu':
                continue
                
            # Get degrees in rasi (sign)
            degrees_in_rasi = graha_data.get('degrees_in_rasi', 0)
            
            # Special handling for Rahu
            if graha_name == 'Rahu':
                degrees_dict[graha_name] = 30 - degrees_in_rasi
            else:
                degrees_dict[graha_name] = degrees_in_rasi
                
        # Sort by degrees (descending)
        sorted_grahas = sorted(degrees_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Assign karakas
        results = []
        for i, (graha_name, degrees) in enumerate(sorted_grahas):
            if i < len(self.KARAKA_ORDER):
                results.append(CharaKarakaResult(
                    planet=graha_name,
                    karaka=self.KARAKA_ORDER[i],
                    degrees=degrees,
                    method='standard'
                ))
                
        return results
        
    def calculate_advanced(self, retrograde_data: Optional[Dict] = None) -> List[CharaKarakaResult]:
        """
        Calculate Chara Karakas using advanced method (total degrees traveled)
        
        Rules:
        - Sun, Moon, Rahu: Use standard degrees (no retrograde tracking)
        - Other planets: Calculate total degrees traveled in current sign
        - Total travel = entry to max forward + (max forward - current)
        
        Args:
            retrograde_data: Optional dictionary containing retrograde motion data
                           Format: {planet: {'max_forward': degrees, 'entry_point': degrees}}
        """
        degrees_dict = {}
        
        for graha_name, graha_data in self.graha_positions.items():
            # Skip Ketu
            if graha_name == 'Ketu':
                continue
                
            degrees_in_rasi = graha_data.get('degrees_in_rasi', 0)
            
            # Special handling for Rahu
            if graha_name == 'Rahu':
                degrees_dict[graha_name] = 30 - degrees_in_rasi
            else:
                # For other planets, check if we have retrograde data
                if retrograde_data and graha_name in retrograde_data:
                    retro_info = retrograde_data[graha_name]
                    max_forward = retro_info.get('max_forward', degrees_in_rasi)
                    entry_point = retro_info.get('entry_point', 0)
                    
                    # Calculate total travel
                    if max_forward > degrees_in_rasi:  # Planet has retrograded
                        total_travel = (max_forward - entry_point) + (max_forward - degrees_in_rasi)
                    else:  # No retrograde or moving forward
                        total_travel = degrees_in_rasi - entry_point
                        
                    degrees_dict[graha_name] = total_travel
                else:
                    # No retrograde data available, use standard degrees
                    degrees_dict[graha_name] = degrees_in_rasi
                    
        # Sort by degrees (descending)
        sorted_grahas = sorted(degrees_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Assign karakas
        results = []
        for i, (graha_name, degrees) in enumerate(sorted_grahas):
            if i < len(self.KARAKA_ORDER):
                results.append(CharaKarakaResult(
                    planet=graha_name,
                    karaka=self.KARAKA_ORDER[i],
                    degrees=degrees,
                    method='advanced'
                ))
                
        return results
        
    def get_karaka_significations(self, karaka: str) -> Dict[str, List[str]]:
        """
        Get the significations of a specific Chara Karaka
        
        Args:
            karaka: Karaka abbreviation (e.g., 'AK', 'AmK')
            
        Returns:
            Dictionary with significations
        """
        significations = {
            'AK': {
                'name': 'Atma Karaka',
                'signifies': ['Soul', 'Self', 'Desires', 'Life purpose', 'Spiritual path'],
                'houses': ['1st house matters', 'Overall life direction']
            },
            'AmK': {
                'name': 'Amatya Karaka',
                'signifies': ['Career', 'Profession', 'Advisors', 'Ministers', 'Authority'],
                'houses': ['10th house matters', '2nd house matters']
            },
            'BK': {
                'name': 'Bhratri Karaka',
                'signifies': ['Siblings', 'Courage', 'Short journeys', 'Communication'],
                'houses': ['3rd house matters', '11th house matters']
            },
            'MK': {
                'name': 'Matri Karaka',
                'signifies': ['Mother', 'Emotions', 'Home', 'Vehicles', 'Comfort'],
                'houses': ['4th house matters', 'Moon significations']
            },
            'PiK': {
                'name': 'Pitru Karaka',
                'signifies': ['Father', 'Ancestors', 'Dharma', 'Higher wisdom', 'Fortune'],
                'houses': ['9th house matters', 'Sun significations']
            },
            'PK': {
                'name': 'Putra Karaka',
                'signifies': ['Children', 'Creativity', 'Intelligence', 'Education', 'Romance'],
                'houses': ['5th house matters']
            },
            'GK': {
                'name': 'Gnati Karaka',
                'signifies': ['Enemies', 'Obstacles', 'Diseases', 'Service', 'Competition'],
                'houses': ['6th house matters']
            },
            'DK': {
                'name': 'Dara Karaka',
                'signifies': ['Spouse', 'Marriage', 'Business partners', 'Relationships'],
                'houses': ['7th house matters']
            }
        }
        
        return significations.get(karaka, {})
        
    def get_both_calculations(self, retrograde_data: Optional[Dict] = None) -> Dict:
        """
        Get both standard and advanced Chara Karaka calculations
        
        Returns:
            Dictionary with both calculation results
        """
        return {
            'standard': self.calculate_standard(),
            'advanced': self.calculate_advanced(retrograde_data)
        }