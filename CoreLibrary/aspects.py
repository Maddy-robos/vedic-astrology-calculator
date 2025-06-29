"""
aspects.py - Planetary aspects (Drishti) calculations

This module provides:
- Traditional planetary aspects calculations
- Graha drishti (planetary aspects) 
- Rasi drishti (sign-based aspects)
- Aspect strength calculations
- Mutual aspect analysis
"""

from typing import Dict, List, Optional, Union, Tuple
import math
try:
    from .calculations_helper import CalculationsHelper
    from .graha import Graha
    from .rasi import Rasi
except ImportError:
    from calculations_helper import CalculationsHelper
    from graha import Graha
    from rasi import Rasi


class Aspects:
    """Class for calculating planetary and sign-based aspects"""
    
    # Special aspects (Drishti) for each graha in degrees
    GRAHA_SPECIAL_ASPECTS = {
        'Sun': [180],               # 7th aspect only
        'Moon': [180],              # 7th aspect only  
        'Mars': [90, 180, 210],     # 4th, 7th, 8th aspects (NO 5th aspect)
        'Mercury': [180],           # 7th aspect only
        'Jupiter': [120, 180, 240], # 5th, 7th, 9th aspects (NO 6th aspect)
        'Venus': [180],             # 7th aspect only
        'Saturn': [60, 180, 270],   # 3rd, 7th, 10th aspects (NO 4th aspect)
        'Rahu': [120, 240],               # 5th, 9th aspects only (+ 2nd/12th based on rasi)
        'Ketu': [120, 240]                # 5th, 9th aspects only (+ 2nd/12th based on rasi)
    }
    
    # Aspect orbs in degrees (how close the aspect needs to be)
    ASPECT_ORBS = {
        'exact': 1.0,      # Within 1 degree = exact aspect
        'close': 3.0,      # Within 3 degrees = close aspect  
        'wide': 5.0,       # Within 5 degrees = wide aspect
        'very_wide': 8.0   # Within 8 degrees = very wide aspect
    }
    
    # Aspect strength based on orb
    ASPECT_STRENGTH = {
        'exact': 1.0,      # 100% strength
        'close': 0.75,     # 75% strength
        'wide': 0.5,       # 50% strength
        'very_wide': 0.25  # 25% strength
    }
    
    def __init__(self, grahas: Dict[str, Graha]):
        """
        Initialize Aspects calculator
        
        Args:
            grahas: Dictionary of graha names to Graha objects
        """
        self.grahas = grahas
        
    def calculate_angular_distance(self, graha1: str, graha2: str) -> float:
        """
        Calculate angular distance between two grahas
        
        Args:
            graha1: Name of first graha
            graha2: Name of second graha
            
        Returns:
            Angular distance in degrees (0-180)
        """
        if graha1 not in self.grahas or graha2 not in self.grahas:
            raise ValueError(f"Graha {graha1} or {graha2} not found")
            
        lon1 = self.grahas[graha1].longitude
        lon2 = self.grahas[graha2].longitude
        
        return CalculationsHelper.get_angular_distance(lon1, lon2)
    
    def get_aspect_orb_category(self, angular_distance: float, target_aspect: float) -> Optional[str]:
        """
        Determine the orb category for an aspect
        
        Args:
            angular_distance: Actual angular distance
            target_aspect: Target aspect angle (e.g., 180, 120, etc.)
            
        Returns:
            Orb category or None if no aspect
        """
        orb = abs(angular_distance - target_aspect)
        
        # Handle aspects crossing 0/360 degrees
        if orb > 180:
            orb = 360 - orb
            
        if orb <= self.ASPECT_ORBS['exact']:
            return 'exact'
        elif orb <= self.ASPECT_ORBS['close']:
            return 'close'
        elif orb <= self.ASPECT_ORBS['wide']:
            return 'wide'
        elif orb <= self.ASPECT_ORBS['very_wide']:
            return 'very_wide'
        else:
            return None
    
    def get_retrograde_adjusted_aspects(self, graha_name: str) -> List[int]:
        """
        Get aspect angles adjusted for retrograde motion
        
        Args:
            graha_name: Name of graha
            
        Returns:
            List of aspect angles adjusted for retrograde motion
        """
        if graha_name not in self.grahas:
            return self.GRAHA_SPECIAL_ASPECTS.get(graha_name, [180])
            
        graha = self.grahas[graha_name]
        base_aspects = self.GRAHA_SPECIAL_ASPECTS.get(graha_name, [180])
        
        # Only Mars and Saturn have retrograde aspect adjustments
        # Sun, Moon, Mercury, Venus, Jupiter, Rahu, Ketu aspects don't change with retrograde
        if graha_name not in ['Mars', 'Saturn'] or not graha.is_retrograde:
            return base_aspects
            
        adjusted_aspects = []
        for aspect in base_aspects:
            if aspect == 180:  # 7th aspect never changes
                adjusted_aspects.append(aspect)
            elif graha_name == 'Mars':
                # Mars retrograde: 4th->10th (90->270), 8th->6th (210->150)
                if aspect == 90:    # 4th becomes 10th
                    adjusted_aspects.append(270)
                elif aspect == 210: # 8th becomes 6th
                    adjusted_aspects.append(150)
            elif graha_name == 'Saturn':
                # Saturn retrograde: 3rd->11th (60->300), 10th->4th (270->90)
                if aspect == 60:    # 3rd becomes 11th
                    adjusted_aspects.append(300)
                elif aspect == 270: # 10th becomes 4th
                    adjusted_aspects.append(90)
                    
        return adjusted_aspects
    
    def calculate_graha_aspects(self, aspecting_graha: str, aspected_graha: str) -> Dict[str, Union[bool, float, str, List]]:
        """
        Calculate aspects between two grahas
        
        Args:
            aspecting_graha: Name of aspecting graha
            aspected_graha: Name of aspected graha
            
        Returns:
            Dictionary with aspect information
        """
        if aspecting_graha not in self.grahas or aspected_graha not in self.grahas:
            raise ValueError(f"Graha not found")
            
        if aspecting_graha == aspected_graha:
            return {
                'is_aspecting': False,
                'aspect_type': 'Self',
                'angular_distance': 0.0,
                'orb_category': None,
                'aspect_strength': 0.0,
                'aspect_angles': []
            }
        
        angular_distance = self.calculate_angular_distance(aspecting_graha, aspected_graha)
        special_aspects = self.get_retrograde_adjusted_aspects(aspecting_graha)
        
        # Check each special aspect
        found_aspects = []
        strongest_aspect = None
        strongest_strength = 0.0
        
        for aspect_angle in special_aspects:
            orb_category = self.get_aspect_orb_category(angular_distance, aspect_angle)
            
            if orb_category:
                strength = self.ASPECT_STRENGTH[orb_category]
                aspect_info = {
                    'angle': aspect_angle,
                    'orb_category': orb_category,
                    'strength': strength,
                    'exact_orb': abs(angular_distance - aspect_angle)
                }
                found_aspects.append(aspect_info)
                
                # Track strongest aspect
                if strength > strongest_strength:
                    strongest_strength = strength
                    strongest_aspect = aspect_info
        
        # Return result
        if found_aspects:
            return {
                'is_aspecting': True,
                'aspect_type': 'Graha Drishti',
                'angular_distance': angular_distance,
                'strongest_aspect': strongest_aspect,
                'all_aspects': found_aspects,
                'total_strength': sum(a['strength'] for a in found_aspects),
                'primary_angle': strongest_aspect['angle'] if strongest_aspect else None,
                'orb_category': strongest_aspect['orb_category'] if strongest_aspect else None
            }
        else:
            return {
                'is_aspecting': False,
                'aspect_type': 'No Aspect',
                'angular_distance': angular_distance,
                'orb_category': None,
                'aspect_strength': 0.0,
                'aspect_angles': []
            }
    
    def get_all_graha_aspects(self) -> Dict[str, Dict[str, Dict]]:
        """
        Calculate all graha-to-graha aspects
        
        Returns:
            Nested dictionary with all aspect relationships
        """
        all_aspects = {}
        
        for aspecting_graha in self.grahas:
            all_aspects[aspecting_graha] = {}
            
            for aspected_graha in self.grahas:
                aspect_info = self.calculate_graha_aspects(aspecting_graha, aspected_graha)
                all_aspects[aspecting_graha][aspected_graha] = aspect_info
                
        return all_aspects
    
    def get_aspects_to_graha(self, target_graha: str) -> Dict[str, Dict]:
        """
        Get all aspects received by a target graha
        
        Args:
            target_graha: Name of target graha
            
        Returns:
            Dictionary of aspecting grahas and their aspect info
        """
        if target_graha not in self.grahas:
            raise ValueError(f"Graha {target_graha} not found")
            
        aspects_received = {}
        
        for aspecting_graha in self.grahas:
            if aspecting_graha != target_graha:
                aspect_info = self.calculate_graha_aspects(aspecting_graha, target_graha)
                if aspect_info['is_aspecting']:
                    aspects_received[aspecting_graha] = aspect_info
                    
        return aspects_received
    
    def get_aspects_from_graha(self, source_graha: str) -> Dict[str, Dict]:
        """
        Get all aspects cast by a source graha
        
        Args:
            source_graha: Name of source graha
            
        Returns:
            Dictionary of aspected grahas and their aspect info
        """
        if source_graha not in self.grahas:
            raise ValueError(f"Graha {source_graha} not found")
            
        aspects_cast = {}
        
        for aspected_graha in self.grahas:
            if aspected_graha != source_graha:
                aspect_info = self.calculate_graha_aspects(source_graha, aspected_graha)
                if aspect_info['is_aspecting']:
                    aspects_cast[aspected_graha] = aspect_info
                    
        return aspects_cast
    
    def calculate_mutual_aspects(self) -> List[Dict]:
        """
        Find mutual aspects between grahas
        
        Returns:
            List of mutual aspect relationships
        """
        mutual_aspects = []
        processed_pairs = set()
        
        for graha1 in self.grahas:
            for graha2 in self.grahas:
                if graha1 != graha2:
                    pair = tuple(sorted([graha1, graha2]))
                    if pair not in processed_pairs:
                        processed_pairs.add(pair)
                        
                        # Check both directions
                        aspect1_2 = self.calculate_graha_aspects(graha1, graha2)
                        aspect2_1 = self.calculate_graha_aspects(graha2, graha1)
                        
                        if aspect1_2['is_aspecting'] and aspect2_1['is_aspecting']:
                            mutual_aspects.append({
                                'graha1': graha1,
                                'graha2': graha2,
                                'aspect1_to_2': aspect1_2,
                                'aspect2_to_1': aspect2_1,
                                'combined_strength': aspect1_2.get('total_strength', 0) + 
                                                   aspect2_1.get('total_strength', 0),
                                'angular_distance': aspect1_2['angular_distance']
                            })
                            
        return mutual_aspects
    
    def calculate_conjunction_aspects(self, orb: float = 8.0) -> List[Dict]:
        """
        Find conjunctions between grahas
        
        Args:
            orb: Maximum orb for conjunction in degrees
            
        Returns:
            List of conjunction relationships
        """
        conjunctions = []
        processed_pairs = set()
        
        for graha1 in self.grahas:
            for graha2 in self.grahas:
                if graha1 != graha2:
                    pair = tuple(sorted([graha1, graha2]))
                    if pair not in processed_pairs:
                        processed_pairs.add(pair)
                        
                        angular_distance = self.calculate_angular_distance(graha1, graha2)
                        
                        if angular_distance <= orb:
                            # Determine conjunction strength
                            if angular_distance <= 1.0:
                                strength = 'Very Close'
                            elif angular_distance <= 3.0:
                                strength = 'Close'
                            elif angular_distance <= 5.0:
                                strength = 'Moderate'
                            else:
                                strength = 'Wide'
                                
                            conjunctions.append({
                                'graha1': graha1,
                                'graha2': graha2,
                                'angular_distance': angular_distance,
                                'strength': strength,
                                'orb': orb,
                                'type': 'Conjunction'
                            })
                            
        return conjunctions
    
    def calculate_graha_to_point_aspect(self, graha_name: str, target_longitude: float) -> Dict:
        """
        Calculate aspect from graha to a specific point (like ascendant, MC, etc.)
        
        Args:
            graha_name: Name of graha
            target_longitude: Longitude of target point
            
        Returns:
            Dictionary with aspect information
        """
        if graha_name not in self.grahas:
            raise ValueError(f"Graha {graha_name} not found")
            
        graha_longitude = self.grahas[graha_name].longitude
        angular_distance = CalculationsHelper.get_angular_distance(graha_longitude, target_longitude)
        
        special_aspects = self.get_retrograde_adjusted_aspects(graha_name)
        
        # Check each special aspect
        found_aspects = []
        for aspect_angle in special_aspects:
            orb_category = self.get_aspect_orb_category(angular_distance, aspect_angle)
            
            if orb_category:
                strength = self.ASPECT_STRENGTH[orb_category]
                found_aspects.append({
                    'angle': aspect_angle,
                    'orb_category': orb_category,
                    'strength': strength,
                    'exact_orb': abs(angular_distance - aspect_angle)
                })
        
        if found_aspects:
            strongest = max(found_aspects, key=lambda x: x['strength'])
            return {
                'is_aspecting': True,
                'graha': graha_name,
                'target_longitude': target_longitude,
                'angular_distance': angular_distance,
                'strongest_aspect': strongest,
                'all_aspects': found_aspects,
                'total_strength': sum(a['strength'] for a in found_aspects)
            }
        else:
            return {
                'is_aspecting': False,
                'graha': graha_name,
                'target_longitude': target_longitude,
                'angular_distance': angular_distance,
                'aspect_strength': 0.0
            }
    
    def get_aspects_to_bhava(self, bhava_number: int, ascendant_longitude: float) -> Dict[str, Dict]:
        """
        Get all graha aspects to a specific bhava
        
        Args:
            bhava_number: Bhava number (1-12)
            ascendant_longitude: Ascendant longitude in degrees
            
        Returns:
            Dictionary of aspecting grahas and their aspect info
        """
        if not 1 <= bhava_number <= 12:
            raise ValueError("Bhava number must be between 1 and 12")
            
        # Calculate bhava cusp (for equal house system)
        bhava_cusp = CalculationsHelper.normalize_degrees(
            ascendant_longitude + (bhava_number - 1) * 30
        )
        
        aspects_to_bhava = {}
        
        for graha_name in self.grahas:
            aspect_info = self.calculate_graha_to_point_aspect(graha_name, bhava_cusp)
            if aspect_info['is_aspecting']:
                aspects_to_bhava[graha_name] = aspect_info
                
        return aspects_to_bhava
    
    def analyze_aspect_patterns(self) -> Dict[str, List]:
        """
        Analyze various aspect patterns in the chart
        
        Returns:
            Dictionary with different aspect patterns
        """
        patterns = {
            'conjunctions': self.calculate_conjunction_aspects(),
            'mutual_aspects': self.calculate_mutual_aspects(),
            'strong_aspects': [],
            'weak_aspects': [],
            'exact_aspects': []
        }
        
        # Analyze all aspects for patterns
        all_aspects = self.get_all_graha_aspects()
        
        for aspecting_graha in all_aspects:
            for aspected_graha, aspect_info in all_aspects[aspecting_graha].items():
                if aspect_info['is_aspecting']:
                    total_strength = aspect_info.get('total_strength', 0)
                    strongest_aspect = aspect_info.get('strongest_aspect', {})
                    
                    aspect_entry = {
                        'aspecting_graha': aspecting_graha,
                        'aspected_graha': aspected_graha,
                        'aspect_info': aspect_info
                    }
                    
                    # Categorize by strength
                    if total_strength >= 0.75:
                        patterns['strong_aspects'].append(aspect_entry)
                    elif total_strength <= 0.25:
                        patterns['weak_aspects'].append(aspect_entry)
                        
                    # Check for exact aspects
                    if strongest_aspect.get('orb_category') == 'exact':
                        patterns['exact_aspects'].append(aspect_entry)
        
        return patterns
    
    def get_aspect_summary(self) -> Dict[str, Union[int, float, Dict]]:
        """
        Get summary statistics of aspects in the chart
        
        Returns:
            Dictionary with aspect summary
        """
        all_aspects = self.get_all_graha_aspects()
        patterns = self.analyze_aspect_patterns()
        
        total_aspects = 0
        total_strength = 0.0
        aspect_types = {}
        
        for aspecting_graha in all_aspects:
            for aspected_graha, aspect_info in all_aspects[aspecting_graha].items():
                if aspect_info['is_aspecting']:
                    total_aspects += 1
                    total_strength += aspect_info.get('total_strength', 0)
                    
                    strongest = aspect_info.get('strongest_aspect', {})
                    angle = strongest.get('angle', 0)
                    aspect_types[angle] = aspect_types.get(angle, 0) + 1
        
        return {
            'total_aspects': total_aspects,
            'average_strength': total_strength / max(total_aspects, 1),
            'total_conjunctions': len(patterns['conjunctions']),
            'total_mutual_aspects': len(patterns['mutual_aspects']),
            'strong_aspects_count': len(patterns['strong_aspects']),
            'exact_aspects_count': len(patterns['exact_aspects']),
            'aspect_type_distribution': aspect_types,
            'most_aspected_graha': self._get_most_aspected_graha(),
            'most_aspecting_graha': self._get_most_aspecting_graha()
        }
    
    def _get_most_aspected_graha(self) -> str:
        """Get the graha that receives the most aspects"""
        aspect_counts = {}
        
        for target_graha in self.grahas:
            aspects_received = self.get_aspects_to_graha(target_graha)
            aspect_counts[target_graha] = len(aspects_received)
            
        return max(aspect_counts, key=aspect_counts.get) if aspect_counts else None
    
    def _get_most_aspecting_graha(self) -> str:
        """Get the graha that casts the most aspects"""
        aspect_counts = {}
        
        for source_graha in self.grahas:
            aspects_cast = self.get_aspects_from_graha(source_graha)
            aspect_counts[source_graha] = len(aspects_cast)
            
        return max(aspect_counts, key=aspect_counts.get) if aspect_counts else None
    
    def to_dict(self) -> Dict:
        """
        Convert aspects analysis to dictionary representation
        
        Returns:
            Dictionary with complete aspect analysis
        """
        return {
            'all_aspects': self.get_all_graha_aspects(),
            'patterns': self.analyze_aspect_patterns(),
            'summary': self.get_aspect_summary(),
            'graha_count': len(self.grahas)
        }
