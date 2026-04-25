# AI Trading Robot Application

A three-level automated trading system combining MetaTrader 5 (EA), Python AI Model, and automated workflow orchestration.

## Architecture Overview

### LEVEL 1 — EA (Trading Executor)
Runs on MetaTrader 5 (MT5)
- **Functions:**
  - Receive BUY/SELL signals
  - Execute orders
  - Set stop-loss and trailing stop orders
  - Limit risk exposure

- **EA Logic:**
  - Only enter positions when receiving AI signals
  - Maximum 1–2 concurrent positions
  - Automatic lot size based on risk (e.g., 1% per trade)

### LEVEL 2 — AI MODEL (Python)
The "brain" that makes trading decisions
- **Data Inputs:**
  - OHLC (Open, High, Low, Close) prices
  - EMA 20 & 50 (Exponential Moving Averages)
  - RSI (Relative Strength Index)
  - ATR (Average True Range / Volatility)

- **Output:** BUY/SELL signals written to `signal.txt`

### LEVEL 3 — FULL SYSTEM (AUTOMATIC)
Automated workflow connecting all components

**Automatic Workflow:**
1. Python script runs every 1–5 minutes (via Task Scheduler/cron)
2. Fetches market data from MT5
3. AI model predicts market direction
4. Writes signal to `signal.txt`
5. EA reads signal file
6. EA auto-executes entry/exit orders

## Installation & Setup

### Prerequisites
1. **MetaTrader 5** - Download and install from [MetaTrader website](https://www.metatrader5.com)
2. **Python 3.8+** - Download from [python.org](https://www.python.org)

### Step 1: Install Python Libraries
```bash
pip install MetaTrader5 pandas scikit-learn numpy ta-lib
```

### Step 2: Configure MT5 Connection
- Open MetaTrader 5
- Enable WebAPI or ensure Python can connect via socket/API
- Note the account number and password for Python connection

### Step 3: Run the Python AI Model

**Option A: Manual Run**
```bash
python ai_model.py
```

**Option B: Automated with Task Scheduler (Windows)**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Every 1-5 minutes
4. Set action: Run `python C:\path\to\ai_model.py`
5. Enable "Run whether user is logged in or not"

**Option C: Automated with Cron (Linux/Mac)**
```bash
crontab -e
# Add: */5 * * * * python /path/to/ai_model.py
```

### Step 4: Deploy EA in MT5
1. Copy the EA file to MT5 Experts folder: `C:\Users\[Username]\AppData\Roaming\MetaQuotes\Terminal\[ID]\MQL5\Experts`
2. Restart MetaTrader 5
3. Open XAUUSD chart (or preferred instrument)
4. Drag the EA onto the chart
5. Configure EA parameters in the EA settings dialog
6. Enable "AutoTrading" checkbox in MT5
7. Click "OK"

## File Structure
```
AI-Trading-Bot/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config.yaml               # Configuration file
├── signal.txt                # Signal output (BUY/SELL)
├── logs/
│   └── trading_log.txt      # Trading activity log
├── ai_model.py              # Level 2: Python AI Model
├── data_fetcher.py          # Market data retrieval
├── trading_executor.mq5     # Level 1: EA Code
└── docs/
    ├── EA_SETUP.md          # EA deployment guide
    ├── PYTHON_SETUP.md      # Python setup guide
    └── TROUBLESHOOTING.md   # Common issues
```

## Configuration

Edit `config.yaml` to customize:
- MT5 account credentials
- Risk percentage per trade
- EMA periods (20, 50)
- RSI thresholds
- ATR multiplier for stop-loss
- Execution interval

## Trading Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Risk % | 1% | Risk per trade based on account |
| Max Positions | 2 | Maximum concurrent trades |
| EMA Short | 20 | Fast moving average period |
| EMA Long | 50 | Slow moving average period |
| RSI Period | 14 | RSI calculation period |
| RSI Upper | 70 | Overbought threshold |
| RSI Lower | 30 | Oversold threshold |
| ATR Period | 14 | Volatility calculation period |
| SL Multiplier | 1.5 | Stop-loss = ATR × multiplier |

## Signal Format

`signal.txt` output format:
```
TIMESTAMP: 2026-04-25 14:30:00
INSTRUMENT: XAUUSD
SIGNAL: BUY
PRICE: 2450.50
CONFIDENCE: 0.75
SL: 2445.00
TP: 2460.00
```

## Trading Logic

### Entry Conditions (BUY)
- EMA 20 > EMA 50 (uptrend)
- RSI > 50 (bullish momentum)
- Price > 20-period EMA
- No existing long positions
- Current positions < 2

### Entry Conditions (SELL)
- EMA 20 < EMA 50 (downtrend)
- RSI < 50 (bearish momentum)
- Price < 20-period EMA
- No existing short positions
- Current positions < 2

### Exit Conditions
- Stop-Loss: Hit ATR-based stop
- Take-Profit: Hit 1.5× risk/reward target
- Time-based: Exit after 4 hours if no profit
- Manual: Can override in MT5

## Monitoring & Logging

All trades logged to `logs/trading_log.txt`:
- Entry/exit times
- Prices and lot sizes
- P&L results
- AI confidence scores
- System status

## Risk Management

✓ **Position Sizing:** Auto-calculated based on 1% risk rule
✓ **Max Drawdown:** Monitor via account equity
✓ **Stop-Loss:** Always set, no exceptions
✓ **Max Positions:** Limited to 2 concurrent trades
✓ **Daily Loss Limit:** Stop trading if -2% daily loss

## Troubleshooting

### Python Can't Connect to MT5
- Ensure MT5 is running
- Verify account number is correct
- Check firewall settings
- See `docs/TROUBLESHOOTING.md`

### EA Not Reading Signals
- Verify `signal.txt` location
- Check EA file permissions
- Restart MetaTrader 5
- Enable "Allow DLL imports" if needed

### No Trades Executing
- Verify AutoTrading is enabled
- Check account balance
- Review EA logs in MT5 journal
- Ensure EA has sufficient margin

## Performance Metrics

Monitor in MT5 Strategy Tester:
- Win Rate (%)
- Profit Factor
- Drawdown (Max, Avg)
- Risk/Reward Ratio
- Sharpe Ratio

## Disclaimer

⚠️ **This is a trading system for educational purposes.** Trading involves risk of loss. Past performance does not guarantee future results. Always use proper risk management and never risk more than you can afford to lose.

## Support & Contributions

For issues, questions, or improvements:
1. Check `docs/TROUBLESHOOTING.md`
2. Review trading logs
3. Open an issue on GitHub
4. Submit a pull request with improvements

## License

MIT License - See LICENSE file for details

## Contact

For questions, reach out via GitHub Issues.

---

**Last Updated:** 2026-04-25
