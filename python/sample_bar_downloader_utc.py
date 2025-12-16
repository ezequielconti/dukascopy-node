#!/usr/bin/env python3
"""
Sample Dukascopy Bar (OHLC) Downloader - Always UTC

This is a simplified, ready-to-use example for downloading bar data from Dukascopy.
All timestamps are in UTC (Unix milliseconds).

Requirements:
    pip install requests

Usage:
    from datetime import datetime, timezone
    from sample_bar_downloader_utc import download_bars
    
    # Download hourly bars
    bars = download_bars(
        instrument='xauusd',
        from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        to_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
        timeframe='h1'
    )
    
    # bars is a list of [timestamp, open, high, low, close, volume]
"""

import struct
import lzma
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional
import time


# =============================================================================
# CONFIGURATION
# =============================================================================

DUKASCOPY_URL_ROOT = "https://datafeed.dukascopy.com/datafeed"

# Instrument decimal factors (for price normalization)
DECIMAL_FACTORS = {
    # Forex
    "eurusd": 100000, "gbpusd": 100000, "usdjpy": 1000, "usdchf": 100000,
    "audusd": 100000, "usdcad": 100000, "nzdusd": 100000, "eurgbp": 100000,
    # Metals
    "xauusd": 1000, "xagusd": 100000,
    # Crypto
    "btcusd": 1000, "ethusd": 1000, "ltcusd": 1000,
    # Indices
    "usa500idxusd": 100, "usa30idxusd": 100, "usatechidxusd": 100,
}

# Timeframe to aggregation mapping (in minutes)
TIMEFRAME_MINUTES = {
    'm1': 1, 'm5': 5, 'm15': 15, 'm30': 30,
    'h1': 60, 'h4': 240, 'd1': 1440
}


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def generate_minute_urls(instrument: str, start: datetime, end: datetime, 
                        price_type: str = 'bid') -> List[str]:
    """
    Generate URLs for downloading minute candle data.
    Returns list of URLs to .bi5 files containing minute data.
    
    All dates are treated as UTC.
    """
    urls = []
    current = start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    
    while current < end:
        year = str(current.year).zfill(4)
        month = str(current.month).zfill(2)
        day = str(current.day).zfill(2)
        
        url = (f"{DUKASCOPY_URL_ROOT}/{instrument.upper()}/{year}/"
               f"{month}/{day}/{price_type.upper()}_candles_min_1.bi5")
        urls.append(url)
        
        current += timedelta(days=1)
    
    return urls


