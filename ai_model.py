#!/usr/bin/env python3
"""
LEVEL 2: AI MODEL (Trading Brain)
Generates BUY/SELL signals based on technical indicators

Author: AI Trading Bot
Date: 2026-04-25
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import json
import traceback

try:
    import MetaTrader5 as mt5
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    import yaml
except ImportError as e:
    print(f"Error: Required library not installed: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging system"""
    os.makedirs('./logs', exist_ok=True)
    
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('./logs/ai_model.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# CONFIGURATION
# ============================================================================

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        logger.info("Configuration loaded successfully")
        return config
    except FileNotFoundError:
        logger.error("config.yaml not found. Using defaults.")
        return {}
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

config = load_config()

# ============================================================================
# MT5 CONNECTION
# ============================================================================

class MT5Connection:
    """Manage MetaTrader 5 connection"""
    
    def __init__(self, config):
        self.config = config.get('mt5', {})
        self.connected = False
    
    def connect(self):
        """Connect to MT5"""
        try:
            # Initialize MT5
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            logger.info("MT5 initialized successfully")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        try:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5 disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting MT5: {e}")
    
    def get_rates(self, symbol, timeframe, bars=100):
        """Fetch OHLC data from MT5"""
        try:
            if not self.connected:
                logger.warning("MT5 not connected")
                return None
            
            # Get the timeframe enum
            tf_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            timeframe_enum = tf_map.get(timeframe, mt5.TIMEFRAME_M5)
            
            # Request data
            rates = mt5.copy_rates_from_pos(symbol, timeframe_enum, 0, bars)
            
            if rates is None:
                logger.error(f"Failed to fetch rates for {symbol}: {mt5.last_error()}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            logger.debug(f"Fetched {len(df)} bars for {symbol}")
            return df
        except Exception as e:
            logger.error(f"Error fetching rates: {e}")
            return None

# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================

class TechnicalIndicators:
    """Calculate technical indicators"""
    
    def __init__(self, config):
        self.config = config.get('indicators', {})
    
    def calculate_ema(self, data, period, column='close'):
        """Calculate Exponential Moving Average"""
        try:
            return data[column].ewm(span=period, adjust=False).mean()
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return None
    
    def calculate_rsi(self, data, period=14, column='close'):
        """Calculate Relative Strength Index"""
        try:
            delta = data[column].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    def calculate_atr(self, data, period=14):
        """Calculate Average True Range (Volatility)"""
        try:
            high = data['high']
            low = data['low']
            close = data['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return None
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9, column='close'):
        """Calculate MACD"""
        try:
            ema_fast = data[column].ewm(span=fast, adjust=False).mean()
            ema_slow = data[column].ewm(span=slow, adjust=False).mean()
            
            macd = ema_fast - ema_slow
            signal_line = macd.ewm(span=signal, adjust=False).mean()
            histogram = macd - signal_line
            
            return macd, signal_line, histogram
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None, None, None
    
    def calculate_all(self, data):
        """Calculate all indicators"""
        try:
            # Moving Averages
            data['EMA_20'] = self.calculate_ema(data, self.config.get('ema_short', 20))
            data['EMA_50'] = self.calculate_ema(data, self.config.get('ema_long', 50))
            
            # RSI
            data['RSI'] = self.calculate_rsi(data, self.config.get('rsi_period', 14))
            
            # ATR
            data['ATR'] = self.calculate_atr(data, self.config.get('atr_period', 14))
            
            # MACD
            macd, signal, hist = self.calculate_macd(
                data,
                self.config.get('macd_fast', 12),
                self.config.get('macd_slow', 26),
                self.config.get('macd_signal', 9)
            )
            data['MACD'] = macd
            data['MACD_Signal'] = signal
            data['MACD_Histogram'] = hist
            
            return data
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return None

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

class SignalGenerator:
    """Generate trading signals based on indicators"""
    
    def __init__(self, config):
        self.config = config
        self.indicators = TechnicalIndicators(config)
    
    def generate_signal(self, data):
        """Generate BUY/SELL signal"""
        try:
            if data is None or len(data) < 50:
                logger.warning("Insufficient data for signal generation")
                return None
            
            # Calculate indicators
            data = self.indicators.calculate_all(data)
            
            # Get latest values
            last_row = data.iloc[-1]
            close = last_row['close']
            ema_20 = last_row['EMA_20']
            ema_50 = last_row['EMA_50']
            rsi = last_row['RSI']
            atr = last_row['ATR']
            
            logger.debug(f"Latest: Close={close:.2f}, EMA20={ema_20:.2f}, EMA50={ema_50:.2f}, RSI={rsi:.2f}, ATR={atr:.2f}")
            
            # Determine signal
            signal = self._determine_signal(close, ema_20, ema_50, rsi)
            
            if signal is None:
                logger.info("No clear signal")
                return None
            
            # Calculate risk management levels
            if signal == 'BUY':
                stop_loss = close - (atr * self.config.get('trading', {}).get('stop_loss_multiplier', 1.5))
                take_profit = close + (atr * self.config.get('trading', {}).get('take_profit_multiplier', 2.0))
            else:  # SELL
                stop_loss = close + (atr * self.config.get('trading', {}).get('stop_loss_multiplier', 1.5))
                take_profit = close - (atr * self.config.get('trading', {}).get('take_profit_multiplier', 2.0))
            
            # Calculate confidence
            confidence = self._calculate_confidence(close, ema_20, ema_50, rsi, signal)
            
            signal_data = {
                'timestamp': datetime.now(),
                'symbol': self.config.get('trading', {}).get('symbol', 'XAUUSD'),
                'signal': signal,
                'price': close,
                'ema_20': ema_20,
                'ema_50': ema_50,
                'rsi': rsi,
                'atr': atr,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence
            }
            
            logger.info(f"Signal Generated: {signal} @ {close:.2f} (Confidence: {confidence:.2%})")
            return signal_data
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            traceback.print_exc()
            return None
    
    def _determine_signal(self, close, ema_20, ema_50, rsi):
        """Determine BUY/SELL signal based on indicators"""
        rsi_threshold = self.config.get('indicators', {}).get('rsi_period', 14)
        
        # BUY Signal
        if (
            ema_20 > ema_50 and
            close > ema_20 and
            rsi > 50 and
            rsi < 70
        ):
            return 'BUY'
        
        # SELL Signal
        if (
            ema_20 < ema_50 and
            close < ema_20 and
            rsi < 50 and
            rsi > 30
        ):
            return 'SELL'
        
        return None
    
    def _calculate_confidence(self, close, ema_20, ema_50, rsi, signal):
        """Calculate signal confidence score (0-1)"""
        confidence = 0.5
        
        try:
            if signal == 'BUY':
                # EMA alignment
                ema_distance = min((ema_20 - ema_50) / ema_50 * 100, 2.0)
                confidence += min(ema_distance / 2.0, 0.2)
                
                # RSI momentum
                rsi_momentum = (rsi - 50) / 50
                confidence += min(rsi_momentum * 0.2, 0.2)
                
                # Price position
                price_position = (close - ema_20) / ema_20 * 100
                if 0 < price_position < 2:
                    confidence += 0.1
            
            elif signal == 'SELL':
                # EMA alignment
                ema_distance = min((ema_50 - ema_20) / ema_50 * 100, 2.0)
                confidence += min(ema_distance / 2.0, 0.2)
                
                # RSI momentum
                rsi_momentum = (50 - rsi) / 50
                confidence += min(rsi_momentum * 0.2, 0.2)
                
                # Price position
                price_position = (ema_20 - close) / ema_20 * 100
                if 0 < price_position < 2:
                    confidence += 0.1
            
            return min(max(confidence, 0.5), 1.0)
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5

# ============================================================================
# SIGNAL OUTPUT
# ============================================================================

class SignalWriter:
    """Write signals to file for EA to read"""
    
    def __init__(self, config):
        self.config = config
        self.signal_file = config.get('execution', {}).get('signal_file', './signal.txt')
    
    def write_signal(self, signal_data):
        """Write signal to file"""
        try:
            if signal_data is None:
                return False
            
            content = f"""TIMESTAMP: {signal_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
INSTRUMENT: {signal_data['symbol']}
SIGNAL: {signal_data['signal']}
PRICE: {signal_data['price']:.2f}
EMA_20: {signal_data['ema_20']:.2f}
EMA_50: {signal_data['ema_50']:.2f}
RSI: {signal_data['rsi']:.2f}
ATR: {signal_data['atr']:.2f}
SL: {signal_data['stop_loss']:.2f}
TP: {signal_data['take_profit']:.2f}
CONFIDENCE: {signal_data['confidence']:.2f}
"""
            
            with open(self.signal_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Signal written to {self.signal_file}")
            return True
        except Exception as e:
            logger.error(f"Error writing signal: {e}")
            return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    logger.info("=" * 80)
    logger.info("AI TRADING BOT - LEVEL 2 (AI Model) Started")
    logger.info("=" * 80)
    
    try:
        # Load configuration
        config = load_config()
        if not config:
            logger.error("Failed to load configuration")
            return False
        
        # Connect to MT5
        mt5_conn = MT5Connection(config)
        if not mt5_conn.connect():
            logger.error("Failed to connect to MT5")
            return False
        
        try:
            # Get trading parameters
            symbol = config.get('trading', {}).get('symbol', 'XAUUSD')
            timeframe = config.get('trading', {}).get('timeframe', 'M5')
            
            # Fetch market data
            logger.info(f"Fetching data for {symbol} on {timeframe}...")
            data = mt5_conn.get_rates(symbol, timeframe, bars=100)
            
            if data is None or len(data) == 0:
                logger.error("No data fetched")
                return False
            
            # Generate signal
            logger.info("Generating signal...")
            signal_gen = SignalGenerator(config)
            signal_data = signal_gen.generate_signal(data)
            
            # Write signal to file
            if signal_data:
                signal_writer = SignalWriter(config)
                signal_writer.write_signal(signal_data)
                logger.info(f"✓ {signal_data['signal']} signal generated with {signal_data['confidence']:.0%} confidence")
            else:
                logger.info("No signal generated")
            
            return True
        finally:
            mt5_conn.disconnect()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()
        return False
    finally:
        logger.info("=" * 80)
        logger.info("AI Model Execution Completed")
        logger.info("=" * 80)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
