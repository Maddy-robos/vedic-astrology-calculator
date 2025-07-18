"""
swiss_ephemeris.py - Swiss Ephemeris integration for accurate astronomical calculations

This module provides:
- Accurate planetary position calculations using Swiss Ephemeris
- Proper ascendant calculations
- Real astronomical coordinate transformations
- Support for all planets and lunar nodes
"""

import swisseph as swe
import math
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional


class SwissEphemeris:
    """Swiss Ephemeris wrapper for Jyotish calculations"""
    
    # Planet constants from Swiss Ephemeris
    PLANETS = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE,  # True node: swe.TRUE_NODE
        'Ketu': swe.MEAN_NODE   # Ketu is 180° opposite to Rahu
    }
    
    # Ayanamsa constants
    AYANAMSA_SYSTEMS = {
        'Lahiri': swe.SIDM_LAHIRI,
        'Raman': swe.SIDM_RAMAN,
        'Krishnamurti': swe.SIDM_KRISHNAMURTI,
        'Fagan_Bradley': swe.SIDM_FAGAN_BRADLEY
    }
    
    def __init__(self, ayanamsa_system: str = 'Lahiri'):
        """
        Initialize Swiss Ephemeris with specified ayanamsa
        
        Args:
            ayanamsa_system: Ayanamsa system to use
        """
        self.ayanamsa_system = ayanamsa_system
        
        # Set ayanamsa
        if ayanamsa_system in self.AYANAMSA_SYSTEMS:
            swe.set_sid_mode(self.AYANAMSA_SYSTEMS[ayanamsa_system])
        else:
            swe.set_sid_mode(swe.SIDM_LAHIRI)  # Default to Lahiri
    
    def julian_day_from_datetime(self, dt: datetime) -> float:
        """
        Convert datetime to Julian Day Number using Swiss Ephemeris
        
        Args:
            dt: datetime object (should be in UTC)
            
        Returns:
            Julian Day Number
        """
        # Ensure datetime is in UTC
        if dt.tzinfo is not None:
            dt_utc = dt.astimezone(timezone.utc)
        else:
            dt_utc = dt
            
        # Swiss Ephemeris Julian Day calculation
        jd = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        )
        
        return jd
    
    def get_planet_position(self, planet_name: str, jd: float) -> Dict:
        """
        Get accurate position of a planet using Swiss Ephemeris
        
        Args:
            planet_name: Name of the planet
            jd: Julian Day Number
            
        Returns:
            Dictionary with planet position data
        """
        if planet_name not in self.PLANETS:
            raise ValueError(f"Unknown planet: {planet_name}")
        
        planet_id = self.PLANETS[planet_name]
        
        try:
            # Calculate tropical position
            result, ret_flag = swe.calc_ut(jd, planet_id)
            
            if ret_flag < 0:
                raise Exception(f"Swiss Ephemeris error for {planet_name}: {ret_flag}")
            
            tropical_longitude = result[0]
            latitude = result[1]
            distance = result[2]
            speed_longitude = result[3]
            speed_latitude = result[4]
            speed_distance = result[5]
            
            # Convert to sidereal longitude
            ayanamsa = swe.get_ayanamsa_ut(jd)
            sidereal_longitude = tropical_longitude - ayanamsa
            
            # Normalize to 0-360 degrees
            sidereal_longitude = sidereal_longitude % 360
            
            # For Ketu, add 180 degrees to Rahu position
            if planet_name == 'Ketu':
                sidereal_longitude = (sidereal_longitude + 180) % 360
            
            return {
                'name': planet_name,
                'longitude': sidereal_longitude,
                'latitude': latitude,
                'distance': distance,
                'speed_longitude': speed_longitude,
                'speed_latitude': speed_latitude,
                'speed_distance': speed_distance,
                'tropical_longitude': tropical_longitude,
                'ayanamsa': ayanamsa,
                'is_retrograde': speed_longitude < 0
            }
            
        except Exception as e:
            print(f"Error calculating position for {planet_name}: {e}")
            return None
    
    def get_all_planet_positions(self, jd: float) -> Dict[str, Dict]:
        """
        Get positions of all planets
        
        Args:
            jd: Julian Day Number
            
        Returns:
            Dictionary with all planet positions
        """
        positions = {}
        
        for planet_name in self.PLANETS.keys():
            position = self.get_planet_position(planet_name, jd)
            if position:
                positions[planet_name] = position
        
        return positions
    
    def calculate_ascendant(self, jd: float, latitude: float, longitude: float) -> Dict:
        """
        Calculate accurate ascendant using Swiss Ephemeris
        
        Args:
            jd: Julian Day Number
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            
        Returns:
            Dictionary with ascendant data
        """
        try:
            # Calculate houses using Placidus system first to get ascendant
            cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P')  # 'P' for Placidus
            
            # Ascendant is the first element in ascmc array
            tropical_ascendant = ascmc[0]
            
            # Convert to sidereal
            ayanamsa = swe.get_ayanamsa_ut(jd)
            sidereal_ascendant = (tropical_ascendant - ayanamsa) % 360
            
            # Calculate local sidereal time
            lst = swe.sidtime(jd) + longitude / 15.0  # Convert longitude to hours
            lst = (lst % 24) * 15  # Convert back to degrees
            
            return {
                'longitude': sidereal_ascendant,
                'tropical_longitude': tropical_ascendant,
                'ayanamsa': ayanamsa,
                'local_sidereal_time': lst,
                'midheaven': (ascmc[1] - ayanamsa) % 360,  # MC in sidereal
                'vertex': (ascmc[3] - ayanamsa) % 360 if len(ascmc) > 3 else None
            }
            
        except Exception as e:
            print(f"Error calculating ascendant: {e}")
            return None
    
    def calculate_house_cusps(self, jd: float, latitude: float, longitude: float, 
                             house_system: str = 'P') -> List[float]:
        """
        Calculate house cusps using specified house system
        
        Args:
            jd: Julian Day Number
            latitude: Geographic latitude
            longitude: Geographic longitude  
            house_system: House system ('P'=Placidus, 'E'=Equal, 'W'=Whole, etc.)
            
        Returns:
            List of 12 house cusp longitudes in sidereal
        """
        try:
            cusps, ascmc = swe.houses_ex(jd, latitude, longitude, house_system.encode())
            
            # Get ayanamsa for sidereal conversion
            ayanamsa = swe.get_ayanamsa_ut(jd)
            
            # Convert tropical cusps to sidereal
            sidereal_cusps = []
            for cusp in cusps[1:]:  # Skip index 0, houses start from index 1
                sidereal_cusp = (cusp - ayanamsa) % 360
                sidereal_cusps.append(sidereal_cusp)
            
            return sidereal_cusps
            
        except Exception as e:
            print(f"Error calculating house cusps: {e}")
            return []
    
    def get_ayanamsa(self, jd: float) -> float:
        """
        Get ayanamsa value for given Julian Day
        
        Args:
            jd: Julian Day Number
            
        Returns:
            Ayanamsa value in degrees
        """
        try:
            return swe.get_ayanamsa_ut(jd)
        except Exception as e:
            print(f"Error getting ayanamsa: {e}")
            return 0.0
    
    def degrees_to_dms(self, degrees: float) -> Tuple[int, int, float]:
        """
        Convert decimal degrees to degrees, minutes, seconds
        
        Args:
            degrees: Decimal degrees
            
        Returns:
            Tuple of (degrees, minutes, seconds)
        """
        d = int(degrees)
        m = int((degrees - d) * 60)
        s = ((degrees - d) * 60 - m) * 60
        
        return (d, m, s)
    
    def track_planetary_motion(self, jd: float, planet: str, days_back: int = 365) -> Dict:
        """
        Track complete planetary motion history including all retrograde cycles
        
        Args:
            jd: Julian Day Number for birth time
            planet: Planet name
            days_back: Number of days to look back (default 365)
            
        Returns:
            Dictionary with complete motion history and total travel
        """
        try:
            # Get current position
            current_pos = self.get_planet_position(planet, jd)
            if not current_pos:
                return {}
                
            current_sign = int(current_pos['longitude'] / 30)
            current_degrees_in_sign = current_pos['longitude'] % 30
            
            # Collect daily positions going back in time
            positions = [(jd, current_degrees_in_sign, current_pos.get('is_retrograde', False))]
            entry_point = None
            entry_date = None
            found_entry = False
            
            # Collect all positions in current sign
            for i in range(1, days_back + 1):
                check_jd = jd - i
                pos = self.get_planet_position(planet, check_jd)
                
                if pos:
                    sign = int(pos['longitude'] / 30)
                    degrees_in_sign = pos['longitude'] % 30
                    
                    if sign == current_sign:
                        positions.append((check_jd, degrees_in_sign, pos.get('is_retrograde', False)))
                    elif not found_entry:
                        # Found the day before entry, find exact entry point
                        for hour in range(24):
                            hour_jd = check_jd + (hour / 24.0)
                            hour_pos = self.get_planet_position(planet, hour_jd)
                            if hour_pos:
                                hour_sign = int(hour_pos['longitude'] / 30)
                                if hour_sign == current_sign:
                                    entry_point = hour_pos['longitude'] % 30
                                    entry_date = hour_jd
                                    found_entry = True
                                    positions.append((hour_jd, entry_point, hour_pos.get('is_retrograde', False)))
                                    break
                        
                        if not found_entry:
                            next_pos = self.get_planet_position(planet, check_jd + 1)
                            if next_pos:
                                entry_point = next_pos['longitude'] % 30
                                entry_date = check_jd + 1
                                positions.append((entry_date, entry_point, next_pos.get('is_retrograde', False)))
                                found_entry = True
                        break
            
            # Sort positions by date (oldest to newest)
            positions.sort(key=lambda x: x[0])
            
            # Find all turning points (direction changes)
            turning_points = []
            motion_segments = []
            
            if len(positions) >= 2:
                # Always include the first position
                turning_points.append({
                    'date': positions[0][0],
                    'degrees': positions[0][1],
                    'type': 'entry'
                })
                
                # Find direction changes
                for i in range(1, len(positions) - 1):
                    prev_deg = positions[i-1][1]
                    curr_deg = positions[i][1]
                    next_deg = positions[i+1][1]
                    
                    # Check if this is a turning point
                    if (curr_deg > prev_deg and curr_deg > next_deg) or \
                       (curr_deg < prev_deg and curr_deg < next_deg):
                        turning_points.append({
                            'date': positions[i][0],
                            'degrees': positions[i][1],
                            'type': 'retrograde' if curr_deg > next_deg else 'direct'
                        })
                
                # Always include the current position
                turning_points.append({
                    'date': positions[-1][0],
                    'degrees': positions[-1][1],
                    'type': 'current'
                })
                
                # Create motion segments from turning points
                for i in range(1, len(turning_points)):
                    from_point = turning_points[i-1]
                    to_point = turning_points[i]
                    
                    motion_segments.append({
                        'from_degrees': from_point['degrees'],
                        'to_degrees': to_point['degrees'],
                        'from_date': from_point['date'],
                        'to_date': to_point['date'],
                        'type': 'retrograde' if to_point['degrees'] < from_point['degrees'] else 'forward',
                        'distance': abs(to_point['degrees'] - from_point['degrees'])
                    })
            
            # Calculate total travel distance
            total_travel = sum(segment['distance'] for segment in motion_segments)
            
            # Find max and min positions
            all_degrees = [pos[1] for pos in positions]
            max_forward = max(all_degrees) if all_degrees else current_degrees_in_sign
            min_position = min(all_degrees) if all_degrees else current_degrees_in_sign
            
            # Get the date when max was reached
            max_forward_date = jd
            for pos_jd, deg, _ in positions:
                if deg == max_forward:
                    max_forward_date = pos_jd
                    break
                
            # Convert Julian dates to readable format
            from datetime import datetime
            
            def jd_to_datetime(jd):
                """Convert Julian Day to datetime"""
                if jd is None:
                    return None
                a = int(jd + 0.5)
                if a < 2299161:
                    b = 0
                else:
                    alpha = int((a - 1867216.25) / 36524.25)
                    b = a + 1 + alpha - int(alpha / 4)
                
                c = b + 1524
                d = int((c - 122.1) / 365.25)
                e = int(365.25 * d)
                f = int((c - e) / 30.6001)
                
                day = c - e - int(30.6001 * f)
                month = f - 1 if f <= 13 else f - 13
                year = d - 4716 if f <= 13 else d - 4715
                
                # Extract time
                fraction = jd + 0.5 - int(jd + 0.5)
                hours = int(fraction * 24)
                minutes = int((fraction * 24 - hours) * 60)
                
                return datetime(year, month, day, hours, minutes)
            
            # Convert dates in turning points and segments
            for tp in turning_points:
                tp['date'] = jd_to_datetime(tp['date'])
                
            for seg in motion_segments:
                seg['from_date'] = jd_to_datetime(seg['from_date'])
                seg['to_date'] = jd_to_datetime(seg['to_date'])
                
            return {
                'entry_point': entry_point if entry_point is not None else min_position,
                'entry_date': jd_to_datetime(entry_date) if entry_date else None,
                'max_forward': max_forward,
                'max_forward_date': jd_to_datetime(max_forward_date) if max_forward_date else None,
                'current_position': current_degrees_in_sign,
                'is_retrograde': current_pos.get('is_retrograde', False),
                'total_travel': total_travel,
                'turning_points': turning_points,
                'motion_segments': motion_segments,
                'min_position': min_position
            }
            
        except Exception as e:
            print(f"Error tracking planetary motion for {planet}: {e}")
            return {}
    
    def calculate_retrograde_data(self, jd: float, days_back: int = 365) -> Dict:
        """
        Calculate motion data for all planets (retrograde and direct)
        
        Args:
            jd: Julian Day Number for birth time
            days_back: Number of days to look back
            
        Returns:
            Dictionary with motion data for each planet
        """
        motion_data_all = {}
        
        # All planets that need motion tracking (exclude Rahu, Ketu which have special rules)
        # Include Sun and Moon even though they don't retrograde, to track their motion
        planets_to_track = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        
        for planet in planets_to_track:
            motion_data = self.track_planetary_motion(jd, planet, days_back)
            if motion_data:
                motion_data_all[planet] = motion_data
                
        return motion_data_all
    
    def close(self):
        """Close Swiss Ephemeris and free resources"""
        swe.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.close()
        except:
            pass


# Convenience functions for common operations
def get_planet_positions_for_datetime(dt: datetime, ayanamsa: str = 'Lahiri') -> Dict[str, Dict]:
    """
    Get all planet positions for a given datetime
    
    Args:
        dt: datetime object (should be timezone-aware)
        ayanamsa: Ayanamsa system to use
        
    Returns:
        Dictionary of planet positions
    """
    se = SwissEphemeris(ayanamsa)
    jd = se.julian_day_from_datetime(dt)
    positions = se.get_all_planet_positions(jd)
    se.close()
    
    return positions


def get_ascendant_for_birth(dt: datetime, latitude: float, longitude: float, 
                           ayanamsa: str = 'Lahiri') -> Dict:
    """
    Get ascendant for birth details
    
    Args:
        dt: Birth datetime (timezone-aware)
        latitude: Birth latitude
        longitude: Birth longitude
        ayanamsa: Ayanamsa system
        
    Returns:
        Ascendant data dictionary
    """
    se = SwissEphemeris(ayanamsa)
    jd = se.julian_day_from_datetime(dt)
    ascendant = se.calculate_ascendant(jd, latitude, longitude)
    se.close()
    
    return ascendant