#!/usr/bin/env python3
"""
JHD CLI Converter - Command Line Interface for JHD Format Conversion

This utility provides command-line access to JHD (Jyotish Hierarchical Data) format
conversion capabilities for batch processing and automation.

Usage:
    python jhd_cli_converter.py csv-to-jhd input.csv --output-dir jhd_files/
    python jhd_cli_converter.py jhd-to-csv input_dir/ --output output.csv
    python jhd_cli_converter.py create-zip input.csv --output charts.zip
"""

import argparse
import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / 'CoreLibrary'))

from CoreLibrary.jhd_converter import JHDConverter
from CoreLibrary.file_handler import FileHandler


def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def csv_to_jhd_command(args, logger):
    """Convert CSV file to JHD files."""
    logger.info(f"Converting CSV file: {args.input}")
    
    # Validate input file
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    # Initialize converter
    jhd_converter = JHDConverter()
    
    # Convert CSV to JHD
    results = jhd_converter.csv_to_jhd(
        csv_data=args.input,
        output_dir=args.output_dir
    )
    
    # Report results
    if results['success']:
        logger.info(f"✅ Conversion successful!")
        logger.info(f"Files created: {results['files_created']}")
        logger.info(f"Output directory: {results['output_directory']}")
        
        if results['errors']:
            logger.warning(f"Errors occurred: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"  - {error}")
    else:
        logger.error("❌ Conversion failed!")
        for error in results['errors']:
            logger.error(f"  - {error}")
        return 1
    
    return 0


def jhd_to_csv_command(args, logger):
    """Convert JHD files to CSV."""
    logger.info(f"Converting JHD files from: {args.input}")
    
    # Validate input
    if not os.path.exists(args.input):
        logger.error(f"Input path not found: {args.input}")
        return 1
    
    # Initialize converter
    jhd_converter = JHDConverter()
    
    # Convert JHD to CSV
    results = jhd_converter.jhd_to_csv(
        jhd_source=args.input,
        output_csv=args.output
    )
    
    # Report results
    if results['success']:
        logger.info(f"✅ Conversion successful!")
        logger.info(f"Records converted: {results['records_converted']}")
        logger.info(f"Output file: {results['output_file']}")
        
        if results['errors']:
            logger.warning(f"Errors occurred: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"  - {error}")
    else:
        logger.error("❌ Conversion failed!")
        for error in results['errors']:
            logger.error(f"  - {error}")
        return 1
    
    return 0


def create_zip_command(args, logger):
    """Create ZIP file with JHD files from CSV."""
    logger.info(f"Creating JHD ZIP from CSV: {args.input}")
    
    # Validate input file
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    # Initialize converter
    jhd_converter = JHDConverter()
    
    # Create JHD ZIP
    results = jhd_converter.create_jhd_zip(
        csv_data=args.input,
        zip_filename=args.output
    )
    
    # Report results
    if results['success']:
        logger.info(f"✅ ZIP creation successful!")
        logger.info(f"Files created: {results['files_created']}")
        logger.info(f"ZIP file: {results['zip_filename']}")
        
        if results['errors']:
            logger.warning(f"Errors occurred: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"  - {error}")
    else:
        logger.error("❌ ZIP creation failed!")
        for error in results['errors']:
            logger.error(f"  - {error}")
        return 1
    
    return 0


def validate_command(args, logger):
    """Validate JHD files."""
    logger.info(f"Validating JHD files in: {args.input}")
    
    # Initialize converter and file handler
    jhd_converter = JHDConverter()
    file_handler = FileHandler()
    
    # Collect JHD files
    jhd_files = []
    if os.path.isfile(args.input):
        if args.input.endswith('.jhd'):
            jhd_files = [args.input]
    elif os.path.isdir(args.input):
        for root, dirs, files in os.walk(args.input):
            for file in files:
                if file.endswith('.jhd'):
                    jhd_files.append(os.path.join(root, file))
    
    if not jhd_files:
        logger.error("No JHD files found")
        return 1
    
    logger.info(f"Found {len(jhd_files)} JHD files")
    
    # Validate each file
    valid_count = 0
    invalid_count = 0
    
    for jhd_file in jhd_files:
        validation = jhd_converter.validate_jhd_format(jhd_file)
        
        if validation['valid']:
            valid_count += 1
            logger.info(f"✅ {os.path.basename(jhd_file)}: Valid")
            if args.verbose:
                birth_data = validation['birth_data']
                logger.debug(f"   Name: {birth_data['name']}")
                logger.debug(f"   Date: {birth_data['birth_datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
                logger.debug(f"   Place: {birth_data['place_name']}")
        else:
            invalid_count += 1
            logger.error(f"❌ {os.path.basename(jhd_file)}: Invalid")
            for error in validation['errors']:
                logger.error(f"   - {error}")
    
    # Summary
    logger.info(f"\n📊 Validation Summary:")
    logger.info(f"Valid files: {valid_count}")
    logger.info(f"Invalid files: {invalid_count}")
    logger.info(f"Total files: {len(jhd_files)}")
    
    return 0 if invalid_count == 0 else 1


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="JHD Format Converter - Convert between CSV and JHD formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert CSV to JHD files in a directory
  python jhd_cli_converter.py csv-to-jhd charts.csv --output-dir jhd_files/
  
  # Convert JHD files to CSV
  python jhd_cli_converter.py jhd-to-csv jhd_files/ --output combined.csv
  
  # Create ZIP archive with JHD files
  python jhd_cli_converter.py create-zip charts.csv --output charts.zip
  
  # Validate JHD files
  python jhd_cli_converter.py validate jhd_files/
        """
    )
    
    # Global options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # CSV to JHD command
    csv_to_jhd = subparsers.add_parser('csv-to-jhd', help='Convert CSV to JHD files')
    csv_to_jhd.add_argument('input', help='Input CSV file')
    csv_to_jhd.add_argument('--output-dir', default='jhd_output',
                           help='Output directory for JHD files (default: jhd_output)')
    
    # JHD to CSV command
    jhd_to_csv = subparsers.add_parser('jhd-to-csv', help='Convert JHD files to CSV')
    jhd_to_csv.add_argument('input', help='Input JHD file, directory, or ZIP file')
    jhd_to_csv.add_argument('--output', default='jhd_to_csv_output.csv',
                           help='Output CSV file (default: jhd_to_csv_output.csv)')
    
    # Create ZIP command
    create_zip = subparsers.add_parser('create-zip', help='Create ZIP with JHD files from CSV')
    create_zip.add_argument('input', help='Input CSV file')
    create_zip.add_argument('--output', help='Output ZIP file')
    
    # Validate command
    validate = subparsers.add_parser('validate', help='Validate JHD files')
    validate.add_argument('input', help='JHD file or directory to validate')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Set default output for create-zip if not provided
    if args.command == 'create-zip' and not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'jhd_charts_{timestamp}.zip'
    
    # Execute command
    try:
        if args.command == 'csv-to-jhd':
            return csv_to_jhd_command(args, logger)
        elif args.command == 'jhd-to-csv':
            return jhd_to_csv_command(args, logger)
        elif args.command == 'create-zip':
            return create_zip_command(args, logger)
        elif args.command == 'validate':
            return validate_command(args, logger)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())