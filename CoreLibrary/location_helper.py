"""
location_helper.py - Location and timezone helper functions

This module provides:
- City/location database for latitude/longitude lookup
- Timezone conversion utilities
- Common location search functionality
"""

from typing import Dict, List, Optional, Tuple
import re


class LocationHelper:
    """Helper class for location and timezone operations"""
    
    # Common cities database with coordinates and timezones
    CITIES_DATABASE = {
        # India
        'mumbai': {'lat': 19.0760, 'lon': 72.8777, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'delhi': {'lat': 28.6139, 'lon': 77.2090, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'new delhi': {'lat': 28.6139, 'lon': 77.2090, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bangalore': {'lat': 12.9716, 'lon': 77.5946, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bengaluru': {'lat': 12.9716, 'lon': 77.5946, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'chennai': {'lat': 13.0827, 'lon': 80.2707, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'kolkata': {'lat': 22.5726, 'lon': 88.3639, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'hyderabad': {'lat': 17.3850, 'lon': 78.4867, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'pune': {'lat': 18.5204, 'lon': 73.8567, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'ahmedabad': {'lat': 23.0225, 'lon': 72.5714, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jaipur': {'lat': 26.9124, 'lon': 75.7873, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'lucknow': {'lat': 26.8467, 'lon': 80.9462, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'kanpur': {'lat': 26.4499, 'lon': 80.3319, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'nagpur': {'lat': 21.1458, 'lon': 79.0882, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'indore': {'lat': 22.7196, 'lon': 75.8577, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bhopal': {'lat': 23.2599, 'lon': 77.4126, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'visakhapatnam': {'lat': 17.6868, 'lon': 83.2185, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'patna': {'lat': 25.5941, 'lon': 85.1376, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'vadodara': {'lat': 22.3072, 'lon': 73.1812, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'ghaziabad': {'lat': 28.6692, 'lon': 77.4538, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'ludhiana': {'lat': 30.9010, 'lon': 75.8573, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'agra': {'lat': 27.1767, 'lon': 78.0081, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'nashik': {'lat': 19.9975, 'lon': 73.7898, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'faridabad': {'lat': 28.4089, 'lon': 77.3178, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'meerut': {'lat': 28.9845, 'lon': 77.7064, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'rajkot': {'lat': 22.3039, 'lon': 70.8022, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'kalyan': {'lat': 19.2403, 'lon': 73.1305, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'vasai': {'lat': 19.4912, 'lon': 72.8054, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'varanasi': {'lat': 25.3176, 'lon': 82.9739, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'srinagar': {'lat': 34.0837, 'lon': 74.7973, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'aurangabad': {'lat': 19.8762, 'lon': 75.3433, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'dhanbad': {'lat': 23.7957, 'lon': 86.4304, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'amritsar': {'lat': 31.6340, 'lon': 74.8723, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'navi mumbai': {'lat': 19.0330, 'lon': 73.0297, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'allahabad': {'lat': 25.4358, 'lon': 81.8463, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'prayagraj': {'lat': 25.4358, 'lon': 81.8463, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'ranchi': {'lat': 23.3441, 'lon': 85.3096, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'haora': {'lat': 22.5958, 'lon': 88.2636, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'coimbatore': {'lat': 11.0168, 'lon': 76.9558, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jabalpur': {'lat': 23.1815, 'lon': 79.9864, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'gwalior': {'lat': 26.2183, 'lon': 78.1828, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'vijayawada': {'lat': 16.5062, 'lon': 80.6480, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jodhpur': {'lat': 26.2389, 'lon': 73.0243, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'madurai': {'lat': 9.9252, 'lon': 78.1198, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'raipur': {'lat': 21.2514, 'lon': 81.6296, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'kota': {'lat': 25.2138, 'lon': 75.8648, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'chandigarh': {'lat': 30.7333, 'lon': 76.7794, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'guwahati': {'lat': 26.1445, 'lon': 91.7362, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'solapur': {'lat': 17.6599, 'lon': 75.9064, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'hubli': {'lat': 15.3647, 'lon': 75.1240, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bareilly': {'lat': 28.3670, 'lon': 79.4304, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'moradabad': {'lat': 28.8386, 'lon': 78.7733, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'mysore': {'lat': 12.2958, 'lon': 76.6394, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'mysuru': {'lat': 12.2958, 'lon': 76.6394, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'tirupati': {'lat': 13.6288, 'lon': 79.4192, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'gurgaon': {'lat': 28.4595, 'lon': 77.0266, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'gurugram': {'lat': 28.4595, 'lon': 77.0266, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'aligarh': {'lat': 27.8974, 'lon': 78.0880, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jalandhar': {'lat': 31.3260, 'lon': 75.5762, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'tiruchirappalli': {'lat': 10.7905, 'lon': 78.7047, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bhubaneswar': {'lat': 20.2961, 'lon': 85.8245, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'salem': {'lat': 11.6643, 'lon': 78.1460, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'mira bhayandar': {'lat': 19.2952, 'lon': 72.8544, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'warangal': {'lat': 17.9689, 'lon': 79.5941, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'thiruvananthapuram': {'lat': 8.5241, 'lon': 76.9366, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'guntur': {'lat': 16.3067, 'lon': 80.4365, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bhiwandi': {'lat': 19.3002, 'lon': 73.0682, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'saharanpur': {'lat': 29.9680, 'lon': 77.5552, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'gorakhpur': {'lat': 26.7606, 'lon': 83.3732, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bikaner': {'lat': 28.0229, 'lon': 73.3119, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'amravati': {'lat': 20.9374, 'lon': 77.7796, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'noida': {'lat': 28.5355, 'lon': 77.3910, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jamshedpur': {'lat': 22.8046, 'lon': 86.2029, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bhilai nagar': {'lat': 21.1938, 'lon': 81.3509, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'cuttack': {'lat': 20.4625, 'lon': 85.8828, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'firozabad': {'lat': 27.1592, 'lon': 78.3957, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'kochi': {'lat': 9.9312, 'lon': 76.2673, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'nellore': {'lat': 14.4426, 'lon': 79.9865, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'bhavnagar': {'lat': 21.7645, 'lon': 72.1519, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'dehradun': {'lat': 30.3165, 'lon': 78.0322, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'durgapur': {'lat': 23.5204, 'lon': 87.3119, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'asansol': {'lat': 23.6739, 'lon': 86.9524, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'rourkela': {'lat': 22.2604, 'lon': 84.8536, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'nanded': {'lat': 19.1383, 'lon': 77.3210, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'kolhapur': {'lat': 16.7050, 'lon': 74.2433, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'ajmer': {'lat': 26.4499, 'lon': 74.6399, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'akola': {'lat': 20.7002, 'lon': 77.0082, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'gulbarga': {'lat': 17.3297, 'lon': 76.8343, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jamnagar': {'lat': 22.4707, 'lon': 70.0577, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'ujjain': {'lat': 23.1765, 'lon': 75.7885, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'loni': {'lat': 28.7333, 'lon': 77.2833, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'siliguri': {'lat': 26.7271, 'lon': 88.3953, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jhansi': {'lat': 25.4484, 'lon': 78.5685, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'ulhasnagar': {'lat': 19.2215, 'lon': 73.1645, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jammu': {'lat': 32.7266, 'lon': 74.8570, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'sangli miraj kupwad': {'lat': 16.8667, 'lon': 74.5667, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'mangalore': {'lat': 12.9141, 'lon': 74.8560, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'erode': {'lat': 11.3410, 'lon': 77.7172, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'belgaum': {'lat': 15.8497, 'lon': 74.4977, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'ambattur': {'lat': 13.1143, 'lon': 80.1548, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'tirunelveli': {'lat': 8.7139, 'lon': 77.7567, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'malegaon': {'lat': 20.5579, 'lon': 74.5287, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'gaya': {'lat': 24.7914, 'lon': 85.0002, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'jalgaon': {'lat': 21.0077, 'lon': 75.5626, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'udaipur': {'lat': 24.5854, 'lon': 73.7125, 'tz': 'Asia/Kolkata', 'country': 'India'},
        'maheshtala': {'lat': 22.5082, 'lon': 88.2533, 'tz': 'Asia/Kolkata', 'country': 'India'},
        
        # USA
        'new york': {'lat': 40.7128, 'lon': -74.0060, 'tz': 'America/New_York', 'country': 'USA'},
        'los angeles': {'lat': 34.0522, 'lon': -118.2437, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'chicago': {'lat': 41.8781, 'lon': -87.6298, 'tz': 'America/Chicago', 'country': 'USA'},
        'houston': {'lat': 29.7604, 'lon': -95.3698, 'tz': 'America/Chicago', 'country': 'USA'},
        'philadelphia': {'lat': 39.9526, 'lon': -75.1652, 'tz': 'America/New_York', 'country': 'USA'},
        'phoenix': {'lat': 33.4484, 'lon': -112.0740, 'tz': 'America/Phoenix', 'country': 'USA'},
        'san antonio': {'lat': 29.4241, 'lon': -98.4936, 'tz': 'America/Chicago', 'country': 'USA'},
        'san diego': {'lat': 32.7157, 'lon': -117.1611, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'dallas': {'lat': 32.7767, 'lon': -96.7970, 'tz': 'America/Chicago', 'country': 'USA'},
        'san jose': {'lat': 37.3382, 'lon': -121.8863, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'austin': {'lat': 30.2672, 'lon': -97.7431, 'tz': 'America/Chicago', 'country': 'USA'},
        'fort worth': {'lat': 32.7555, 'lon': -97.3308, 'tz': 'America/Chicago', 'country': 'USA'},
        'columbus': {'lat': 39.9612, 'lon': -82.9988, 'tz': 'America/New_York', 'country': 'USA'},
        'charlotte': {'lat': 35.2271, 'lon': -80.8431, 'tz': 'America/New_York', 'country': 'USA'},
        'seattle': {'lat': 47.6062, 'lon': -122.3321, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'denver': {'lat': 39.7392, 'lon': -104.9903, 'tz': 'America/Denver', 'country': 'USA'},
        'washington': {'lat': 38.9072, 'lon': -77.0369, 'tz': 'America/New_York', 'country': 'USA'},
        'boston': {'lat': 42.3601, 'lon': -71.0589, 'tz': 'America/New_York', 'country': 'USA'},
        'el paso': {'lat': 31.7619, 'lon': -106.4850, 'tz': 'America/Denver', 'country': 'USA'},
        'detroit': {'lat': 42.3314, 'lon': -83.0458, 'tz': 'America/Detroit', 'country': 'USA'},
        'nashville': {'lat': 36.1627, 'lon': -86.7816, 'tz': 'America/Chicago', 'country': 'USA'},
        'portland': {'lat': 45.5152, 'lon': -122.6784, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'memphis': {'lat': 35.1495, 'lon': -90.0490, 'tz': 'America/Chicago', 'country': 'USA'},
        'oklahoma city': {'lat': 35.4676, 'lon': -97.5164, 'tz': 'America/Chicago', 'country': 'USA'},
        'las vegas': {'lat': 36.1699, 'lon': -115.1398, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'louisville': {'lat': 38.2527, 'lon': -85.7585, 'tz': 'America/New_York', 'country': 'USA'},
        'baltimore': {'lat': 39.2904, 'lon': -76.6122, 'tz': 'America/New_York', 'country': 'USA'},
        'milwaukee': {'lat': 43.0389, 'lon': -87.9065, 'tz': 'America/Chicago', 'country': 'USA'},
        'albuquerque': {'lat': 35.0844, 'lon': -106.6504, 'tz': 'America/Denver', 'country': 'USA'},
        'tucson': {'lat': 32.2226, 'lon': -110.9747, 'tz': 'America/Phoenix', 'country': 'USA'},
        'fresno': {'lat': 36.7378, 'lon': -119.7871, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'sacramento': {'lat': 38.5816, 'lon': -121.4944, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'long beach': {'lat': 33.7701, 'lon': -118.1937, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'kansas city': {'lat': 39.0997, 'lon': -94.5786, 'tz': 'America/Chicago', 'country': 'USA'},
        'mesa': {'lat': 33.4152, 'lon': -111.8315, 'tz': 'America/Phoenix', 'country': 'USA'},
        'atlanta': {'lat': 33.7490, 'lon': -84.3880, 'tz': 'America/New_York', 'country': 'USA'},
        'colorado springs': {'lat': 38.8339, 'lon': -104.8214, 'tz': 'America/Denver', 'country': 'USA'},
        'raleigh': {'lat': 35.7796, 'lon': -78.6382, 'tz': 'America/New_York', 'country': 'USA'},
        'omaha': {'lat': 41.2565, 'lon': -95.9345, 'tz': 'America/Chicago', 'country': 'USA'},
        'miami': {'lat': 25.7617, 'lon': -80.1918, 'tz': 'America/New_York', 'country': 'USA'},
        'oakland': {'lat': 37.8044, 'lon': -122.2711, 'tz': 'America/Los_Angeles', 'country': 'USA'},
        'minneapolis': {'lat': 44.9778, 'lon': -93.2650, 'tz': 'America/Chicago', 'country': 'USA'},
        'tulsa': {'lat': 36.1540, 'lon': -95.9928, 'tz': 'America/Chicago', 'country': 'USA'},
        'cleveland': {'lat': 41.4993, 'lon': -81.6944, 'tz': 'America/New_York', 'country': 'USA'},
        'wichita': {'lat': 37.6872, 'lon': -97.3301, 'tz': 'America/Chicago', 'country': 'USA'},
        'arlington': {'lat': 32.7357, 'lon': -97.1081, 'tz': 'America/Chicago', 'country': 'USA'},
        
        # UK
        'london': {'lat': 51.5074, 'lon': -0.1278, 'tz': 'Europe/London', 'country': 'UK'},
        'birmingham': {'lat': 52.4862, 'lon': -1.8904, 'tz': 'Europe/London', 'country': 'UK'},
        'leeds': {'lat': 53.8008, 'lon': -1.5491, 'tz': 'Europe/London', 'country': 'UK'},
        'glasgow': {'lat': 55.8642, 'lon': -4.2518, 'tz': 'Europe/London', 'country': 'UK'},
        'sheffield': {'lat': 53.3811, 'lon': -1.4701, 'tz': 'Europe/London', 'country': 'UK'},
        'bradford': {'lat': 53.7960, 'lon': -1.7594, 'tz': 'Europe/London', 'country': 'UK'},
        'edinburgh': {'lat': 55.9533, 'lon': -3.1883, 'tz': 'Europe/London', 'country': 'UK'},
        'liverpool': {'lat': 53.4084, 'lon': -2.9916, 'tz': 'Europe/London', 'country': 'UK'},
        'manchester': {'lat': 53.4808, 'lon': -2.2426, 'tz': 'Europe/London', 'country': 'UK'},
        
        # Canada
        'toronto': {'lat': 43.6532, 'lon': -79.3832, 'tz': 'America/Toronto', 'country': 'Canada'},
        'montreal': {'lat': 45.5017, 'lon': -73.5673, 'tz': 'America/Montreal', 'country': 'Canada'},
        'vancouver': {'lat': 49.2827, 'lon': -123.1207, 'tz': 'America/Vancouver', 'country': 'Canada'},
        'calgary': {'lat': 51.0447, 'lon': -114.0719, 'tz': 'America/Edmonton', 'country': 'Canada'},
        'edmonton': {'lat': 53.5461, 'lon': -113.4938, 'tz': 'America/Edmonton', 'country': 'Canada'},
        'ottawa': {'lat': 45.4215, 'lon': -75.6972, 'tz': 'America/Toronto', 'country': 'Canada'},
        'winnipeg': {'lat': 49.8951, 'lon': -97.1384, 'tz': 'America/Winnipeg', 'country': 'Canada'},
        'quebec city': {'lat': 46.8139, 'lon': -71.2080, 'tz': 'America/Montreal', 'country': 'Canada'},
        'hamilton': {'lat': 43.2557, 'lon': -79.8711, 'tz': 'America/Toronto', 'country': 'Canada'},
        'kitchener': {'lat': 43.4516, 'lon': -80.4925, 'tz': 'America/Toronto', 'country': 'Canada'},
        
        # Australia
        'sydney': {'lat': -33.8688, 'lon': 151.2093, 'tz': 'Australia/Sydney', 'country': 'Australia'},
        'melbourne': {'lat': -37.8136, 'lon': 144.9631, 'tz': 'Australia/Melbourne', 'country': 'Australia'},
        'brisbane': {'lat': -27.4698, 'lon': 153.0251, 'tz': 'Australia/Brisbane', 'country': 'Australia'},
        'perth': {'lat': -31.9505, 'lon': 115.8605, 'tz': 'Australia/Perth', 'country': 'Australia'},
        'adelaide': {'lat': -34.9285, 'lon': 138.6007, 'tz': 'Australia/Adelaide', 'country': 'Australia'},
        'gold coast': {'lat': -28.0167, 'lon': 153.4000, 'tz': 'Australia/Brisbane', 'country': 'Australia'},
        'newcastle': {'lat': -32.9283, 'lon': 151.7817, 'tz': 'Australia/Sydney', 'country': 'Australia'},
        'canberra': {'lat': -35.2809, 'lon': 149.1300, 'tz': 'Australia/Sydney', 'country': 'Australia'},
        'sunshine coast': {'lat': -26.6500, 'lon': 153.0667, 'tz': 'Australia/Brisbane', 'country': 'Australia'},
        'wollongong': {'lat': -34.4278, 'lon': 150.8931, 'tz': 'Australia/Sydney', 'country': 'Australia'},
        
        # Other major cities
        'singapore': {'lat': 1.3521, 'lon': 103.8198, 'tz': 'Asia/Singapore', 'country': 'Singapore'},
        'hong kong': {'lat': 22.3193, 'lon': 114.1694, 'tz': 'Asia/Hong_Kong', 'country': 'Hong Kong'},
        'dubai': {'lat': 25.2048, 'lon': 55.2708, 'tz': 'Asia/Dubai', 'country': 'UAE'},
        'tokyo': {'lat': 35.6762, 'lon': 139.6503, 'tz': 'Asia/Tokyo', 'country': 'Japan'},
        'beijing': {'lat': 39.9042, 'lon': 116.4074, 'tz': 'Asia/Shanghai', 'country': 'China'},
        'shanghai': {'lat': 31.2304, 'lon': 121.4737, 'tz': 'Asia/Shanghai', 'country': 'China'},
        'seoul': {'lat': 37.5665, 'lon': 126.9780, 'tz': 'Asia/Seoul', 'country': 'South Korea'},
        'kuala lumpur': {'lat': 3.1390, 'lon': 101.6869, 'tz': 'Asia/Kuala_Lumpur', 'country': 'Malaysia'},
        'bangkok': {'lat': 13.7563, 'lon': 100.5018, 'tz': 'Asia/Bangkok', 'country': 'Thailand'},
        'jakarta': {'lat': -6.2088, 'lon': 106.8456, 'tz': 'Asia/Jakarta', 'country': 'Indonesia'},
        'manila': {'lat': 14.5995, 'lon': 120.9842, 'tz': 'Asia/Manila', 'country': 'Philippines'},
        'karachi': {'lat': 24.8607, 'lon': 67.0011, 'tz': 'Asia/Karachi', 'country': 'Pakistan'},
        'lahore': {'lat': 31.5804, 'lon': 74.3587, 'tz': 'Asia/Karachi', 'country': 'Pakistan'},
        'islamabad': {'lat': 33.6844, 'lon': 73.0479, 'tz': 'Asia/Karachi', 'country': 'Pakistan'},
        'dhaka': {'lat': 23.8103, 'lon': 90.4125, 'tz': 'Asia/Dhaka', 'country': 'Bangladesh'},
        'colombo': {'lat': 6.9271, 'lon': 79.8612, 'tz': 'Asia/Colombo', 'country': 'Sri Lanka'},
        'kathmandu': {'lat': 27.7172, 'lon': 85.3240, 'tz': 'Asia/Kathmandu', 'country': 'Nepal'},
        'cairo': {'lat': 30.0444, 'lon': 31.2357, 'tz': 'Africa/Cairo', 'country': 'Egypt'},
        'riyadh': {'lat': 24.7136, 'lon': 46.6753, 'tz': 'Asia/Riyadh', 'country': 'Saudi Arabia'},
        'tel aviv': {'lat': 32.0853, 'lon': 34.7818, 'tz': 'Asia/Jerusalem', 'country': 'Israel'},
        'tehran': {'lat': 35.6892, 'lon': 51.3890, 'tz': 'Asia/Tehran', 'country': 'Iran'},
        'istanbul': {'lat': 41.0082, 'lon': 28.9784, 'tz': 'Europe/Istanbul', 'country': 'Turkey'},
        'moscow': {'lat': 55.7558, 'lon': 37.6176, 'tz': 'Europe/Moscow', 'country': 'Russia'},
        'paris': {'lat': 48.8566, 'lon': 2.3522, 'tz': 'Europe/Paris', 'country': 'France'},
        'berlin': {'lat': 52.5200, 'lon': 13.4050, 'tz': 'Europe/Berlin', 'country': 'Germany'},
        'rome': {'lat': 41.9028, 'lon': 12.4964, 'tz': 'Europe/Rome', 'country': 'Italy'},
        'madrid': {'lat': 40.4168, 'lon': -3.7038, 'tz': 'Europe/Madrid', 'country': 'Spain'},
        'amsterdam': {'lat': 52.3676, 'lon': 4.9041, 'tz': 'Europe/Amsterdam', 'country': 'Netherlands'},
        'brussels': {'lat': 50.8503, 'lon': 4.3517, 'tz': 'Europe/Brussels', 'country': 'Belgium'},
        'zurich': {'lat': 47.3769, 'lon': 8.5417, 'tz': 'Europe/Zurich', 'country': 'Switzerland'},
        'stockholm': {'lat': 59.3293, 'lon': 18.0686, 'tz': 'Europe/Stockholm', 'country': 'Sweden'},
        'oslo': {'lat': 59.9139, 'lon': 10.7522, 'tz': 'Europe/Oslo', 'country': 'Norway'},
        'copenhagen': {'lat': 55.6761, 'lon': 12.5683, 'tz': 'Europe/Copenhagen', 'country': 'Denmark'},
        'helsinki': {'lat': 60.1699, 'lon': 24.9384, 'tz': 'Europe/Helsinki', 'country': 'Finland'},
        'vienna': {'lat': 48.2082, 'lon': 16.3738, 'tz': 'Europe/Vienna', 'country': 'Austria'},
        'budapest': {'lat': 47.4979, 'lon': 19.0402, 'tz': 'Europe/Budapest', 'country': 'Hungary'},
        'prague': {'lat': 50.0755, 'lon': 14.4378, 'tz': 'Europe/Prague', 'country': 'Czech Republic'},
        'warsaw': {'lat': 52.2297, 'lon': 21.0122, 'tz': 'Europe/Warsaw', 'country': 'Poland'},
        'bucharest': {'lat': 44.4268, 'lon': 26.1025, 'tz': 'Europe/Bucharest', 'country': 'Romania'},
        'athens': {'lat': 37.9838, 'lon': 23.7275, 'tz': 'Europe/Athens', 'country': 'Greece'},
        'lisbon': {'lat': 38.7223, 'lon': -9.1393, 'tz': 'Europe/Lisbon', 'country': 'Portugal'},
        'dublin': {'lat': 53.3498, 'lon': -6.2603, 'tz': 'Europe/Dublin', 'country': 'Ireland'},
        'mexico city': {'lat': 19.4326, 'lon': -99.1332, 'tz': 'America/Mexico_City', 'country': 'Mexico'},
        'sao paulo': {'lat': -23.5558, 'lon': -46.6396, 'tz': 'America/Sao_Paulo', 'country': 'Brazil'},
        'rio de janeiro': {'lat': -22.9068, 'lon': -43.1729, 'tz': 'America/Sao_Paulo', 'country': 'Brazil'},
        'buenos aires': {'lat': -34.6118, 'lon': -58.3960, 'tz': 'America/Argentina/Buenos_Aires', 'country': 'Argentina'},
        'lima': {'lat': -12.0464, 'lon': -77.0428, 'tz': 'America/Lima', 'country': 'Peru'},
        'bogota': {'lat': 4.7110, 'lon': -74.0721, 'tz': 'America/Bogota', 'country': 'Colombia'},
        'santiago': {'lat': -33.4489, 'lon': -70.6693, 'tz': 'America/Santiago', 'country': 'Chile'},
        'lagos': {'lat': 6.5244, 'lon': 3.3792, 'tz': 'Africa/Lagos', 'country': 'Nigeria'},
        'johannesburg': {'lat': -26.2041, 'lon': 28.0473, 'tz': 'Africa/Johannesburg', 'country': 'South Africa'},
        'cape town': {'lat': -33.9249, 'lon': 18.4241, 'tz': 'Africa/Johannesburg', 'country': 'South Africa'},
        'nairobi': {'lat': -1.2921, 'lon': 36.8219, 'tz': 'Africa/Nairobi', 'country': 'Kenya'},
        'addis ababa': {'lat': 9.1450, 'lon': 40.4897, 'tz': 'Africa/Addis_Ababa', 'country': 'Ethiopia'},
        'casablanca': {'lat': 33.5731, 'lon': -7.5898, 'tz': 'Africa/Casablanca', 'country': 'Morocco'},
        'tunis': {'lat': 36.8065, 'lon': 10.1815, 'tz': 'Africa/Tunis', 'country': 'Tunisia'},
        'algiers': {'lat': 36.7373, 'lon': 3.0860, 'tz': 'Africa/Algiers', 'country': 'Algeria'}
    }
    
    # Timezone examples for user reference
    TIMEZONE_EXAMPLES = {
        'UTC': 'UTC (Universal Time)',
        'UTC+05:30': 'UTC+05:30 (India Standard Time)',
        'UTC+08:00': 'UTC+08:00 (China, Singapore, Malaysia)',
        'UTC+09:00': 'UTC+09:00 (Japan, South Korea)',
        'UTC+10:00': 'UTC+10:00 (Australia East)',
        'UTC+11:00': 'UTC+11:00 (Australia East DST)',
        'UTC-05:00': 'UTC-05:00 (US Eastern)',
        'UTC-06:00': 'UTC-06:00 (US Central)',
        'UTC-07:00': 'UTC-07:00 (US Mountain)',
        'UTC-08:00': 'UTC-08:00 (US Pacific)',
        'UTC+01:00': 'UTC+01:00 (Central Europe)',
        'UTC+02:00': 'UTC+02:00 (Eastern Europe)',
        'UTC+03:00': 'UTC+03:00 (Russia, Middle East)',
        'UTC+04:00': 'UTC+04:00 (Gulf States)',
        'UTC+05:00': 'UTC+05:00 (Pakistan)',
        'UTC+06:00': 'UTC+06:00 (Bangladesh)',
        'UTC+07:00': 'UTC+07:00 (Thailand, Indonesia)',
        'UTC-03:00': 'UTC-03:00 (Argentina, Brazil)',
        'UTC-04:00': 'UTC-04:00 (Chile, Venezuela)',
        'UTC+12:00': 'UTC+12:00 (New Zealand)',
        'Asia/Kolkata': 'Asia/Kolkata (India)',
        'Asia/Dubai': 'Asia/Dubai (UAE)',
        'Asia/Tokyo': 'Asia/Tokyo (Japan)',
        'Asia/Shanghai': 'Asia/Shanghai (China)',
        'Asia/Bangkok': 'Asia/Bangkok (Thailand)',
        'Asia/Singapore': 'Asia/Singapore (Singapore)',
        'Asia/Karachi': 'Asia/Karachi (Pakistan)',
        'Asia/Dhaka': 'Asia/Dhaka (Bangladesh)',
        'Asia/Kathmandu': 'Asia/Kathmandu (Nepal)',
        'Asia/Seoul': 'Asia/Seoul (South Korea)',
        'America/New_York': 'America/New_York (US Eastern)',
        'America/Chicago': 'America/Chicago (US Central)',
        'America/Denver': 'America/Denver (US Mountain)',
        'America/Los_Angeles': 'America/Los_Angeles (US Pacific)',
        'America/Toronto': 'America/Toronto (Canada Eastern)',
        'America/Vancouver': 'America/Vancouver (Canada Pacific)',
        'Europe/London': 'Europe/London (UK)',
        'Europe/Paris': 'Europe/Paris (France)',
        'Europe/Berlin': 'Europe/Berlin (Germany)',
        'Europe/Rome': 'Europe/Rome (Italy)',
        'Europe/Moscow': 'Europe/Moscow (Russia)',
        'Australia/Sydney': 'Australia/Sydney (Australia East)',
        'Australia/Melbourne': 'Australia/Melbourne (Australia Southeast)',
        'Australia/Perth': 'Australia/Perth (Australia West)',
        'Africa/Cairo': 'Africa/Cairo (Egypt)',
        'Africa/Johannesburg': 'Africa/Johannesburg (South Africa)'
    }
    
    @classmethod
    def search_location(cls, query: str) -> List[Dict]:
        """
        Search for locations matching the query
        
        Args:
            query: Search query (city name)
            
        Returns:
            List of matching location dictionaries
        """
        query = query.lower().strip()
        matches = []
        
        for city_name, city_data in cls.CITIES_DATABASE.items():
            if query in city_name.lower():
                match = {
                    'name': city_name.title(),
                    'latitude': city_data['lat'],
                    'longitude': city_data['lon'],
                    'timezone': city_data['tz'],
                    'country': city_data['country']
                }
                matches.append(match)
        
        # Sort by exact match first, then by length
        matches.sort(key=lambda x: (not x['name'].lower().startswith(query), len(x['name'])))
        
        return matches
    
    @classmethod
    def get_location_by_name(cls, city_name: str) -> Optional[Dict]:
        """
        Get location data for a specific city
        
        Args:
            city_name: Name of the city
            
        Returns:
            Location dictionary or None if not found
        """
        city_name = city_name.lower().strip()
        
        if city_name in cls.CITIES_DATABASE:
            city_data = cls.CITIES_DATABASE[city_name]
            return {
                'name': city_name.title(),
                'latitude': city_data['lat'],
                'longitude': city_data['lon'],
                'timezone': city_data['tz'],
                'country': city_data['country']
            }
        
        return None
    
    @classmethod
    def parse_timezone_offset(cls, timezone_str: str) -> Optional[str]:
        """
        Parse timezone string and convert to standard format
        
        Args:
            timezone_str: Timezone string (e.g., "UTC+5:30", "+05:30", "Asia/Kolkata")
            
        Returns:
            Standardized timezone string or None if invalid
        """
        timezone_str = timezone_str.strip()
        
        # Check if it's already a valid timezone name
        if timezone_str in cls.TIMEZONE_EXAMPLES or '/' in timezone_str:
            return timezone_str
        
        # Parse UTC offset formats
        utc_pattern = re.compile(r'^UTC?([+-])(\d{1,2}):?(\d{2})?$', re.IGNORECASE)
        offset_pattern = re.compile(r'^([+-])(\d{1,2}):?(\d{2})?$')
        
        match = utc_pattern.match(timezone_str) or offset_pattern.match(timezone_str)
        
        if match:
            sign = match.group(1)
            hours = int(match.group(2))
            minutes = int(match.group(3)) if match.group(3) else 0
            
            # Validate ranges
            if hours > 14 or minutes >= 60:
                return None
                
            return f"UTC{sign}{hours:02d}:{minutes:02d}"
        
        return None
    
    @classmethod
    def get_popular_cities(cls, country: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get list of popular cities
        
        Args:
            country: Filter by country (optional)
            limit: Maximum number of cities to return
            
        Returns:
            List of city dictionaries
        """
        cities = []
        
        for city_name, city_data in cls.CITIES_DATABASE.items():
            if country is None or city_data['country'].lower() == country.lower():
                city = {
                    'name': city_name.title(),
                    'latitude': city_data['lat'],
                    'longitude': city_data['lon'],
                    'timezone': city_data['tz'],
                    'country': city_data['country']
                }
                cities.append(city)
        
        return cities[:limit]
    
    @classmethod
    def get_timezone_examples(cls) -> Dict[str, str]:
        """Get timezone examples for user reference"""
        return cls.TIMEZONE_EXAMPLES.copy()
    
    @classmethod
    def display_timezone_help(cls):
        """Display timezone input help"""
        print("\nTimezone Input Examples:")
        print("-" * 40)
        print("Format 1 - UTC Offset:")
        print("  UTC+05:30  (India)")
        print("  UTC-05:00  (US Eastern)")
        print("  UTC+08:00  (China/Singapore)")
        print("  +05:30     (Short format)")
        print("  -08:00     (Short format)")
        print()
        print("Format 2 - IANA Timezone Names:")
        print("  Asia/Kolkata       (India)")
        print("  America/New_York   (US Eastern)")
        print("  Europe/London      (UK)")
        print("  Asia/Tokyo         (Japan)")
        print("  Australia/Sydney   (Australia)")
        print()
        print("Common Offsets:")
        print("  UTC+05:30 = India, Sri Lanka")
        print("  UTC+08:00 = China, Singapore, Malaysia")
        print("  UTC+09:00 = Japan, South Korea")
        print("  UTC-05:00 = US Eastern Time")
        print("  UTC-08:00 = US Pacific Time")
        print("  UTC+00:00 = UK, GMT")
        print()