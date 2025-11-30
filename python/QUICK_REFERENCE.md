# Quick Reference - Python Dukascopy Downloader

## Installation
```bash
pip install requests
```

## Import
```python
from datetime import datetime
from dukascopy_downloader import download_tick_data, download_candle_data, DukascopyDownloader
```

## Quick Commands

### Your Original Request: XAUUSD Tick Data (First Week 2025)
```python
download_tick_data('xauusd', datetime(2025, 1, 1), datetime(2025, 1, 7))
```

### Common Use Cases

**1. Download Tick Data**
```python
download_tick_data('xauusd', datetime(2025, 1, 1), datetime(2025, 1, 7))
```

**2. Download 1-Minute Candles**
```python
download_candle_data('btcusd', datetime(2024, 1, 1), datetime(2024, 1, 31), timeframe='m1')
```

**3. Download Hourly Candles**
```python
download_candle_data('eurusd', datetime(2024, 1, 1), datetime(2024, 12, 31), timeframe='h1')
```

**4. Download Daily Candles**
```python
download_candle_data('xauusd', datetime(2020, 1, 1), datetime(2024, 12, 31), timeframe='d1')
```

**5. Download ASK Prices Instead of BID**
```python
download_candle_data('gbpusd', datetime(2024, 1, 1), datetime(2024, 12, 31), 
                     timeframe='h1', price_type='ask')
```

**6. Custom Output Directory**
```python
download_candle_data('btcusd', datetime(2024, 1, 1), datetime(2024, 1, 31),
                     timeframe='d1', output_dir='./my_data')
```

**7. Custom Filename**
```python
downloader = DukascopyDownloader(
    instrument='eurusd',
    from_date=datetime(2024, 1, 1),
    to_date=datetime(2024, 12, 31),
    timeframe='d1',
    output_dir='./data',
    custom_filename='eurusd_2024_daily'
)
downloader.download()
```

**8. Slow Download (Large Tick Data)**
```python
download_tick_data('xauusd', datetime(2025, 1, 1), datetime(2025, 1, 2),
                   batch_size=3, batch_pause_ms=3000)
```

**9. Fast Download (Small Date Range)**
```python
download_candle_data('eurusd', datetime(2024, 1, 1), datetime(2024, 12, 31),
                     timeframe='d1', batch_size=20, batch_pause_ms=500)
```

**10. Silent Mode (No Progress Output)**
```python
downloader = DukascopyDownloader(
    instrument='btcusd',
    from_date=datetime(2024, 1, 1),
    to_date=datetime(2024, 1, 31),
    timeframe='h1',
    verbose=False  # Silent mode
)
downloader.download()
```

## Timeframes
| Code | Description |
|------|-------------|
| `'tick'` | Every quote update |
| `'s1'` | 1 second |
| `'m1'` | 1 minute |
| `'m5'` | 5 minutes |
| `'m15'` | 15 minutes |
| `'m30'` | 30 minutes |
| `'h1'` | 1 hour |
| `'h4'` | 4 hours |
| `'d1'` | 1 day |
| `'mn1'` | 1 month |

## Common Instruments
| Symbol | Description |
|--------|-------------|
| `'xauusd'` | Gold |
| `'xagusd'` | Silver |
| `'btcusd'` | Bitcoin |
| `'ethusd'` | Ethereum |
| `'eurusd'` | EUR/USD |
| `'gbpusd'` | GBP/USD |
| `'usdjpy'` | USD/JPY |

## Parameters

### Essential
```python
instrument='xauusd'              # Required
from_date=datetime(2025, 1, 1)   # Required
to_date=datetime(2025, 1, 7)     # Required
timeframe='h1'                   # Default: 'd1'
price_type='bid'                 # Default: 'bid', Options: 'bid', 'ask'
```

### Performance
```python
batch_size=10                    # Default: 10 (parallel downloads)
batch_pause_ms=1000              # Default: 1000ms (pause between batches)
retry_count=3                    # Default: 3 (retry failed downloads)
retry_pause_ms=500               # Default: 500ms (pause between retries)
```

### Output
```python
output_dir='./download'          # Default: './download'
custom_filename='myfile'         # Default: auto-generated
ignore_flats=True                # Default: True (skip zero-volume candles)
verbose=True                     # Default: True (show progress)
```

