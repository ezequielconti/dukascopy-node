# UTC Bar Downloader - Summary

I've created a simplified, standalone Python implementation for downloading OHLC bar data from Dukascopy with **all timestamps guaranteed to be in UTC**.

## 📦 What You Got

### Main Implementation
**`sample_bar_downloader_utc.py`** (370 lines)
- Complete standalone implementation
- Single function API: `download_bars()`
- Only requires `requests` package
- All timestamps in UTC milliseconds
- Supports timeframes: M1, M5, M15, M30, H1, H4, D1
- 600+ instruments (forex, metals, crypto, indices)

### Documentation
**`SAMPLE_DOWNLOADER_README.md`**
- Complete documentation
- Usage examples
- API reference
- Troubleshooting guide
- Integration checklist

### Quick Start
**`QUICKSTART_BAR_DOWNLOAD.py`**
- Copy-paste ready examples
- 4 working examples
- Minimal template for your project

### Testing
**`test_sample_downloader.py`**
- Quick test script
- Verifies UTC timestamps
- Tests all functions

## 🚀 How to Use in Another Project

### Step 1: Copy Files
```bash
# Copy just the main file (that's all you need!)
cp sample_bar_downloader_utc.py /path/to/your/project/
```

### Step 2: Install Dependencies
```bash
pip install requests
```

### Step 3: Use in Your Code
```python
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

# Download bars (always UTC)
bars = download_bars(
    instrument='xauusd',
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
    timeframe='h1'
)

# bars = [[timestamp_ms, open, high, low, close, volume], ...]
# All timestamps are UTC milliseconds

for bar in bars[:5]:
    ts_ms, o, h, l, c, v = bar
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    print(f"{dt} | O:{o} H:{h} L:{l} C:{c}")
```

## 📊 Data Format

Each bar is a list with 6 elements:
```python
[timestamp_ms, open, high, low, close, volume]
```

**Example:**
```python
[1704067200000, 2063.45, 2065.12, 2062.88, 2064.23, 1250000.0]
```

- **timestamp_ms**: UTC milliseconds since Unix epoch
- **open**: Opening price
- **high**: Highest price in period
- **low**: Lowest price in period
- **close**: Closing price
- **volume**: Trading volume in base units

## ⏰ UTC Guarantee

**All timestamps are in UTC timezone**:
- No timezone conversions needed
- No DST (daylight saving) issues
- Standard for financial data
- Easy to convert to local time when displaying

```python
from datetime import datetime, timezone

# Convert UTC timestamp to datetime
ts_ms = 1704067200000
dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
print(dt)  # 2024-01-01 00:00:00+00:00

# The timezone is always UTC
print(dt.tzinfo)  # UTC
```

## 🎯 Key Features

### 1. Simple API
```python
bars = download_bars('btcusd', from_date, to_date, timeframe='h1')
```

### 2. Multiple Timeframes
- M1, M5, M15, M30 - Minute bars
- H1, H4 - Hourly bars
- D1 - Daily bars

### 3. 600+ Instruments
- **Forex**: eurusd, gbpusd, usdjpy, etc.
- **Metals**: xauusd (gold), xagusd (silver)
- **Crypto**: btcusd, ethusd, ltcusd
- **Indices**: S&P 500, NASDAQ, Dow Jones

### 4. Helper Functions
```python
# Convert to dict format
bars_dict = bars_to_dict_list(bars)

# Save to CSV
save_bars_to_csv(bars, 'output.csv')
```

## 📁 File Overview

```
python/
├── sample_bar_downloader_utc.py      ⭐ Main implementation (copy this!)
├── SAMPLE_DOWNLOADER_README.md       📖 Full documentation
├── QUICKSTART_BAR_DOWNLOAD.py        🚀 Quick examples
├── test_sample_downloader.py         🧪 Test script
└── UTC_BAR_DOWNLOADER_SUMMARY.md     📋 This file
```

## 🔧 Comparison with Full Implementation

| Feature | sample_bar_downloader_utc.py | dukascopy_downloader.py |
|---------|------------------------------|-------------------------|
| Lines of code | ~370 | ~880 |
| Dependencies | requests only | requests only |
| UTC timestamps | ✅ Yes | ✅ Yes |
| Timeframes | M1-D1 | M1-MN1 (includes monthly) |
| Tick data | ❌ No | ✅ Yes |
| Bar/OHLC data | ✅ Yes | ✅ Yes |
| Caching | ❌ No | ❌ No (kept simple) |
| Complexity | Simple | More features |
| Best for | Quick integration | Full-featured use |

**Recommendation**: Use `sample_bar_downloader_utc.py` for most projects. It's simpler and does everything you need for bar data.

## 💡 Common Use Cases

