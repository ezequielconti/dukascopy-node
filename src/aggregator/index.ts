import {
  getOHLC,
  getMinuteOHLCfromTicks,
  getMonthlyOHLCfromDays,
  getSecondOHLCfromTicks
} from './ohlc';
import { splitArrayInChunks } from '../utils/general';
import { AggregateInput } from './types';
import { Timeframe } from '../config/timeframes';

export function aggregate({
  data,
  fromTimeframe,
  toTimeframe,
  priceType,
  ignoreFlats,
  startTs,
  volumes,
  volumeMode
}: AggregateInput): number[][] {
  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.tick) {
    // ignoring of flats is skipped for tick data
    return data;
  }

  if (fromTimeframe === Timeframe.m1 && toTimeframe === Timeframe.m1) {
    if (ignoreFlats) {
      return data.filter(item => item[5] !== 0);
    }
    return data;
  }

  if (fromTimeframe === toTimeframe) {
    return splitArrayInChunks(data, 1).map(d =>
      getOHLC({ input: d, filterFlats: ignoreFlats, volumes })
    );
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.s1) {
    return getSecondOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.m1) {
    return getMinuteOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.m5) {
    return getMinuteOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.m15) {
    return getMinuteOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.m30) {
    return getMinuteOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.h1) {
    return getMinuteOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.h4) {
    return getMinuteOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.d1) {
    return getMinuteOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.tick && toTimeframe === Timeframe.mn1) {
    return getMinuteOHLCfromTicks(data, priceType, startTs, volumes, volumeMode);
  }

  if (fromTimeframe === Timeframe.d1 && toTimeframe === Timeframe.mn1) {
    return getMonthlyOHLCfromDays(data, volumes);
  }

  return data;
}
