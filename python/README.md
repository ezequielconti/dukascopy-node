# Dukascopy Historical Data Downloader - Python Implementation

This directory contains a complete Python implementation of dukascopy-node for downloading historical market data.

## 📁 Files

- **`dukascopy_downloader.py`** - Main implementation (single file, ready to use)
- **`test_dukascopy.py`** - Test suite with working examples
- **`requirements_dukascopy.txt`** - Dependencies (just `requests`)

## 📚 Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - ⭐ Start here! Quick commands and examples
- **[README_PYTHON.md](README_PYTHON.md)** - Complete documentation
- **[PYTHON_IMPLEMENTATION_SUMMARY.md](PYTHON_IMPLEMENTATION_SUMMARY.md)** - Technical details

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_dukascopy.txt
```

### 2. Download Data
```python
from datetime import datetime
from dukascopy_downloader import download_tick_data, download_candle_data

# Download tick data
download_tick_data('xauusd', datetime(2025, 1, 1), datetime(2025, 1, 7))

# Download candle data
download_candle_data('btcusd', datetime(2024, 1, 1), datetime(2024, 1, 31), 
                     timeframe='h1')
```

### 3. Run Tests
```bash
python test_dukascopy.py
```

## ✨ Features

✅ Download tick data  
✅ Download candle data (all timeframes)  
✅ 600+ instruments supported  
✅ Automatic retry logic  
✅ CSV output with volumes  
✅ UTC timestamps  
✅ Single file, minimal dependencies  

## 📖 Example Usage

```python
from datetime import datetime
from dukascopy_downloader import DukascopyDownloader

# Download XAUUSD hourly data for 2024
downloader = DukascopyDownloader(
    instrument='xauusd',
    from_date=datetime(2024, 1, 1),
    to_date=datetime(2024, 12, 31),
    timeframe='h1',
    price_type='bid',
    output_dir='../download',
    verbose=True
)

output_file = downloader.download()
print(f"Data saved to: {output_file}")
```

## 📊 Output Format

**Tick Data CSV:**
```csv
timestamp,askPrice,bidPrice,askVolume,bidVolume
1735772400455,2626.592,2625.098,449.99999227,449.99999227
```

**Candle Data CSV:**
```csv
timestamp,open,high,low,close,volume
1704067200000,42250.5,42350.2,42200.1,42300.8,1250000.0
```

## 🔧 Integration

To use in your project:

1. Copy `dukascopy_downloader.py` to your project
2. Install `requests`: `pip install requests`
3. Import and use:
   ```python
   from dukascopy_downloader import download_tick_data
   ```

## 📝 Available Timeframes

- `'tick'` - Tick data (every quote update)
- `'s1'` - 1 second
- `'m1'` - 1 minute
- `'m5'` - 5 minutes
- `'m15'` - 15 minutes
- `'m30'` - 30 minutes
- `'h1'` - 1 hour
- `'h4'` - 4 hours
- `'d1'` - 1 day
- `'mn1'` - 1 month

## 🎯 Common Instruments

**Forex:** eurusd, gbpusd, usdjpy, usdchf, audusd, usdcad, nzdusd  
**Metals:** xauusd, xagusd  
**Crypto:** btcusd, ethusd, ltcusd, bchusd  
**Commodities:** lightcmdusd, brentcmdusd, gascmdusd  
**Indices:** usa500idxusd, usa30idxusd, usatechidxusd  

## 📖 More Information

See [README_PYTHON.md](README_PYTHON.md) for complete documentation including:
- All available parameters
- Performance tips
- Error handling
- Integration examples
- Troubleshooting

## 📞 Need Help?

Check these files in order:
1. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick examples
2. [README_PYTHON.md](README_PYTHON.md) - Full documentation
3. `dukascopy_downloader.py` - Source code with comments

## License

MIT License - Same as the original dukascopy-node project

