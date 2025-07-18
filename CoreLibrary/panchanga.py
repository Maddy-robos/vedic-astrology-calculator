"""
Panchanga calculations - Five limbs of time
Vara (Weekday), Tithi (Lunar day), Nakshatra (Star), Yoga, Karana
"""

from typing import Dict, Tuple, Optional
from datetime import datetime
import math


class Panchanga:
    """Calculate the five limbs (angas) of Panchanga"""
    
    # Tithi names (30 lunar days)
    TITHI_NAMES = [
        'Shukla Pratipada', 'Shukla Dvitiya', 'Shukla Tritiya', 'Shukla Chaturthi', 'Shukla Panchami',
        'Shukla Shashti', 'Shukla Saptami', 'Shukla Ashtami', 'Shukla Navami', 'Shukla Dashami',
        'Shukla Ekadashi', 'Shukla Dvadashi', 'Shukla Trayodashi', 'Shukla Chaturdashi', 'Purnima',
        'Krishna Pratipada', 'Krishna Dvitiya', 'Krishna Tritiya', 'Krishna Chaturthi', 'Krishna Panchami',
        'Krishna Shashti', 'Krishna Saptami', 'Krishna Ashtami', 'Krishna Navami', 'Krishna Dashami',
        'Krishna Ekadashi', 'Krishna Dvadashi', 'Krishna Trayodashi', 'Krishna Chaturdashi', 'Amavasya'
    ]
    
    # Tithi lords (deities)
    TITHI_LORDS = [
        'Agni', 'Brahma', 'Gauri', 'Ganesha', 'Naga',
        'Kartikeya', 'Surya', 'Shiva', 'Durga', 'Yama',
        'Vishvedeva', 'Vishnu', 'Kamadeva', 'Shiva', 'Chandra',
        'Agni', 'Brahma', 'Gauri', 'Ganesha', 'Naga',
        'Kartikeya', 'Surya', 'Shiva', 'Durga', 'Yama',
        'Vishvedeva', 'Vishnu', 'Kamadeva', 'Shiva', 'Pitru'
    ]
    
    # Vara (weekday) names and lords
    VARA_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    VARA_LORDS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    # Yoga names (27 yogas)
    YOGA_NAMES = [
        'Vishkumbha', 'Preeti', 'Ayushman', 'Saubhagya', 'Shobhana',
        'Atiganda', 'Sukarman', 'Dhriti', 'Shoola', 'Ganda',
        'Vriddhi', 'Dhruva', 'Vyaghata', 'Harshana', 'Vajra',
        'Siddhi', 'Vyatipata', 'Variyan', 'Parigha', 'Shiva',
        'Siddha', 'Sadhya', 'Shubha', 'Shukla', 'Brahma',
        'Indra', 'Vaidhriti'
    ]
    
    # Karana names (11 karanas, repeated to make 60 half-tithis)
    KARANA_NAMES = [
        'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti',
        'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti',
        'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti',
        'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti',
        'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti',
        'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti',
        'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti',
        'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti',
        'Shakuni', 'Chatushpada', 'Naga', 'Kimstughna'
    ]
    
    # Fixed Karanas (last 4)
    FIXED_KARANAS = ['Shakuni', 'Chatushpada', 'Naga', 'Kimstughna']
    
    def __init__(self, sun_longitude: float, moon_longitude: float, birth_datetime: datetime, 
                 sunrise_time: Optional[datetime] = None):
        """
        Initialize Panchanga calculator
        
        Args:
            sun_longitude: Sun's longitude in degrees (0-360)
            moon_longitude: Moon's longitude in degrees (0-360)
            birth_datetime: Birth date and time
            sunrise_time: Optional sunrise time for vara calculation
        """
        self.sun_longitude = sun_longitude
        self.moon_longitude = moon_longitude
        self.birth_datetime = birth_datetime
        self.sunrise_time = sunrise_time or birth_datetime
        
    def calculate_tithi(self) -> Dict:
        """
        Calculate current Tithi and its lord
        
        Tithi = (Moon - Sun + 360) % 360 / 12
        Each tithi is 12 degrees of angular separation
        """
        # Calculate angular difference
        angular_diff = (self.moon_longitude - self.sun_longitude + 360) % 360
        
        # Calculate tithi number (1-30)
        tithi_number = int(angular_diff / 12) + 1
        if tithi_number > 30:
            tithi_number = 30
            
        # Calculate percentage completion
        tithi_remainder = angular_diff % 12
        percentage_complete = (tithi_remainder / 12) * 100
        
        # Get tithi index (0-29)
        tithi_index = tithi_number - 1
        
        # Determine paksha (fortnight)
        if tithi_number <= 15:
            paksha = 'Shukla' if tithi_number < 15 else 'Purnima'
        else:
            paksha = 'Krishna' if tithi_number < 30 else 'Amavasya'
            
        return {
            'number': tithi_number,
            'name': self.TITHI_NAMES[tithi_index],
            'lord': self.TITHI_LORDS[tithi_index],
            'paksha': paksha,
            'percentage_complete': round(percentage_complete, 2),
            'degrees_traversed': round(tithi_remainder, 2),
            'degrees_remaining': round(12 - tithi_remainder, 2)
        }
        
    def calculate_nakshatra(self) -> Dict:
        """
        Calculate current Nakshatra based on Moon's position
        
        Each nakshatra = 13°20' = 13.3333 degrees
        """
        # Nakshatra names and lords
        nakshatra_names = [
            'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
            'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
            'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
            'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
            'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
        ]
        
        nakshatra_lords = [
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
            'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus', 'Sun',
            'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
            'Jupiter', 'Saturn', 'Mercury'
        ]
        
        # Calculate nakshatra
        nakshatra_index = int(self.moon_longitude / 13.3333)
        if nakshatra_index >= 27:
            nakshatra_index = 26
            
        # Calculate pada (quarter)
        nakshatra_remainder = self.moon_longitude % 13.3333
        pada = int(nakshatra_remainder / 3.3333) + 1
        if pada > 4:
            pada = 4
            
        # Calculate percentage completion
        percentage_complete = (nakshatra_remainder / 13.3333) * 100
        
        return {
            'number': nakshatra_index + 1,
            'name': nakshatra_names[nakshatra_index],
            'lord': nakshatra_lords[nakshatra_index],
            'pada': pada,
            'percentage_complete': round(percentage_complete, 2),
            'degrees_traversed': round(nakshatra_remainder, 2),
            'degrees_remaining': round(13.3333 - nakshatra_remainder, 2)
        }
        
    def calculate_vara(self) -> Dict:
        """
        Calculate weekday (Vara) and its lord
        
        Based on sunrise time if available, otherwise birth time
        """
        # Get day of week (0 = Monday, 6 = Sunday in Python)
        weekday = self.sunrise_time.weekday()
        
        # Convert to traditional order (0 = Sunday, 6 = Saturday)
        vara_index = (weekday + 1) % 7
        
        return {
            'number': vara_index + 1,
            'name': self.VARA_NAMES[vara_index],
            'lord': self.VARA_LORDS[vara_index]
        }
        
    def calculate_yoga(self) -> Dict:
        """
        Calculate current Yoga
        
        Yoga = (Sun + Moon) % 360 / (360/27)
        Each yoga = 13°20' = 13.3333 degrees
        """
        # Calculate sum of longitudes
        longitude_sum = (self.sun_longitude + self.moon_longitude) % 360
        
        # Calculate yoga number (1-27)
        yoga_index = int(longitude_sum / 13.3333)
        if yoga_index >= 27:
            yoga_index = 26
            
        # Calculate percentage completion
        yoga_remainder = longitude_sum % 13.3333
        percentage_complete = (yoga_remainder / 13.3333) * 100
        
        # Determine if yoga is benefic or malefic
        malefic_yogas = ['Vishkumbha', 'Atiganda', 'Shoola', 'Ganda', 'Vyaghata', 
                        'Vajra', 'Vyatipata', 'Parigha', 'Vaidhriti']
        is_benefic = self.YOGA_NAMES[yoga_index] not in malefic_yogas
        
        return {
            'number': yoga_index + 1,
            'name': self.YOGA_NAMES[yoga_index],
            'benefic': is_benefic,
            'percentage_complete': round(percentage_complete, 2),
            'degrees_traversed': round(yoga_remainder, 2),
            'degrees_remaining': round(13.3333 - yoga_remainder, 2)
        }
        
    def calculate_karana(self) -> Dict:
        """
        Calculate current Karana (half of tithi)
        
        Each Karana = 6 degrees of Moon-Sun angular difference
        There are 60 Karanas in a lunar month (2 per tithi)
        """
        # Calculate angular difference
        angular_diff = (self.moon_longitude - self.sun_longitude + 360) % 360
        
        # Calculate karana number (1-60)
        karana_number = int(angular_diff / 6) + 1
        if karana_number > 60:
            karana_number = 60
            
        # Calculate percentage completion
        karana_remainder = angular_diff % 6
        percentage_complete = (karana_remainder / 6) * 100
        
        # Determine karana name
        if karana_number <= 56:
            # Repeating karanas (Chara Karanas)
            karana_index = (karana_number - 1) % 7
            karana_name = ['Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti'][karana_index]
            karana_type = 'Chara'
        else:
            # Fixed karanas (Sthira Karanas) - last 4
            karana_index = karana_number - 57
            karana_name = self.FIXED_KARANAS[karana_index]
            karana_type = 'Sthira'
            
        # Determine if benefic
        malefic_karanas = ['Vishti', 'Shakuni', 'Chatushpada', 'Naga']
        is_benefic = karana_name not in malefic_karanas
        
        return {
            'number': karana_number,
            'name': karana_name,
            'type': karana_type,
            'benefic': is_benefic,
            'percentage_complete': round(percentage_complete, 2),
            'degrees_traversed': round(karana_remainder, 2),
            'degrees_remaining': round(6 - karana_remainder, 2)
        }
        
    def get_complete_panchanga(self) -> Dict:
        """Get all five limbs of Panchanga"""
        return {
            'tithi': self.calculate_tithi(),
            'vara': self.calculate_vara(),
            'nakshatra': self.calculate_nakshatra(),
            'yoga': self.calculate_yoga(),
            'karana': self.calculate_karana()
        }
