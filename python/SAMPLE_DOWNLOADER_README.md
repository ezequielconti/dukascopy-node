# Dukascopy Bar Downloader - Sample Implementation (UTC)

A simplified, standalone Python implementation for downloading OHLC bar data from Dukascopy with **all timestamps in UTC**.

## 🎯 Features

- ✅ **Always UTC** - All timestamps are in UTC (no timezone confusion)
- ✅ **Simple API** - One function to download bars
- ✅ **Multiple Timeframes** - M1, M5, M15, M30, H1, H4, D1
- ✅ **600+ Instruments** - Forex, metals, crypto, indices, commodities
- ✅ **Minimal Dependencies** - Only requires `requests`
- ✅ **Ready to Copy** - Single file, easy to integrate into any project

## 📦 Installation

### Option 1: Copy to Your Project

```bash
# Just copy the file to your project
cp sample_bar_downloader_utc.py /path/to/your/project/
```

### Option 2: Install Dependencies

```bash
pip install requests
```

That's it! No other dependencies needed.

## 🚀 Quick Start

### Basic Usage

```python
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

# Download hourly bars for Gold (XAU/USD)
bars = download_bars(
    instrument='xauusd',
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
    timeframe='h1'
)

# bars is a list: [[timestamp_ms, open, high, low, close, volume], ...]
# All timestamps are UTC milliseconds

for bar in bars[:5]:
    ts_ms, o, h, l, c, v = bar
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    print(f"{dt} | O:{o} H:{h} L:{l} C:{c} V:{v}")
```

### Output Format

Each bar is a list with 6 elements:
```python
[timestamp_ms, open, high, low, close, volume]
```

**Example:**
```python
[1704067200000, 2063.45, 2065.12, 2062.88, 2064.23, 1250000.0]
```

- `timestamp_ms`: UTC milliseconds since Unix epoch (1970-01-01 00:00:00 UTC)
- `open`: Opening price
- `high`: Highest price in the period
- `low`: Lowest price in the period
- `close`: Closing price
- `volume`: Trading volume (in base units)

### Convert to Dictionary Format

```python
from sample_bar_downloader_utc import download_bars, bars_to_dict_list

bars = download_bars('btcusd', from_date, to_date, timeframe='h4')

# Convert to dict for easier access
bars_dict = bars_to_dict_list(bars)

for bar in bars_dict[:3]:
    print(f"Time: {bar['datetime_utc']}")
    print(f"OHLC: {bar['open']}, {bar['high']}, {bar['low']}, {bar['close']}")
    print(f"Volume: {bar['volume']}")
    print()
```

### Save to CSV

```python
from sample_bar_downloader_utc import download_bars, save_bars_to_csv

bars = download_bars('eurusd', from_date, to_date, timeframe='d1')

# Save to CSV file
save_bars_to_csv(bars, 'eurusd_daily.csv')
```

**CSV Output:**
```csv
timestamp_utc_ms,datetime_utc,open,high,low,close,volume
1704067200000,2024-01-01 00:00:00,1.10450,1.10523,1.10398,1.10456,125000000.0
```

## 📋 Available Timeframes

| Timeframe | Description | Code |
|-----------|-------------|------|
| 1 minute | M1 | `'m1'` |
| 5 minutes | M5 | `'m5'` |
| 15 minutes | M15 | `'m15'` |
| 30 minutes | M30 | `'m30'` |
| 1 hour | H1 | `'h1'` |
| 4 hours | H4 | `'h4'` |
| 1 day | D1 | `'d1'` |

## 🎯 Available Instruments

### Forex Majors
`eurusd`, `gbpusd`, `usdjpy`, `usdchf`, `audusd`, `usdcad`, `nzdusd`, `eurgbp`

### Metals
`xauusd` (Gold), `xagusd` (Silver)

### Cryptocurrencies
`btcusd` (Bitcoin), `ethusd` (Ethereum), `ltcusd` (Litecoin)

