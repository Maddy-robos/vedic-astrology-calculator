"""
chart_visualization.py - North Indian Chart Visualization

This module provides SVG-based visualization for Vedic astrology charts,
specifically the North Indian diamond-style chart format.
"""

import math
import json
import os
from typing import Dict, List, Tuple, Optional
import xml.etree.ElementTree as ET


class NorthIndianChart:
    """
    Creates North Indian style diamond chart visualization.
    
    The chart has fixed houses in diamond pattern:
    - Houses are numbered 1-12 anti-clockwise
    - House 1 (Lagna) is always at the top
    - Signs rotate based on the ascendant
    """
    
    def __init__(self, width: int = 400, height: int = 400, config_path: str = None):
        """
        Initialize the North Indian Chart.
        
        Args:
            width: Chart width in pixels
            height: Chart height in pixels
            config_path: Path to configuration file (optional)
        """
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.config_path = config_path
        
        # Load configuration
        self.config = self._load_config()
        
        # Define the 12 house positions in the diamond
        # Anti-clockwise from top center
        self._calculate_house_centers()
    
    def _load_config(self) -> Dict:
        """Load chart positions configuration from JSON file."""
        if self.config_path and os.path.exists(self.config_path):
            config_file = self.config_path
        else:
            # Try to find config in project structure
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(current_dir)
            config_file = os.path.join(project_root, 'Config', 'chart_positions.json')
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load chart config: {e}")
        
        # Return default config if file not found
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default chart configuration."""
        return {
            "house_centers": {
                "1": {"x": 0.5, "y": 0.2, "type": "square"},
                "2": {"x": 0.35, "y": 0.35, "type": "triangle"},
                "3": {"x": 0.15, "y": 0.65, "type": "triangle"},
                "4": {"x": 0.2, "y": 1.0, "type": "square"},
                "5": {"x": 0.15, "y": 1.35, "type": "triangle"},
                "6": {"x": 0.35, "y": 1.65, "type": "triangle"},
                "7": {"x": 1.0, "y": 1.8, "type": "square"},
                "8": {"x": 1.65, "y": 1.65, "type": "triangle"},
                "9": {"x": 1.85, "y": 1.35, "type": "triangle"},
                "10": {"x": 1.8, "y": 1.0, "type": "square"},
                "11": {"x": 1.85, "y": 0.65, "type": "triangle"},
                "12": {"x": 1.65, "y": 0.35, "type": "triangle"}
            },
            "house_areas": {
                "1": {"width": 0.6, "height": 0.4, "max_cols": 3, "max_rows": 3},
                "2": {"width": 0.3, "height": 0.3, "max_cols": 2, "max_rows": 2},
                "3": {"width": 0.25, "height": 0.4, "max_cols": 2, "max_rows": 3},
                "4": {"width": 0.4, "height": 0.6, "max_cols": 2, "max_rows": 4},
                "5": {"width": 0.25, "height": 0.4, "max_cols": 2, "max_rows": 3},
                "6": {"width": 0.3, "height": 0.3, "max_cols": 2, "max_rows": 2},
                "7": {"width": 0.6, "height": 0.4, "max_cols": 3, "max_rows": 3},
                "8": {"width": 0.3, "height": 0.3, "max_cols": 2, "max_rows": 2},
                "9": {"width": 0.25, "height": 0.4, "max_cols": 2, "max_rows": 3},
                "10": {"width": 0.4, "height": 0.6, "max_cols": 2, "max_rows": 4},
                "11": {"width": 0.25, "height": 0.4, "max_cols": 2, "max_rows": 3},
                "12": {"width": 0.3, "height": 0.3, "max_cols": 2, "max_rows": 2}
            }
        }
    
    def _calculate_house_centers(self):
        """Calculate the center points for each house from configuration."""
        cx = self.center_x
        cy = self.center_y
        
        # Load positions from config
        config_centers = self.config.get('house_centers', {})
        config_areas = self.config.get('house_areas', {})
        
        # Convert config ratios to actual pixel positions
        self.house_centers = {}
        self.house_areas = {}
        
        for house_num in range(1, 13):
            house_str = str(house_num)
            
            if house_str in config_centers:
                center_config = config_centers[house_str]
                # Convert ratios to actual positions
                self.house_centers[house_num] = (
                    cx * center_config['x'],
                    cy * center_config['y']
                )
            
            if house_str in config_areas:
                area_config = config_areas[house_str]
                # Convert ratios to actual sizes
                self.house_areas[house_num] = {
                    'width': cx * area_config['width'],
                    'height': cy * area_config['height'],
                    'max_cols': area_config['max_cols'],
                    'max_rows': area_config['max_rows']
                }
    
    def update_positions(self, new_positions: Dict) -> None:
        """Update house positions and areas dynamically."""
        # Update the config
        if 'house_centers' in new_positions:
            self.config['house_centers'].update(new_positions['house_centers'])
        if 'house_areas' in new_positions:
            self.config['house_areas'].update(new_positions['house_areas'])
        
        # Recalculate positions
        self._calculate_house_centers()
    
    def save_config(self, filepath: str = None) -> bool:
        """Save current configuration to file."""
        if not filepath:
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(current_dir)
            filepath = os.path.join(project_root, 'Config', 'chart_positions.json')
        
        try:
            # Update timestamp
            self.config['last_modified'] = '2025-07-06'
            
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _create_svg_root(self) -> ET.Element:
        """Create the root SVG element."""
        svg = ET.Element('svg', {
            'width': str(self.width),
            'height': str(self.height),
            'viewBox': f'0 0 {self.width} {self.height}',
            'xmlns': 'http://www.w3.org/2000/svg'
        })
        return svg
    
    def _draw_chart_structure(self, svg: ET.Element):
        """Draw the basic diamond structure of the chart."""
        # Outer square
        ET.SubElement(svg, 'rect', {
            'x': '0',
            'y': '0',
            'width': str(self.width),
            'height': str(self.height),
            'fill': 'white',
            'stroke': 'black',
            'stroke-width': '2'
        })
        
        # Main diamond (connects midpoints of outer square)
        diamond_points = f"{self.center_x},0 {self.width},{self.center_y} " \
                        f"{self.center_x},{self.height} 0,{self.center_y}"
        ET.SubElement(svg, 'polygon', {
            'points': diamond_points,
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': '2'
        })
        
        # Diagonal lines (corner to corner)
        # Top-left to bottom-right
        ET.SubElement(svg, 'line', {
            'x1': '0', 'y1': '0',
            'x2': str(self.width), 'y2': str(self.height),
            'stroke': 'black',
            'stroke-width': '2'
        })
        
        # Top-right to bottom-left
        ET.SubElement(svg, 'line', {
            'x1': str(self.width), 'y1': '0',
            'x2': '0', 'y2': str(self.height),
            'stroke': 'black',
            'stroke-width': '2'
        })
    
    def _add_house_numbers(self, svg: ET.Element, lagna_house: int = 1):
        """Add house numbers to the chart."""
        for house_num, (x, y) in self.house_centers.items():
            # Position house number at corner of each area
            # Offset to corner so it doesn't interfere with planets
            area_info = self.house_areas[house_num]
            
            # Position at top-left corner of each house area
            number_x = x - (area_info['width'] / 2) + 15
            number_y = y - (area_info['height'] / 2) + 15
            
            # Add house number
            text = ET.SubElement(svg, 'text', {
                'x': str(number_x),
                'y': str(number_y),
                'text-anchor': 'middle',
                'font-family': 'Arial',
                'font-size': '9',
                'fill': 'gray',
                'font-weight': 'normal'
            })
            text.text = str(house_num)
            
            # Mark Lagna house with special indicator
            if house_num == 1:
                lagna_indicator = ET.SubElement(svg, 'circle', {
                    'cx': str(number_x + 12),
                    'cy': str(number_y - 3),
                    'r': '3',
                    'fill': 'red',
                    'opacity': '0.7'
                })
    
    def _add_sign_numbers(self, svg: ET.Element, lagna_sign: str):
        """Add zodiac sign numbers based on Lagna."""
        # Map sign names to numbers
        sign_to_num = {
            'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
            'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
            'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
        }
        
        lagna_num = sign_to_num.get(lagna_sign, 1)
        
        # Calculate sign for each house
        for house_num, (x, y) in self.house_centers.items():
            # Sign number = (Lagna number + house number - 2) % 12 + 1
            sign_num = ((lagna_num + house_num - 2) % 12) + 1
            
            # Position sign number at bottom-right corner of each area
            area_info = self.house_areas[house_num]
            sign_x = x + (area_info['width'] / 2) - 15
            sign_y = y + (area_info['height'] / 2) - 5
            
            # Add sign number
            sign_text = ET.SubElement(svg, 'text', {
                'x': str(sign_x),
                'y': str(sign_y),
                'text-anchor': 'middle',
                'font-family': 'Arial',
                'font-size': '11',
                'fill': 'darkgreen',
                'font-weight': 'bold'
            })
            sign_text.text = str(sign_num)
    
    def _add_planets(self, svg: ET.Element, house_planets: Dict[int, List[str]]):
        """Add planets to their respective houses with proper layout."""
        # Planet abbreviations
        planet_abbr = {
            'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me',
            'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa',
            'Rahu': 'Ra', 'Ketu': 'Ke'
        }
        
        for house_num, planets in house_planets.items():
            if planets and house_num in self.house_centers:
                center_x, center_y = self.house_centers[house_num]
                area_info = self.house_areas[house_num]
                
                # Get abbreviated planet names
                abbrev_planets = [planet_abbr.get(p, p[:2]) for p in planets]
                
                # Calculate layout for multiple planets
                max_cols = area_info['max_cols']
                max_rows = area_info['max_rows']
                
                # Calculate grid layout
                total_planets = len(abbrev_planets)
                if total_planets <= max_cols:
                    # Single row
                    cols = total_planets
                    rows = 1
                else:
                    # Multiple rows
                    cols = max_cols
                    rows = min(max_rows, (total_planets + max_cols - 1) // max_cols)
                
                # Calculate spacing
                col_spacing = area_info['width'] / (cols + 1) if cols > 1 else 0
                row_spacing = area_info['height'] / (rows + 1) if rows > 1 else 0
                
                # Starting positions
                start_x = center_x - (area_info['width'] / 2)
                start_y = center_y - (area_info['height'] / 2)
                
                # Place planets
                for i, planet in enumerate(abbrev_planets):
                    if i >= max_cols * max_rows:  # Don't exceed max capacity
                        break
                        
                    row = i // cols
                    col = i % cols
                    
                    # Calculate position within the area
                    if cols == 1:
                        x = center_x
                    else:
                        x = start_x + col_spacing + (col * col_spacing)
                    
                    if rows == 1:
                        y = center_y
                    else:
                        y = start_y + row_spacing + (row * row_spacing)
                    
                    # Add planet text
                    planet_text = ET.SubElement(svg, 'text', {
                        'x': str(x),
                        'y': str(y),
                        'text-anchor': 'middle',
                        'font-family': 'Arial',
                        'font-size': '10',
                        'fill': 'darkblue',
                        'font-weight': 'bold'
                    })
                    planet_text.text = planet
    
    def generate_chart(self, 
                      lagna_sign: str,
                      house_planets: Dict[int, List[str]],
                      chart_title: Optional[str] = None) -> str:
        """
        Generate the complete North Indian chart as SVG string.
        
        Args:
            lagna_sign: The ascendant sign name
            house_planets: Dictionary mapping house numbers to list of planets
            chart_title: Optional title for the chart
            
        Returns:
            SVG string of the chart
        """
        # Create SVG root
        svg = self._create_svg_root()
        
        # Add title if provided
        if chart_title:
            title = ET.SubElement(svg, 'text', {
                'x': str(self.center_x),
                'y': '20',
                'text-anchor': 'middle',
                'font-family': 'Arial',
                'font-size': '16',
                'font-weight': 'bold',
                'fill': 'black'
            })
            title.text = chart_title
        
        # Draw chart structure
        self._draw_chart_structure(svg)
        
        # Add house numbers
        self._add_house_numbers(svg)
        
        # Add sign numbers based on Lagna
        self._add_sign_numbers(svg, lagna_sign)
        
        # Add planets
        self._add_planets(svg, house_planets)
        
        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')
    
    def save_chart(self, 
                   filename: str,
                   lagna_sign: str,
                   house_planets: Dict[int, List[str]],
                   chart_title: Optional[str] = None):
        """
        Save the chart to an SVG file.
        
        Args:
            filename: Output filename
            lagna_sign: The ascendant sign name
            house_planets: Dictionary mapping house numbers to list of planets
            chart_title: Optional title for the chart
        """
        svg_string = self.generate_chart(lagna_sign, house_planets, chart_title)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_string)


def create_north_indian_chart(chart_data: dict, 
                            width: int = 400, 
                            height: int = 400) -> str:
    """
    Convenience function to create a North Indian chart from chart data.
    
    Args:
        chart_data: Dictionary containing chart information
        width: Chart width in pixels
        height: Chart height in pixels
        
    Returns:
        SVG string of the chart
    """
    # Extract lagna sign
    lagna_sign = chart_data.get('ascendant', {}).get('rasi', 'Aries')
    
    # Extract house placements
    house_planets = {}
    bhava_analysis = chart_data.get('bhava_analysis', {})
    graha_placements = bhava_analysis.get('graha_placements', {})
    
    for house_str, planets in graha_placements.items():
        house_num = int(house_str)
        house_planets[house_num] = planets
    
    # Create chart
    chart = NorthIndianChart(width, height)
    return chart.generate_chart(lagna_sign, house_planets)


# Example usage
if __name__ == "__main__":
    # Example data
    test_house_planets = {
        1: ['Sun', 'Mercury'],
        2: ['Venus'],
        3: [],
        4: ['Mars'],
        5: [],
        6: [],
        7: ['Moon'],
        8: [],
        9: ['Jupiter'],
        10: ['Saturn'],
        11: [],
        12: ['Rahu', 'Ketu']
    }
    
    # Create chart
    chart = NorthIndianChart()
    svg_string = chart.generate_chart(
        lagna_sign='Aries',
        house_planets=test_house_planets,
        chart_title='Example Chart'
    )
    
    # Save to file
    chart.save_chart(
        'example_north_indian_chart.svg',
        lagna_sign='Aries',
        house_planets=test_house_planets,
        chart_title='Example Chart'
    )
    
    print("Chart generated successfully!")