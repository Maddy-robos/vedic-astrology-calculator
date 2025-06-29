"""
bhava_analysis.py - Comprehensive bhava (house) analysis

This module provides:
- Graha placement analysis in bhavas
- Bhava strength calculations
- Lord analysis and placement
- Bhava yogas and combinations
- Influence and aspect analysis
"""

from typing import Dict, List, Optional, Union, Tuple
try:
    from .calculations_helper import CalculationsHelper
    from .graha import Graha
    from .bhava import Bhava
    from .rasi import Rasi
    from .aspects import Aspects
except ImportError:
    from calculations_helper import CalculationsHelper
    from graha import Graha
    from bhava import Bhava
    from rasi import Rasi
    from aspects import Aspects


class BhavaAnalysis:
    """Class for comprehensive bhava analysis"""
    
    def __init__(self, grahas: Dict[str, Graha], ascendant_longitude: float, 
                 house_system: str = 'Equal'):
        """
        Initialize BhavaAnalysis
        
        Args:
            grahas: Dictionary of graha names to Graha objects
            ascendant_longitude: Ascendant longitude in degrees
            house_system: House system to use for calculations
        """
        self.grahas = grahas
        self.ascendant_longitude = ascendant_longitude
        self.house_system = house_system
        
        # Create all bhavas
        self.bhavas = Bhava.get_all_bhavas(ascendant_longitude, house_system)
        
        # Create aspects calculator
        self.aspects = Aspects(grahas)
        
        # Calculate graha placements in bhavas
        self.graha_placements = self._calculate_graha_placements()
        
        # Calculate bhava lords
        self.bhava_lords = self._calculate_bhava_lords()
    
    def _calculate_graha_placements(self) -> Dict[int, List[str]]:
        """Calculate which grahas are placed in each bhava"""
        placements = {i: [] for i in range(1, 13)}
        
        for graha_name, graha in self.grahas.items():
            bhava_number = self.get_bhava_of_graha(graha_name)
            if bhava_number:
                placements[bhava_number].append(graha_name)
                
        return placements
    
    def _calculate_bhava_lords(self) -> Dict[int, str]:
        """Calculate the lord of each bhava based on rasi in bhava"""
        lords = {}
        
        for i, bhava in enumerate(self.bhavas, 1):
            if bhava.rasi:
                rasi_obj = Rasi(bhava.rasi)
                ruling_planet = rasi_obj.get_ruling_planet()
                lords[i] = ruling_planet
                
        return lords
    
    def get_bhava_of_graha(self, graha_name: str) -> Optional[int]:
        """
        Determine which bhava a graha is placed in
        
        Args:
            graha_name: Name of graha
            
        Returns:
            Bhava number (1-12) or None if not found
        """
        if graha_name not in self.grahas:
            return None
            
        graha_longitude = self.grahas[graha_name].longitude
        
        for i, bhava in enumerate(self.bhavas, 1):
            # Get next bhava cusp for span calculation
            next_bhava = self.bhavas[i % 12]  # Wrap around to 1st bhava
            
            if bhava.contains_degree(graha_longitude, next_bhava.cusp_degree):
                return i
                
        return None
    
    def get_grahas_in_bhava(self, bhava_number: int) -> List[str]:
        """
        Get all grahas placed in a specific bhava
        
        Args:
            bhava_number: Bhava number (1-12)
            
        Returns:
            List of graha names in the bhava
        """
        if not 1 <= bhava_number <= 12:
            raise ValueError("Bhava number must be between 1 and 12")
            
        return self.graha_placements.get(bhava_number, [])
    
    def get_bhava_lord(self, bhava_number: int) -> Optional[str]:
        """
        Get the lord of a specific bhava
        
        Args:
            bhava_number: Bhava number (1-12)
            
        Returns:
            Name of ruling graha or None
        """
        if not 1 <= bhava_number <= 12:
            raise ValueError("Bhava number must be between 1 and 12")
            
        return self.bhava_lords.get(bhava_number)
    
    def get_bhava_lord_placement(self, bhava_number: int) -> Optional[Dict]:
        """
        Get placement details of bhava lord
        
        Args:
            bhava_number: Bhava number (1-12)
            
        Returns:
            Dictionary with lord placement details
        """
        lord = self.get_bhava_lord(bhava_number)
        if not lord or lord not in self.grahas:
            return None
            
        lord_bhava = self.get_bhava_of_graha(lord)
        lord_graha = self.grahas[lord]
        
        return {
            'lord_graha': lord,
            'placed_in_bhava': lord_bhava,
            'placed_in_rasi': lord_graha.rasi,
            'longitude': lord_graha.longitude,
            'dignity': lord_graha.get_dignity(),
            'is_retrograde': lord_graha.is_retrograde,
            'distance_from_own_bhava': self._calculate_lord_distance(bhava_number, lord_bhava)
        }
    
    def _calculate_lord_distance(self, own_bhava: int, placed_bhava: Optional[int]) -> Optional[int]:
        """Calculate distance of lord from its own bhava"""
        if placed_bhava is None:
            return None
            
        distance = placed_bhava - own_bhava
        if distance <= 0:
            distance += 12
            
        return distance
    
    def calculate_bhava_strength(self, bhava_number: int) -> Dict[str, Union[float, str, List]]:
        """
        Calculate the strength of a bhava based on multiple factors
        
        Args:
            bhava_number: Bhava number (1-12)
            
        Returns:
            Dictionary with strength analysis
        """
        if not 1 <= bhava_number <= 12:
            raise ValueError("Bhava number must be between 1 and 12")
            
        bhava = self.bhavas[bhava_number - 1]
        lord = self.get_bhava_lord(bhava_number)
        lord_placement = self.get_bhava_lord_placement(bhava_number)
        grahas_in_bhava = self.get_grahas_in_bhava(bhava_number)
        
        strength_factors = {
            'base_strength': self._get_base_bhava_strength(bhava_number),
            'lord_strength': self._calculate_lord_strength(lord_placement),
            'occupant_strength': self._calculate_occupant_strength(grahas_in_bhava),
            'aspect_strength': self._calculate_aspect_strength_to_bhava(bhava_number),
            'rasi_strength': self._calculate_rasi_strength(bhava.rasi)
        }
        
        # Calculate weighted total strength
        weights = {
            'base_strength': 0.2,
            'lord_strength': 0.3,
            'occupant_strength': 0.25,
            'aspect_strength': 0.15,
            'rasi_strength': 0.1
        }
        
        total_strength = sum(
            strength_factors[factor] * weights[factor] 
            for factor in strength_factors
        )
        
        # Determine strength category
        if total_strength >= 0.8:
            strength_category = 'Very Strong'
        elif total_strength >= 0.6:
            strength_category = 'Strong'
        elif total_strength >= 0.4:
            strength_category = 'Moderate'
        elif total_strength >= 0.2:
            strength_category = 'Weak'
        else:
            strength_category = 'Very Weak'
        
        return {
            'total_strength': total_strength,
            'strength_category': strength_category,
            'strength_factors': strength_factors,
            'weights_used': weights,
            'bhava_nature': bhava.get_nature(),
            'contributing_factors': self._get_strength_contributors(strength_factors)
        }
    
    def _get_base_bhava_strength(self, bhava_number: int) -> float:
        """Get base strength based on bhava nature"""
        bhava = self.bhavas[bhava_number - 1]
        
        if bhava.is_kendra() and bhava.is_trikona():  # 1st house
            return 1.0
        elif bhava.is_kendra() or bhava.is_trikona():
            return 0.8
        elif bhava.is_upachaya():
            return 0.6
        elif bhava.is_dusthana():
            return 0.2
        else:
            return 0.5
    
    def _calculate_lord_strength(self, lord_placement: Optional[Dict]) -> float:
        """Calculate strength contribution from bhava lord"""
        if not lord_placement:
            return 0.0
            
        strength = 0.5  # Base strength
        
        # Dignity bonus
        dignity = lord_placement.get('dignity', 'Neutral')
        if 'Exalted' in dignity:
            strength += 0.4
        elif 'Own Sign' in dignity or 'Moolatrikona' in dignity:
            strength += 0.3
        elif 'Debilitated' in dignity:
            strength -= 0.3
        
        # Placement bonus/penalty
        placed_bhava = lord_placement.get('placed_in_bhava')
        if placed_bhava:
            placed_bhava_obj = self.bhavas[placed_bhava - 1]
            if placed_bhava_obj.is_kendra() or placed_bhava_obj.is_trikona():
                strength += 0.2
            elif placed_bhava_obj.is_dusthana():
                strength -= 0.2
        
        # Retrograde penalty
        if lord_placement.get('is_retrograde'):
            strength -= 0.1
            
        return max(0.0, min(1.0, strength))
    
    def _calculate_occupant_strength(self, grahas_in_bhava: List[str]) -> float:
        """Calculate strength from grahas occupying the bhava"""
        if not grahas_in_bhava:
            return 0.3  # Empty bhava gets neutral strength
            
        total_strength = 0.0
        
        for graha_name in grahas_in_bhava:
            graha = self.grahas[graha_name]
            graha_strength = 0.5  # Base
            
            # Dignity
            dignity = graha.get_dignity()
            if 'Exalted' in dignity:
                graha_strength += 0.4
            elif 'Own Sign' in dignity or 'Moolatrikona' in dignity:
                graha_strength += 0.3
            elif 'Debilitated' in dignity:
                graha_strength -= 0.3
            
            # Natural benefic/malefic
            if graha.is_benefic():
                graha_strength += 0.1
            else:
                graha_strength -= 0.05
                
            # Retrograde
            if graha.is_retrograde:
                graha_strength -= 0.1
                
            total_strength += max(0.0, min(1.0, graha_strength))
        
        # Average strength of occupants
        return total_strength / len(grahas_in_bhava)
    
    def _calculate_aspect_strength_to_bhava(self, bhava_number: int) -> float:
        """Calculate strength from aspects to the bhava"""
        aspects_to_bhava = self.aspects.get_aspects_to_bhava(bhava_number, self.ascendant_longitude)
        
        if not aspects_to_bhava:
            return 0.3  # Neutral if no aspects
            
        total_aspect_strength = 0.0
        aspect_count = 0
        
        for graha_name, aspect_info in aspects_to_bhava.items():
            if aspect_info['is_aspecting']:
                graha = self.grahas[graha_name]
                aspect_strength = aspect_info.get('total_strength', 0)
                
                # Weight by graha benefic/malefic nature
                if graha.is_benefic():
                    weighted_strength = aspect_strength * 1.2
                else:
                    weighted_strength = aspect_strength * 0.8
                    
                total_aspect_strength += weighted_strength
                aspect_count += 1
        
        if aspect_count == 0:
            return 0.3
            
        return min(1.0, total_aspect_strength / aspect_count)
    
    def _calculate_rasi_strength(self, rasi_name: Optional[str]) -> float:
        """Calculate strength based on the rasi in the bhava"""
        if not rasi_name:
            return 0.5
            
        rasi = Rasi(rasi_name)
        
        # Base strength by element and quality
        element_strength = {
            'Fire': 0.7,
            'Earth': 0.6,
            'Air': 0.5,
            'Water': 0.6
        }
        
        quality_strength = {
            'Cardinal': 0.7,
            'Fixed': 0.8,
            'Mutable': 0.5
        }
        
        element = rasi.get_element()
        quality = rasi.get_quality()
        
        base = (element_strength.get(element, 0.5) + quality_strength.get(quality, 0.5)) / 2
        
        return base
    
    def _get_strength_contributors(self, strength_factors: Dict) -> List[str]:
        """Identify the main contributors to bhava strength"""
        contributors = []
        
        for factor, strength in strength_factors.items():
            if strength >= 0.7:
                contributors.append(f"Strong {factor}")
            elif strength <= 0.3:
                contributors.append(f"Weak {factor}")
                
        return contributors
    
    def analyze_bhava_yoga(self, bhava_number: int) -> Dict[str, List]:
        """
        Analyze yogas related to a specific bhava
        
        Args:
            bhava_number: Bhava number (1-12)
            
        Returns:
            Dictionary with identified yogas
        """
        yogas = {
            'kendra_trikona_yoga': [],
            'exchange_yoga': [],
            'conjunction_yoga': [],
            'aspect_yoga': [],
            'special_yoga': []
        }
        
        lord = self.get_bhava_lord(bhava_number)
        lord_placement = self.get_bhava_lord_placement(bhava_number)
        grahas_in_bhava = self.get_grahas_in_bhava(bhava_number)
        
        # Kendra-Trikona Yoga
        if lord_placement:
            placed_bhava = lord_placement.get('placed_in_bhava')
            if placed_bhava:
                placed_bhava_obj = self.bhavas[placed_bhava - 1]
                bhava_obj = self.bhavas[bhava_number - 1]
                
                if ((bhava_obj.is_kendra() and placed_bhava_obj.is_trikona()) or
                    (bhava_obj.is_trikona() and placed_bhava_obj.is_kendra())):
                    yogas['kendra_trikona_yoga'].append({
                        'type': 'Lord in Kendra-Trikona',
                        'lord': lord,
                        'from_bhava': bhava_number,
                        'to_bhava': placed_bhava
                    })
        
        # Exchange Yoga (Parivartana)
        if lord and lord in self.grahas:
            lord_bhava = self.get_bhava_of_graha(lord)
            if lord_bhava:
                other_lord = self.get_bhava_lord(lord_bhava)
                if other_lord and self.get_bhava_of_graha(other_lord) == bhava_number:
                    yogas['exchange_yoga'].append({
                        'type': 'Parivartana Yoga',
                        'bhava1': bhava_number,
                        'bhava2': lord_bhava,
                        'lord1': lord,
                        'lord2': other_lord
                    })
        
        # Conjunction Yogas
        if len(grahas_in_bhava) >= 2:
            conjunctions = self.aspects.calculate_conjunction_aspects()
            for conj in conjunctions:
                if (conj['graha1'] in grahas_in_bhava and 
                    conj['graha2'] in grahas_in_bhava):
                    yogas['conjunction_yoga'].append({
                        'type': f"{conj['graha1']}-{conj['graha2']} Conjunction",
                        'strength': conj['strength'],
                        'distance': conj['angular_distance'],
                        'bhava': bhava_number
                    })
        
        return yogas
    
    def get_bhava_summary(self, bhava_number: int) -> Dict:
        """
        Get comprehensive summary of a bhava
        
        Args:
            bhava_number: Bhava number (1-12)
            
        Returns:
            Complete bhava analysis summary
        """
        if not 1 <= bhava_number <= 12:
            raise ValueError("Bhava number must be between 1 and 12")
            
        bhava = self.bhavas[bhava_number - 1]
        strength = self.calculate_bhava_strength(bhava_number)
        yogas = self.analyze_bhava_yoga(bhava_number)
        
        return {
            'bhava_info': bhava.to_dict(),
            'grahas_placed': self.get_grahas_in_bhava(bhava_number),
            'bhava_lord': self.get_bhava_lord(bhava_number),
            'lord_placement': self.get_bhava_lord_placement(bhava_number),
            'strength_analysis': strength,
            'yogas': yogas,
            'aspects_received': self.aspects.get_aspects_to_bhava(bhava_number, self.ascendant_longitude),
            'significations': bhava.get_all_significations()
        }
    
    def get_all_bhava_analysis(self) -> Dict[int, Dict]:
        """Get complete analysis for all bhavas"""
        analysis = {}
        
        for i in range(1, 13):
            analysis[i] = self.get_bhava_summary(i)
            
        return analysis
    
    def find_strongest_bhavas(self, count: int = 3) -> List[Tuple[int, float]]:
        """
        Find the strongest bhavas in the chart
        
        Args:
            count: Number of strongest bhavas to return
            
        Returns:
            List of (bhava_number, strength) tuples
        """
        bhava_strengths = []
        
        for i in range(1, 13):
            strength = self.calculate_bhava_strength(i)
            bhava_strengths.append((i, strength['total_strength']))
        
        # Sort by strength and return top N
        bhava_strengths.sort(key=lambda x: x[1], reverse=True)
        return bhava_strengths[:count]
    
    def find_weakest_bhavas(self, count: int = 3) -> List[Tuple[int, float]]:
        """
        Find the weakest bhavas in the chart
        
        Args:
            count: Number of weakest bhavas to return
            
        Returns:
            List of (bhava_number, strength) tuples
        """
        bhava_strengths = []
        
        for i in range(1, 13):
            strength = self.calculate_bhava_strength(i)
            bhava_strengths.append((i, strength['total_strength']))
        
        # Sort by strength and return bottom N
        bhava_strengths.sort(key=lambda x: x[1])
        return bhava_strengths[:count]
    
    def to_dict(self) -> Dict:
        """
        Convert complete bhava analysis to dictionary
        
        Returns:
            Dictionary with all bhava analysis data
        """
        return {
            'ascendant_longitude': self.ascendant_longitude,
            'house_system': self.house_system,
            'all_bhavas': self.get_all_bhava_analysis(),
            'graha_placements': self.graha_placements,
            'bhava_lords': self.bhava_lords,
            'strongest_bhavas': self.find_strongest_bhavas(),
            'weakest_bhavas': self.find_weakest_bhavas()
        }
