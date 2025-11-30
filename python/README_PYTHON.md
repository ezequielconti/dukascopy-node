# Dukascopy Historical Data Downloader (Python)

A pure Python implementation of dukascopy-node functionality for downloading historical market data (tick data and OHLC candles) from Dukascopy's free data feed.

## Features

✅ **Download tick data** - Get every market quote update  
✅ **Download candle data** - OHLC data at multiple timeframes  
✅ **Multiple timeframes** - tick, s1, m1, m5, m15, m30, h1, h4, d1, mn1  
✅ **600+ instruments** - Forex, Crypto, Commodities, Indices, Stocks  
✅ **Automatic retry logic** - Robust error handling  
✅ **Batch downloading** - Efficient parallel downloads  
✅ **CSV output** - Always outputs to CSV format  
✅ **Volume data** - Always includes volume in units  
✅ **UTC timestamps** - All timestamps in UTC

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the required dependency:

```bash
pip install -r requirements_dukascopy.txt
```

Or manually:
```bash
pip install requests
```

That's it! The script uses only standard library modules plus `requests`.

## Quick Start

### Example 1: Download Tick Data

```python
from datetime import datetime
from dukascopy_downloader import download_tick_data

# Download XAUUSD tick data for first week of 2025
download_tick_data(
    instrument='xauusd',
    from_date=datetime(2025, 1, 1),
    to_date=datetime(2025, 1, 7),
    price_type='bid',
    output_dir='./download'
)
```

Output CSV format:
```csv
timestamp,askPrice,bidPrice,askVolume,bidVolume
1735772400455,2626.592,2625.098,449.99999227,449.99999227
1735772400557,2626.482,2625.698,449.99999227,449.99999227
...
```

### Example 2: Download Candle Data

```python
from datetime import datetime
from dukascopy_downloader import download_candle_data

# Download BTCUSD hourly candles for January 2024
download_candle_data(
    instrument='btcusd',
    from_date=datetime(2024, 1, 1),
    to_date=datetime(2024, 1, 31),
    timeframe='h1',
    price_type='bid',
    output_dir='./download'
)
```

Output CSV format:
```csv
timestamp,open,high,low,close,volume
1704067200000,42250.5,42350.2,42200.1,42300.8,1250000.0
1704070800000,42300.8,42400.5,42280.0,42350.2,980000.0
...
```

### Example 3: Custom Settings

```python
from datetime import datetime
from dukascopy_downloader import DukascopyDownloader

# Create downloader with custom settings
downloader = DukascopyDownloader(
    instrument='eurusd',
    from_date=datetime(2024, 12, 1),
    to_date=datetime(2024, 12, 31),
    timeframe='m5',
    price_type='ask',
    batch_size=5,              # Smaller batch size
    batch_pause_ms=2000,       # Longer pause between batches
    retry_count=5,             # More retries
    retry_pause_ms=1000,       # Longer pause between retries
    ignore_flats=True,         # Ignore zero-volume candles
    output_dir='./my_data',
    custom_filename='eurusd_dec_2024',
    verbose=True
)

output_file = downloader.download()
print(f"Data saved to: {output_file}")
```

## Available Parameters

### Main Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `instrument` | str | **Required** | Trading instrument (e.g., 'xauusd', 'btcusd', 'eurusd') |
| `from_date` | datetime | **Required** | Start date |
| `to_date` | datetime | **Required** | End date |
| `timeframe` | str | `'d1'` | Data timeframe (see below) |
| `price_type` | str | `'bid'` | Price type: 'bid' or 'ask' |
| `output_dir` | str | `'./download'` | Output directory |
| `custom_filename` | str | `None` | Custom filename (without .csv extension) |

### Performance Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_size` | int | `10` | Number of parallel downloads per batch |
| `batch_pause_ms` | int | `1000` | Pause between batches (milliseconds) |
| `retry_count` | int | `3` | Number of retries for failed downloads |
| `retry_pause_ms` | int | `500` | Pause between retries (milliseconds) |

### Data Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ignore_flats` | bool | `True` | Ignore candles with zero volume |
| `verbose` | bool | `True` | Print progress messages |

## Available Timeframes

| Timeframe | Description |
|-----------|-------------|
| `'tick'` | Tick data (every quote update) |
| `'s1'` | 1 second candles |
| `'m1'` | 1 minute candles |
| `'m5'` | 5 minute candles |
| `'m15'` | 15 minute candles |
| `'m30'` | 30 minute candles |
| `'h1'` | 1 hour candles |
| `'h4'` | 4 hour candles |
| `'d1'` | Daily candles |
| `'mn1'` | Monthly candles |

## Available Instruments (Common)

