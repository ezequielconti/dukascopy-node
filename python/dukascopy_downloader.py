#!/usr/bin/env python3
"""
Dukascopy Historical Data Downloader

A Python implementation of dukascopy-node functionality for downloading
historical market data (tick, candle) from Dukascopy's free data feed.

Author: Python port of dukascopy-node
License: MIT
"""

import struct
import lzma
import csv
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import time
import sys


# ============================================================================
# INSTRUMENT METADATA
# ============================================================================

INSTRUMENT_METADATA = {
    # Forex Majors
    "eurusd": {"name": "EUR/USD", "decimal_factor": 100000, "description": "Euro vs US Dollar"},
    "gbpusd": {"name": "GBP/USD", "decimal_factor": 100000, "description": "British Pound vs US Dollar"},
    "usdjpy": {"name": "USD/JPY", "decimal_factor": 1000, "description": "US Dollar vs Japanese Yen"},
    "usdchf": {"name": "USD/CHF", "decimal_factor": 100000, "description": "US Dollar vs Swiss Franc"},
    "audusd": {"name": "AUD/USD", "decimal_factor": 100000, "description": "Australian Dollar vs US Dollar"},
    "usdcad": {"name": "USD/CAD", "decimal_factor": 100000, "description": "US Dollar vs Canadian Dollar"},
    "nzdusd": {"name": "NZD/USD", "decimal_factor": 100000, "description": "New Zealand Dollar vs US Dollar"},
    
    # Forex Metals
    "xauusd": {"name": "XAU/USD", "decimal_factor": 1000, "description": "Spot gold"},
    "xagusd": {"name": "XAG/USD", "decimal_factor": 100000, "description": "Spot silver"},
    
    # Crypto
    "btcusd": {"name": "BTC/USD", "decimal_factor": 1000, "description": "Bitcoin vs US Dollar"},
    "ethusd": {"name": "ETH/USD", "decimal_factor": 1000, "description": "Ether vs US Dollar"},
    "ltcusd": {"name": "LTC/USD", "decimal_factor": 1000, "description": "Litecoin vs US Dollar"},
    "bchusd": {"name": "BCH/USD", "decimal_factor": 1000, "description": "Bitcoin Cash vs US dollar"},
    
    # Commodities
    "lightcmdusd": {"name": "Light Crude Oil", "decimal_factor": 1000, "description": "US Light Crude Oil"},
    "brentcmdusd": {"name": "Brent Crude Oil", "decimal_factor": 1000, "description": "US Brent Crude Oil"},
    "gascmdusd": {"name": "Natural Gas", "decimal_factor": 1000, "description": "Natural Gas"},
    
    # Indices
    "usa500idxusd": {"name": "S&P 500", "decimal_factor": 100, "description": "S&P 500 Index"},
    "usa30idxusd": {"name": "Dow Jones", "decimal_factor": 100, "description": "Dow Jones Industrial Average"},
    "usatechidxusd": {"name": "NASDAQ", "decimal_factor": 100, "description": "NASDAQ 100"},
}


# ============================================================================
# CONFIGURATION
# ============================================================================

class DukascopyConfig:
    """Configuration for Dukascopy data download"""
    
    URL_ROOT = "https://datafeed.dukascopy.com/datafeed"
    
    TIMEFRAMES = {
        'tick': 'tick',
        's1': 's1',
        'm1': 'm1',
        'm5': 'm5',
        'm15': 'm15',
        'm30': 'm30',
        'h1': 'h1',
        'h4': 'h4',
        'd1': 'd1',
        'mn1': 'mn1'
    }
    
    PRICE_TYPES = ['bid', 'ask']
    
    # Struct formats for binary data unpacking
    TICK_FORMAT = '>3i2f'  # Big-endian: 3 integers, 2 floats
    CANDLE_FORMAT = '>5i1f'  # Big-endian: 5 integers, 1 float
    
    # Default values
    DEFAULT_BATCH_SIZE = 10
    DEFAULT_BATCH_PAUSE_MS = 1000
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_RETRY_PAUSE_MS = 500


# ============================================================================
# URL GENERATOR
# ============================================================================

