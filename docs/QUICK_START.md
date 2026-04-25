# AI Trading Bot - Quick Start Guide (5 Minutes)

## Prerequisites
- MetaTrader 5 installed
- Python 3.8+ installed
- Trading account with MT5 broker

## Quick Setup

### 1. Install Python Libraries (1 min)
```bash
pip install -r requirements.txt
```

### 2. Configure (1 min)

Edit `config.yaml`:
```yaml
mt5:
  account: YOUR_ACCOUNT_NUMBER    # Your MT5 account
  password: "YOUR_PASSWORD"        # Your MT5 password
  server: "Your-Server-Name"       # e.g., "MetaQuotes-Demo"
```

Save file.

### 3. Test Connection (1 min)
```bash
python data_fetcher.py
```

Expected: ✓ Fetched 500 bars

### 4. Generate Signal (1 min)
```bash
python ai_model.py
```

Expected: ✓ Signal Generated: BUY @ 2450.50

### 5. Deploy EA (1 min)
1. Copy `trading_executor.mq5` to MT5 Experts folder
2. Restart MT5
3. Drag EA onto XAUUSD chart
4. Enable AutoTrading

## Running Live

### Windows Task Scheduler
1. Press `Win + R` → `taskschd.msc`
2. Create Basic Task
3. Name: "AI Trading"
4. Trigger: Repeat every 5 minutes
5. Action: `C:\Python\python.exe C:\path\to\ai_model.py`
6. Create

### Linux/Mac Cron
```bash
crontab -e
# Add: */5 * * * * python /path/to/ai_model.py
```

## Monitor

Check logs:
```bash
tail -f logs/trading_log.txt
```

Check latest signal:
```bash
cat signal.txt
```

## Done! 🎉

System is now running automatically every 5 minutes.

---

**For detailed setup:** See `docs/INSTALLATION.md`
