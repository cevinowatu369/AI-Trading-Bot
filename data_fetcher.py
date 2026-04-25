#!/usr/bin/env python3
"""
DATA FETCHER - Utility for fetching and managing market data
Supports MT5 and other data sources

Author: AI Trading Bot
Date: 2026-04-25
"""

import os
import logging
from datetime import datetime, timedelta
import pandas as pd
import json

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging"""
    os.makedirs('./logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('./logs/data_fetcher.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# DATA FETCHER CLASS
# ============================================================================

class DataFetcher:
    """Fetch market data from various sources"""
    
    TIMEFRAME_MAP = {
        'M1': mt5.TIMEFRAME_M1 if mt5 else 1,
        'M5': mt5.TIMEFRAME_M5 if mt5 else 5,
        'M15': mt5.TIMEFRAME_M15 if mt5 else 15,
        'M30': mt5.TIMEFRAME_M30 if mt5 else 30,
        'H1': mt5.TIMEFRAME_H1 if mt5 else 60,
        'H4': mt5.TIMEFRAME_H4 if mt5 else 240,
        'D1': mt5.TIMEFRAME_D1 if mt5 else 1440,
        'W1': mt5.TIMEFRAME_W1 if mt5 else 10080,
    }
    
    def __init__(self, source='mt5'):
        """
        Initialize data fetcher
        
        Args:
            source: 'mt5', 'csv', or 'api'
        """
        self.source = source
        self.mt5_connected = False
        
        if source == 'mt5':
            self._connect_mt5()
    
    def _connect_mt5(self):
        """Connect to MetaTrader 5"""
        try:
            if mt5 is None:
                logger.error("MetaTrader5 library not installed")
                return False
            
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            logger.info("Connected to MetaTrader 5")
            self.mt5_connected = True
            return True
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
    
    def get_ohlc(self, symbol, timeframe, bars=100, start_date=None):
        """
        Fetch OHLC data
        
        Args:
            symbol: Trading instrument (e.g., 'XAUUSD')
            timeframe: Timeframe (M1, M5, H1, D1, etc.)
            bars: Number of bars to fetch
            start_date: Start date (datetime object, optional)
        
        Returns:
            DataFrame with OHLC data
        """
        if self.source == 'mt5':
            return self._fetch_from_mt5(symbol, timeframe, bars)
        elif self.source == 'csv':
            return self._fetch_from_csv(symbol)
        else:
            logger.error(f"Unknown data source: {self.source}")
            return None
    
    def _fetch_from_mt5(self, symbol, timeframe, bars):
        """Fetch data from MT5"""
        try:
            if not self.mt5_connected:
                logger.error("MT5 not connected")
                return None
            
            # Get timeframe enum
            tf_enum = self.TIMEFRAME_MAP.get(timeframe)
            if tf_enum is None:
                logger.error(f"Unknown timeframe: {timeframe}")
                return None
            
            # Fetch rates
            logger.info(f"Fetching {bars} bars of {symbol} {timeframe}...")
            rates = mt5.copy_rates_from_pos(symbol, tf_enum, 0, bars)
            
            if rates is None:
                logger.error(f"Failed to fetch data: {mt5.last_error()}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            df.rename(columns={
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'tick_volume': 'volume'
            }, inplace=True)
            
            logger.info(f"✓ Fetched {len(df)} bars")
            return df
        except Exception as e:
            logger.error(f"Error fetching from MT5: {e}")
            return None
    
    def _fetch_from_csv(self, filename):
        """Load data from CSV file"""
        try:
            df = pd.read_csv(filename, parse_dates=['time'], index_col='time')
            logger.info(f"✓ Loaded {len(df)} bars from {filename}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return None
    
    def save_to_csv(self, df, filename):
        """Save data to CSV file"""
        try:
            df.to_csv(filename)
            logger.info(f"✓ Data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        try:
            if self.mt5_connected:
                mt5.shutdown()
                logger.info("Disconnected from MT5")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def fetch_and_save_data(symbol='XAUUSD', timeframe='H1', bars=500, output_file=None):
    """
    Fetch data and optionally save to CSV
    
    Args:
        symbol: Trading instrument
        timeframe: Timeframe
        bars: Number of bars
        output_file: CSV filename to save
    """
    fetcher = DataFetcher(source='mt5')
    
    try:
        df = fetcher.get_ohlc(symbol, timeframe, bars)
        
        if df is not None:
            print(f"\n{symbol} {timeframe}")
            print(f"Bars: {len(df)}")
            print(f"Date Range: {df.index[0]} to {df.index[-1]}")
            print(f"\nLatest 5 bars:")
            print(df.tail())
            
            if output_file:
                fetcher.save_to_csv(df, output_file)
                print(f"\nData saved to {output_file}")
    finally:
        fetcher.disconnect()

if __name__ == "__main__":
    # Example usage
    fetch_and_save_data(
        symbol='XAUUSD',
        timeframe='H1',
        bars=500,
        output_file='xauusd_data.csv'
    )