class URLGenerator:
    """Generates Dukascopy data URLs based on instrument, timeframe, and date range"""
    
    def __init__(self, instrument: str, price_type: str = 'bid'):
        self.instrument = instrument.upper()
        self.price_type = price_type.upper()
    
    def _pad(self, num: int, length: int = 2) -> str:
        """Pad number with zeros"""
        return str(num).zfill(length)
    
    def _get_url(self, date: datetime, range_type: str) -> str:
        """Generate single URL for given date and range type"""
        year = self._pad(date.year, 4)
        month = self._pad(date.month, 2)
        day = self._pad(date.day, 2)
        hour = self._pad(date.hour, 2)
        
        base_url = f"{DukascopyConfig.URL_ROOT}/{self.instrument}/{year}/"
        
        if range_type == 'year':
            return f"{base_url}{self.price_type}_candles_day_1.bi5"
        elif range_type == 'month':
            return f"{base_url}{month}/{self.price_type}_candles_hour_1.bi5"
        elif range_type == 'day':
            return f"{base_url}{month}/{day}/{self.price_type}_candles_min_1.bi5"
        elif range_type == 'hour':
            return f"{base_url}{month}/{day}/{hour}h_ticks.bi5"
        
        return ""
    
    def _get_start_of_utc(self, date: datetime, period: str, offset: int = 0) -> datetime:
        """Get start of period in UTC"""
        if period == 'hour':
            return datetime(date.year, date.month, date.day, date.hour, 0, 0, tzinfo=timezone.utc) + timedelta(hours=offset)
        elif period == 'day':
            return datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=timezone.utc) + timedelta(days=offset)
        elif period == 'month':
            month = date.month + offset
            year = date.year
            while month > 12:
                month -= 12
                year += 1
            while month < 1:
                month += 12
                year -= 1
            return datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        elif period == 'year':
            return datetime(date.year + offset, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        return date
    
    def _is_current_range(self, range_type: str, date: datetime) -> bool:
        """Check if date is in current range"""
        now = datetime.now(timezone.utc)
        
        if range_type == 'year':
            return date.year == now.year
        elif range_type == 'month':
            return date.year == now.year and date.month == now.month
        elif range_type == 'day':
            return date.year == now.year and date.month == now.month and date.day == now.day
        elif range_type == 'hour':
            return (date.year == now.year and date.month == now.month and 
                    date.day == now.day and date.hour == now.hour)
        
        return False
    
    def _get_lower_range(self, range_type: str) -> Optional[str]:
        """Get next lower range type"""
        ranges = ['year', 'month', 'day', 'hour']
        try:
            idx = ranges.index(range_type)
            return ranges[idx + 1] if idx + 1 < len(ranges) else None
        except ValueError:
            return None
    
    def _construct_urls(self, range_type: str, start_date: datetime, end_date: datetime) -> List[str]:
        """Recursively construct URLs for date range"""
        urls = []
        temp_date = self._get_start_of_utc(start_date, range_type)
        
        while temp_date < end_date:
            if self._is_current_range(range_type, temp_date):
                # If current range, go to lower granularity
                lower_range = self._get_lower_range(range_type)
                if lower_range:
                    urls.extend(self._construct_urls(lower_range, temp_date, end_date))
                else:
                    urls.append(self._get_url(temp_date, range_type))
            else:
                urls.append(self._get_url(temp_date, range_type))
            
            temp_date = self._get_start_of_utc(temp_date, range_type, 1)
        
        return urls
    
    def _get_closest_available_range(self, timeframe: str, start_date: datetime) -> str:
        """Get closest available range for timeframe"""
        now = datetime.now(timezone.utc)
        is_current_year = start_date.year == now.year
        is_current_month = is_current_year and start_date.month == now.month
        is_current_day = is_current_month and start_date.day == now.day
        
        range_map = {
            'mn1': ['year', 'month', 'day'],
            'd1': ['year', 'month', 'day'],
            'h4': ['month', 'day', 'hour'],
            'h1': ['month', 'day', 'hour'],
            'm30': ['day', 'hour'],
            'm15': ['day', 'hour'],
            'm5': ['day', 'hour'],
            'm1': ['day', 'hour'],
            'tick': ['hour'],
            's1': ['hour']
        }
        
        ranges = range_map.get(timeframe, ['day', 'hour'])
        
        for r in ranges:
            if r == 'year' and not is_current_year:
                return r
            elif r == 'month' and not is_current_month:
                return r
            elif r == 'day' and not is_current_day:
                return r
            elif r == 'hour':
                return r
        
        return 'hour'
    
    def generate_urls(self, timeframe: str, start_date: datetime, end_date: datetime) -> List[str]:
        """Generate all URLs for downloading data"""
        # Ensure dates are in UTC
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        
        # Adjust end date to not exceed current time
        now = datetime.now(timezone.utc)
        if end_date > now:
            end_date = now
        
        # Get starting range type
        range_type = self._get_closest_available_range(timeframe, start_date)
        
        # Generate URLs
        urls = self._construct_urls(range_type, start_date, end_date)
        
        return urls


# ============================================================================
# DATA FETCHER & DECOMPRESSOR
# ============================================================================

class DataFetcher:
    """Fetches and decompresses Dukascopy data files"""
    
    def __init__(self, batch_size: int = DukascopyConfig.DEFAULT_BATCH_SIZE,
                 batch_pause_ms: int = DukascopyConfig.DEFAULT_BATCH_PAUSE_MS,
                 retry_count: int = DukascopyConfig.DEFAULT_RETRY_COUNT,
                 retry_pause_ms: int = DukascopyConfig.DEFAULT_RETRY_PAUSE_MS,
                 verbose: bool = True):
        self.batch_size = batch_size
        self.batch_pause_ms = batch_pause_ms
        self.retry_count = retry_count
        self.retry_pause_ms = retry_pause_ms
        self.verbose = verbose
        self.session = requests.Session()
    
    def fetch_url(self, url: str) -> Optional[bytes]:
        """Fetch single URL with retry logic"""
        for attempt in range(self.retry_count + 1):
            try:
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 404:
                    # File doesn't exist (no data for this period)
                    return b''
                else:
                    if self.verbose and attempt < self.retry_count:
                        print(f"  Warning: Status {response.status_code} for {url}, retrying...")
                    
            except Exception as e:
                if self.verbose and attempt < self.retry_count:
                    print(f"  Error fetching {url}: {e}, retrying...")
            
            if attempt < self.retry_count:
                time.sleep(self.retry_pause_ms / 1000.0)
        
        if self.verbose:
            print(f"  Failed to fetch after {self.retry_count + 1} attempts: {url}")
        return None
    
    def fetch_urls(self, urls: List[str]) -> List[Tuple[str, bytes]]:
        """Fetch multiple URLs in batches"""
        results = []
        total = len(urls)
        
        for i in range(0, total, self.batch_size):
            batch = urls[i:i + self.batch_size]
            
            if self.verbose:
                print(f"Fetching batch {i // self.batch_size + 1}/{(total + self.batch_size - 1) // self.batch_size} "
                      f"({i + 1}-{min(i + len(batch), total)} of {total})")
            
            for url in batch:
                data = self.fetch_url(url)
                if data is not None:
                    results.append((url, data))
            
            # Pause between batches (except after last batch)
            if i + self.batch_size < total:
                time.sleep(self.batch_pause_ms / 1000.0)
        
        return results
    
    def decompress(self, data: bytes, timeframe: str) -> List[List[Any]]:
        """Decompress and parse binary data"""
        if not data or len(data) == 0:
            return []
        
        try:
            # Decompress LZMA
            decompressed = lzma.decompress(data)
            
            # Choose struct format based on timeframe
            if timeframe == 'tick':
                format_str = DukascopyConfig.TICK_FORMAT
            else:
                format_str = DukascopyConfig.CANDLE_FORMAT
            
            # Calculate record size
            record_size = struct.calcsize(format_str)
            
            # Unpack all records
            records = []
            for i in range(0, len(decompressed), record_size):
                chunk = decompressed[i:i + record_size]
                if len(chunk) == record_size:
                    unpacked = struct.unpack(format_str, chunk)
                    records.append(list(unpacked))
            
            return records
            
        except Exception as e:
            if self.verbose:
                print(f"  Error decompressing data: {e}")
            return []


# ============================================================================
# DATA NORMALIZER
# ============================================================================

class DataNormalizer:
    """Normalizes raw data to human-readable format"""
    
    def __init__(self, instrument: str):
        self.instrument = instrument.lower()
        self.metadata = INSTRUMENT_METADATA.get(self.instrument, {
            "name": instrument.upper(),
            "decimal_factor": 100000,
            "description": instrument.upper()
        })
        self.decimal_factor = self.metadata["decimal_factor"]
    
    def normalize_tick_data(self, data: List[List[Any]], start_ts: int, 
                           include_volumes: bool = True) -> List[List[Any]]:
        """Normalize tick data"""
        normalized = []
        
        for record in data:
            ms, ask, bid, ask_volume, bid_volume = record
            
            row = [
                ms + start_ts,  # timestamp
                ask / self.decimal_factor,  # askPrice
                bid / self.decimal_factor,  # bidPrice
            ]
            
            if include_volumes:
                # Volume units = "units" means multiply by 1,000,000
                row.append(ask_volume * 1000000)  # askVolume
                row.append(bid_volume * 1000000)  # bidVolume
            
            normalized.append(row)
        
        return normalized
    
    def normalize_candle_data(self, data: List[List[Any]], start_ts: int,
                             include_volumes: bool = True) -> List[List[Any]]:
        """Normalize candle (OHLC) data"""
        normalized = []
        
        for record in data:
            sec, open_price, close_price, low, high, volume = record
            
            row = [
                sec * 1000 + start_ts,  # timestamp (convert sec to ms)
                open_price / self.decimal_factor,  # open
                high / self.decimal_factor,  # high
                low / self.decimal_factor,  # low
                close_price / self.decimal_factor,  # close
            ]
            
            if include_volumes:
                # Volume units = "units" means multiply by 1,000,000
                row.append(volume * 1000000)  # volume
            
            normalized.append(row)
        
        return normalized


# ============================================================================
# DATA AGGREGATOR
# ============================================================================

class DataAggregator:
    """Aggregates data to different timeframes"""
    
    @staticmethod
    def aggregate_candles(data: List[List[Any]], from_timeframe: str, to_timeframe: str,
                         ignore_flats: bool = True, include_volumes: bool = True) -> List[List[Any]]:
        """Aggregate candle data from one timeframe to another"""
        
        # Timeframe multipliers (in minutes for minute-based timeframes)
        timeframe_minutes = {
            'm1': 1,
            'm5': 5,
            'm15': 15,
            'm30': 30,
            'h1': 60,
            'h4': 240,
            'd1': 1440,
        }
        
        if from_timeframe not in timeframe_minutes or to_timeframe not in timeframe_minutes:
            return data
        
        from_mins = timeframe_minutes[from_timeframe]
        to_mins = timeframe_minutes[to_timeframe]
        
        if to_mins <= from_mins:
            # Can't aggregate to smaller timeframe
            return data
        
        chunk_size = to_mins // from_mins
        aggregated = []
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            
            if not chunk:
                continue
            
            # Filter flats if requested
            if ignore_flats and include_volumes:
                chunk = [c for c in chunk if c[5] != 0]  # volume is at index 5
            
            if not chunk:
                continue
            
            # Calculate OHLC
            timestamp = chunk[0][0]
            open_price = chunk[0][1]
            high = max(c[2] for c in chunk)
            low = min(c[3] for c in chunk)
            close_price = chunk[-1][4]
            
            row = [timestamp, open_price, high, low, close_price]
            
            if include_volumes:
                volume = sum(c[5] for c in chunk)
                row.append(volume)
            
            aggregated.append(row)
        
        return aggregated


# ============================================================================
# CSV WRITER
# ============================================================================

class CSVWriter:
    """Writes data to CSV file"""
    
    @staticmethod
    def write_tick_data(filepath: Path, data: List[List[Any]], include_volumes: bool = True):
        """Write tick data to CSV"""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            if include_volumes:
                writer.writerow(['timestamp', 'askPrice', 'bidPrice', 'askVolume', 'bidVolume'])
            else:
                writer.writerow(['timestamp', 'askPrice', 'bidPrice'])
            
            # Write data
            writer.writerows(data)
    
    @staticmethod
    def write_candle_data(filepath: Path, data: List[List[Any]], include_volumes: bool = True):
        """Write candle data to CSV"""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            if include_volumes:
                writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            else:
                writer.writerow(['timestamp', 'open', 'high', 'low', 'close'])
            
            # Write data
            writer.writerows(data)


# ============================================================================
# MAIN DOWNLOADER CLASS
# ============================================================================

class DukascopyDownloader:
    """Main class for downloading Dukascopy historical data"""
    
    def __init__(self, 
                 instrument: str,
                 from_date: datetime,
                 to_date: datetime,
                 timeframe: str = 'd1',
                 price_type: str = 'bid',
                 batch_size: int = DukascopyConfig.DEFAULT_BATCH_SIZE,
                 batch_pause_ms: int = DukascopyConfig.DEFAULT_BATCH_PAUSE_MS,
                 retry_count: int = DukascopyConfig.DEFAULT_RETRY_COUNT,
                 retry_pause_ms: int = DukascopyConfig.DEFAULT_RETRY_PAUSE_MS,
                 ignore_flats: bool = True,
                 output_dir: str = './download',
                 custom_filename: Optional[str] = None,
                 verbose: bool = True):
        """
        Initialize Dukascopy Downloader
        
        Args:
            instrument: Trading instrument (e.g., 'xauusd', 'btcusd', 'eurusd')
            from_date: Start date (datetime object)
            to_date: End date (datetime object)
            timeframe: Timeframe ('tick', 's1', 'm1', 'm5', 'm15', 'm30', 'h1', 'h4', 'd1', 'mn1')
            price_type: Price type ('bid' or 'ask')
            batch_size: Number of parallel downloads per batch
            batch_pause_ms: Pause between batches in milliseconds
            retry_count: Number of retries for failed downloads
            retry_pause_ms: Pause between retries in milliseconds
            ignore_flats: Ignore candles with zero volume
            output_dir: Output directory for downloaded files
            custom_filename: Custom filename (without extension)
            verbose: Print progress messages
        """
        self.instrument = instrument.lower()
        self.from_date = from_date
        self.to_date = to_date
        self.timeframe = timeframe
        self.price_type = price_type
        self.batch_size = batch_size
        self.batch_pause_ms = batch_pause_ms
        self.retry_count = retry_count
        self.retry_pause_ms = retry_pause_ms
        self.ignore_flats = ignore_flats
        self.output_dir = Path(output_dir)
        self.custom_filename = custom_filename
        self.verbose = verbose
        
        # Validate inputs
        self._validate_inputs()
        
        # Initialize components
        self.url_generator = URLGenerator(self.instrument, self.price_type)
        self.data_fetcher = DataFetcher(batch_size, batch_pause_ms, retry_count, 
                                       retry_pause_ms, verbose)
        self.normalizer = DataNormalizer(self.instrument)
    
    def _validate_inputs(self):
        """Validate input parameters"""
        if self.instrument not in INSTRUMENT_METADATA:
            print(f"Warning: '{self.instrument}' not in known instruments. Using default decimal factor.")
        
        if self.timeframe not in DukascopyConfig.TIMEFRAMES:
            raise ValueError(f"Invalid timeframe: {self.timeframe}. "
                           f"Must be one of {list(DukascopyConfig.TIMEFRAMES.keys())}")
        
        if self.price_type not in DukascopyConfig.PRICE_TYPES:
            raise ValueError(f"Invalid price type: {self.price_type}. "
                           f"Must be one of {DukascopyConfig.PRICE_TYPES}")
        
        if self.from_date >= self.to_date:
            raise ValueError("from_date must be before to_date")
    
    def _get_output_filename(self) -> str:
        """Generate output filename"""
        if self.custom_filename:
            return f"{self.custom_filename}.csv"
        
        # Format dates
        from_str = self.from_date.strftime('%Y-%m-%d')
        to_str = self.to_date.strftime('%Y-%m-%d')
        
        if self.timeframe == 'tick':
            return f"{self.instrument}-{self.timeframe}-{from_str}-{to_str}.csv"
        else:
            return f"{self.instrument}-{self.timeframe}-{self.price_type}-{from_str}-{to_str}.csv"
    
    def _extract_start_timestamp(self, url: str) -> int:
        """Extract start timestamp from URL"""
        import re
        match = re.search(r'/(\d{4})/(\d{2})?/?(\d{2})?/?(\d{2})?h?_?', url)
        if match:
            year = int(match.group(1))
            month = int(match.group(2)) if match.group(2) else 1
            day = int(match.group(3)) if match.group(3) else 1
            hour = int(match.group(4)) if match.group(4) else 0
            
            dt = datetime(year, month, day, hour, 0, 0, tzinfo=timezone.utc)
            return int(dt.timestamp() * 1000)
        
        return int(self.from_date.timestamp() * 1000)
    
    def download(self) -> Path:
        """Download data and save to CSV"""
        start_time = time.time()
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Dukascopy Historical Data Downloader")
            print(f"{'='*70}")
            print(f"Instrument:  {self.instrument.upper()}")
            print(f"Timeframe:   {self.timeframe}")
            print(f"Price Type:  {self.price_type}")
            print(f"Date Range:  {self.from_date.strftime('%Y-%m-%d')} to {self.to_date.strftime('%Y-%m-%d')}")
            print(f"{'='*70}\n")
        
        # Generate URLs
        if self.verbose:
            print("Generating download URLs...")
        urls = self.url_generator.generate_urls(self.timeframe, self.from_date, self.to_date)
        
        if self.verbose:
            print(f"Generated {len(urls)} URLs to fetch\n")
        
        # Fetch data
        if self.verbose:
            print("Downloading data...")
        fetched_data = self.data_fetcher.fetch_urls(urls)
        
        if self.verbose:
            print(f"\nSuccessfully fetched {len(fetched_data)} files\n")
        
        # Process data
        if self.verbose:
            print("Processing and normalizing data...")
        
        all_normalized_data = []
        
        for url, raw_data in fetched_data:
            # Decompress
            decompressed = self.data_fetcher.decompress(raw_data, self.timeframe)
            
            if not decompressed:
                continue
            
            # Get start timestamp from URL
            start_ts = self._extract_start_timestamp(url)
            
            # Normalize
            if self.timeframe == 'tick':
                normalized = self.normalizer.normalize_tick_data(decompressed, start_ts, True)
            else:
                normalized = self.normalizer.normalize_candle_data(decompressed, start_ts, True)
            
            all_normalized_data.extend(normalized)
        
        # Sort by timestamp
        all_normalized_data.sort(key=lambda x: x[0])
        
        # Filter by date range
        from_ts = int(self.from_date.timestamp() * 1000)
        to_ts = int(self.to_date.timestamp() * 1000)
        all_normalized_data = [d for d in all_normalized_data if from_ts <= d[0] <= to_ts]
        
        if self.verbose:
            print(f"Total records: {len(all_normalized_data)}\n")
        
        # Write to CSV
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / self._get_output_filename()
        
        if self.verbose:
            print(f"Writing to {output_path}...")
        
        if self.timeframe == 'tick':
            CSVWriter.write_tick_data(output_path, all_normalized_data, True)
        else:
            CSVWriter.write_candle_data(output_path, all_normalized_data, True)
        
        elapsed = time.time() - start_time
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"✓ Download complete!")
            print(f"  File: {output_path}")
            print(f"  Size: {output_path.stat().st_size / 1024:.2f} KB")
            print(f"  Records: {len(all_normalized_data)}")
            print(f"  Time: {elapsed:.2f}s")
            print(f"{'='*70}\n")
        
        return output_path


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def download_tick_data(instrument: str, from_date: datetime, to_date: datetime,
                      price_type: str = 'bid', output_dir: str = './download',
                      **kwargs) -> Path:
    """
    Download tick data for an instrument
    
    Example:
        download_tick_data('xauusd', 
                          datetime(2025, 1, 1), 
                          datetime(2025, 1, 7))
    """
    downloader = DukascopyDownloader(
        instrument=instrument,
        from_date=from_date,
        to_date=to_date,
        timeframe='tick',
        price_type=price_type,
        output_dir=output_dir,
        **kwargs
    )
    return downloader.download()


