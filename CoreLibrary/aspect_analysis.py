"""
aspect_analysis.py - Enhanced aspects analysis for bhavas and grahas

This module provides:
- Detailed bhava aspects analysis
- Graha dignity in aspect positions
- Benefic/Malefic classification of drishti
- Comprehensive aspect strength and effects
"""

from typing import Dict, List, Optional, Union, Tuple
import math
try:
    from .calculations_helper import CalculationsHelper
    from .graha import Graha
    from .aspects import Aspects
except ImportError:
    from calculations_helper import CalculationsHelper
    from graha import Graha
    from aspects import Aspects


class AspectAnalysis:
    """Enhanced aspects analysis with dignity and benefic/malefic classification"""
    
    # Graha classification
    NATURAL_BENEFICS = ['Jupiter', 'Venus', 'Moon']  # Moon when bright (Shukla Paksha)
    NATURAL_MALEFICS = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']
    NEUTRAL_GRAHAS = ['Mercury']  # Mercury takes nature of conjunct planet
    
    # Aspect names in traditional format
    ASPECT_NAMES = {
        30: '2nd Aspect',
        60: '3rd Aspect',
        90: '4th Aspect', 
        120: '5th Aspect',
        150: '6th Aspect',
        180: '7th Aspect',
        210: '8th Aspect',
        240: '9th Aspect',
        270: '10th Aspect',
        330: '12th Aspect'
    }
    
    # Dignity keywords
    DIGNITY_KEYWORDS = {
        'Own Sign': 'Swakshetra',
        'Exalted': 'Uccha',
        'Moolatrikona': 'Moolatrikona', 
        'Friend': 'Mitra',
        'Neutral': 'Sama',
        'Enemy': 'Shatru',
        'Debilitated': 'Neecha'
    }
    
    def __init__(self, chart_data: Dict, aspect_mode: str = 'rasi'):
        """
        Initialize aspect analysis
        
        Args:
            chart_data: Complete chart data with grahas and bhavas
            aspect_mode: 'rasi' for sign-based (default) or 'degree' for orb-based
        """
        self.chart_data = chart_data
        self.grahas = chart_data['grahas']
        self.bhavas = chart_data['bhavas']
        self.aspect_mode = aspect_mode
        self.aspects_calc = self._create_aspects_calculator()
        
    def _create_aspects_calculator(self) -> Aspects:
        """Create Aspects calculator from graha data"""
        graha_objects = {}
        for name, data in self.grahas.items():
            graha_objects[name] = Graha(name, data['longitude'])
        return Aspects(graha_objects)
    
    def get_bhava_aspects_analysis(self, bhava_number: int) -> Dict:
        """
        Get comprehensive aspects analysis for a specific bhava
        
        Args:
            bhava_number: House number (1-12)
            
        Returns:
            Dictionary with detailed aspects analysis
        """
        if bhava_number not in self.bhavas:
            raise ValueError(f"Bhava {bhava_number} not found")
            
        bhava = self.bhavas[bhava_number]
        bhava_longitude = bhava['cusp_degree']
        
        aspects_to_bhava = []
        
        # Check each graha's aspects to this bhava
        for graha_name, graha_data in self.grahas.items():
            graha_aspects = self._get_graha_aspects_to_point(
                graha_name, graha_data, bhava_longitude, bhava_number
            )
            
            if graha_aspects:
                aspects_to_bhava.extend(graha_aspects)
        
        # Sort by aspect strength
        aspects_to_bhava.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'bhava_number': bhava_number,
            'bhava_name': bhava['name'],
            'bhava_rasi': bhava['rasi'],
            'bhava_degrees': bhava['degrees_in_rasi'],
            'total_aspects': len(aspects_to_bhava),
            'aspects': aspects_to_bhava,
            'summary': self._create_aspects_summary(aspects_to_bhava)
        }
    
    def _get_graha_aspects_to_point(self, graha_name: str, graha_data: Dict, 
                                   target_longitude: float, bhava_number: int) -> List[Dict]:
        """Get all aspects from a graha to a specific point"""
        if self.aspect_mode == 'rasi':
            return self._get_rasi_based_aspects(graha_name, graha_data, bhava_number)
        else:
            return self._get_degree_based_aspects(graha_name, graha_data, target_longitude)
    
    def _get_rasi_based_aspects(self, graha_name: str, graha_data: Dict, 
                               bhava_number: int) -> List[Dict]:
        """Calculate rasi-based (sign-based) aspects"""
        graha_rasi = graha_data['rasi']
        bhava = self.bhavas[bhava_number]
        target_rasi = bhava['rasi']
        
        # Get rasi numbers (0-11)
        rasi_list = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        graha_rasi_num = rasi_list.index(graha_rasi)
        target_rasi_num = rasi_list.index(target_rasi)
        
        # Get special aspects for this graha (with dynamic Rahu/Ketu handling)
        special_aspects = self._get_graha_aspects(graha_name, graha_rasi)
        
        aspects = []
        
        for aspect_angle in special_aspects:
            # Convert angle to house count (30° = 1 house)
            houses_away = int(aspect_angle / 30)
            
            # Calculate which rasi is aspected
            aspected_rasi_num = (graha_rasi_num + houses_away) % 12
            
            # Check if target rasi is the aspected rasi
            if aspected_rasi_num == target_rasi_num:
                aspected_rasi = rasi_list[aspected_rasi_num]
                
                # Calculate aspect dignity: graha's dignity IF it were in the aspected rasi
                aspect_longitude = aspected_rasi_num * 30 + 15  # Middle of the aspected rasi
                aspect_dignity = Graha(graha_name, aspect_longitude).get_dignity()
                
                # Determine benefic/malefic nature
                benefic_nature = self._get_benefic_nature(graha_name, graha_data)
                
                # For rasi-based aspects, strength is always 100%
                drishti_effect = self._calculate_rasi_drishti_effect(
                    graha_name, aspect_dignity, benefic_nature
                )
                
                aspect_info = {
                    'graha': graha_name,
                    'aspect_type': self.ASPECT_NAMES.get(aspect_angle, f'{aspect_angle}° Aspect'),
                    'aspect_angle': aspect_angle,
                    'aspect_mode': 'Rasi-based',
                    'strength': 1.0,  # 100% for rasi-based
                    'graha_position': {
                        'rasi': graha_rasi,
                        'degrees': graha_data['degrees_in_rasi']
                    },
                    'aspect_position': {
                        'rasi': aspected_rasi,
                        'degrees': 'Full Sign'
                    },
                    'dignity': aspect_dignity,
                    'dignity_sanskrit': self.DIGNITY_KEYWORDS.get(aspect_dignity, aspect_dignity),
                    'benefic_nature': benefic_nature,
                    'drishti_effect': drishti_effect,
                    'effect_description': self._get_effect_description(drishti_effect, aspect_dignity)
                }
                
                aspects.append(aspect_info)
        
        return aspects
    
    def _get_graha_aspects(self, graha_name: str, graha_rasi: str) -> List[int]:
        """Get aspects for a graha, handling special cases for Rahu/Ketu"""
        # Get base aspects
        base_aspects = Aspects.GRAHA_SPECIAL_ASPECTS.get(graha_name, [180]).copy()
        
        # Handle Rahu/Ketu special aspects based on odd/even rasi
        if graha_name in ['Rahu', 'Ketu']:
            # Even rasis: Taurus(1), Cancer(3), Virgo(5), Scorpio(7), Capricorn(9), Pisces(11)
            # Odd rasis: Aries(0), Gemini(2), Leo(4), Libra(6), Sagittarius(8), Aquarius(10)
            rasi_list = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
            
            graha_rasi_num = rasi_list.index(graha_rasi)
            
            if graha_rasi_num % 2 == 1:  # Even rasi (index 1,3,5,7,9,11)
                base_aspects.append(30)   # 2nd aspect (30° × 1 = 30°)
            else:  # Odd rasi (index 0,2,4,6,8,10)
                base_aspects.append(330)  # 12th aspect (30° × 11 = 330°)
        
        return base_aspects
    
    def _get_degree_based_aspects(self, graha_name: str, graha_data: Dict, 
                                 target_longitude: float) -> List[Dict]:
        """Calculate degree-based aspects with orbs"""
        graha_longitude = graha_data['longitude']
        graha_rasi = graha_data['rasi']
        
        # Get special aspects for this graha (with dynamic Rahu/Ketu handling)
        special_aspects = self._get_graha_aspects(graha_name, graha_rasi)
        
        aspects = []
        
        for aspect_angle in special_aspects:
            # Calculate expected position of aspect
            aspect_longitude = (graha_longitude + aspect_angle) % 360
            
            # Check if this aspect hits the target point
            angular_distance = CalculationsHelper.get_angular_distance(
                aspect_longitude, target_longitude
            )
            
            # Check if aspect is within orb
            orb_category = self.aspects_calc.get_aspect_orb_category(
                angular_distance, 0  # 0 because we're checking if aspect hits the point
            )
            
            if orb_category:  # If aspect is within orb
                # Calculate dignity at aspect position (graha's dignity in the aspected position)
                aspect_rasi_data = CalculationsHelper.degrees_to_rasi(aspect_longitude)
                aspect_rasi = aspect_rasi_data['rasi']
                
                # Get graha dignity in aspect position
                aspect_graha = Graha(graha_name, aspect_longitude)
                aspect_dignity = aspect_graha.get_dignity()
                
                # Determine benefic/malefic nature
                benefic_nature = self._get_benefic_nature(graha_name, graha_data)
                
                # Calculate drishti effect
                drishti_effect = self._calculate_drishti_effect(
                    graha_name, aspect_dignity, benefic_nature, orb_category
                )
                
                aspect_info = {
                    'graha': graha_name,
                    'aspect_type': self.ASPECT_NAMES.get(aspect_angle, f'{aspect_angle}° Aspect'),
                    'aspect_angle': aspect_angle,
                    'aspect_mode': 'Degree-based',
                    'orb_category': orb_category,
                    'strength': Aspects.ASPECT_STRENGTH[orb_category],
                    'graha_position': {
                        'rasi': graha_rasi,
                        'degrees': graha_data['degrees_in_rasi']
                    },
                    'aspect_position': {
                        'rasi': aspect_rasi,
                        'degrees': aspect_rasi_data['degrees']
                    },
                    'dignity': aspect_dignity,
                    'dignity_sanskrit': self.DIGNITY_KEYWORDS.get(aspect_dignity, aspect_dignity),
                    'benefic_nature': benefic_nature,
                    'drishti_effect': drishti_effect,
                    'effect_description': self._get_effect_description(drishti_effect, aspect_dignity)
                }
                
                aspects.append(aspect_info)
        
        return aspects
    
    def _get_benefic_nature(self, graha_name: str, graha_data: Dict) -> str:
        """Determine if graha is benefic or malefic"""
        if graha_name in self.NATURAL_BENEFICS:
            return 'Benefic'
        elif graha_name in self.NATURAL_MALEFICS:
            return 'Malefic'
        elif graha_name == 'Mercury':
            # Mercury takes nature of conjunct planet
            # For now, classify as neutral
            return 'Neutral'
        else:
            return 'Unknown'
    
    def _calculate_rasi_drishti_effect(self, graha_name: str, dignity: str, 
                                       benefic_nature: str) -> str:
        """Calculate drishti effect for rasi-based aspects (always full strength)"""
        # Base classification
        if benefic_nature == 'Benefic':
            if dignity in ['Exalted', 'Own Sign', 'Moolatrikona']:
                return 'Very Auspicious'
            elif dignity in ['Friend']:
                return 'Auspicious'
            elif dignity in ['Neutral']:
                return 'Mildly Auspicious'
            elif dignity in ['Enemy']:
                return 'Neutral'
            elif dignity in ['Debilitated']:
                return 'Neutral'  # Benefic + debilitation = neutral
            else:
                return 'Auspicious'
                
        elif benefic_nature == 'Malefic':
            if dignity in ['Exalted', 'Own Sign', 'Moolatrikona']:
                return 'Neutral'  # Malefic but dignified = neutral
            elif dignity in ['Friend']:
                return 'Mildly Inauspicious'
            elif dignity in ['Neutral']:
                return 'Inauspicious'
            elif dignity in ['Enemy']:
                return 'Very Inauspicious'
            elif dignity in ['Debilitated']:
                return 'Extremely Inauspicious'
            else:
                return 'Inauspicious'
        else:
            return 'Neutral'
    
    def _calculate_drishti_effect(self, graha_name: str, dignity: str, 
                                 benefic_nature: str, orb_category: str) -> str:
        """Calculate the overall effect of the drishti"""
        strength_factor = Aspects.ASPECT_STRENGTH[orb_category]
        
        # Base classification
        if benefic_nature == 'Benefic':
            if dignity in ['Exalted', 'Own Sign', 'Moolatrikona']:
                base_effect = 'Very Auspicious'
            elif dignity in ['Friend']:
                base_effect = 'Auspicious'
            elif dignity in ['Neutral']:
                base_effect = 'Mildly Auspicious'
            elif dignity in ['Enemy']:
                base_effect = 'Neutral'
            elif dignity in ['Debilitated']:
                base_effect = 'Neutral'  # Benefic + debilitation = neutral
            else:
                base_effect = 'Auspicious'
                
        elif benefic_nature == 'Malefic':
            if dignity in ['Exalted', 'Own Sign', 'Moolatrikona']:
                base_effect = 'Neutral'  # Malefic but dignified = neutral
            elif dignity in ['Friend']:
                base_effect = 'Mildly Inauspicious'
            elif dignity in ['Neutral']:
                base_effect = 'Inauspicious'
            elif dignity in ['Enemy']:
                base_effect = 'Very Inauspicious'
            elif dignity in ['Debilitated']:
                base_effect = 'Extremely Inauspicious'
            else:
                base_effect = 'Inauspicious'
        else:
            base_effect = 'Neutral'
        
        # Modify based on strength
        if strength_factor >= 0.75:
            return f'Strong {base_effect}'
        elif strength_factor >= 0.5:
            return f'Moderate {base_effect}'
        else:
            return f'Weak {base_effect}'
    
    def _get_effect_description(self, drishti_effect: str, dignity: str) -> str:
        """Get detailed description of drishti effect"""
        descriptions = {
            'Strong Very Auspicious': f'Excellent influence with {dignity} strength',
            'Strong Auspicious': f'Good influence with {dignity} strength',
            'Strong Neutral': f'Balanced influence with {dignity} strength',
            'Strong Inauspicious': f'Challenging influence with {dignity} strength',
            'Strong Very Inauspicious': f'Very challenging influence with {dignity} strength',
            'Strong Extremely Inauspicious': f'Extremely challenging influence with {dignity} strength'
        }
        
        return descriptions.get(drishti_effect, f'{drishti_effect} influence with {dignity} dignity')
    
    def _create_aspects_summary(self, aspects: List[Dict]) -> Dict:
        """Create summary of aspects"""
        if not aspects:
            return {
                'total_aspects': 0,
                'benefic_aspects': 0,
                'malefic_aspects': 0,
                'neutral_aspects': 0,
                'strongest_aspect': None,
                'overall_influence': 'No major aspects'
            }
        
        benefic_count = len([a for a in aspects if 'Auspicious' in a['drishti_effect']])
        malefic_count = len([a for a in aspects if 'Inauspicious' in a['drishti_effect']])
        neutral_count = len([a for a in aspects if 'Neutral' in a['drishti_effect']])
        
        strongest_aspect = max(aspects, key=lambda x: x['strength'])
        
        # Determine overall influence
        if benefic_count > malefic_count:
            overall = 'Predominantly Auspicious'
        elif malefic_count > benefic_count:
            overall = 'Predominantly Inauspicious'
        else:
            overall = 'Mixed Influences'
        
        return {
            'total_aspects': len(aspects),
            'benefic_aspects': benefic_count,
            'malefic_aspects': malefic_count,
            'neutral_aspects': neutral_count,
            'strongest_aspect': strongest_aspect,
            'overall_influence': overall
        }
    
    def format_aspects_table(self, bhava_analysis: Dict) -> str:
        """Format aspects analysis as a table"""
        if not bhava_analysis['aspects']:
            return f"\nNo major aspects to Bhava {bhava_analysis['bhava_number']}"
        
        # Table header
        header = f"\n{'='*80}\n"
        header += f"ASPECTS TO BHAVA {bhava_analysis['bhava_number']} - {bhava_analysis['bhava_name']}\n"
        header += f"Position: {bhava_analysis['bhava_rasi']} {bhava_analysis['bhava_degrees']:.2f}°\n"
        header += f"Mode: {'Rasi-based (Sign-to-Sign)' if self.aspect_mode == 'rasi' else 'Degree-based (With Orbs)'}\n"
        header += f"{'='*80}\n"
        
        # Column headers
        # Column headers based on aspect mode
        if self.aspect_mode == 'rasi':
            table = f"{'Graha':<8} {'Aspect':<12} {'Dignity':<12} {'Nature':<8} {'Effect':<20}\n"
            table += f"{'-'*70}\n"
        else:
            table = f"{'Graha':<8} {'Aspect':<12} {'Dignity':<12} {'Nature':<8} {'Effect':<20} {'Strength':<8}\n"
            table += f"{'-'*80}\n"
        
        # Data rows
        for aspect in bhava_analysis['aspects']:
            graha = aspect['graha']
            aspect_type = aspect['aspect_type']
            dignity = aspect['dignity'][:11]  # Truncate if too long
            nature = aspect['benefic_nature'][:7]
            effect = aspect['drishti_effect'][:19]
            
            if self.aspect_mode == 'rasi':
                table += f"{graha:<8} {aspect_type:<12} {dignity:<12} {nature:<8} {effect:<20}\n"
            else:
                strength = f"{aspect['strength']:.0%}"
                table += f"{graha:<8} {aspect_type:<12} {dignity:<12} {nature:<8} {effect:<20} {strength:<8}\n"
        
        # Summary
        summary = bhava_analysis['summary']
        table += f"\n{'-'*80}\n"
        table += f"SUMMARY: {summary['overall_influence']}\n"
        table += f"Benefic: {summary['benefic_aspects']} | "
        table += f"Malefic: {summary['malefic_aspects']} | "
        table += f"Neutral: {summary['neutral_aspects']}\n"
        table += f"{'='*80}\n"
        
        return header + table