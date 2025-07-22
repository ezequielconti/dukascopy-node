const fs = require('fs');

// Read both files
const regularData = fs.readFileSync('download/xauusd-m1-2015-regular.csv', 'utf8')
    .split('\n')
    .slice(1) // Skip header
    .filter(line => line.trim())
    .map(line => {
        const [timestamp, open, high, low, close, volume] = line.split(',');
        return {
            timestamp: parseInt(timestamp),
            open: parseFloat(open),
            high: parseFloat(high),
            low: parseFloat(low),
            close: parseFloat(close),
            volume: parseFloat(volume)
        };
    });

const tickVolumeData = fs.readFileSync('download/xauusd-m1-2015-tick-volume.csv', 'utf8')
    .split('\n')
    .slice(1) // Skip header
    .filter(line => line.trim())
    .map(line => {
        const [timestamp, open, high, low, close, volume] = line.split(',');
        return {
            timestamp: parseInt(timestamp),
            open: parseFloat(open),
            high: parseFloat(high),
            low: parseFloat(low),
            close: parseFloat(close),
            volume: parseFloat(volume)
        };
    });

console.log('=== 2015 Data Consistency Test ===\n');

// Basic statistics
console.log('File Statistics:');
console.log(`Regular data: ${regularData.length} candles`);
console.log(`Tick-volume data: ${tickVolumeData.length} candles`);
console.log(`Difference: ${Math.abs(regularData.length - tickVolumeData.length)} candles`);

// Data range analysis
const regularStart = new Date(regularData[0].timestamp);
const regularEnd = new Date(regularData[regularData.length - 1].timestamp);
const tickStart = new Date(tickVolumeData[0].timestamp);
const tickEnd = new Date(tickVolumeData[tickVolumeData.length - 1].timestamp);

console.log('\nData Range:');
console.log(`Regular: ${regularStart.toISOString()} to ${regularEnd.toISOString()}`);
console.log(`Tick-volume: ${tickStart.toISOString()} to ${tickEnd.toISOString()}`);

// Find overlapping timestamps
const regularTimestamps = new Set(regularData.map(d => d.timestamp));
const tickTimestamps = new Set(tickVolumeData.map(d => d.timestamp));

const overlappingTimestamps = Array.from(regularTimestamps).filter(ts => tickTimestamps.has(ts)).sort();
const regularOnlyTimestamps = Array.from(regularTimestamps).filter(ts => !tickTimestamps.has(ts)).sort();
const tickOnlyTimestamps = Array.from(tickTimestamps).filter(ts => !regularTimestamps.has(ts)).sort();

console.log('\nTimestamp Analysis:');
console.log(`Overlapping timestamps: ${overlappingTimestamps.length}`);
console.log(`Regular only: ${regularOnlyTimestamps.length}`);
console.log(`Tick-volume only: ${tickOnlyTimestamps.length}`);

if (regularOnlyTimestamps.length > 0) {
    console.log('\nFirst 5 regular-only timestamps:');
    regularOnlyTimestamps.slice(0, 5).forEach(ts => {
        console.log(`  ${new Date(ts).toISOString()}`);
    });
}

if (tickOnlyTimestamps.length > 0) {
    console.log('\nFirst 5 tick-only timestamps:');
    tickOnlyTimestamps.slice(0, 5).forEach(ts => {
        console.log(`  ${new Date(ts).toISOString()}`);
    });
}

// Create maps for easy lookup
const regularMap = new Map(regularData.map(d => [d.timestamp, d]));
const tickMap = new Map(tickVolumeData.map(d => [d.timestamp, d]));

// Compare OHLC values for overlapping timestamps
console.log('\n=== OHLC Comparison for Overlapping Timestamps ===');

let ohlcMatches = 0;
let ohlcDifferences = 0;
const differences = [];

overlappingTimestamps.forEach(timestamp => {
    const regular = regularMap.get(timestamp);
    const tick = tickMap.get(timestamp);

    const openMatch = Math.abs(regular.open - tick.open) < 0.001;
    const highMatch = Math.abs(regular.high - tick.high) < 0.001;
    const lowMatch = Math.abs(regular.low - tick.low) < 0.001;
    const closeMatch = Math.abs(regular.close - tick.close) < 0.001;

    if (openMatch && highMatch && lowMatch && closeMatch) {
        ohlcMatches++;
    } else {
        ohlcDifferences++;
        if (differences.length < 10) {
            differences.push({
                timestamp: new Date(timestamp).toISOString(),
                regular: { open: regular.open, high: regular.high, low: regular.low, close: regular.close },
                tick: { open: tick.open, high: tick.high, low: tick.low, close: tick.close }
            });
        }
    }
});

console.log(`OHLC matches: ${ohlcMatches}`);
console.log(`OHLC differences: ${ohlcDifferences}`);

if (differences.length > 0) {
    console.log('\nFirst 10 OHLC differences:');
    differences.forEach(diff => {
        console.log(`  ${diff.timestamp}:`);
        console.log(`    Regular: O=${diff.regular.open}, H=${diff.regular.high}, L=${diff.regular.low}, C=${diff.regular.close}`);
        console.log(`    Tick:    O=${diff.tick.open}, H=${diff.tick.high}, L=${diff.tick.low}, C=${diff.tick.close}`);
    });
}

// Volume comparison
console.log('\n=== Volume Comparison ===');
console.log('Regular volumes (first 5):');
regularData.slice(0, 5).forEach(d => {
    console.log(`  ${new Date(d.timestamp).toISOString()}: ${d.volume}`);
});

console.log('\nTick volumes (first 5):');
tickVolumeData.slice(0, 5).forEach(d => {
    console.log(`  ${new Date(d.timestamp).toISOString()}: ${d.volume}`);
});

// Simple volume statistics (avoiding stack overflow)
let regularMin = Infinity, regularMax = -Infinity, regularSum = 0;
let tickMin = Infinity, tickMax = -Infinity, tickSum = 0;

regularData.forEach(d => {
    regularMin = Math.min(regularMin, d.volume);
    regularMax = Math.max(regularMax, d.volume);
    regularSum += d.volume;
});

tickVolumeData.forEach(d => {
    tickMin = Math.min(tickMin, d.volume);
    tickMax = Math.max(tickMax, d.volume);
    tickSum += d.volume;
});

console.log('\nVolume Statistics:');
console.log(`Regular volume range: ${regularMin} to ${regularMax}`);
console.log(`Tick volume range: ${tickMin} to ${tickMax}`);
console.log(`Regular volume avg: ${(regularSum / regularData.length).toFixed(6)}`);
console.log(`Tick volume avg: ${(tickSum / tickVolumeData.length).toFixed(2)}`);

// Summary
console.log('\n=== Summary ===');
console.log(`✅ Feature working: ${ohlcDifferences === 0 ? 'YES' : 'NO'}`);
console.log(`📊 Data coverage: ${((overlappingTimestamps.length / regularData.length) * 100).toFixed(1)}%`);
console.log(`🔍 OHLC accuracy: ${overlappingTimestamps.length > 0 ? ((ohlcMatches / overlappingTimestamps.length) * 100).toFixed(1) : 0}%`);

if (ohlcDifferences === 0) {
    console.log('\n🎉 PERFECT SUCCESS: All overlapping OHLC values are identical!');
} else {
    console.log('\n⚠️  WARNING: Some OHLC values differ between sources.');
    console.log(`   Differences: ${ohlcDifferences} out of ${overlappingTimestamps.length} (${(ohlcDifferences / overlappingTimestamps.length * 100).toFixed(3)}%)`);
} 