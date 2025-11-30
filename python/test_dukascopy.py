#!/usr/bin/env python3
"""
Simple test/example script for dukascopy_downloader.py
"""

from datetime import datetime
from dukascopy_downloader import (
    DukascopyDownloader,
    download_tick_data,
    download_candle_data
)


def test_simple_download():
    """Test a simple small download"""
    print("Testing simple download: EURUSD hourly data for 1 day")
    
    try:
        output_file = download_candle_data(
            instrument='eurusd',
            from_date=datetime(2024, 1, 1),
            to_date=datetime(2024, 1, 2),
            timeframe='h1',
            price_type='bid',
            output_dir='./test_download',
            batch_size=5,
            verbose=True
        )
        
        print(f"\n✓ Success! Data saved to: {output_file}")
        
        # Read and display first few lines
        print("\nFirst 5 rows of data:")
        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if i < 5:
                    print(line.strip())
                else:
                    break
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_tick_download():
    """Test tick data download (small range)"""
    print("\n\nTesting tick data download: XAUUSD for 1 hour")
    
    try:
        output_file = download_tick_data(
            instrument='xauusd',
            from_date=datetime(2025, 1, 1, 0, 0),
            to_date=datetime(2025, 1, 1, 1, 0),
            price_type='bid',
            output_dir='./test_download',
            batch_size=5,
            verbose=True
        )
        
        print(f"\n✓ Success! Data saved to: {output_file}")
        
        # Count rows
        with open(output_file, 'r') as f:
            row_count = sum(1 for _ in f) - 1  # -1 for header
        
        print(f"Total tick records: {row_count}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_custom_settings():
    """Test with custom downloader settings"""
    print("\n\nTesting custom downloader: BTCUSD daily data")
    
    try:
        downloader = DukascopyDownloader(
            instrument='btcusd',
            from_date=datetime(2024, 1, 1),
            to_date=datetime(2024, 1, 7),
            timeframe='d1',
            price_type='bid',
            batch_size=3,
            batch_pause_ms=1500,
            retry_count=2,
            ignore_flats=True,
            output_dir='./test_download',
            custom_filename='btcusd_test',
            verbose=True
        )
        
        output_file = downloader.download()
        
        print(f"\n✓ Success! Data saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == '__main__':
    print("="*70)
    print("Dukascopy Downloader Test Suite")
    print("="*70)
    
    # Run tests
    test1 = test_simple_download()
    test2 = test_tick_download()
    test3 = test_custom_settings()
    
    # Summary
    print("\n\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Simple candle download: {'✓ PASS' if test1 else '✗ FAIL'}")
    print(f"Tick data download:     {'✓ PASS' if test2 else '✗ FAIL'}")
    print(f"Custom settings:        {'✓ PASS' if test3 else '✗ FAIL'}")
    print("="*70)

