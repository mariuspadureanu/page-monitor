#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper script to create a test Excel file with first 5 pages.
This allows quick testing without scanning all 231 pages.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

try:
    import pandas as pd
except ImportError:
    print("[ERROR] pandas not installed")
    print("Run: pip install pandas openpyxl")
    sys.exit(1)

def create_test_file(source_file='all-offerings-pages.xlsx', 
                     output_file='test-pages.xlsx', 
                     num_pages=5):
    """
    Extract first N pages from source Excel file.
    
    Args:
        source_file: Source Excel file path
        output_file: Output test file path
        num_pages: Number of pages to extract (default: 5)
    """
    try:
        # Check if source file exists
        if not Path(source_file).exists():
            print(f"[ERROR] Source file '{source_file}' not found")
            print(f"   Make sure {source_file} is in the current directory")
            return False
        
        print(f"[INFO] Reading {source_file}...")
        
        # Read Excel file
        df = pd.read_excel(source_file, sheet_name='Pages')
        
        print(f"[SUCCESS] Found {len(df)} pages in source file")
        
        # Extract first N pages
        test_df = df.head(num_pages)
        
        print(f"[INFO] Extracting first {num_pages} pages:")
        for idx, row in test_df.iterrows():
            offering = row.get('Offering', 'N/A')
            url = row.get('URL', 'N/A')
            print(f"   {int(idx)+1}. {offering}: {url}")
        
        # Save to new file
        test_df.to_excel(output_file, index=False, sheet_name='Pages')
        
        print(f"\n[SUCCESS] Created {output_file} with {num_pages} pages")
        print(f"   File size: {Path(output_file).stat().st_size / 1024:.1f} KB")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Create test Excel file with subset of pages'
    )
    parser.add_argument(
        '--source',
        default='all-offerings-pages.xlsx',
        help='Source Excel file (default: all-offerings-pages.xlsx)'
    )
    parser.add_argument(
        '--output',
        default='test-pages.xlsx',
        help='Output test file (default: test-pages.xlsx)'
    )
    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        help='Number of pages to extract (default: 5)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("IBM Page Monitor - Test File Creator")
    print("=" * 60)
    
    success = create_test_file(args.source, args.output, args.pages)
    
    if success:
        print("\n" + "=" * 60)
        print("Next steps:")
        print("=" * 60)
        print("1. Update config/config.yaml:")
        print(f"   excel:")
        print(f"     file_path: \"{args.output}\"")
        print()
        print("2. Disable notifications for testing:")
        print("   notifications:")
        print("     slack:")
        print("       enabled: false")
        print()
        print("3. Run test:")
        print("   python run.py")
        print("=" * 60)
        sys.exit(0)
    else:
        sys.exit(1)

# Made with Bob
