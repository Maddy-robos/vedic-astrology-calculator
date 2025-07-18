"""
chart.py - Birth chart generation and analysis

This module provides:
- Complete birth chart generation from birth details
- Integration of all calculation modules
- Chart analysis and interpretation
- Export functionality for charts
"""

from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime
import json
import os

try:
    # Try relative imports first (when used as package)
    from .conversions import Conversions
    from .calculations_helper import CalculationsHelper
    from .graha import Graha
    from .rasi import Rasi
    from .bhava import Bhava
    from .aspects import Aspects
    from .bhava_analysis import BhavaAnalysis
    from .swiss_ephemeris import SwissEphemeris
    from .chara_karaka import CharaKaraka
    from .panchanga import Panchanga
except ImportError:
    # Fall back to absolute imports (when used directly)
    from conversions import Conversions
    from calculations_helper import CalculationsHelper
    from graha import Graha
    from rasi import Rasi
    from bhava import Bhava
    from aspects import Aspects
    from bhava_analysis import BhavaAnalysis
    from swiss_ephemeris import SwissEphemeris
    from chara_karaka import CharaKaraka
    from panchanga import Panchanga


class Chart:
    """Main class for generating and analyzing birth charts"""
    
    def __init__(self, birth_datetime: datetime, latitude: float, longitude: float,
                 timezone_str: str = 'UTC', ayanamsa: str = 'Lahiri', 
                 house_system: str = 'Equal'):
        """
        Initialize a birth chart
        
        Args:
            birth_datetime: Birth date and time
            latitude: Birth latitude in degrees
            longitude: Birth longitude in degrees (positive East)
            timezone_str: Timezone string (e.g., 'Asia/Kolkata')
            ayanamsa: Ayanamsa system to use
            house_system: House system for calculations
        """
        self.birth_datetime = birth_datetime
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_str = timezone_str
        self.ayanamsa = ayanamsa
        self.house_system = house_system
        
        # Initialize conversion utilities
        self.conversions = Conversions(ayanamsa)
        self.swiss_ephemeris = SwissEphemeris(ayanamsa)
        
        # Convert birth time to UTC and Julian Day
        self.birth_datetime_utc = self.conversions.local_to_utc(birth_datetime, timezone_str)
        self.julian_day = self.swiss_ephemeris.julian_day_from_datetime(self.birth_datetime_utc)
        
        # Calculate chart
        self.chart_data = self._calculate_chart()
        
        # Calculate retrograde motion data
        self.retrograde_data = self._calculate_retrograde_data()
        
    def _calculate_chart(self) -> Dict:
        """Calculate complete chart data"""
        chart_data = {
            'birth_info': self._get_birth_info(),
            'grahas': self._calculate_graha_positions(),
            'ascendant': self._calculate_ascendant(),
            'bhavas': self._calculate_bhavas(),
            'aspects': None,  # Will be calculated after grahas
            'bhava_analysis': None,  # Will be calculated after bhavas
            'special_points': self._calculate_special_points()
        }
        
        # Create Graha objects
        graha_objects = {}
        for graha_name, graha_data in chart_data['grahas'].items():
            graha_objects[graha_name] = Graha(
                name=graha_name,
                longitude=graha_data['longitude'],
                latitude=graha_data.get('latitude', 0.0),
                speed=graha_data.get('speed', 0.0)
            )
        
        # Calculate aspects
        aspects_calc = Aspects(graha_objects)
        chart_data['aspects'] = aspects_calc.to_dict()
        
        # Calculate bhava analysis
        bhava_analysis = BhavaAnalysis(
            graha_objects, 
            chart_data['ascendant']['longitude'],
            self.house_system
        )
        chart_data['bhava_analysis'] = bhava_analysis.to_dict()
        
        return chart_data
    
    def _get_birth_info(self) -> Dict:
        """Get basic birth information"""
        return {
            'birth_datetime': self.birth_datetime,
            'birth_datetime_utc': self.birth_datetime_utc,
            'julian_day': self.julian_day,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone_str,
            'ayanamsa': self.ayanamsa,
            'house_system': self.house_system,
            'ayanamsa_value': self.conversions.get_ayanamsa(self.julian_day)
        }
    
    def _calculate_graha_positions(self) -> Dict[str, Dict]:
        """
        Calculate accurate positions for all grahas using Swiss Ephemeris
        """
        # Get accurate planetary positions from Swiss Ephemeris
        se_positions = self.swiss_ephemeris.get_all_planet_positions(self.julian_day)
        
        # Convert to our format with rasi and nakshatra data
        graha_positions = {}
        for graha_name, se_data in se_positions.items():
            if se_data is None:
                continue
                
            longitude = se_data['longitude']
            
            # Calculate rasi placement
            rasi_data = CalculationsHelper.degrees_to_rasi(longitude)
            
            # Calculate nakshatra placement
            nakshatra_data = CalculationsHelper.get_nakshatra_pada(longitude)
            
            graha_positions[graha_name] = {
                'longitude': longitude,
                'latitude': se_data['latitude'],
                'speed': se_data['speed_longitude'],
                'rasi': rasi_data['rasi'],
                'degrees_in_rasi': rasi_data['degrees'],
                'nakshatra': nakshatra_data['nakshatra'],
                'pada': nakshatra_data['pada'],
                'is_retrograde': se_data['is_retrograde'],
                'distance': se_data['distance'],
                'tropical_longitude': se_data['tropical_longitude'],
                'ayanamsa': se_data['ayanamsa']
            }
        
        return graha_positions
    
    def _calculate_ascendant(self) -> Dict:
        """
        Calculate accurate ascendant using Swiss Ephemeris
        """
        # Get accurate ascendant calculation from Swiss Ephemeris
        se_ascendant = self.swiss_ephemeris.calculate_ascendant(
            self.julian_day, self.latitude, self.longitude
        )
        
        if se_ascendant is None:
            # Fallback to simplified calculation if Swiss Ephemeris fails
            lst = self.conversions.calculate_sidereal_time(self.julian_day, self.longitude)
            ascendant_longitude = (lst + self.latitude * 0.5) % 360
            ascendant_longitude = self.conversions.tropical_to_sidereal(
                ascendant_longitude, self.julian_day
            )
        else:
            ascendant_longitude = se_ascendant['longitude']
            lst = se_ascendant['local_sidereal_time']
        
        # Calculate rasi and nakshatra
        rasi_data = CalculationsHelper.degrees_to_rasi(ascendant_longitude)
        nakshatra_data = CalculationsHelper.get_nakshatra_pada(ascendant_longitude)
        
        ascendant_data = {
            'longitude': ascendant_longitude,
            'rasi': rasi_data['rasi'],
            'degrees_in_rasi': rasi_data['degrees'],
            'nakshatra': nakshatra_data['nakshatra'],
            'pada': nakshatra_data['pada'],
            'local_sidereal_time': lst
        }
        
        # Add additional Swiss Ephemeris data if available
        if se_ascendant:
            ascendant_data.update({
                'tropical_longitude': se_ascendant.get('tropical_longitude'),
                'ayanamsa': se_ascendant.get('ayanamsa'),
                'midheaven': se_ascendant.get('midheaven'),
                'vertex': se_ascendant.get('vertex')
            })
        
        return ascendant_data
    
    def _calculate_bhavas(self) -> Dict[int, Dict]:
        """Calculate all 12 bhavas"""
        # Calculate ascendant directly to avoid circular reference
        ascendant_data = self._calculate_ascendant()
        ascendant_longitude = ascendant_data['longitude']
        
        bhavas = Bhava.get_all_bhavas(ascendant_longitude, self.house_system)
        
        bhavas_dict = {}
        for i, bhava in enumerate(bhavas, 1):
            bhavas_dict[i] = bhava.to_dict()
            
        return bhavas_dict
    
    def _calculate_special_points(self) -> Dict:
        """Calculate special points like midheaven, fortune, etc."""
        # Calculate ascendant directly to avoid circular reference
        ascendant = self._calculate_ascendant()
        
        # Midheaven (10th house cusp)
        midheaven_longitude = CalculationsHelper.normalize_degrees(
            ascendant['longitude'] + 270  # 10th house in equal house system
        )
        
        # Part of Fortune (simplified calculation)
        # In production: Ascendant + Moon - Sun (for day birth)
        # Calculate graha positions directly to avoid circular reference
        graha_positions = self._calculate_graha_positions()
        sun_longitude = graha_positions.get('Sun', {}).get('longitude', 0)
        moon_longitude = graha_positions.get('Moon', {}).get('longitude', 0)
        
        if not sun_longitude or not moon_longitude:
            # Use placeholder if graha positions not calculated yet
            fortune_longitude = ascendant['longitude'] + 45
        else:
            fortune_longitude = ascendant['longitude'] + moon_longitude - sun_longitude
        
        fortune_longitude = CalculationsHelper.normalize_degrees(fortune_longitude)
        
        return {
            'midheaven': {
                'longitude': midheaven_longitude,
                'rasi': CalculationsHelper.degrees_to_rasi(midheaven_longitude)['rasi']
            },
            'part_of_fortune': {
                'longitude': fortune_longitude,
                'rasi': CalculationsHelper.degrees_to_rasi(fortune_longitude)['rasi']
            }
        }
    
    def get_graha_positions(self) -> Dict[str, Dict]:
        """Get all graha positions"""
        return self.chart_data['grahas']
    
    def get_graha_position(self, graha_name: str) -> Optional[Dict]:
        """Get position of a specific graha"""
        return self.chart_data['grahas'].get(graha_name)
    
    def get_ascendant(self) -> Dict:
        """Get ascendant information"""
        return self.chart_data['ascendant']
    
    def get_bhavas(self) -> Dict[int, Dict]:
        """Get all bhava information"""
        return self.chart_data['bhavas']
    
    def get_bhava(self, bhava_number: int) -> Optional[Dict]:
        """Get specific bhava information"""
        return self.chart_data['bhavas'].get(bhava_number)
    
    def get_aspects(self) -> Dict:
        """Get all aspect information"""
        return self.chart_data['aspects']
    
    def get_bhava_analysis(self) -> Dict:
        """Get complete bhava analysis"""
        return self.chart_data['bhava_analysis']
    
    def get_chart_summary(self) -> Dict:
        """Get high-level chart summary"""
        birth_info = self.chart_data['birth_info']
        ascendant = self.chart_data['ascendant']
        grahas = self.chart_data['grahas']
        aspects = self.chart_data['aspects']['summary']
        bhava_analysis = self.chart_data['bhava_analysis']
        
        # Find strongest planets
        strongest_grahas = []
        for graha_name, graha_data in grahas.items():
            dignity = Graha(graha_name, graha_data['longitude']).get_dignity()
            if 'Exalted' in dignity or 'Own Sign' in dignity:
                strongest_grahas.append(f"{graha_name} ({dignity})")
        
        return {
            'birth_details': {
                'datetime': birth_info['birth_datetime'],
                'location': f"Lat: {birth_info['latitude']}, Lon: {birth_info['longitude']}",
                'timezone': birth_info['timezone']
            },
            'ascendant': {
                'rasi': ascendant['rasi'],
                'degrees': f"{ascendant['degrees_in_rasi']:.2f}°",
                'nakshatra': f"{ascendant['nakshatra']} pada {ascendant['pada']}"
            },
            'strongest_grahas': strongest_grahas,
            'strongest_bhavas': bhava_analysis.get('strongest_bhavas', []),
            'total_aspects': aspects.get('total_aspects', 0),
            'conjunctions': aspects.get('total_conjunctions', 0),
            'chart_strength': self._calculate_overall_chart_strength()
        }
    
    def _calculate_overall_chart_strength(self) -> str:
        """Calculate overall chart strength"""
        # Simplified chart strength calculation
        strength_points = 0
        total_points = 0
        
        # Check graha dignities
        for graha_name, graha_data in self.chart_data['grahas'].items():
            graha = Graha(graha_name, graha_data['longitude'])
            dignity = graha.get_dignity()
            
            if 'Exalted' in dignity:
                strength_points += 3
            elif 'Own Sign' in dignity or 'Moolatrikona' in dignity:
                strength_points += 2
            elif 'Debilitated' in dignity:
                strength_points -= 2
            else:
                strength_points += 1
            
            total_points += 3
        
        # Check kendra/trikona placements
        bhava_analysis = self.chart_data['bhava_analysis']
        strongest_bhavas = bhava_analysis.get('strongest_bhavas', [])
        if len(strongest_bhavas) >= 3:
            strength_points += 2
        
        # Calculate percentage
        strength_percentage = (strength_points / max(total_points, 1)) * 100
        
        if strength_percentage >= 80:
            return 'Very Strong'
        elif strength_percentage >= 60:
            return 'Strong'
        elif strength_percentage >= 40:
            return 'Moderate'
        elif strength_percentage >= 20:
            return 'Weak'
        else:
            return 'Very Weak'
    
    def find_yogas(self) -> Dict[str, List]:
        """Find major yogas in the chart"""
        yogas = {
            'raj_yogas': [],
            'dhana_yogas': [],
            'spiritual_yogas': [],
            'challenging_yogas': []
        }
        
        # Simple yoga detection
        bhava_analysis = self.chart_data['bhava_analysis']['all_bhavas']
        
        # Check for Raj Yogas (kendra-trikona connections)
        for bhava_num, bhava_data in bhava_analysis.items():
            if bhava_data['yogas']['kendra_trikona_yoga']:
                yogas['raj_yogas'].extend(bhava_data['yogas']['kendra_trikona_yoga'])
        
        # Check for Dhana Yogas (wealth combinations)
        bhava_2_lord = bhava_analysis.get(2, {}).get('bhava_lord')
        bhava_11_lord = bhava_analysis.get(11, {}).get('bhava_lord')
        
        if bhava_2_lord and bhava_11_lord:
            # Check if 2nd and 11th lords are connected
            yogas['dhana_yogas'].append({
                'type': 'Dhana Yoga potential',
                'lords': [bhava_2_lord, bhava_11_lord]
            })
        
        return yogas
    
    def _calculate_retrograde_data(self) -> Dict:
        """
        Calculate retrograde motion data for all planets
        
        Returns:
            Dictionary with retrograde data for each planet
        """
        try:
            return self.swiss_ephemeris.calculate_retrograde_data(self.julian_day)
        except Exception as e:
            print(f"Error calculating retrograde data: {e}")
            return {}
    
    def get_chara_karakas(self, retrograde_data: Optional[Dict] = None) -> Dict:
        """
        Calculate Chara Karakas using both standard and advanced methods
        
        Args:
            retrograde_data: Optional retrograde motion data for advanced calculation
            
        Returns:
            Dictionary with both calculation methods and retrograde data
        """
        # Initialize Chara Karaka calculator
        chara_karaka = CharaKaraka(self.chart_data['grahas'])
        
        # Use stored retrograde data if not provided
        if retrograde_data is None:
            retrograde_data = self.retrograde_data
        
        # Get both calculations
        result = chara_karaka.get_both_calculations(retrograde_data)
        
        # Add retrograde data to result for UI display
        result['retrograde_data'] = retrograde_data
        
        return result
    
    def get_panchanga(self) -> Dict:
        """
        Calculate Panchanga (five limbs of time)
        
        Returns:
            Dictionary with all panchanga elements
        """
        # Get Sun and Moon longitudes
        sun_data = self.chart_data['grahas'].get('Sun', {})
        moon_data = self.chart_data['grahas'].get('Moon', {})
        
        if not sun_data or not moon_data:
            return {}
            
        # Initialize Panchanga calculator
        panchanga = Panchanga(
            sun_longitude=sun_data['longitude'],
            moon_longitude=moon_data['longitude'],
            birth_datetime=self.birth_datetime,
            sunrise_time=None  # TODO: Calculate sunrise time
        )
        
        # Get complete panchanga
        return panchanga.get_complete_panchanga()
    
    def to_dict(self) -> Dict:
        """Convert entire chart to dictionary"""
        return {
            'birth_info': self.chart_data['birth_info'],
            'chart_data': self.chart_data,
            'summary': self.get_chart_summary(),
            'yogas': self.find_yogas()
        }
    
    def to_json(self, filepath: Optional[str] = None) -> str:
        """
        Export chart data to JSON
        
        Args:
            filepath: Optional file path to save JSON
            
        Returns:
            JSON string representation
        """
        chart_dict = self.to_dict()
        
        # Convert datetime objects to strings for JSON serialization
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        json_str = json.dumps(chart_dict, indent=2, default=default_serializer)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
                
        return json_str
    
    @classmethod
    def from_birth_details(cls, year: int, month: int, day: int, hour: int, 
                          minute: int, latitude: float, longitude: float,
                          timezone_str: str = 'UTC', **kwargs) -> 'Chart':
        """
        Create chart from individual birth detail components
        
        Args:
            year: Birth year
            month: Birth month (1-12)
            day: Birth day (1-31)
            hour: Birth hour (0-23)
            minute: Birth minute (0-59)
            latitude: Birth latitude in degrees
            longitude: Birth longitude in degrees
            timezone_str: Timezone string
            **kwargs: Additional arguments for Chart initialization
            
        Returns:
            Chart object
        """
        birth_datetime = datetime(year, month, day, hour, minute)
        return cls(birth_datetime, latitude, longitude, timezone_str, **kwargs)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Chart':
        """
        Create chart from JSON data
        
        Args:
            json_str: JSON string with chart data
            
        Returns:
            Chart object
        """
        data = json.loads(json_str)
        birth_info = data['birth_info']
        
        # Parse datetime from ISO format
        birth_datetime = datetime.fromisoformat(birth_info['birth_datetime'])
        
        return cls(
            birth_datetime=birth_datetime,
            latitude=birth_info['latitude'],
            longitude=birth_info['longitude'],
            timezone_str=birth_info['timezone'],
            ayanamsa=birth_info['ayanamsa'],
            house_system=birth_info['house_system']
        )
    
    def __str__(self) -> str:
        """String representation of the chart"""
        birth_info = self.chart_data['birth_info']
        ascendant = self.chart_data['ascendant']
        
        return (f"Chart for {birth_info['birth_datetime']} "
                f"({birth_info['latitude']:.2f}, {birth_info['longitude']:.2f}) "
                f"Ascendant: {ascendant['rasi']} {ascendant['degrees_in_rasi']:.2f}°")
    
    def __repr__(self) -> str:
        """Detailed representation of the chart"""
        return (f"Chart(birth_datetime={self.birth_datetime}, "
                f"latitude={self.latitude}, longitude={self.longitude}, "
                f"ayanamsa='{self.ayanamsa}', house_system='{self.house_system}')")
    
    def close(self):
        """Close Swiss Ephemeris and free resources"""
        if hasattr(self, 'swiss_ephemeris'):
            self.swiss_ephemeris.close()
    
    def __del__(self):
        """Cleanup when Chart object is destroyed"""
        try:
            self.close()
        except:
            pass
