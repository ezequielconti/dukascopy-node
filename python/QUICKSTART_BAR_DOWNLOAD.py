#!/usr/bin/env python3
"""
QUICKSTART: Download Bars from Dukascopy (Always UTC)

Copy this code to your project and start downloading!
Only requires: pip install requests

All timestamps are in UTC milliseconds.
"""

from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars, save_bars_to_csv


# =============================================================================
# EXAMPLE 1: Download Hourly Gold Bars
# =============================================================================

print("Example 1: Download XAUUSD (Gold) Hourly Bars")
print("-" * 70)

bars = download_bars(
    instrument='xauusd',
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 7, tzinfo=timezone.utc),
    timeframe='h1',
    price_type='bid'
)

print(f"\nGot {len(bars)} hourly bars")
print("\nFirst 3 bars:")
for bar in bars[:3]:
    ts_ms, o, h, l, c, v = bar
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    print(f"  {dt.strftime('%Y-%m-%d %H:%M')} UTC | "
          f"O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f}")


# =============================================================================
# EXAMPLE 2: Download Daily Bitcoin Bars
# =============================================================================

print("\n\nExample 2: Download BTCUSD (Bitcoin) Daily Bars")
print("-" * 70)

bars = download_bars(
    instrument='btcusd',
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
    timeframe='d1',
    price_type='bid'
)

print(f"\nGot {len(bars)} daily bars")
print("\nFirst 3 bars:")
for bar in bars[:3]:
    ts_ms, o, h, l, c, v = bar
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    print(f"  {dt.strftime('%Y-%m-%d')} | Close: {c:.2f}")


# =============================================================================
# EXAMPLE 3: Download and Save to CSV
# =============================================================================

print("\n\nExample 3: Download EURUSD and Save to CSV")
print("-" * 70)

bars = download_bars(
    instrument='eurusd',
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 7, tzinfo=timezone.utc),
    timeframe='h4',
    price_type='bid'
)

save_bars_to_csv(bars, 'eurusd_h4.csv')
print(f"Saved {len(bars)} bars to eurusd_h4.csv")


# =============================================================================
# EXAMPLE 4: Work with Timestamps
# =============================================================================

print("\n\nExample 4: Understanding UTC Timestamps")
print("-" * 70)

if bars:
    first_bar = bars[0]
    ts_ms, o, h, l, c, v = first_bar
    
    print(f"Timestamp (UTC milliseconds): {ts_ms}")
    print(f"As integer: {int(ts_ms)}")
    
    # Convert to datetime
    dt_utc = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    print(f"As UTC datetime: {dt_utc}")
    print(f"Formatted: {dt_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Bar data
    print(f"\nBar OHLC:")
    print(f"  Open:   {o:.5f}")
    print(f"  High:   {h:.5f}")
    print(f"  Low:    {l:.5f}")
    print(f"  Close:  {c:.5f}")
    print(f"  Volume: {v:,.0f}")


# =============================================================================
# COPY-PASTE TEMPLATE FOR YOUR PROJECT
# =============================================================================

"""
MINIMAL CODE TO COPY-PASTE INTO YOUR PROJECT:
----------------------------------------------

from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

# Download bars
bars = download_bars(
    instrument='xauusd',        # Change to your instrument
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
    timeframe='h1'              # m1, m5, m15, m30, h1, h4, d1
)

# Use the data
for bar in bars:
    timestamp_ms, open, high, low, close, volume = bar
    # Your code here...


AVAILABLE INSTRUMENTS:
---------------------
Forex:    eurusd, gbpusd, usdjpy, usdchf, audusd, usdcad, nzdusd
Metals:   xauusd, xagusd
Crypto:   btcusd, ethusd, ltcusd
Indices:  usa500idxusd, usa30idxusd, usatechidxusd

AVAILABLE TIMEFRAMES:
--------------------
'm1'  - 1 minute
'm5'  - 5 minutes
'm15' - 15 minutes
'm30' - 30 minutes
'h1'  - 1 hour
'h4'  - 4 hours
'd1'  - 1 day

BAR FORMAT:
----------
[timestamp_utc_ms, open, high, low, close, volume]

Example:
[1704067200000, 2063.45, 2065.12, 2062.88, 2064.23, 1250000.0]
     ^            ^       ^       ^       ^        ^
     |            |       |       |       |        |
  UTC timestamp  open   high    low    close   volume
  (milliseconds)
"""

print("\n\n" + "="*70)
print("✓ All examples completed!")
print("="*70)
print("\nNow you can:")
print("  1. Copy sample_bar_downloader_utc.py to your project")
print("  2. pip install requests")
print("  3. Use download_bars() to get OHLC data")
print("  4. All timestamps are guaranteed to be UTC!")
print("="*70)