def download_and_decompress(url: str, retries: int = 3) -> Optional[bytes]:
    """
    Download and decompress a .bi5 file from Dukascopy.
    Returns decompressed bytes or None if failed.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200 and len(response.content) > 0:
                # Decompress LZMA
                decompressed = lzma.decompress(response.content)
                return decompressed
            elif response.status_code == 404:
                # No data for this day
                return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(0.5)
            else:
                print(f"Failed to fetch {url}: {e}")
    return None


def parse_minute_candles(data: bytes, decimal_factor: int, 
                        day_start_ts: int) -> List[List[float]]:
    """
    Parse decompressed minute candle data.
    
    Binary format: >5i1f (big-endian: 5 integers, 1 float)
    Returns: [[timestamp, open, high, low, close, volume], ...]
    
    All timestamps are in UTC milliseconds.
    """
    if not data:
        return []
    
    candles = []
    format_str = '>5i1f'  # timestamp_sec, open, close, low, high, volume
    record_size = struct.calcsize(format_str)
    
    for i in range(0, len(data), record_size):
        chunk = data[i:i + record_size]
        if len(chunk) == record_size:
            timestamp_sec, open_val, close_val, low, high, volume = struct.unpack(format_str, chunk)
            
            # Convert to human-readable format
            timestamp_ms = timestamp_sec * 1000 + day_start_ts  # UTC milliseconds
            open_price = open_val / decimal_factor
            high_price = high / decimal_factor
            low_price = low / decimal_factor
            close_price = close_val / decimal_factor
            volume_normalized = volume * 1_000_000  # Volume in base units
            
            candles.append([timestamp_ms, open_price, high_price, low_price, 
                          close_price, volume_normalized])
    
    return candles


def aggregate_to_timeframe(m1_candles: List[List[float]], 
                          target_timeframe: str,
                          ignore_zero_volume: bool = True) -> List[List[float]]:
    """
    Aggregate M1 candles to higher timeframe (M5, M15, M30, H1, H4, D1).
    
    Args:
        m1_candles: List of [timestamp, open, high, low, close, volume]
        target_timeframe: Target timeframe ('m5', 'm15', 'm30', 'h1', 'h4', 'd1')
        ignore_zero_volume: Skip candles with zero volume
    
    Returns:
        List of aggregated candles [timestamp, open, high, low, close, volume]
    
    All timestamps remain in UTC milliseconds.
    """
    if target_timeframe == 'm1':
        return m1_candles
    
    target_minutes = TIMEFRAME_MINUTES.get(target_timeframe, 60)
    interval_ms = target_minutes * 60 * 1000
    
    aggregated = []
    candles_by_period = {}
    
    # Group candles by period
    for candle in m1_candles:
        ts, o, h, l, c, v = candle
        
        # Skip zero volume if requested
        if ignore_zero_volume and v == 0:
            continue
        
        # Calculate period start (floor to interval in UTC)
        period_start = (ts // interval_ms) * interval_ms
        
        if period_start not in candles_by_period:
            candles_by_period[period_start] = []
        candles_by_period[period_start].append(candle)
    
    # Aggregate each period
    for period_start in sorted(candles_by_period.keys()):
        period_candles = candles_by_period[period_start]
        
        if not period_candles:
            continue
        
        # Calculate OHLC
        timestamp = period_start
        open_price = period_candles[0][1]  # First candle's open
        high_price = max(c[2] for c in period_candles)  # Max high
        low_price = min(c[3] for c in period_candles)  # Min low
        close_price = period_candles[-1][4]  # Last candle's close
        total_volume = sum(c[5] for c in period_candles)  # Sum volume
        
        aggregated.append([timestamp, open_price, high_price, low_price, 
                         close_price, total_volume])
    
    return aggregated


def download_bars(instrument: str,
                 from_date: datetime,
                 to_date: datetime,
                 timeframe: str = 'h1',
                 price_type: str = 'bid',
                 ignore_zero_volume: bool = True,
                 verbose: bool = True) -> List[List[float]]:
    """
    Download OHLC bar data from Dukascopy.
    
    Args:
        instrument: Trading instrument (e.g., 'xauusd', 'eurusd', 'btcusd')
        from_date: Start date (datetime object, will be treated as UTC)
        to_date: End date (datetime object, will be treated as UTC)
        timeframe: Bar timeframe ('m1', 'm5', 'm15', 'm30', 'h1', 'h4', 'd1')
        price_type: 'bid' or 'ask'
        ignore_zero_volume: Skip bars with zero volume
        verbose: Print progress messages
    
    Returns:
        List of bars: [[timestamp_ms, open, high, low, close, volume], ...]
        
    All timestamps are in UTC milliseconds (Unix epoch).
    All prices are normalized to decimal values.
    
    Example:
        >>> from datetime import datetime, timezone
        >>> bars = download_bars(
        ...     'xauusd',
        ...     datetime(2024, 1, 1, tzinfo=timezone.utc),
        ...     datetime(2024, 1, 7, tzinfo=timezone.utc),
        ...     timeframe='h1'
        ... )
        >>> # bars[0] = [1704067200000, 2063.45, 2065.12, 2062.88, 2064.23, 1250000.0]
    """
    instrument = instrument.lower()
    
    # Ensure dates are in UTC
    if from_date.tzinfo is None:
        from_date = from_date.replace(tzinfo=timezone.utc)
    if to_date.tzinfo is None:
        to_date = to_date.replace(tzinfo=timezone.utc)
    
    # Get decimal factor
    decimal_factor = DECIMAL_FACTORS.get(instrument, 100000)
    
    if verbose:
        print(f"\nDownloading {instrument.upper()} {timeframe} bars (UTC)")
        print(f"Period: {from_date.strftime('%Y-%m-%d %H:%M')} to "
              f"{to_date.strftime('%Y-%m-%d %H:%M')} UTC")
    
    # Generate URLs for minute data
    urls = generate_minute_urls(instrument, from_date, to_date, price_type)
    
    if verbose:
        print(f"Fetching {len(urls)} daily files...")
    
    # Download and parse all M1 data
    all_m1_candles = []
    
    for i, url in enumerate(urls):
        # Extract date from URL for start timestamp
        parts = url.split('/')
        year, month, day = int(parts[-4]), int(parts[-3]), int(parts[-2])
        day_start = datetime(year, month, day, tzinfo=timezone.utc)
        day_start_ts = int(day_start.timestamp() * 1000)
        
        # Download and decompress
        decompressed = download_and_decompress(url)
        
        if decompressed:
            candles = parse_minute_candles(decompressed, decimal_factor, day_start_ts)
            all_m1_candles.extend(candles)
            
            if verbose and (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(urls)} files...")
    
    if verbose:
        print(f"Total M1 candles: {len(all_m1_candles)}")
    
    # Sort by timestamp (ensure chronological order)
    all_m1_candles.sort(key=lambda x: x[0])
    
    # Filter by exact date range (UTC timestamps)
    from_ts = int(from_date.timestamp() * 1000)
    to_ts = int(to_date.timestamp() * 1000)
    all_m1_candles = [c for c in all_m1_candles if from_ts <= c[0] < to_ts]
    
    # Aggregate to target timeframe
    if timeframe != 'm1':
        if verbose:
            print(f"Aggregating to {timeframe.upper()}...")
        bars = aggregate_to_timeframe(all_m1_candles, timeframe, ignore_zero_volume)
    else:
        bars = all_m1_candles
    
    if verbose:
        print(f"Final {timeframe.upper()} bars: {len(bars)}\n")
    
    return bars


def bars_to_dict_list(bars: List[List[float]]) -> List[dict]:
    """
    Convert bars to list of dictionaries for easier handling.
    
    Args:
        bars: List of [timestamp, open, high, low, close, volume]
    
    Returns:
        List of dicts with keys: timestamp, datetime_utc, open, high, low, close, volume
    """
    result = []
    for bar in bars:
        ts_ms, o, h, l, c, v = bar
        result.append({
            'timestamp': int(ts_ms),
            'datetime_utc': datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc),
            'open': o,
            'high': h,
            'low': l,
            'close': c,
            'volume': v
        })
    return result


def save_bars_to_csv(bars: List[List[float]], filename: str):
    """
    Save bars to CSV file.
    
    Args:
        bars: List of [timestamp, open, high, low, close, volume]
        filename: Output CSV filename
    """
    import csv
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp_utc_ms', 'datetime_utc', 'open', 'high', 'low', 'close', 'volume'])
        
        for bar in bars:
            ts_ms, o, h, l, c, v = bar
            dt_utc = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([int(ts_ms), dt_utc, o, h, l, c, v])
    
    print(f"Saved {len(bars)} bars to {filename}")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_usage():
    """Example usage demonstrations"""
    
    print("="*70)
    print("Dukascopy Bar Downloader - UTC Examples")
    print("="*70)
    
    # Example 1: Download hourly gold bars
    print("\n--- Example 1: XAUUSD Hourly Bars ---")
    bars_h1 = download_bars(
        instrument='xauusd',
        from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        to_date=datetime(2024, 1, 7, tzinfo=timezone.utc),
        timeframe='h1',
        price_type='bid',
        verbose=True
    )
    
    # Display first 3 bars
    print("First 3 bars:")
    for bar in bars_h1[:3]:
        ts_ms, o, h, l, c, v = bar
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        print(f"  {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC | "
              f"O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f} V:{v:.0f}")
    
    # Example 2: Download daily EUR/USD bars
    print("\n--- Example 2: EURUSD Daily Bars ---")
    bars_d1 = download_bars(
        instrument='eurusd',
        from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        to_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
        timeframe='d1',
        price_type='bid',
        verbose=True
    )
    
    # Convert to dict format
    bars_dict = bars_to_dict_list(bars_d1[:3])
    print("First 3 bars (dict format):")
    for bar in bars_dict:
        print(f"  {bar['datetime_utc']} | "
              f"O:{bar['open']:.5f} H:{bar['high']:.5f} "
              f"L:{bar['low']:.5f} C:{bar['close']:.5f}")
    
    # Example 3: Save to CSV
    print("\n--- Example 3: Save to CSV ---")
    save_bars_to_csv(bars_h1[:24], 'sample_xauusd_h1.csv')
    
    print("\n" + "="*70)
    print("✓ All examples completed successfully!")
    print("="*70)


if __name__ == '__main__':
    # Run examples
    example_usage()
    
    """
    QUICK USAGE IN YOUR PROJECT:
    
    from datetime import datetime, timezone
    from sample_bar_downloader_utc import download_bars
    
    # Download bars (always UTC)
    bars = download_bars(
        instrument='btcusd',
        from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        to_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
        timeframe='h4'
    )
    
    # bars is a list: [[timestamp_ms, open, high, low, close, volume], ...]
    # All timestamps are UTC milliseconds since Unix epoch
    
    for bar in bars[:5]:
        ts_ms, o, h, l, c, v = bar
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        print(f"{dt} | O:{o} H:{h} L:{l} C:{c} V:{v}")
    """