## CSV Output Formats

### Tick Data
```csv
timestamp,askPrice,bidPrice,askVolume,bidVolume
1735772400455,2626.592,2625.098,449.99999227,449.99999227
```

### Candle Data
```csv
timestamp,open,high,low,close,volume
1704067200000,42250.5,42350.2,42200.1,42300.8,1250000.0
```

## Integration with Pandas

```python
import pandas as pd
from dukascopy_downloader import download_candle_data

# Download data
file = download_candle_data('xauusd', datetime(2024, 1, 1), datetime(2024, 12, 31), 
                            timeframe='d1', verbose=False)

# Load into DataFrame
df = pd.read_csv(file)

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
df.set_index('timestamp', inplace=True)

# Analyze
print(df.head())
print(df['close'].describe())
print(df['close'].rolling(20).mean())
```

## Common Patterns

### Download Multiple Instruments
```python
instruments = ['xauusd', 'xagusd', 'btcusd', 'ethusd']

for symbol in instruments:
    print(f"Downloading {symbol}...")
    download_candle_data(symbol, datetime(2024, 1, 1), datetime(2024, 12, 31),
                         timeframe='d1', verbose=False)
    print(f"✓ {symbol} complete\n")
```

### Download Multiple Timeframes
```python
timeframes = ['m1', 'm5', 'm15', 'h1', 'd1']

for tf in timeframes:
    print(f"Downloading {tf} data...")
    download_candle_data('eurusd', datetime(2024, 1, 1), datetime(2024, 1, 31),
                         timeframe=tf, verbose=False)
```

### Download Both Bid and Ask
```python
for price_type in ['bid', 'ask']:
    download_candle_data('gbpusd', datetime(2024, 1, 1), datetime(2024, 12, 31),
                         timeframe='h1', price_type=price_type,
                         custom_filename=f'gbpusd_2024_{price_type}',
                         verbose=False)
```

### Error Handling
```python
try:
    file = download_candle_data('xauusd', datetime(2024, 1, 1), datetime(2024, 12, 31),
                                timeframe='h1')
    print(f"Success! File: {file}")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

### For Tick Data (Large)
```python
# Use smaller batches and longer pauses
download_tick_data('xauusd', start, end,
                   batch_size=3,
                   batch_pause_ms=3000)
```

### For Large Date Ranges
```python
# Use larger batches and shorter pauses
download_candle_data('eurusd', start, end,
                     timeframe='d1',
                     batch_size=20,
                     batch_pause_ms=500)
```

### For Production (Reliable)
```python
# More retries, longer pauses
downloader = DukascopyDownloader(
    instrument='btcusd',
    from_date=start,
    to_date=end,
    timeframe='h1',
    retry_count=5,
    retry_pause_ms=1000,
    batch_size=10,
    verbose=False
)
```

## Command Line Usage

Save as `download.py`:
```python
#!/usr/bin/env python3
from datetime import datetime
from dukascopy_downloader import download_candle_data
import sys

if len(sys.argv) < 4:
    print("Usage: python download.py <instrument> <from_date> <to_date> [timeframe]")
    sys.exit(1)

instrument = sys.argv[1]
from_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
to_date = datetime.strptime(sys.argv[3], '%Y-%m-%d')
timeframe = sys.argv[4] if len(sys.argv) > 4 else 'h1'

download_candle_data(instrument, from_date, to_date, timeframe=timeframe)
```

Then run:
```bash
python download.py xauusd 2024-01-01 2024-12-31 h1
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty CSV | Try different date range or check instrument availability |
| Slow download | Reduce `batch_size`, increase `batch_pause_ms` |
| Connection errors | Increase `retry_count` and `retry_pause_ms` |
| Wrong prices | Check `price_type` is correct ('bid' or 'ask') |
| Missing module | Run `pip install requests` |

## File Locations

After running the examples, files will be in:
```
./download/
├── xauusd-tick-2025-01-01-2025-01-07.csv
├── btcusd-h1-bid-2024-01-01-2024-01-31.csv
├── eurusd-d1-bid-2024-01-01-2024-12-31.csv
└── ...
```

## Get Help
```python
help(DukascopyDownloader)
help(download_candle_data)
help(download_tick_data)
```

