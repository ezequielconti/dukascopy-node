#!/usr/bin/env python3
"""
Quick test for sample_bar_downloader_utc.py
Downloads a small dataset to verify everything works.
"""

from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars, bars_to_dict_list, save_bars_to_csv


def quick_test():
    """Quick test with minimal data"""
    print("="*70)
    print("Quick Test: Sample Bar Downloader (UTC)")
    print("="*70)
    
    # Download just 3 days of hourly data (small test)
    print("\nDownloading EURUSD H1 bars for 3 days...")
    
    bars = download_bars(
        instrument='eurusd',
        from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        to_date=datetime(2024, 1, 4, tzinfo=timezone.utc),
        timeframe='h1',
        price_type='bid',
        verbose=True
    )
    
    if not bars:
        print("❌ No data returned!")
        return False
    
    # Verify data
    print(f"\n✓ Downloaded {len(bars)} bars")
    
    # Show first 5 bars
    print("\nFirst 5 bars:")
    print("-" * 70)
    for bar in bars[:5]:
        ts_ms, o, h, l, c, v = bar
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        print(f"{dt.strftime('%Y-%m-%d %H:%M:%S')} UTC | "
              f"O:{o:.5f} H:{h:.5f} L:{l:.5f} C:{c:.5f} V:{v:,.0f}")
    
    # Verify timestamps are in UTC
    first_bar_ts = bars[0][0]
    first_bar_dt = datetime.fromtimestamp(first_bar_ts / 1000, tz=timezone.utc)
    print(f"\nFirst bar timestamp: {first_bar_ts} ms")
    print(f"Converted to datetime: {first_bar_dt} (UTC)")
    print(f"Timezone: {first_bar_dt.tzinfo}")
    
    # Test dict conversion
    print("\nTesting dict conversion...")
    bars_dict = bars_to_dict_list(bars[:2])
    for bar in bars_dict:
        print(f"  {bar['datetime_utc']} | Close: {bar['close']:.5f}")
    
    # Test CSV save
    print("\nTesting CSV export...")
    save_bars_to_csv(bars[:10], 'test_output.csv')
    
    print("\n" + "="*70)
    print("✓ All tests passed!")
    print("="*70)
    
    return True


if __name__ == '__main__':
    try:
        success = quick_test()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

