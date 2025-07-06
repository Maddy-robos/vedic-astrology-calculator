"""
conversions.py - Astronomical and time conversion utilities for Jyotish calculations

This module provides functions for:
- Julian Day Number conversions
- Local time to UTC conversions
- Sidereal time calculations
- Coordinate transformations
- Ayanamsa calculations
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Optional, Union
import pytz
import json
import os


class Conversions:
    """Utility class for astronomical and time conversions"""
    
    # Ayanamsa values (in degrees) for different systems as of J2000.0
    AYANAMSA_VALUES = {
        'Lahiri': 23.85,  # Lahiri (Chitrapaksha)
        'Raman': 22.50,   # Raman
        'Krishnamurti': 23.77,  # KP System
        'Fagan_Bradley': 24.04  # Fagan-Bradley
    }
    
    # Rate of precession per year (approximate)
    PRECESSION_RATE = 50.29 / 3600  # arcseconds to degrees
    
    def __init__(self, ayanamsa: str = 'Lahiri'):
        """Initialize with specified ayanamsa system"""
        self.ayanamsa_system = ayanamsa
        self.load_ayanamsa_config()
        
    def load_ayanamsa_config(self):
        """Load ayanamsa configuration from JSON file if available"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'ayanamsa_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'ayanamsa_values' in config:
                    self.AYANAMSA_VALUES.update(config['ayanamsa_values'])
    
    def datetime_to_julian_day(self, dt: datetime) -> float:
        """
        Convert datetime to Julian Day Number
        
        Args:
            dt: datetime object (should be timezone-aware)
            
        Returns:
            Julian Day Number as float
        """
        # Convert to UTC if timezone-aware
        if dt.tzinfo is not None:
            dt_utc = dt.astimezone(timezone.utc)
        else:
            dt_utc = dt
            
        year = dt_utc.year
        month = dt_utc.month
        day = dt_utc.day
        hour = dt_utc.hour
        minute = dt_utc.minute
        second = dt_utc.second + dt_utc.microsecond / 1000000.0
        
        # Handle January and February
        if month <= 2:
            year -= 1
            month += 12
            
        # Calculate Julian Day Number
        a = math.floor(year / 100)
        b = 2 - a + math.floor(a / 4)
        
        jd = math.floor(365.25 * (year + 4716)) + \
             math.floor(30.6001 * (month + 1)) + \
             day + b - 1524.5
             
        # Add time fraction
        jd += (hour + minute / 60.0 + second / 3600.0) / 24.0
        
        return jd
    
    def julian_day_to_datetime(self, jd: float) -> datetime:
        """
        Convert Julian Day Number to datetime
        
        Args:
            jd: Julian Day Number
            
        Returns:
            datetime object in UTC
        """
        jd += 0.5
        z = math.floor(jd)
        f = jd - z
        
        if z < 2299161:
            a = z
        else:
            alpha = math.floor((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - math.floor(alpha / 4)
            
        b = a + 1524
        c = math.floor((b - 122.1) / 365.25)
        d = math.floor(365.25 * c)
        e = math.floor((b - d) / 30.6001)
        
        day = b - d - math.floor(30.6001 * e) + f
        
        if e < 14:
            month = e - 1
        else:
            month = e - 13
            
        if month > 2:
            year = c - 4716
        else:
            year = c - 4715
            
        # Extract time components
        day_int = int(day)
        day_frac = day - day_int
        
        hours = day_frac * 24
        hour = int(hours)
        
        minutes = (hours - hour) * 60
        minute = int(minutes)
        
        seconds = (minutes - minute) * 60
        second = int(seconds)
        microsecond = int((seconds - second) * 1000000)
        
        return datetime(year, month, day_int, hour, minute, second, 
                       microsecond, tzinfo=timezone.utc)
    
    def local_to_utc(self, local_time: datetime, timezone_str: str) -> datetime:
        """
        Convert local time to UTC
        
        Args:
            local_time: Local datetime
            timezone_str: Timezone string (e.g., 'Asia/Kolkata', 'UTC+05:30')
            
        Returns:
            UTC datetime
        """
        if local_time.tzinfo is None:
            # Parse timezone string to get offset
            tz_offset_hours = self._parse_timezone_string(timezone_str)
            
            # Create UTC offset timezone
            tz_offset = timedelta(hours=tz_offset_hours)
            tz = timezone(tz_offset)
            local_time = local_time.replace(tzinfo=tz)
            
        return local_time.astimezone(timezone.utc)
    
    def _parse_timezone_string(self, timezone_str: str) -> float:
        """Parse timezone string to hours offset."""
        timezone_str = timezone_str.strip()
        
        # Handle IANA timezone names
        if '/' in timezone_str:
            try:
                tz = pytz.timezone(timezone_str)
                # Use a reference date to get offset
                ref_dt = datetime(2000, 1, 1)
                localized = tz.localize(ref_dt)
                return localized.utcoffset().total_seconds() / 3600.0
            except:
                pass
        
        # Handle UTC offset format (+05:30, -08:00, etc.)
        if timezone_str.startswith(('+', '-')) or timezone_str.startswith('UTC'):
            # Remove 'UTC' prefix if present
            if timezone_str.startswith('UTC'):
                timezone_str = timezone_str[3:]
            
            # Parse +HH:MM or -HH:MM format
            if ':' in timezone_str:
                parts = timezone_str.split(':')
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours + (minutes / 60.0) * (1 if hours >= 0 else -1)
            else:
                # Handle +HH or -HH format
                return float(timezone_str)
        
        # Default to UTC
        return 0.0
    
    def utc_to_local(self, utc_time: datetime, timezone_str: str) -> datetime:
        """
        Convert UTC time to local time
        
        Args:
            utc_time: UTC datetime
            timezone_str: Timezone string
            
        Returns:
            Local datetime
        """
        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(tzinfo=timezone.utc)
            
        tz = pytz.timezone(timezone_str)
        return utc_time.astimezone(tz)
    
    def calculate_sidereal_time(self, jd: float, longitude: float) -> float:
        """
        Calculate Local Sidereal Time
        
        Args:
            jd: Julian Day Number
            longitude: Geographic longitude in degrees (positive East)
            
        Returns:
            Local Sidereal Time in degrees
        """
        # Calculate centuries from J2000.0
        t = (jd - 2451545.0) / 36525.0
        
        # Greenwich Mean Sidereal Time at 0h UT
        gmst = 280.46061837 + \
               360.98564736629 * (jd - 2451545.0) + \
               0.000387933 * t * t - \
               t * t * t / 38710000.0
               
        # Normalize to 0-360 degrees
        gmst = gmst % 360.0
        if gmst < 0:
            gmst += 360.0
            
        # Local Sidereal Time
        lst = gmst + longitude
        
        # Normalize
        lst = lst % 360.0
        if lst < 0:
            lst += 360.0
            
        return lst
    
    def get_ayanamsa(self, jd: float) -> float:
        """
        Calculate ayanamsa value for given Julian Day
        
        Args:
            jd: Julian Day Number
            
        Returns:
            Ayanamsa value in degrees
        """
        # Years from J2000.0
        years_from_2000 = (jd - 2451545.0) / 365.25
        
        # Base ayanamsa value
        base_ayanamsa = self.AYANAMSA_VALUES.get(self.ayanamsa_system, 23.85)
        
        # Apply precession
        ayanamsa = base_ayanamsa + (years_from_2000 * self.PRECESSION_RATE)
        
        return ayanamsa
    
    def tropical_to_sidereal(self, longitude: float, jd: float) -> float:
        """
        Convert tropical longitude to sidereal
        
        Args:
            longitude: Tropical longitude in degrees
            jd: Julian Day Number
            
        Returns:
            Sidereal longitude in degrees
        """
        ayanamsa = self.get_ayanamsa(jd)
        sidereal = longitude - ayanamsa
        
        # Normalize to 0-360
        sidereal = sidereal % 360.0
        if sidereal < 0:
            sidereal += 360.0
            
        return sidereal
    
    def sidereal_to_tropical(self, longitude: float, jd: float) -> float:
        """
        Convert sidereal longitude to tropical
        
        Args:
            longitude: Sidereal longitude in degrees
            jd: Julian Day Number
            
        Returns:
            Tropical longitude in degrees
        """
        ayanamsa = self.get_ayanamsa(jd)
        tropical = longitude + ayanamsa
        
        # Normalize to 0-360
        tropical = tropical % 360.0
        if tropical < 0:
            tropical += 360.0
            
        return tropical
    
    def degrees_to_dms(self, degrees: float) -> Dict[str, int]:
        """
        Convert decimal degrees to degrees, minutes, seconds
        
        Args:
            degrees: Decimal degrees
            
        Returns:
            Dictionary with 'degrees', 'minutes', 'seconds'
        """
        sign = 1 if degrees >= 0 else -1
        degrees = abs(degrees)
        
        d = int(degrees)
        m = int((degrees - d) * 60)
        s = int(((degrees - d) * 60 - m) * 60)
        
        return {
            'degrees': d * sign,
            'minutes': m,
            'seconds': s
        }
    
    def dms_to_degrees(self, degrees: int, minutes: int, seconds: int) -> float:
        """
        Convert degrees, minutes, seconds to decimal degrees
        
        Args:
            degrees: Degrees
            minutes: Minutes
            seconds: Seconds
            
        Returns:
            Decimal degrees
        """
        sign = 1 if degrees >= 0 else -1
        return sign * (abs(degrees) + minutes / 60.0 + seconds / 3600.0)
    
    def rasi_to_degrees(self, rasi: str, degree_in_rasi: float) -> float:
        """
        Convert rasi position to absolute degrees
        
        Args:
            rasi: Rasi name (e.g., 'Aries', 'Taurus')
            degree_in_rasi: Degrees within the rasi (0-30)
            
        Returns:
            Absolute degrees (0-360)
        """
        rasi_order = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        if rasi not in rasi_order:
            raise ValueError(f"Invalid rasi: {rasi}")
            
        rasi_index = rasi_order.index(rasi)
        return rasi_index * 30 + degree_in_rasi
    
    def degrees_to_rasi(self, degrees: float) -> Dict[str, Union[str, float]]:
        """
        Convert absolute degrees to rasi and degrees within rasi
        
        Args:
            degrees: Absolute degrees (0-360)
            
        Returns:
            Dictionary with 'rasi' and 'degrees'
        """
        rasi_order = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        # Normalize degrees
        degrees = degrees % 360.0
        if degrees < 0:
            degrees += 360.0
            
        rasi_index = int(degrees / 30)
        degrees_in_rasi = degrees % 30
        
        return {
            'rasi': rasi_order[rasi_index],
            'degrees': degrees_in_rasi
        }
    
    def ecliptic_to_equatorial(self, longitude: float, latitude: float, 
                             obliquity: float = 23.44) -> Tuple[float, float]:
        """
        Convert ecliptic coordinates to equatorial
        
        Args:
            longitude: Ecliptic longitude in degrees
            latitude: Ecliptic latitude in degrees
            obliquity: Obliquity of ecliptic in degrees
            
        Returns:
            Tuple of (right_ascension, declination) in degrees
        """
        # Convert to radians
        lon_rad = math.radians(longitude)
        lat_rad = math.radians(latitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate right ascension
        ra = math.atan2(
            math.sin(lon_rad) * math.cos(obl_rad) - 
            math.tan(lat_rad) * math.sin(obl_rad),
            math.cos(lon_rad)
        )
        
        # Calculate declination
        dec = math.asin(
            math.sin(lat_rad) * math.cos(obl_rad) + 
            math.cos(lat_rad) * math.sin(obl_rad) * math.sin(lon_rad)
        )
        
        # Convert to degrees and normalize
        ra_deg = math.degrees(ra) % 360.0
        if ra_deg < 0:
            ra_deg += 360.0
            
        dec_deg = math.degrees(dec)
        
        return ra_deg, dec_deg
    
    def equatorial_to_ecliptic(self, ra: float, dec: float, 
                             obliquity: float = 23.44) -> Tuple[float, float]:
        """
        Convert equatorial coordinates to ecliptic
        
        Args:
            ra: Right ascension in degrees
            dec: Declination in degrees
            obliquity: Obliquity of ecliptic in degrees
            
        Returns:
            Tuple of (longitude, latitude) in degrees
        """
        # Convert to radians
        ra_rad = math.radians(ra)
        dec_rad = math.radians(dec)
        obl_rad = math.radians(obliquity)
        
        # Calculate longitude
        lon = math.atan2(
            math.sin(ra_rad) * math.cos(obl_rad) + 
            math.tan(dec_rad) * math.sin(obl_rad),
            math.cos(ra_rad)
        )
        
        # Calculate latitude
        lat = math.asin(
            math.sin(dec_rad) * math.cos(obl_rad) - 
            math.cos(dec_rad) * math.sin(obl_rad) * math.sin(ra_rad)
        )
        
        # Convert to degrees and normalize
        lon_deg = math.degrees(lon) % 360.0
        if lon_deg < 0:
            lon_deg += 360.0
            
        lat_deg = math.degrees(lat)
        
        return lon_deg, lat_deg