### Indices
`usa500idxusd` (S&P 500), `usa30idxusd` (Dow Jones), `usatechidxusd` (NASDAQ)

### Commodities
`lightcmdusd` (Light Crude Oil), `brentcmdusd` (Brent Crude Oil), `gascmdusd` (Natural Gas)

## 🔧 Function Reference

### `download_bars()`

Main function to download OHLC bar data.

```python
def download_bars(
    instrument: str,           # e.g., 'xauusd', 'btcusd'
    from_date: datetime,       # Start date (UTC)
    to_date: datetime,         # End date (UTC)
    timeframe: str = 'h1',     # 'm1', 'm5', 'm15', 'm30', 'h1', 'h4', 'd1'
    price_type: str = 'bid',   # 'bid' or 'ask'
    ignore_zero_volume: bool = True,  # Skip bars with zero volume
    verbose: bool = True       # Print progress
) -> List[List[float]]
```

**Returns:** List of bars `[[timestamp, open, high, low, close, volume], ...]`

### `bars_to_dict_list()`

Convert bars to list of dictionaries.

```python
def bars_to_dict_list(bars: List[List[float]]) -> List[dict]
```

**Returns:** List of dicts with keys: `timestamp`, `datetime_utc`, `open`, `high`, `low`, `close`, `volume`

### `save_bars_to_csv()`

Save bars to CSV file.

```python
def save_bars_to_csv(bars: List[List[float]], filename: str)
```

## 💡 Usage Examples

### Example 1: Download and Analyze

```python
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

# Download daily bars for EUR/USD
bars = download_bars(
    instrument='eurusd',
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 12, 31, tzinfo=timezone.utc),
    timeframe='d1',
    price_type='bid'
)

# Calculate average daily range
daily_ranges = [(h - l) for _, _, h, l, _, _ in bars]
avg_range = sum(daily_ranges) / len(daily_ranges)
print(f"Average daily range: {avg_range:.5f}")

# Find highest high and lowest low
highest = max(bar[2] for bar in bars)  # bar[2] is high
lowest = min(bar[3] for bar in bars)   # bar[3] is low
print(f"Year range: {lowest:.5f} - {highest:.5f}")
```

### Example 2: Create Pandas DataFrame

```python
import pandas as pd
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars, bars_to_dict_list

# Download bars
bars = download_bars('btcusd', 
                    datetime(2024, 1, 1, tzinfo=timezone.utc),
                    datetime(2024, 1, 31, tzinfo=timezone.utc),
                    timeframe='h4')

# Convert to DataFrame
bars_dict = bars_to_dict_list(bars)
df = pd.DataFrame(bars_dict)
df.set_index('datetime_utc', inplace=True)

print(df.head())
print(f"\nStats:\n{df[['open', 'high', 'low', 'close']].describe()}")
```

### Example 3: Multiple Instruments

```python
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

instruments = ['eurusd', 'gbpusd', 'usdjpy']
from_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
to_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

data = {}
for instrument in instruments:
    print(f"\nDownloading {instrument.upper()}...")
    bars = download_bars(instrument, from_date, to_date, timeframe='d1')
    data[instrument] = bars
    print(f"  Got {len(bars)} daily bars")

# Now you have all data in the 'data' dictionary
```

### Example 4: Real-time Update Pattern

```python
from datetime import datetime, timezone, timedelta
from sample_bar_downloader_utc import download_bars

# Download last 7 days, update daily
def get_recent_data(instrument, days=7):
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=days)
    
    bars = download_bars(
        instrument=instrument,
        from_date=from_date,
        to_date=to_date,
        timeframe='h1',
        verbose=False
    )
    
    return bars

# Use in your trading bot
gold_bars = get_recent_data('xauusd', days=7)
print(f"Latest gold bar: {gold_bars[-1]}")
```

## ⏰ Understanding UTC Timestamps

All timestamps in this implementation are:
- **UTC timezone** (Coordinated Universal Time)
- **Milliseconds** since Unix epoch (January 1, 1970, 00:00:00 UTC)

