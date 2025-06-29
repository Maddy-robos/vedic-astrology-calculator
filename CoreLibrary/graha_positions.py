"""
Calculate planetary positions in rasis with degrees
"""

class GrahaPositions:
    def __init__(self, datetime, location, ayanamsa='lahiri'):
        self.datetime = datetime
        self.location = location
        self.ayanamsa = ayanamsa
    
    def calculate_positions(self):
        """Calculate positions of all grahas"""
        pass
    
    def get_graha_in_rasi(self, graha):
        """Get rasi and degree position of a graha"""
        pass