def download_candle_data(instrument: str, from_date: datetime, to_date: datetime,
                        timeframe: str = 'm1', price_type: str = 'bid',
                        output_dir: str = './download', **kwargs) -> Path:
    """
    Download candle data for an instrument
    
    Example:
        download_candle_data('xauusd', 
                            datetime(2025, 1, 1), 
                            datetime(2025, 1, 31),
                            timeframe='h1',
                            price_type='bid')
    """
    downloader = DukascopyDownloader(
        instrument=instrument,
        from_date=from_date,
        to_date=to_date,
        timeframe=timeframe,
        price_type=price_type,
        output_dir=output_dir,
        **kwargs
    )
    return downloader.download()


# ============================================================================
# MAIN / EXAMPLES
# ============================================================================

def main():
    """Example usage"""
    
    # Example 1: Download tick data for XAUUSD (first week of 2025)
    print("Example 1: Downloading XAUUSD tick data for first week of 2025")
    download_tick_data(
        instrument='xauusd',
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 7),
        price_type='bid',
        output_dir='./download'
    )
    
    # Example 2: Download 1-hour candle data for BTCUSD
    print("\n\nExample 2: Downloading BTCUSD hourly data")
    download_candle_data(
        instrument='btcusd',
        from_date=datetime(2024, 1, 1),
        to_date=datetime(2024, 1, 31),
        timeframe='h1',
        price_type='bid',
        output_dir='./download'
    )
    
    # Example 3: Using the main class directly with custom settings
    print("\n\nExample 3: Custom download with specific settings")
    downloader = DukascopyDownloader(
        instrument='eurusd',
        from_date=datetime(2024, 12, 1),
        to_date=datetime(2024, 12, 7),
        timeframe='m5',
        price_type='ask',
        batch_size=5,              # Smaller batch size
        batch_pause_ms=2000,       # Longer pause between batches
        retry_count=5,             # More retries
        ignore_flats=True,         # Ignore zero-volume candles
        output_dir='./download',
        custom_filename='eurusd_custom',
        verbose=True
    )
    downloader.download()


