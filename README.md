# Zerodha Portfolio Status Checker

A Python script to check your Zerodha portfolio status directly from your terminal using Kite Connect API.

## Overview

This script provides a comprehensive view of your Zerodha trading account by:
- Authenticating to Zerodha Kite Connect using an existing ACCESS_TOKEN or API credentials
- Fetching holdings, positions (day & net), and equity margins (funds)
- Computing portfolio-level and per-scrip P&L, returns, and basic risk checks
- Displaying data in neat, readable tables
- Saving CSV snapshots for record-keeping

## Features

- **Multiple Display Modes**: Simple summary or detailed tables
- **Advanced Sorting**: Sort holdings by 8 different criteria
- **Holdings Analysis**: View all your equity holdings with average price, current value, and P&L
- **Day Change Tracking**: See today's specific gains/losses for each stock
- **Positions Tracking**: Monitor both day and net positions with M2M calculations
- **Funds Overview**: Check available cash and utilized margins
- **Visual Indicators**: Trend arrows (↗️↘️) for gains/losses
- **Debug Mode**: View raw API responses for troubleshooting
- **CSV Export**: Automatically saves timestamped snapshots of your portfolio
- **IST Timezone**: All timestamps are in Indian Standard Time
- **Error Handling**: Graceful handling of API errors with retry mechanism

## Prerequisites

### Python Dependencies

```bash
pip install kiteconnect python-dateutil
```

### Kite Connect Setup

You'll need a Zerodha Kite Connect developer account. Visit [Kite Connect](https://kite.trade/) to create an app and get your API credentials.

## Authentication Flow