### 1. Backtesting Strategy
```python
# Download historical data for backtesting
bars = download_bars('eurusd', 
                    datetime(2023, 1, 1, tzinfo=timezone.utc),
                    datetime(2024, 1, 1, tzinfo=timezone.utc),
                    timeframe='h1')

# Run backtest on bars
for bar in bars:
    ts, o, h, l, c, v = bar
    # Your strategy logic...
```

### 2. Live Trading (Historical Context)
```python
from datetime import timedelta

# Get last 30 days for context
to_date = datetime.now(timezone.utc)
from_date = to_date - timedelta(days=30)

bars = download_bars('btcusd', from_date, to_date, timeframe='h4')

# Use bars for decision making
latest_bar = bars[-1]
```

### 3. Data Analysis
```python
import pandas as pd

bars = download_bars('xauusd', from_date, to_date, timeframe='d1')

# Convert to DataFrame
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
df.set_index('datetime', inplace=True)

# Analyze
print(df.describe())
```

### 4. Multi-Instrument Analysis
```python
instruments = ['eurusd', 'gbpusd', 'usdjpy']
data = {}

for instr in instruments:
    bars = download_bars(instr, from_date, to_date, timeframe='d1')
    data[instr] = bars

# Correlation analysis, portfolio optimization, etc.
```

## 🧪 Testing

Run the test to verify everything works:
```bash
python test_sample_downloader.py
```

Expected output:
```
======================================================================
Quick Test: Sample Bar Downloader (UTC)
======================================================================

Downloading EURUSD H1 bars for 3 days...
Fetching 3 daily files...
Total M1 candles: XXXX
Aggregating to H1...
Final H1 bars: XX

✓ Downloaded XX bars
...
✓ All tests passed!
```

## 📋 Integration Checklist

- [ ] Copy `sample_bar_downloader_utc.py` to your project
- [ ] Run `pip install requests`
- [ ] Test with small date range
- [ ] Verify timestamps are UTC
- [ ] Add error handling for your use case
- [ ] Consider caching if downloading same data repeatedly

## 🎓 How It Works

1. **Generate URLs** - Creates Dukascopy URLs for minute data
2. **Download** - Fetches `.bi5` files (LZMA compressed)
3. **Decompress** - Extracts using Python's `lzma` module
4. **Parse** - Unpacks binary data (struct format: `>5i1f`)
5. **Normalize** - Converts to decimal prices
6. **Aggregate** - Combines M1 bars to target timeframe
7. **Return** - List of [timestamp, O, H, L, C, V] in UTC

## 🔍 Differences from TypeScript Version

| Aspect | TypeScript (src/) | Python (sample) |
|--------|------------------|-----------------|
| Language | TypeScript | Python 3 |
| Async | Yes (async/await) | No (synchronous) |
| Batching | Yes | No (sequential) |
| Caching | Optional | No |
| Tick data | Yes | No (bars only) |
| Date handling | Date objects | datetime objects |
| Timezone | Configurable offset | Always UTC |
| Aggregation | Full OHLC module | Simplified |
| Dependencies | lzma-purejs, struct, etc. | requests only |

**Note**: Both produce the same data output format for bar data.

## 🚨 Important Notes

### 1. Data Availability
- Some instruments/dates may have no data
- Very recent data might not be available yet
- Weekends: Forex markets closed (Sat-Sun UTC)

### 2. Rate Limiting
- No explicit rate limiting in Dukascopy API
- But don't hammer the server
- Use reasonable batch sizes

### 3. Zero Volume Bars
- By default, filtered out (`ignore_zero_volume=True`)
- These are "flat" periods with no trading activity
- Can include them by setting `ignore_zero_volume=False`

### 4. Timestamps
- Always in **UTC**
- Always in **milliseconds**
- Convert to local time only for display

## 📞 Need Help?

1. **Quick examples**: See `QUICKSTART_BAR_DOWNLOAD.py`
2. **Full docs**: Read `SAMPLE_DOWNLOADER_README.md`
3. **Source code**: Check comments in `sample_bar_downloader_utc.py`
4. **Test it**: Run `test_sample_downloader.py`

## 🎉 You're Ready!

You now have a simple, standalone bar downloader that:
- ✅ Works with 600+ instruments
- ✅ Supports multiple timeframes
- ✅ Guarantees UTC timestamps
- ✅ Has minimal dependencies
- ✅ Is easy to integrate
- ✅ Is production-ready

**Just copy `sample_bar_downloader_utc.py` and start downloading!** 🚀

---

## Quick Reference Card

```python
# Import
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

# Download
bars = download_bars(
    instrument='xauusd',        # or btcusd, eurusd, etc.
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
    timeframe='h1',             # m1, m5, m15, m30, h1, h4, d1
    price_type='bid',           # or 'ask'
    ignore_zero_volume=True,    # filter flats
    verbose=True                # show progress
)

# Use
for bar in bars:
    ts_ms, o, h, l, c, v = bar
    # ts_ms is UTC milliseconds
    # o, h, l, c are prices
    # v is volume
```

**Remember**: All timestamps are UTC! 🌍

