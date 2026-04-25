# AI Trading Bot - Installation Guide

## System Requirements

- **Operating System:** Windows (MT5 + Python), Linux (Python only), macOS (Python only)
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 1GB for MT5 + Python + Libraries
- **Internet:** Stable connection for MT5 and data fetching

## Step 1: Install MetaTrader 5

### Windows
1. Download from [MetaTrader 5 Official Site](https://www.metatrader5.com)
2. Run the installer
3. Complete the setup wizard
4. Create/login with your trading account
5. Note your account number (needed for Python)

### Linux/Mac (Alternative)
- MT5 is not natively available on Linux/Mac
- Use Wine/Proton (Linux) or Virtual Machine
- Alternatively, use the web terminal version

## Step 2: Install Python

### Windows
1. Download Python 3.8+ from [python.org](https://www.python.org)
2. Run installer
3. **Important:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```

### Linux
```bash
sudo apt update
sudo apt install python3.10 python3-pip
python3 --version
```

### macOS
```bash
brew install python3
python3 --version
```

## Step 3: Clone/Download Repository

```bash
# Clone from GitHub
git clone https://github.com/cevinowatu369/AI-Trading-Bot.git
cd AI-Trading-Bot

# Or download as ZIP and extract
```

## Step 4: Create Virtual Environment (Recommended)

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 5: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**If you encounter errors:**

- **ta-lib installation issue:**
  ```bash
  # Windows
  pip install ta-lib-python
  
  # Linux
  sudo apt install libta-lib0 libta-lib-dev
  pip install ta-lib
  ```

- **MetaTrader5 not found:**
  ```bash
  pip install MetaTrader5==5.0.45
  ```

## Step 6: Configure the System

### Edit config.yaml

1. Open `config.yaml` in a text editor
2. Update MT5 credentials:
   ```yaml
   mt5:
     account: YOUR_ACCOUNT_NUMBER
     password: "YOUR_PASSWORD"
     server: "Your-Server-Name"
   ```
3. Adjust trading parameters as needed
4. Save the file

### Create Logs Directory

```bash
mkdir logs
```

## Step 7: Test the Installation

### Test Python Setup
```bash
python -c "import MetaTrader5; print('MT5 library OK')"
python -c "import pandas; print('Pandas OK')"
python -c "import sklearn; print('Scikit-learn OK')"
```

### Test MT5 Connection
```bash
python data_fetcher.py
```

Expected output:
```
Connected to MetaTrader 5
Fetching 500 bars of XAUUSD H1...
✓ Fetched 500 bars
```

### Test AI Model
```bash
python ai_model.py
```

Expected output:
```
AI TRADING BOT - LEVEL 2 (AI Model) Started
Configuration loaded successfully
MT5 initialized successfully
Signal Generated: BUY @ 2450.50 (Confidence: 75%)
Signal written to ./signal.txt
```

## Step 8: Set Up Automated Execution

### Option A: Windows Task Scheduler

1. Press `Win + R`, type `taskschd.msc`
2. Click "Create Basic Task"
3. Name: "AI Trading Bot - Python"
4. Set trigger: "Repeat every 5 minutes"
5. Set action:
   - Program: `C:\Python310\python.exe` (your Python path)
   - Arguments: `C:\path\to\ai_model.py`
   - Start in: `C:\path\to\AI-Trading-Bot`
6. Configure with highest privileges if needed
7. Click "Finish"

### Option B: Linux/macOS Cron

1. Edit crontab:
   ```bash
   crontab -e
   ```

2. Add line:
   ```
   */5 * * * * cd /path/to/AI-Trading-Bot && /usr/bin/python3 ai_model.py
   ```

3. Save and exit

4. Verify cron job:
   ```bash
   crontab -l
   ```

## Step 9: Deploy EA to MetaTrader 5

### Copy EA File

1. Locate MT5 folder:
   - Windows: `C:\Users\[YourUsername]\AppData\Roaming\MetaQuotes\Terminal\[TerminalID]\MQL5\Experts`
   - Linux: `~/.wine/drive_c/users/[username]/AppData/Roaming/MetaQuotes/Terminal`

2. Copy `trading_executor.mq5` to this folder

3. Restart MetaTrader 5

### Attach EA to Chart

1. Open XAUUSD chart (or preferred symbol)
2. Drag `Trading Executor` from Navigator to the chart
3. Configuration dialog appears
4. Click "OK" to use default settings
5. Confirm "AutoTrading" is enabled (green icon in toolbar)

## Troubleshooting

### Python can't import MetaTrader5

**Error:** `ModuleNotFoundError: No module named 'MetaTrader5'`

**Solution:**
```bash
# Ensure virtual environment is activated
# Then reinstall
pip install --force-reinstall MetaTrader5==5.0.45
```

### MT5 initialization failed

**Error:** `MT5 initialization failed: (1, 'MT5 not available')`

**Solution:**
- Ensure MT5 is running
- Check MT5 is installed correctly
- Verify Python can find MT5 installation

### No signals generated

**Check:**
1. Is MT5 running and connected?
2. Are there at least 100 bars of data?
3. Check logs: `cat logs/ai_model.log`
4. Verify symbol is correct (XAUUSD, EURUSD, etc.)

### Task Scheduler / Cron not executing

**Windows:**
- Check Task Scheduler logs
- Ensure program/script path is correct
- Test command manually first

**Linux/macOS:**
```bash
# Check cron logs
grep CRON /var/log/syslog
# or
log stream --predicate 'process == "cron"'

# Ensure script has execute permissions
chmod +x ai_model.py
```

## Verification Checklist

- [ ] Python installed and in PATH
- [ ] All libraries installed (`pip list`)
- [ ] config.yaml configured with MT5 credentials
- [ ] MT5 connected and running
- [ ] `data_fetcher.py` can fetch data
- [ ] `ai_model.py` generates signals
- [ ] `signal.txt` file created and updated
- [ ] Automated execution configured (Task Scheduler/Cron)
- [ ] EA copied to MT5 Experts folder
- [ ] EA attached to chart
- [ ] AutoTrading enabled

## Next Steps

1. Run in demo mode for 24 hours
2. Monitor logs for any errors
3. Verify signals are generated every 5 minutes
4. Verify EA reads signals and executes (in demo)
5. Monitor P&L over time
6. Optimize parameters in config.yaml

## Support

If you encounter issues:
1. Check `logs/` directory for error messages
2. Review `docs/TROUBLESHOOTING.md`
3. Open an issue on GitHub
4. Consult MT5 documentation

---

Happy trading! 📈
