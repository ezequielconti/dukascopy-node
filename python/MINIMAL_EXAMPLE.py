#!/usr/bin/env python3
"""
MINIMAL EXAMPLE - Copy this to get started fast!

This is the absolute minimum code you need to download bars.
Just 10 lines of actual code!
"""

from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

# Download bars (UTC) - That's it!
bars = download_bars(
    instrument='xauusd',
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 7, tzinfo=timezone.utc),
    timeframe='h1'
)

# Use the data
print(f"Downloaded {len(bars)} bars\n")

for i, bar in enumerate(bars[:5]):
    timestamp_ms, open_price, high, low, close, volume = bar
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    print(f"Bar {i+1}: {dt.strftime('%Y-%m-%d %H:%M')} UTC | "
          f"O:{open_price:.2f} H:{high:.2f} L:{low:.2f} C:{close:.2f}")

print(f"\n✓ Done! All timestamps are UTC.")


# =============================================================================
# COPY-PASTE THIS TO YOUR PROJECT:
# =============================================================================

"""
from datetime import datetime, timezone
from sample_bar_downloader_utc import download_bars

# Download
bars = download_bars(
    'xauusd',  # instrument
    datetime(2024, 1, 1, tzinfo=timezone.utc),  # from
    datetime(2024, 1, 31, tzinfo=timezone.utc),  # to
    'h1'  # timeframe
)

# Use
for bar in bars:
    ts, o, h, l, c, v = bar
    # Your code here
"""