### Step 1: Create a Kite Connect App
1. Sign up at [Kite Connect](https://kite.trade/)
2. Create a new app
3. Note down your `API Key` and `API Secret`
4. Set a redirect URL in your app settings

### Step 2: Generate Request Token
1. Navigate to the Kite Connect login URL:
   ```
   https://kite.zerodha.com/connect/login?v=3&api_key=YOUR_API_KEY
   ```
2. Log in with your Zerodha credentials
3. After successful login, you'll be redirected to your registered redirect URL with a `request_token` parameter
4. Copy this `request_token` (it's valid only for a few minutes)

### Step 3: Exchange for Access Token
The script will automatically exchange your request token for an access token when you run it with the proper credentials. The access token is valid until 6 AM the next day.

## Configuration

You can configure the API credentials and default sorting preferences:

### Method 1: Direct Configuration in Script

Edit the configuration variables at the top of `zerodha.py`:

```python
# Configuration - API Credentials
API_KEY = "your_api_key"  # From your Kite Connect app
API_SECRET = "your_api_secret"  # From your Kite Connect app
REQUEST_TOKEN = "your_request_token"  # From login flow (Step 2)
ACCESS_TOKEN = ""  # Leave empty, will be generated automatically

# Display Configuration
DEFAULT_MODE = "simple"         # Options: simple, detailed, holdings, positions, funds
DEFAULT_SORT_BY = "day_change"  # Options: symbol, quantity, ltp, invested, value, pnl, pnl_pct, day_change
DEFAULT_SORT_ORDER = "desc"     # Options: asc, desc
DEFAULT_DEBUG = False           # True to show debug info by default, False to hide
```

### Method 2: Environment Variables

Set environment variables (these will override the script values):

#### First Time Setup (with Request Token)
```bash
export KITE_API_KEY="your_api_key"
export KITE_API_SECRET="your_api_secret"
export KITE_REQUEST_TOKEN="your_request_token"
```

Run the script once, and it will display your access token:
```bash
python zerodha.py
```

#### Subsequent Runs (with Access Token)
After obtaining the access token, you can use it directly:
```bash
export KITE_ACCESS_TOKEN="your_access_token"
```

Or update the script:
```python
ACCESS_TOKEN = "your_access_token"  # Token obtained from first run
```

**Important Notes:**
- Access tokens expire at 6 AM daily (regulatory requirement)
- Never expose your `API_SECRET` in client-side applications
- Keep your `ACCESS_TOKEN` private and secure
- Request tokens are valid only for a few minutes after generation

## Usage

The script supports multiple display modes for different use cases:

### Simple Mode (Default)
Perfect for daily portfolio checking with a clean, focused summary:
```bash
python zerodha.py
```

### Detailed Mode
Shows all information including detailed tables:
```bash
python zerodha.py --detailed
# or
python zerodha.py -d
```

### Focused Views
View specific sections only:
```bash
python zerodha.py --holdings     # Holdings table only
python zerodha.py --positions    # Positions tables only  
python zerodha.py --funds        # Funds information only
```

### Sorting Options
Sort holdings by different criteria in detailed/focused views:
```bash
python zerodha.py --detailed --sort pnl_pct --order desc    # Sort by P&L percentage, highest first
python zerodha.py --holdings --sort value --order desc      # Sort by current value, largest first
python zerodha.py --detailed --sort day_change --order desc # Sort by today's change (default)
python zerodha.py --holdings --sort symbol --order asc      # Sort alphabetically
```

**Available sort fields:**
- `symbol` - Stock symbol (alphabetical)
- `quantity` - Number of shares held
- `ltp` - Last traded price
- `invested` - Total invested amount
- `value` - Current market value
- `pnl` - Profit/loss amount
- `pnl_pct` - Profit/loss percentage
- `day_change` - Today's change in rupees (default)

**Sort direction:**
```bash
--order asc     # Ascending order (smallest to largest)
--order desc    # Descending order (largest to smallest, default)
```

### Debug Mode
View raw API responses for troubleshooting:
```bash
python zerodha.py --debug        # Simple mode with raw data
python zerodha.py --detailed --debug  # Detailed mode with raw data
```

### Making it Executable
```bash
chmod +x zerodha.py
./zerodha.py                     # Simple mode
./zerodha.py --detailed          # Detailed mode
./zerodha.py --holdings --sort pnl_pct --order desc  # Holdings sorted by P&L%
```

## Example Output
### Simple Mode (Default)
```
Zerodha Portfolio Status @ 2024-01-15_14-30-45 IST

📊 TODAY'S PERFORMANCE
Portfolio Value: ₹85,250.00
Total Invested: ₹75,000.00
Holdings P&L: ₹10,250.00 (↗️ 13.67%)

💹 TRADING PERFORMANCE
Holdings Day Change: ₹450.75 (↗️ 0.53%)
Positions Day Trading: ₹-125.50 (↘️ -0.15%)
Net Positions P&L: ₹2,850.00 (↗️ 3.34%)
Total P&L: ₹13,100.00 (↗️ 17.47%)

🔥 TOP MOVERS
📈 Top Gainers:
  RELIANCE: ₹2,500.00 (↗️ 25.00%)
  INFY: ₹1,800.00 (↗️ 18.00%)
  TCS: ₹1,200.00 (↗️ 12.00%)
📉 Top Losers:
  HDFC: ₹-300.00 (↘️ -3.00%)
  ICICIBANK: ₹-150.00 (↘️ -1.50%)
  SBIN: ₹-100.00 (↘️ -1.00%)

💰 FUNDS
Available Cash: ₹15,000.00
Utilised: ₹5,000.00
```

### Detailed Mode with Sorting
```
Zerodha Portfolio Status @ 2024-01-15_14-30-45 IST
Holdings (sorted by day_change, desc):
--------------------------------------------------------------------------------------------------------------
Symbol     | Exch | Qty | Avg     | LTP     | Invested | Value    | PnL     | PnL % | Day Change
--------------------------------------------------------------------------------------------------------------
RELIANCE   | NSE  | 10  | 2450.00 | 2500.00 | 24500.00 | 25000.00 | 500.00  | 2.04  | 250.00
INFY       | NSE  | 20  | 1400.00 | 1450.00 | 28000.00 | 29000.00 | 1000.00 | 3.57  | 180.00
TCS        | NSE  | 5   | 3200.00 | 3300.00 | 16000.00 | 16500.00 | 500.00  | 3.13  | 120.00
HDFC       | NSE  | 8   | 1600.00 | 1550.00 | 12800.00 | 12400.00 | -400.00 | -3.13 | -75.00
ICICIBANK  | NSE  | 15  | 800.00  | 790.00  | 12000.00 | 11850.00 | -150.00 | -1.25 | -45.00
...
--------------------------------------------------------------------------------------------------------------
Total Invested: ₹75,000.00
Current Value:  ₹85,250.00
Unrealized PnL: ₹10,250.00 (13.67%)
Zerodha Portfolio Status @ 2025-09-22_19-32-49 IST

📊 TODAY'S PERFORMANCE
Portfolio Value: ₹127,351.05
Total Invested: ₹111,079.08
Holdings P&L: ₹16,271.97 (↗️ 14.65%)

💹 TRADING PERFORMANCE
Holdings Day Change: ₹810.50 (↗️ 0.64%)
Positions Day Trading: ₹-73.90 (↘️ -0.06%)
Net Positions P&L: ₹8,239.10 (↗️ 6.47%)
Total P&L: ₹24,511.07 (↗️ 22.07%)

🔥 TOP MOVERS
📈 Top Gainers:
  WAAREEENER: ₹1,349.65 (↗️ 64.12%)
  PAUSHAKLTD: ₹2,464.55 (↗️ 55.89%)
  PERMAGN: ₹4,495.75 (↗️ 38.26%)
📉 Top Losers:
  INDIGOPNTS: ₹-141.00 (↘️ -4.10%)
  RAJOOENG: ₹-183.00 (↘️ -1.92%)
  NH: ₹-127.20 (↘️ -1.79%)

💰 FUNDS
Available Cash: ₹13,032.30
Utilised: ₹12,557.00
```

### Detailed Mode with Sorting
```
Zerodha Portfolio Status @ 2025-09-22_19-38-13 IST
Holdings (sorted by day_change, desc):
--------------------------------------------------------------------------------------------------------------
Symbol     | Exch | Qty | Avg     | LTP     | Invested | Value    | PnL     | PnL % | Day Change
--------------------------------------------------------------------------------------------------------------
PERMAGN    | BSE  | 15  | 783.33  | 1083.05 | 11750.00 | 16245.75 | 4495.75 | 38.26 | 773.25
MOLDTECH   | NSE  | 50  | 142.18  | 174.62  | 7109.24  | 8731.00  | 1621.76 | 22.81 | 632.00
PAUSHAKLTD | BSE  | 1   | 4410.00 | 6874.55 | 4410.00  | 6874.55  | 2464.55 | 55.89 | 333.70
...
--------------------------------------------------------------------------------------------------------------
Total Invested: ₹111,079.08
Current Value:  ₹127,351.05
Unrealized PnL: ₹16,271.97 (14.65%)
Day's Change: ₹810.50 (↗️ 0.64%)
```
Zerodha Portfolio Status @ 2025-09-22_19-32-49 IST

📊 TODAY'S PERFORMANCE
Portfolio Value: ₹127,351.05
Total Invested: ₹111,079.08
Holdings P&L: ₹16,271.97 (↗️ 14.65%)

💹 TRADING PERFORMANCE
Holdings Day Change: ₹810.50 (↗️ 0.64%)
Positions Day Trading: ₹-73.90 (↘️ -0.06%)
Net Positions P&L: ₹8,239.10 (↗️ 6.47%)
Total P&L: ₹24,511.07 (↗️ 22.07%)

🔥 TOP MOVERS
📈 Top Gainers:
  WAAREEENER: ₹1,349.65 (↗️ 64.12%)
  PAUSHAKLTD: ₹2,464.55 (↗️ 55.89%)
  PERMAGN: ₹4,495.75 (↗️ 38.26%)
📉 Top Losers:
  INDIGOPNTS: ₹-141.00 (↘️ -4.10%)
  RAJOOENG: ₹-183.00 (↘️ -1.92%)
  NH: ₹-127.20 (↘️ -1.79%)

💰 FUNDS
Available Cash: ₹13,032.30
Utilised: ₹12,557.00
```

### Detailed Mode with Sorting
```
Zerodha Portfolio Status @ 2025-09-22_19-38-13 IST
Holdings (sorted by day_change, desc):
--------------------------------------------------------------------------------------------------------------
Symbol     | Exch | Qty | Avg     | LTP     | Invested | Value    | PnL     | PnL % | Day Change
--------------------------------------------------------------------------------------------------------------
PERMAGN    | BSE  | 15  | 783.33  | 1083.05 | 11750.00 | 16245.75 | 4495.75 | 38.26 | 773.25
MOLDTECH   | NSE  | 50  | 142.18  | 174.62  | 7109.24  | 8731.00  | 1621.76 | 22.81 | 632.00
PAUSHAKLTD | BSE  | 1   | 4410.00 | 6874.55 | 4410.00  | 6874.55  | 2464.55 | 55.89 | 333.70
...
--------------------------------------------------------------------------------------------------------------
Total Invested: ₹111,079.08
Current Value:  ₹127,351.05
Unrealized PnL: ₹16,271.97 (14.65%)
Day's Change: ₹810.50 (↗️ 0.64%)
```
Day's Change: ₹450.75 (↗️ 0.53%)
```
Zerodha Portfolio Status @ 2025-09-22_19-32-49 IST

📊 TODAY'S PERFORMANCE
Portfolio Value: ₹127,351.05
Total Invested: ₹111,079.08
Holdings P&L: ₹16,271.97 (↗️ 14.65%)

💹 TRADING PERFORMANCE
Holdings Day Change: ₹810.50 (↗️ 0.64%)
Positions Day Trading: ₹-73.90 (↘️ -0.06%)
Net Positions P&L: ₹8,239.10 (↗️ 6.47%)
Total P&L: ₹24,511.07 (↗️ 22.07%)

🔥 TOP MOVERS
📈 Top Gainers:
  WAAREEENER: ₹1,349.65 (↗️ 64.12%)
  PAUSHAKLTD: ₹2,464.55 (↗️ 55.89%)
  PERMAGN: ₹4,495.75 (↗️ 38.26%)
📉 Top Losers:
  INDIGOPNTS: ₹-141.00 (↘️ -4.10%)
  RAJOOENG: ₹-183.00 (↘️ -1.92%)
  NH: ₹-127.20 (↘️ -1.79%)

💰 FUNDS
Available Cash: ₹13,032.30
Utilised: ₹12,557.00
```

### Detailed Mode with Sorting
```
Zerodha Portfolio Status @ 2025-09-22_19-38-13 IST
Holdings (sorted by day_change, desc):
--------------------------------------------------------------------------------------------------------------
Symbol     | Exch | Qty | Avg     | LTP     | Invested | Value    | PnL     | PnL % | Day Change
--------------------------------------------------------------------------------------------------------------
PERMAGN    | BSE  | 15  | 783.33  | 1083.05 | 11750.00 | 16245.75 | 4495.75 | 38.26 | 773.25
MOLDTECH   | NSE  | 50  | 142.18  | 174.62  | 7109.24  | 8731.00  | 1621.76 | 22.81 | 632.00
PAUSHAKLTD | BSE  | 1   | 4410.00 | 6874.55 | 4410.00  | 6874.55  | 2464.55 | 55.89 | 333.70
...
--------------------------------------------------------------------------------------------------------------
Total Invested: ₹111,079.08
Current Value:  ₹127,351.05
Unrealized PnL: ₹16,271.97 (14.65%)
Day's Change: ₹810.50 (↗️ 0.64%)
```
Day's Change: ₹450.75 (↗️ 0.53%)
```
====================================================================================================
Zerodha Portfolio Status @ 2025-09-22_19-32-49 IST
====================================================================================================

📊 TODAY'S PERFORMANCE
Portfolio Value: ₹127,351.05
Total Invested: ₹111,079.08
Holdings P&L: ₹16,271.97 (↗️ 14.65%)

💹 TRADING PERFORMANCE
Holdings Day Change: ₹810.50 (↗️ 0.64%)
Positions Day Trading: ₹-73.90 (↘️ -0.06%)
Net Positions P&L: ₹8,239.10 (↗️ 6.47%)
Total P&L: ₹24,511.07 (↗️ 22.07%)

🔥 TOP MOVERS
📈 Top Gainers:
  WAAREEENER: ₹1,349.65 (↗️ 64.12%)
  PAUSHAKLTD: ₹2,464.55 (↗️ 55.89%)
  PERMAGN: ₹4,495.75 (↗️ 38.26%)
📉 Top Losers:
  INDIGOPNTS: ₹-141.00 (↘️ -4.10%)
  RAJOOENG: ₹-183.00 (↘️ -1.92%)
  NH: ₹-127.20 (↘️ -1.79%)

💰 FUNDS
Available Cash: ₹13,032.30
Utilised: ₹12,557.00
====================================================================================================
```

### Detailed Mode with Sorting
```
====================================================================================================
Zerodha Portfolio Status @ 2025-09-22_19-38-13 IST
====================================================================================================
Holdings (sorted by day_change, desc):
--------------------------------------------------------------------------------------------------------------
Symbol     | Exch | Qty | Avg     | LTP     | Invested | Value    | PnL     | PnL % | Day Change
--------------------------------------------------------------------------------------------------------------
PERMAGN    | BSE  | 15  | 783.33  | 1083.05 | 11750.00 | 16245.75 | 4495.75 | 38.26 | 773.25
MOLDTECH   | NSE  | 50  | 142.18  | 174.62  | 7109.24  | 8731.00  | 1621.76 | 22.81 | 632.00
PAUSHAKLTD | BSE  | 1   | 4410.00 | 6874.55 | 4410.00  | 6874.55  | 2464.55 | 55.89 | 333.70
...
--------------------------------------------------------------------------------------------------------------
Total Invested: ₹111,079.08
Current Value:  ₹127,351.05
Unrealized PnL: ₹16,271.97 (14.65%)
Day's Change: ₹810.50 (↗️ 0.64%)
```

## Output Details

The script displays:

1. **Simple Mode Features**
   - Portfolio overview with total values
   - Holdings day change (today's specific profit/loss)
   - Trading performance breakdown
   - Top 3 gainers and losers
   - Available funds

2. **Detailed Mode Features**
   - Complete holdings table with day change column
   - Sortable by any field (symbol, value, P&L, day change, etc.)
   - Positions tables (day and net)
   - Funds information
   - CSV export functionality

3. **Holdings Table Columns**
   - Symbol and Exchange
   - Quantity held
   - Average price and Last Traded Price (LTP)
   - Invested amount and current value
   - Profit/Loss in absolute and percentage terms
   - **Day Change** - Today's specific gain/loss per stock

4. **Positions Tables** (Day and Net)
   - Product type
   - Symbol and Exchange
   - Quantity
   - Average price and LTP
   - Mark-to-Market (M2M) value

5. **CSV Snapshots**
   - Saved in `kite_snapshots/` directory
   - Timestamped files for holdings and positions
   - Format: `holdings_YYYY-MM-DD_HH-MM-SS.csv`

## Advanced Usage Examples

```bash
# Quick daily check
python zerodha.py

# See best/worst performers
python zerodha.py --holdings --sort pnl_pct

# See biggest day movers
python zerodha.py --detailed --sort day_change

# See largest holdings by value
python zerodha.py --holdings --sort value

# Debug API issues
python zerodha.py --debug

# Holdings only, sorted alphabetically
python zerodha.py --holdings --sort symbol

# Positions only
python zerodha.py --positions
```

## Important Notes

- This is a **read-only** script - it does not place or cancel orders
- All monetary values are displayed in Indian Rupees (₹)
- The script includes a retry mechanism for transient network issues
- CSV files are saved locally for record-keeping and analysis
- **Holdings Day Change** shows today's specific movements using Zerodha's `day_change` field
- Default sorting is by `day_change` (descending) to show biggest daily movers first

## Error Handling

The script handles various error scenarios:
- Missing or invalid credentials
- Network connectivity issues
- API rate limits
- Invalid responses from Kite Connect

## Security Considerations

- Never commit your API credentials or access tokens to version control
- Use environment variables or secure credential management systems
- Access tokens expire daily and need to be regenerated
- Consider using read-only API permissions if you only need portfolio viewing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for informational purposes only. Always verify your portfolio details on the official Zerodha platform. The authors are not responsible for any financial decisions made based on this tool's output.