### Forex Majors
- `'eurusd'`, `'gbpusd'`, `'usdjpy'`, `'usdchf'`, `'audusd'`, `'usdcad'`, `'nzdusd'`

### Forex Metals
- `'xauusd'` (Gold), `'xagusd'` (Silver)

### Cryptocurrencies
- `'btcusd'`, `'ethusd'`, `'ltcusd'`, `'bchusd'`

### Commodities
- `'lightcmdusd'` (Crude Oil), `'brentcmdusd'` (Brent Oil), `'gascmdusd'` (Natural Gas)

### Indices
- `'usa500idxusd'` (S&P 500), `'usa30idxusd'` (Dow Jones), `'usatechidxusd'` (NASDAQ)

**Note:** Over 600+ instruments are supported. See the original dukascopy-node README for the full list, or add them to the `INSTRUMENT_METADATA` dictionary in the Python file.

## Data Specifications

### Volume Units
- **Always in "units"** - Volume is multiplied by 1,000,000 to show actual units
- This matches the behavior when using `--volume-units units` in the Node.js version

### Timestamps
- **Always in UTC** - All timestamps are in UTC milliseconds since epoch
- Use Python's `datetime.fromtimestamp(ts/1000, tz=timezone.utc)` to convert

### CSV Format

**Tick Data:**
```csv
timestamp,askPrice,bidPrice,askVolume,bidVolume
```

**Candle Data:**
```csv
timestamp,open,high,low,close,volume
```

## Performance Tips

### For Tick Data
Tick data downloads can be large and slow. Recommended settings:

```python
download_tick_data(
    instrument='xauusd',
    from_date=datetime(2025, 1, 1),
    to_date=datetime(2025, 1, 2),  # Keep ranges small
    batch_size=5,                   # Smaller batches
    batch_pause_ms=2000,            # Longer pauses
    verbose=True
)
```

### For Large Date Ranges
For downloading months or years of data:

```python
download_candle_data(
    instrument='eurusd',
    from_date=datetime(2020, 1, 1),
    to_date=datetime(2024, 12, 31),
    timeframe='d1',
    batch_size=15,                  # Larger batches for faster download
    batch_pause_ms=500,             # Shorter pauses
    retry_count=5,                  # More retries for reliability
    verbose=True
)
```

## Class Structure

The implementation consists of several modular classes:

- **`DukascopyDownloader`** - Main class orchestrating the download
- **`URLGenerator`** - Generates Dukascopy data URLs
- **`DataFetcher`** - Fetches and decompresses binary data
- **`DataNormalizer`** - Normalizes raw data to readable format
- **`DataAggregator`** - Aggregates data between timeframes
- **`CSVWriter`** - Writes data to CSV files

You can use these classes independently if you need custom functionality.

## Error Handling

The downloader includes robust error handling:

1. **Automatic retries** - Failed downloads are retried automatically
2. **404 handling** - Missing data files (no trading on that period) are handled gracefully
3. **Data validation** - Inputs are validated before starting
4. **Progress feedback** - Verbose mode shows detailed progress

## Comparison with Node.js Version

### Included Features
✅ All core download functionality  
✅ All timeframes (tick through monthly)  
✅ Retry logic with configurable attempts  
✅ Batch downloading with pauses  
✅ Progress reporting  
✅ Date range filtering  
✅ Ignore flats option  

### Simplified (by design)
- **Format**: CSV only (no JSON/array)
- **Volumes**: Always included in units (no millions/thousands option)
- **Dates**: Always UTC (no timezone conversion or custom formats)
- **No caching**: Each download fetches fresh data
- **No tick volume mode**: No aggregation from tick to higher timeframes

These simplifications match your requirements and make the code more maintainable.

## Testing

Run the test suite:

```bash
python test_dukascopy.py
```

This will download small samples to verify everything works correctly.

## License

MIT License - Same as the original dukascopy-node project

## Credits

This is a Python port of [dukascopy-node](https://github.com/Leo4815162342/dukascopy-node) by Leo4815162342.

## Troubleshooting

### "No module named 'requests'"
Install the requests library:
```bash
pip install requests
```

### "Invalid timeframe" error
Check that your timeframe is one of: `'tick'`, `'s1'`, `'m1'`, `'m5'`, `'m15'`, `'m30'`, `'h1'`, `'h4'`, `'d1'`, `'mn1'`

### Downloads are slow
For tick data or large date ranges:
- Reduce `batch_size`
- Increase `batch_pause_ms`
- Download smaller date ranges

### Empty CSV file
The date range may have no trading data (weekends, holidays, or before instrument was listed). Try a different date range or check the instrument's data availability.

## Contributing

Feel free to extend the `INSTRUMENT_METADATA` dictionary with additional instruments or modify the code for your specific needs.