### Converting Timestamps

```python
from datetime import datetime, timezone

# Timestamp to datetime
ts_ms = 1704067200000
dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
print(dt)  # 2024-01-01 00:00:00+00:00

# Datetime to timestamp
dt = datetime(2024, 1, 1, 12, 30, tzinfo=timezone.utc)
ts_ms = int(dt.timestamp() * 1000)
print(ts_ms)  # 1704112200000
```

### Why UTC?

1. **No DST confusion** - UTC doesn't have daylight saving time
2. **Unambiguous** - One standard for all locations
3. **Easy conversion** - Convert to local time only when displaying
4. **Standard for finance** - Market data is typically in UTC

## 🧪 Testing

Run the included test:

```bash
python test_sample_downloader.py
```

This will:
1. Download a small dataset
2. Verify timestamps are UTC
3. Test dict conversion
4. Test CSV export

## 📊 Data Quality Notes

1. **Missing Data**: Some instruments/dates may have no data (returns empty list)
2. **Zero Volume Bars**: By default, zero-volume bars are filtered out
3. **Market Hours**: Forex is 24/5, crypto is 24/7, indices follow exchange hours
4. **Aggregation**: Higher timeframes (H4, D1) are aggregated from M1 data

## 🔍 Troubleshooting

### No Data Returned

```python
bars = download_bars('xauusd', from_date, to_date, timeframe='h1')
if not bars:
    print("No data available for this period")
    # Possible reasons:
    # 1. Weekend (forex markets closed)
    # 2. Very recent data (not yet available)
    # 3. Invalid date range
```

### Slow Downloads

```python
# For large date ranges, use higher timeframes
# BAD: Downloading 1 year of M1 data (slow)
# GOOD: Downloading 1 year of D1 data (fast)

# Or download in chunks
from datetime import timedelta

def download_in_chunks(instrument, from_date, to_date, chunk_days=30):
    all_bars = []
    current = from_date
    
    while current < to_date:
        chunk_end = min(current + timedelta(days=chunk_days), to_date)
        bars = download_bars(instrument, current, chunk_end, timeframe='h1')
        all_bars.extend(bars)
        current = chunk_end
    
    return all_bars
```

### Connection Errors

The downloader includes automatic retry logic (3 attempts by default). If you still have issues:

```python
# Increase timeout in the code:
# In download_and_decompress() function, change:
response = requests.get(url, timeout=60)  # Increase from 30 to 60 seconds
```

## 📝 Integration Checklist

When integrating into your project:

- [ ] Copy `sample_bar_downloader_utc.py` to your project
- [ ] Install `requests` package
- [ ] Test with small date range first
- [ ] Verify timestamps are in UTC
- [ ] Handle empty results (no data)
- [ ] Add error handling for network issues
- [ ] Consider caching for repeated requests

## 🔗 Related Files

- `dukascopy_downloader.py` - Full-featured implementation with more options
- `test_sample_downloader.py` - Test script
- `requirements_dukascopy.txt` - Dependencies

## 📄 License

MIT License - Free to use in your projects

## 🤝 Support

This is a standalone implementation based on the dukascopy-node project. 

For issues or questions:
1. Check the code comments in `sample_bar_downloader_utc.py`
2. Review the examples in this README
3. Test with `test_sample_downloader.py`

## 🎓 How It Works

1. **URL Generation** - Creates URLs to Dukascopy's data feed based on instrument and dates
2. **Download** - Fetches `.bi5` files (LZMA compressed binary)
3. **Decompression** - Extracts using Python's `lzma` module
4. **Parsing** - Unpacks binary data using `struct` module
5. **Normalization** - Converts integers to decimal prices
6. **Aggregation** - Combines M1 bars into higher timeframes if needed
7. **Output** - Returns as list of lists (timestamp, OHLC, volume)

All date/time operations use UTC timezone to ensure consistency.

---

**Ready to use in production!** 🚀

