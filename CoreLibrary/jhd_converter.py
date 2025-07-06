"""
JHD Converter Module for Vedic Astrology Research Platform

This module provides functionality to convert between CSV birth data and JHD (Jyotish Hierarchical Data) format,
which is used by Jagannatha Hora and other Vedic astrology software.

JHD File Format:
- Month (1-12)
- Day (1-31)
- Year (4 digits)
- Time (UTC fractional day, 24-hour format)
- LMT Offset (Local Mean Time offset in hours)
- Longitude (decimal degrees)
- Latitude (decimal degrees)
- Elevation (meters, usually 0)
- Timezone Offset (hours from UTC)
- Daylight Saving Time Offset (hours)
- Daylight Saving Time Flag (0 or 1)
- Ayanamsa (usually 105 for Lahiri)
- Place Name
- Country
- Birth Type (1 for normal birth)
- Atmospheric Pressure (usually 1013.25 mb)
- Temperature (usually 20.0°C)
- Chart Type (usually 2)
"""

import pandas as pd
import os
import re
import json
import zipfile
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Union
import pytz
import math
from io import StringIO, BytesIO


class JHDConverter:
    """
    Converter class for handling JHD (Jyotish Hierarchical Data) format conversions.
    """

    # Standard JHD parameters
    DEFAULT_ELEVATION = 0.0
    DEFAULT_PRESSURE = 1013.25
    DEFAULT_TEMPERATURE = 20.0
    DEFAULT_AYANAMSA = 105  # Lahiri ayanamsa
    DEFAULT_BIRTH_TYPE = 1
    DEFAULT_CHART_TYPE = 2
    DEFAULT_DST_FLAG = 0

    def __init__(self, geocode_cache: Optional[Dict] = None):
        """
        Initialize the JHD converter.
        
        Args:
            geocode_cache: Optional dictionary of location data for coordinate lookup
        """
        self.geocode_cache = geocode_cache or {}
        self.errors = []
        self.warnings = []

    def csv_to_jhd(self, csv_data: Union[str, pd.DataFrame], output_dir: str = "jhd_output") -> Dict:
        """
        Convert CSV birth data to JHD files.
        
        Args:
            csv_data: CSV file path or pandas DataFrame
            output_dir: Directory to save JHD files
            
        Returns:
            Dictionary with conversion results and statistics
        """
        # Read CSV data
        if isinstance(csv_data, str):
            df = pd.read_csv(csv_data)
        else:
            df = csv_data.copy()

        # Validate CSV format
        validation_result = self._validate_csv_format(df)
        if not validation_result['valid']:
            return {'success': False, 'errors': validation_result['errors']}

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        results = {
            'success': True,
            'total_records': len(df),
            'files_created': 0,
            'errors': [],
            'warnings': [],
            'output_directory': output_dir
        }

        # Process each row
        for idx, row in df.iterrows():
            try:
                # Extract birth data
                birth_data = self._extract_birth_data_from_row(row)
                
                # Generate JHD content
                jhd_content = self._create_jhd_content(birth_data)
                
                # Create filename
                filename = self._generate_jhd_filename(birth_data)
                filepath = os.path.join(output_dir, filename)
                
                # Write JHD file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(jhd_content)
                
                results['files_created'] += 1
                
            except Exception as e:
                error_msg = f"Row {idx + 1} ({row.get('name', 'Unknown')}): {str(e)}"
                results['errors'].append(error_msg)

        results['success'] = len(results['errors']) == 0
        return results

    def jhd_to_csv(self, jhd_source: Union[str, List[str]], output_csv: str = "jhd_to_csv_output.csv") -> Dict:
        """
        Convert JHD files to CSV format.
        
        Args:
            jhd_source: JHD file path, directory path, or list of JHD file paths
            output_csv: Output CSV file path
            
        Returns:
            Dictionary with conversion results
        """
        # Collect JHD files
        jhd_files = self._collect_jhd_files(jhd_source)
        
        if not jhd_files:
            return {'success': False, 'errors': ['No JHD files found']}

        csv_data = []
        results = {
            'success': True,
            'total_files': len(jhd_files),
            'records_converted': 0,
            'errors': [],
            'warnings': [],
            'output_file': output_csv
        }

        # Process each JHD file
        for jhd_file in jhd_files:
            try:
                # Parse JHD file
                birth_data = self._parse_jhd_file(jhd_file)
                
                # Convert to CSV row format
                csv_row = self._convert_jhd_to_csv_row(birth_data, jhd_file)
                csv_data.append(csv_row)
                
                results['records_converted'] += 1
                
            except Exception as e:
                error_msg = f"File {jhd_file}: {str(e)}"
                results['errors'].append(error_msg)

        # Create DataFrame and save CSV
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(output_csv, index=False)
        else:
            results['success'] = False
            results['errors'].append("No valid JHD files could be processed")

        return results

    def create_jhd_zip(self, csv_data: Union[str, pd.DataFrame], zip_filename: str = "jhd_charts.zip") -> Dict:
        """
        Create a ZIP file containing JHD files converted from CSV data.
        
        Args:
            csv_data: CSV file path or pandas DataFrame
            zip_filename: Output ZIP file name
            
        Returns:
            Dictionary with creation results
        """
        # Read CSV data
        if isinstance(csv_data, str):
            df = pd.read_csv(csv_data)
        else:
            df = csv_data.copy()

        # Validate CSV format
        validation_result = self._validate_csv_format(df)
        if not validation_result['valid']:
            return {'success': False, 'errors': validation_result['errors']}

        results = {
            'success': True,
            'total_records': len(df),
            'files_created': 0,
            'errors': [],
            'warnings': [],
            'zip_filename': zip_filename
        }

        # Create ZIP file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for idx, row in df.iterrows():
                try:
                    # Extract birth data
                    birth_data = self._extract_birth_data_from_row(row)
                    
                    # Generate JHD content
                    jhd_content = self._create_jhd_content(birth_data)
                    
                    # Create filename
                    filename = self._generate_jhd_filename(birth_data)
                    
                    # Add to ZIP
                    zipf.writestr(filename, jhd_content)
                    results['files_created'] += 1
                    
                except Exception as e:
                    error_msg = f"Row {idx + 1} ({row.get('name', 'Unknown')}): {str(e)}"
                    results['errors'].append(error_msg)

        results['success'] = len(results['errors']) == 0
        return results

    def _validate_csv_format(self, df: pd.DataFrame) -> Dict:
        """Validate CSV format for JHD conversion."""
        required_columns = ['name', 'date', 'time', 'latitude', 'longitude', 'timezone']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'valid': False,
                'errors': [f"Missing required columns: {', '.join(missing_columns)}"]
            }
        
        return {'valid': True, 'errors': []}

    def _extract_birth_data_from_row(self, row: pd.Series) -> Dict:
        """Extract birth data from a CSV row."""
        # Parse date and time
        try:
            birth_date = pd.to_datetime(row['date']).date()
            birth_time = pd.to_datetime(row['time'], format='%H:%M:%S').time()
            birth_datetime = datetime.combine(birth_date, birth_time)
        except Exception as e:
            raise ValueError(f"Invalid date/time format: {e}")

        # Parse coordinates
        try:
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])
        except Exception as e:
            raise ValueError(f"Invalid coordinates: {e}")

        # Parse timezone
        timezone_str = str(row['timezone'])
        
        # Extract location info
        place_name = str(row.get('place_name', row.get('name', 'Unknown')))
        country = str(row.get('country', 'Unknown'))

        return {
            'name': str(row['name']),
            'birth_datetime': birth_datetime,
            'latitude': latitude,
            'longitude': longitude,
            'timezone_str': timezone_str,
            'place_name': place_name,
            'country': country
        }

    def _create_jhd_content(self, birth_data: Dict) -> str:
        """Create JHD file content from birth data."""
        dt = birth_data['birth_datetime']
        
        # Parse timezone
        tz_offset = self._parse_timezone(birth_data['timezone_str'])
        
        # Calculate UTC time
        utc_dt = dt - timedelta(hours=tz_offset)
        
        # Convert to fractional day (UTC)
        fractional_day = (utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0) / 24.0
        
        # Calculate Local Mean Time offset
        lmt_offset = birth_data['longitude'] / 15.0
        
        # Clean place names
        place_name = re.sub(r'[^\w\s-]', '', birth_data['place_name'])[:50]
        country = re.sub(r'[^\w\s-]', '', birth_data['country'])[:50]
        
        # Create JHD content
        jhd_content = f"""{dt.month}
{dt.day}
{dt.year}
{fractional_day:.15f}
{lmt_offset:.6f}
{birth_data['longitude']:.6f}
{birth_data['latitude']:.6f}
{self.DEFAULT_ELEVATION:.6f}
{tz_offset:.6f}
{self.DEFAULT_DST_FLAG:.6f}
{self.DEFAULT_DST_FLAG}
{self.DEFAULT_AYANAMSA}
{place_name}
{country}
{self.DEFAULT_BIRTH_TYPE}
{self.DEFAULT_PRESSURE:.6f}
{self.DEFAULT_TEMPERATURE:.6f}
{self.DEFAULT_CHART_TYPE}"""
        
        return jhd_content

    def _generate_jhd_filename(self, birth_data: Dict) -> str:
        """Generate JHD filename from birth data."""
        # Clean name for filename
        name = re.sub(r'[^\w\s-]', '', birth_data['name'])
        name = re.sub(r'\s+', '_', name)
        name = name.strip('_')[:30]  # Limit length
        
        # Format date
        date_str = birth_data['birth_datetime'].strftime('%Y%m%d')
        
        return f"{name}_{date_str}.jhd"

    def _parse_timezone(self, timezone_str: str) -> float:
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

    def _collect_jhd_files(self, jhd_source: Union[str, List[str]]) -> List[str]:
        """Collect JHD files from various sources."""
        jhd_files = []
        
        if isinstance(jhd_source, list):
            # List of file paths
            jhd_files = [f for f in jhd_source if f.endswith('.jhd')]
        elif isinstance(jhd_source, str):
            if os.path.isfile(jhd_source):
                # Single file
                if jhd_source.endswith('.jhd'):
                    jhd_files = [jhd_source]
                elif jhd_source.endswith('.zip'):
                    # ZIP file
                    jhd_files = self._extract_jhd_from_zip(jhd_source)
            elif os.path.isdir(jhd_source):
                # Directory
                for root, dirs, files in os.walk(jhd_source):
                    for file in files:
                        if file.endswith('.jhd'):
                            jhd_files.append(os.path.join(root, file))
        
        return jhd_files

    def _extract_jhd_from_zip(self, zip_path: str) -> List[str]:
        """Extract JHD files from ZIP and return temporary file paths."""
        import tempfile
        
        jhd_files = []
        temp_dir = tempfile.mkdtemp()
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for filename in zipf.namelist():
                if filename.endswith('.jhd'):
                    extracted_path = zipf.extract(filename, temp_dir)
                    jhd_files.append(extracted_path)
        
        return jhd_files

    def _parse_jhd_file(self, jhd_file: str) -> Dict:
        """Parse JHD file and extract birth data."""
        try:
            with open(jhd_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]
            
            if len(lines) < 17:
                raise ValueError(f"Invalid JHD file format: insufficient lines ({len(lines)})")
            
            # Extract data from JHD format
            month = int(lines[0])
            day = int(lines[1])
            year = int(lines[2])
            fractional_day = float(lines[3])
            lmt_offset = float(lines[4])
            longitude = float(lines[5])
            latitude = float(lines[6])
            elevation = float(lines[7])
            tz_offset = float(lines[8])
            dst_offset = float(lines[9])
            dst_flag = int(lines[10])
            ayanamsa = int(lines[11])
            place_name = lines[12]
            country = lines[13]
            birth_type = int(lines[14])
            pressure = float(lines[15])
            temperature = float(lines[16])
            chart_type = int(lines[17])
            
            # Convert fractional day back to time
            # Handle both formats: fractional day (0.0-1.0) and hours (0-24)
            if fractional_day > 1.0:
                # Value is already in hours format (0-24)
                hours = fractional_day
            else:
                # Value is in fractional day format (0.0-1.0)
                hours = fractional_day * 24
            
            hour = int(hours)
            minute = int((hours - hour) * 60)
            second = int(((hours - hour) * 60 - minute) * 60)
            
            # Create UTC datetime
            utc_dt = datetime(year, month, day, hour, minute, second)
            
            # Convert to local datetime
            local_dt = utc_dt + timedelta(hours=tz_offset)
            
            # Extract name from filename if place_name is generic
            filename = os.path.basename(jhd_file)
            name = filename.replace('.jhd', '')
            if place_name.lower() in ['unknown', 'location']:
                place_name = name
            
            return {
                'name': name,
                'birth_datetime': local_dt,
                'latitude': latitude,
                'longitude': longitude,
                'timezone_offset': tz_offset,
                'place_name': place_name,
                'country': country,
                'jhd_file': jhd_file
            }
            
        except Exception as e:
            raise ValueError(f"Error parsing JHD file {jhd_file}: {e}")

    def _convert_jhd_to_csv_row(self, birth_data: Dict, jhd_file: str) -> Dict:
        """Convert JHD birth data to CSV row format."""
        dt = birth_data['birth_datetime']
        
        # Format timezone as offset
        tz_offset = birth_data['timezone_offset']
        if tz_offset >= 0:
            tz_str = f"+{int(tz_offset):02d}:{int((tz_offset % 1) * 60):02d}"
        else:
            tz_str = f"{int(tz_offset):03d}:{int((abs(tz_offset) % 1) * 60):02d}"
        
        return {
            'name': birth_data['name'],
            'date': dt.strftime('%Y-%m-%d'),
            'time': dt.strftime('%H:%M:%S'),
            'latitude': birth_data['latitude'],
            'longitude': birth_data['longitude'],
            'timezone': f"UTC{tz_str}",
            'place_name': birth_data['place_name'],
            'country': birth_data['country'],
            'source_jhd': os.path.basename(jhd_file)
        }

    def validate_jhd_format(self, jhd_file: str) -> Dict:
        """Validate JHD file format."""
        try:
            birth_data = self._parse_jhd_file(jhd_file)
            return {
                'valid': True,
                'birth_data': birth_data,
                'errors': []
            }
        except Exception as e:
            return {
                'valid': False,
                'birth_data': None,
                'errors': [str(e)]
            }

    def get_conversion_summary(self, results: Dict) -> str:
        """Generate a human-readable summary of conversion results."""
        if not results['success']:
            return f"Conversion failed with {len(results['errors'])} errors"
        
        summary = f"Conversion successful!\n"
        summary += f"Total records: {results['total_records']}\n"
        summary += f"Files created: {results.get('files_created', results.get('records_converted', 0))}\n"
        
        if results['errors']:
            summary += f"Errors: {len(results['errors'])}\n"
        
        if results['warnings']:
            summary += f"Warnings: {len(results['warnings'])}\n"
        
        return summary