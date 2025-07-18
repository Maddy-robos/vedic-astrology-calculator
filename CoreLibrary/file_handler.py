"""
File Handler Module for Vedic Astrology Research Platform

This module provides comprehensive file handling capabilities for the Jyotish Research Platform,
including support for CSV, JHD, JSON, and other file formats used in astrological research.
"""

import os
import json
import csv
import zipfile
import tempfile
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import pandas as pd
from pathlib import Path
import mimetypes

# Optional dependency - graceful fallback if not available
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
from io import StringIO, BytesIO


class FileHandler:
    """
    Comprehensive file handler for multiple formats used in Jyotish research.
    """
    
    # Supported file formats
    SUPPORTED_FORMATS = {
        'csv': ['text/csv', 'application/csv'],
        'jhd': ['text/plain', 'application/octet-stream'],
        'json': ['application/json', 'text/json'],
        'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        'zip': ['application/zip', 'application/x-zip-compressed']
    }
    
    def __init__(self):
        """Initialize the file handler."""
        self.temp_files = []
        self.errors = []
        self.warnings = []
    
    def detect_file_format(self, file_path: str) -> Dict:
        """
        Detect file format based on content and extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with format detection results
        """
        try:
            # Get file extension
            file_ext = Path(file_path).suffix.lower().lstrip('.')
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # Try to detect using python-magic if available
            if HAS_MAGIC:
                try:
                    mime_type_magic = magic.from_file(file_path, mime=True)
                    if mime_type_magic:
                        mime_type = mime_type_magic
                except Exception:
                    # If magic fails for any reason, continue with mimetypes
                    pass
            
            # Determine format
            detected_format = None
            for format_name, mime_types in self.SUPPORTED_FORMATS.items():
                if file_ext == format_name or mime_type in mime_types:
                    detected_format = format_name
                    break
            
            # Special handling for JHD files (often detected as text/plain)
            if detected_format is None and file_ext == 'jhd':
                detected_format = 'jhd'
            
            return {
                'format': detected_format,
                'extension': file_ext,
                'mime_type': mime_type,
                'supported': detected_format in self.SUPPORTED_FORMATS
            }
            
        except Exception as e:
            return {
                'format': None,
                'extension': None,
                'mime_type': None,
                'supported': False,
                'error': str(e)
            }
    
    def validate_file(self, file_path: str, expected_format: Optional[str] = None) -> Dict:
        """
        Validate file format and structure.
        
        Args:
            file_path: Path to the file
            expected_format: Expected format ('csv', 'jhd', 'json', etc.)
            
        Returns:
            Dictionary with validation results
        """
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'errors': [f"File not found: {file_path}"]
            }
        
        # Detect format
        format_info = self.detect_file_format(file_path)
        
        if not format_info['supported']:
            return {
                'valid': False,
                'errors': [f"Unsupported file format: {format_info.get('format', 'unknown')}"]
            }
        
        detected_format = format_info['format']
        
        # Check if format matches expected
        if expected_format and detected_format != expected_format:
            return {
                'valid': False,
                'errors': [f"Expected {expected_format} format, got {detected_format}"]
            }
        
        # Format-specific validation
        validation_result = {'valid': True, 'errors': [], 'warnings': []}
        
        if detected_format == 'csv':
            validation_result.update(self._validate_csv_file(file_path))
        elif detected_format == 'jhd':
            validation_result.update(self._validate_jhd_file(file_path))
        elif detected_format == 'json':
            validation_result.update(self._validate_json_file(file_path))
        elif detected_format == 'zip':
            validation_result.update(self._validate_zip_file(file_path))
        
        validation_result['format'] = detected_format
        return validation_result
    
    def read_file(self, file_path: str, format_hint: Optional[str] = None) -> Dict:
        """
        Read file content based on format.
        
        Args:
            file_path: Path to the file
            format_hint: Hint about file format
            
        Returns:
            Dictionary with file content and metadata
        """
        # Validate file
        validation = self.validate_file(file_path, format_hint)
        if not validation['valid']:
            return {
                'success': False,
                'errors': validation['errors']
            }
        
        detected_format = validation['format']
        
        try:
            if detected_format == 'csv':
                content = self._read_csv_file(file_path)
            elif detected_format == 'jhd':
                content = self._read_jhd_file(file_path)
            elif detected_format == 'json':
                content = self._read_json_file(file_path)
            elif detected_format == 'zip':
                content = self._read_zip_file(file_path)
            else:
                return {
                    'success': False,
                    'errors': [f"Reading {detected_format} files not yet implemented"]
                }
            
            return {
                'success': True,
                'format': detected_format,
                'content': content,
                'file_path': file_path,
                'warnings': validation.get('warnings', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Error reading file: {str(e)}"]
            }
    
    def write_file(self, file_path: str, content: Any, format_type: str) -> Dict:
        """
        Write content to file in specified format.
        
        Args:
            file_path: Output file path
            content: Content to write
            format_type: File format ('csv', 'jhd', 'json', etc.)
            
        Returns:
            Dictionary with write results
        """
        try:
            if format_type == 'csv':
                result = self._write_csv_file(file_path, content)
            elif format_type == 'jhd':
                result = self._write_jhd_file(file_path, content)
            elif format_type == 'json':
                result = self._write_json_file(file_path, content)
            elif format_type == 'zip':
                result = self._write_zip_file(file_path, content)
            else:
                return {
                    'success': False,
                    'errors': [f"Writing {format_type} files not yet implemented"]
                }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Error writing file: {str(e)}"]
            }
    
    def create_temp_file(self, content: str, suffix: str = '.tmp') -> str:
        """
        Create a temporary file with given content.
        
        Args:
            content: Content to write to temp file
            suffix: File suffix/extension
            
        Returns:
            Path to the temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def cleanup_temp_files(self):
        """Clean up temporary files created during processing."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                self.warnings.append(f"Could not delete temp file {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def _validate_csv_file(self, file_path: str) -> Dict:
        """Validate CSV file structure."""
        try:
            df = pd.read_csv(file_path)
            
            if df.empty:
                return {
                    'valid': False,
                    'errors': ['CSV file is empty']
                }
            
            # Check for basic required columns for birth data
            common_columns = ['name', 'date', 'time', 'latitude', 'longitude', 'timezone']
            missing_columns = [col for col in common_columns if col not in df.columns]
            
            warnings = []
            if missing_columns:
                warnings.append(f"Missing common columns: {', '.join(missing_columns)}")
            
            return {
                'valid': True,
                'errors': [],
                'warnings': warnings,
                'rows': len(df),
                'columns': list(df.columns)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Invalid CSV file: {str(e)}"]
            }
    
    def _validate_jhd_file(self, file_path: str) -> Dict:
        """Validate JHD file structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if len(lines) < 17:
                return {
                    'valid': False,
                    'errors': [f"JHD file has insufficient lines: {len(lines)} (expected at least 17)"]
                }
            
            # Validate basic structure
            errors = []
            
            # Check month (1-12)
            try:
                month = int(lines[0])
                if not (1 <= month <= 12):
                    errors.append(f"Invalid month: {month}")
            except ValueError:
                errors.append(f"Invalid month format: {lines[0]}")
            
            # Check day (1-31)
            try:
                day = int(lines[1])
                if not (1 <= day <= 31):
                    errors.append(f"Invalid day: {day}")
            except ValueError:
                errors.append(f"Invalid day format: {lines[1]}")
            
            # Check year
            try:
                year = int(lines[2])
                if not (1900 <= year <= 2100):
                    errors.append(f"Invalid year: {year}")
            except ValueError:
                errors.append(f"Invalid year format: {lines[2]}")
            
            # Check fractional day (0.0-1.0)
            try:
                fractional_day = float(lines[3])
                if not (0.0 <= fractional_day <= 1.0):
                    errors.append(f"Invalid fractional day: {fractional_day}")
            except ValueError:
                errors.append(f"Invalid fractional day format: {lines[3]}")
            
            # Check coordinates
            try:
                longitude = float(lines[5])
                if not (-180.0 <= longitude <= 180.0):
                    errors.append(f"Invalid longitude: {longitude}")
            except ValueError:
                errors.append(f"Invalid longitude format: {lines[5]}")
            
            try:
                latitude = float(lines[6])
                if not (-90.0 <= latitude <= 90.0):
                    errors.append(f"Invalid latitude: {latitude}")
            except ValueError:
                errors.append(f"Invalid latitude format: {lines[6]}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': [],
                'lines': len(lines)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Error validating JHD file: {str(e)}"]
            }
    
    def _validate_json_file(self, file_path: str) -> Dict:
        """Validate JSON file structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'valid': True,
                'errors': [],
                'warnings': [],
                'type': type(data).__name__,
                'size': len(data) if isinstance(data, (list, dict)) else 1
            }
            
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'errors': [f"Invalid JSON: {str(e)}"]
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Error validating JSON file: {str(e)}"]
            }
    
    def _validate_zip_file(self, file_path: str) -> Dict:
        """Validate ZIP file structure."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                file_list = zf.namelist()
                
                # Check for JHD files
                jhd_files = [f for f in file_list if f.endswith('.jhd')]
                csv_files = [f for f in file_list if f.endswith('.csv')]
                
                return {
                    'valid': True,
                    'errors': [],
                    'warnings': [],
                    'total_files': len(file_list),
                    'jhd_files': len(jhd_files),
                    'csv_files': len(csv_files),
                    'file_list': file_list
                }
                
        except zipfile.BadZipFile:
            return {
                'valid': False,
                'errors': ['Invalid ZIP file']
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Error validating ZIP file: {str(e)}"]
            }
    
    def _read_csv_file(self, file_path: str) -> pd.DataFrame:
        """Read CSV file."""
        return pd.read_csv(file_path)
    
    def _read_jhd_file(self, file_path: str) -> Dict:
        """Read JHD file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
        
        return {
            'lines': lines,
            'raw_content': '\n'.join(lines)
        }
    
    def _read_json_file(self, file_path: str) -> Any:
        """Read JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _read_zip_file(self, file_path: str) -> Dict:
        """Read ZIP file contents."""
        contents = {}
        
        with zipfile.ZipFile(file_path, 'r') as zf:
            for filename in zf.namelist():
                if not filename.endswith('/'):  # Skip directories
                    with zf.open(filename) as f:
                        content = f.read().decode('utf-8')
                        contents[filename] = content
        
        return contents
    
    def _write_csv_file(self, file_path: str, content: pd.DataFrame) -> Dict:
        """Write CSV file."""
        content.to_csv(file_path, index=False)
        return {
            'success': True,
            'file_path': file_path,
            'rows_written': len(content)
        }
    
    def _write_jhd_file(self, file_path: str, content: str) -> Dict:
        """Write JHD file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {
            'success': True,
            'file_path': file_path
        }
    
    def _write_json_file(self, file_path: str, content: Any) -> Dict:
        """Write JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, default=str)
        return {
            'success': True,
            'file_path': file_path
        }
    
    def _write_zip_file(self, file_path: str, content: Dict) -> Dict:
        """Write ZIP file."""
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, file_content in content.items():
                zf.writestr(filename, file_content)
        
        return {
            'success': True,
            'file_path': file_path,
            'files_written': len(content)
        }
    
    def __del__(self):
        """Cleanup temporary files on deletion."""
        self.cleanup_temp_files()
