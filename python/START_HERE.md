# 🚀 START HERE - Dukascopy Bar Downloader for Python

## What You Need

I've created a **simplified, standalone Python implementation** for downloading OHLC bar data from Dukascopy with **all timestamps in UTC**.

## 📦 Files Created

| File | Purpose | Lines |
|------|---------|-------|
| **`sample_bar_downloader_utc.py`** ⭐ | Main implementation - Copy this to your project! | 370 |
| `SAMPLE_DOWNLOADER_README.md` | Complete documentation with examples | - |
| `QUICKSTART_BAR_DOWNLOAD.py` | Copy-paste ready examples | 200 |
| `test_sample_downloader.py` | Test script to verify it works | 130 |
| `UTC_BAR_DOWNLOADER_SUMMARY.md` | Detailed summary and comparison | - |
| `START_HERE.md` | This file - Quick overview | - |

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependency
```bash
pip install requests
```

### Step 2: Copy the Main File
```bash
# Copy to your project
cp sample_bar_downloader_utc.py /path/to/your/project/
```

### Step 3: Use in Your Code
```python
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

# Download bars (always UTC!)
bars = download_bars(
    instrument='xauusd',
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
    timeframe='h1'
)

# bars = [[timestamp_ms, open, high, low, close, volume], ...]
print(f"Downloaded {len(bars)} bars")

# First bar
ts_ms, o, h, l, c, v = bars[0]
dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
print(f"{dt} | Open: {o}, High: {h}, Low: {l}, Close: {c}")
```

## 🎯 What You Get

### Data Format
Each bar is a list:
```python
[timestamp_ms, open, high, low, close, volume]
[1704067200000, 2063.45, 2065.12, 2062.88, 2064.23, 1250000.0]
```

- **timestamp_ms**: UTC milliseconds since Unix epoch
- **open, high, low, close**: Decimal prices
- **volume**: Trading volume in base units

### Supported Features
✅ **Timeframes**: M1, M5, M15, M30, H1, H4, D1  
✅ **Instruments**: 600+ (forex, metals, crypto, indices, commodities)  
✅ **UTC Timestamps**: Guaranteed UTC, no timezone confusion  
✅ **Simple API**: One function to download bars  
✅ **Minimal Dependencies**: Only `requests` package  

### Example Instruments
- **Forex**: `eurusd`, `gbpusd`, `usdjpy`, `usdchf`, `audusd`
- **Metals**: `xauusd` (gold), `xagusd` (silver)
- **Crypto**: `btcusd`, `ethusd`, `ltcusd`
- **Indices**: `usa500idxusd` (S&P 500), `usatechidxusd` (NASDAQ)

## 📖 Documentation Flow

Read in this order:

1. **`START_HERE.md`** (this file) - Quick overview
2. **`QUICKSTART_BAR_DOWNLOAD.py`** - Run examples
3. **`SAMPLE_DOWNLOADER_README.md`** - Full documentation
4. **`sample_bar_downloader_utc.py`** - Source code (well commented)

## 🧪 Test It Works

```bash
cd python
python3 test_sample_downloader.py
```

Expected output:
```
======================================================================
Quick Test: Sample Bar Downloader (UTC)
======================================================================

Downloading EURUSD H1 bars for 3 days...
...
✓ All tests passed!
```

## 💡 Common Usage Patterns

### Pattern 1: Simple Download
```python
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

bars = download_bars('btcusd', 
                    datetime(2024, 1, 1, tzinfo=timezone.utc),
                    datetime(2024, 1, 31, tzinfo=timezone.utc),
                    timeframe='d1')
```

### Pattern 2: Convert to DataFrame
```python
import pandas as pd

bars = download_bars('eurusd', from_date, to_date, timeframe='h1')
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
```

### Pattern 3: Save to CSV
```python
from sample_bar_downloader_utc import download_bars, save_bars_to_csv

bars = download_bars('xauusd', from_date, to_date, timeframe='h4')
save_bars_to_csv(bars, 'gold_h4.csv')
```

## ⏰ UTC Timestamps - Important!

**All timestamps are UTC milliseconds:**

```python
from datetime import datetime, timezone

# Timestamp to datetime (UTC)
ts_ms = 1704067200000
dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
print(dt)  # 2024-01-01 00:00:00+00:00

# Datetime to timestamp
dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
ts_ms = int(dt.timestamp() * 1000)
print(ts_ms)  # 1704110400000
```

**Why UTC?**
- ✅ No daylight saving time issues
- ✅ Standard for financial data
- ✅ Unambiguous across timezones
- ✅ Easy to convert to local time for display