if __name__ == '__main__':
    # Run examples
    main()
    
    """
    MORE USAGE EXAMPLES:
    
    # Basic tick data download
    from datetime import datetime
    from dukascopy_downloader import download_tick_data
    
    download_tick_data('xauusd', datetime(2025, 1, 1), datetime(2025, 1, 7))
    
    
    # Download minute candles
    from dukascopy_downloader import download_candle_data
    
    download_candle_data(
        'btcusd', 
        datetime(2024, 1, 1), 
        datetime(2024, 1, 31),
        timeframe='m1'
    )
    
    
    # Download with custom settings
    from dukascopy_downloader import DukascopyDownloader
    
    downloader = DukascopyDownloader(
        instrument='eurusd',
        from_date=datetime(2024, 1, 1),
        to_date=datetime(2024, 12, 31),
        timeframe='d1',
        price_type='bid',
        batch_size=15,
        batch_pause_ms=500,
        retry_count=3,
        output_dir='./my_data',
        verbose=True
    )
    output_file = downloader.download()
    print(f"Data saved to: {output_file}")
    
    
    # Available timeframes:
    #   'tick' - Tick data
    #   's1'   - 1 second
    #   'm1'   - 1 minute
    #   'm5'   - 5 minutes
    #   'm15'  - 15 minutes
    #   'm30'  - 30 minutes
    #   'h1'   - 1 hour
    #   'h4'   - 4 hours
    #   'd1'   - 1 day
    #   'mn1'  - 1 month
    
    # Available instruments (partial list):
    #   Forex: 'eurusd', 'gbpusd', 'usdjpy', 'usdchf', etc.
    #   Metals: 'xauusd', 'xagusd'
    #   Crypto: 'btcusd', 'ethusd', 'ltcusd', 'bchusd'
    #   Commodities: 'lightcmdusd', 'brentcmdusd', 'gascmdusd'
    #   Indices: 'usa500idxusd', 'usa30idxusd', 'usatechidxusd'
    """