## 🔥 Run Examples Now

```bash
cd python
python3 QUICKSTART_BAR_DOWNLOAD.py
```

This will:
1. Download XAUUSD hourly bars
2. Download BTCUSD daily bars
3. Download EURUSD and save to CSV
4. Show you how to work with timestamps

## 📋 Integration Checklist

When adding to your project:

- [ ] Copy `sample_bar_downloader_utc.py` to your project directory
- [ ] Install `requests`: `pip install requests`
- [ ] Test with small date range (3-7 days)
- [ ] Verify timestamps are UTC
- [ ] Handle empty results (no data available)
- [ ] Add error handling for your specific use case
- [ ] Consider caching if downloading same data repeatedly

## 🎓 How It Works (High Level)

```
1. Generate URLs → Dukascopy data feed URLs
2. Download      → Fetch .bi5 files (LZMA compressed)
3. Decompress    → Python's lzma module
4. Parse         → Unpack binary data (struct)
5. Normalize     → Convert to decimal prices
6. Aggregate     → Combine M1 to target timeframe
7. Return        → List of [timestamp, OHLC, volume] in UTC
```

## 🆚 Comparison: Two Implementations

You have two Python options:

| Feature | `sample_bar_downloader_utc.py` | `dukascopy_downloader.py` |
|---------|-------------------------------|---------------------------|
| **Complexity** | ⭐ Simple (370 lines) | Full-featured (880 lines) |
| **Bar data** | ✅ Yes | ✅ Yes |
| **Tick data** | ❌ No | ✅ Yes |
| **Timeframes** | M1-D1 | M1-MN1 (includes monthly) |
| **Dependencies** | requests only | requests only |
| **UTC** | ✅ Always | ✅ Always |
| **Best for** | Most projects | Advanced features |

**Recommendation**: Start with `sample_bar_downloader_utc.py`. It's simpler and covers 90% of use cases.

## 🚨 Common Issues

### Issue: No data returned
```python
bars = download_bars('xauusd', from_date, to_date)
if not bars:
    print("No data - check date range or instrument name")
```

**Possible reasons:**
- Weekend (forex markets closed Sat-Sun UTC)
- Very recent data (not available yet)
- Invalid instrument name
- Future dates

### Issue: Slow downloads
```python
# Use higher timeframes for large date ranges
# BAD:  1 year of M1 data (slow)
# GOOD: 1 year of D1 data (fast)

# Or download in chunks
from datetime import timedelta

def download_chunks(instrument, start, end, chunk_days=30):
    all_bars = []
    current = start
    while current < end:
        chunk_end = min(current + timedelta(days=chunk_days), end)
        bars = download_bars(instrument, current, chunk_end, 'h1')
        all_bars.extend(bars)
        current = chunk_end
    return all_bars
```

## 📚 Full Documentation

For complete documentation, see:
- **`SAMPLE_DOWNLOADER_README.md`** - Full API reference, examples, troubleshooting
- **`UTC_BAR_DOWNLOADER_SUMMARY.md`** - Detailed comparison and use cases

## 🎯 Next Steps

1. **Test it**: Run `python3 test_sample_downloader.py`
2. **See examples**: Run `python3 QUICKSTART_BAR_DOWNLOAD.py`
3. **Copy to project**: `cp sample_bar_downloader_utc.py /your/project/`
4. **Start coding**: Use `download_bars()` in your code

## 💬 Quick Reference

```python
# The only function you need
download_bars(
    instrument='xauusd',      # Required: 'xauusd', 'btcusd', 'eurusd', etc.
    from_date=datetime(...),  # Required: Start date (UTC)
    to_date=datetime(...),    # Required: End date (UTC)
    timeframe='h1',           # Optional: 'm1','m5','m15','m30','h1','h4','d1'
    price_type='bid',         # Optional: 'bid' or 'ask'
    ignore_zero_volume=True,  # Optional: Filter flats
    verbose=True              # Optional: Show progress
)
# Returns: [[timestamp_ms, open, high, low, close, volume], ...]
```

## ✅ You're Ready!

You now have everything you need to download bar data from Dukascopy in Python with UTC timestamps!

**Just copy `sample_bar_downloader_utc.py` and start downloading!** 🚀

---

**Questions?** Read the docs:
- Quick: `QUICKSTART_BAR_DOWNLOAD.py`
- Full: `SAMPLE_DOWNLOADER_README.md`
- Code: `sample_bar_downloader_utc.py` (well commented)

**Happy trading! 📈**

