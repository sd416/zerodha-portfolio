#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zerodha Portfolio Status Checker - Kite Connect Integration
See README.md for detailed documentation and usage instructions.
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from dateutil.tz import gettz
from kiteconnect import KiteConnect


# Configuration - API Credentials
# You can either set these directly here or use environment variables
API_KEY = os.getenv("KITE_API_KEY", "")  # Your Kite Connect API Key
API_SECRET = os.getenv("KITE_API_SECRET", "")  # Your Kite Connect API Secret
REQUEST_TOKEN = os.getenv("KITE_REQUEST_TOKEN", "")  # Request token from login flow
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN", "")  # Access token (if available)

# For direct configuration, uncomment and set your credentials below:
# API_KEY = "your_api_key_here"
# API_SECRET = "your_api_secret_here"
# REQUEST_TOKEN = "your_request_token_here"
# ACCESS_TOKEN = "your_access_token_here"

# Display Configuration
DEFAULT_MODE = "simple"         # Options: simple, detailed, holdings, positions, funds
DEFAULT_SORT_BY = "day_change"  # Options: symbol, quantity, ltp, invested, value, pnl, pnl_pct, day_change
DEFAULT_SORT_ORDER = "desc"     # Options: asc, desc
DEFAULT_DEBUG = False           # True to show debug info by default, False to hide
DEFAULT_EXPORT_CSV = False      # True to export CSV files by default, False to disable



# Helper Functions
def d(x):
    """Convert to Decimal safely."""
    if x is None:
        return Decimal("0")
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal("0")


def pct(n, dnm):
    """Calculate percentage with 2 decimal places."""
    if dnm == 0:
        return Decimal("0")
    return (n / dnm * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def q2(x, places="0.01"):
    """Quantize decimal to specified places."""
    return d(x).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def rupee(n):
    """Format number as Indian Rupee."""
    return f"₹{q2(n, '0.01'):,.2f}"


def ts():
    """Get current timestamp in IST."""
    ist = gettz("Asia/Kolkata")
    return datetime.now(ist).strftime("%Y-%m-%d_%H-%M-%S")


def print_rule(char="-", width=100):
    """Print a horizontal rule."""
    print(char * width)


def safe_get(m, k, default=None):
    """Safely get value from dict."""
    try:
        return m.get(k, default)
    except Exception:
        return default


def write_csv(path, rows, header):
    """Write data to CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in header})


# Authentication
def get_kite():
    """Initialize Kite Connect with credentials."""
    api_key = API_KEY.strip()
    api_secret = API_SECRET.strip()
    request_token = REQUEST_TOKEN.strip()
    access_token = ACCESS_TOKEN.strip()

    if access_token:
        kite = KiteConnect(api_key=api_key or "anonymous")
        kite.set_access_token(access_token)
        return kite

    if not (api_key and api_secret and request_token):
        print("ERROR: Provide ACCESS_TOKEN or (API_KEY, API_SECRET, REQUEST_TOKEN).", file=sys.stderr)
        print("Set them at the top of the script or via environment variables.", file=sys.stderr)
        sys.exit(1)

    kite = KiteConnect(api_key=api_key)
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        kite.set_access_token(access_token)
        print(f"[info] Access token fetched. You may save it for reuse:\nACCESS_TOKEN = \"{access_token}\"\n")
        return kite
    except Exception as e:
        print(f"ERROR: Failed to generate session: {e}", file=sys.stderr)
        sys.exit(1)


# Data Fetchers
def fetch_holdings(kite, debug=False):
    """Fetch holdings from Kite."""
    try:
        holdings = kite.holdings() or []
        if debug:
            print("\n" + "="*80)
            print("DEBUG: RAW HOLDINGS API RESPONSE")
            print("="*80)
            import json
            print(json.dumps(holdings, indent=2, default=str))
            print("="*80 + "\n")
        return holdings
    except Exception as e:
        print(f"ERROR: holdings(): {e}", file=sys.stderr)
        return []


def fetch_positions(kite, debug=False):
    """Fetch day and net positions from Kite."""
    try:
        p = kite.positions() or {}
        if debug:
            print("\n" + "="*80)
            print("DEBUG: RAW POSITIONS API RESPONSE")
            print("="*80)
            import json
            print(json.dumps(p, indent=2, default=str))
            print("="*80 + "\n")
        return p.get("day", []), p.get("net", [])
    except Exception as e:
        print(f"ERROR: positions(): {e}", file=sys.stderr)
        return [], []


def fetch_margins(kite, debug=False):
    """Fetch equity margins from Kite."""
    try:
        m = kite.margins()
        if debug:
            print("\n" + "="*80)
            print("DEBUG: RAW MARGINS API RESPONSE")
            print("="*80)
            import json
            print(json.dumps(m, indent=2, default=str))
            print("="*80 + "\n")
        return m.get("equity", {}) if isinstance(m, dict) else {}
    except Exception as e:
        print(f"ERROR: margins(): {e}", file=sys.stderr)
        return {}


# Data Processing
def summarize_holdings(holdings):
    """Process holdings data and calculate P&L."""
    rows = []
    total_invested = Decimal("0")
    total_ltp_value = Decimal("0")
    total_pnl = Decimal("0")
    total_day_change = Decimal("0")

    for h in holdings:
        qty = d(safe_get(h, "quantity", 0))
        avg = d(safe_get(h, "average_price", 0))
        ltp = d(safe_get(h, "last_price", 0))
        day_change = d(safe_get(h, "day_change", 0))
        invested = qty * avg
        value = qty * ltp
        pnl = value - invested

        total_invested += invested
        total_ltp_value += value
        total_pnl += pnl
        total_day_change += day_change * qty  # Total day change for this holding

        rows.append({
            "tradingsymbol": safe_get(h, "tradingsymbol", ""),
            "exchange": safe_get(h, "exchange", ""),
            "quantity": str(qty),
            "avg_price": str(q2(avg)),
            "last_price": str(q2(ltp)),
            "invested": str(q2(invested)),
            "value": str(q2(value)),
            "pnl": str(q2(pnl)),
            "pnl_pct": str(pct(pnl, invested)),
            "day_change": str(q2(day_change * qty))
        })

    agg = {
        "invested": total_invested,
        "value": total_ltp_value,
        "pnl": total_pnl,
        "pnl_pct": pct(total_pnl, total_invested) if total_invested != 0 else Decimal("0"),
        "day_change": total_day_change
    }
    return rows, agg


def summarize_positions(positions):
    """Process positions data and calculate M2M."""
    rows = []
    total_m2m = Decimal("0")
    
    for p in positions:
        qty = d(safe_get(p, "quantity", 0))
        avg = d(safe_get(p, "average_price", 0))
        ltp = d(safe_get(p, "last_price", 0))
        m2m = (ltp - avg) * qty
        total_m2m += m2m
        
        rows.append({
            "product": safe_get(p, "product", ""),
            "tradingsymbol": safe_get(p, "tradingsymbol", ""),
            "exchange": safe_get(p, "exchange", ""),
            "qty": str(qty),
            "avg_price": str(q2(avg)),
            "ltp": str(q2(ltp)),
            "m2m": str(q2(m2m)),
        })
    
    return rows, total_m2m


# Display Functions
def print_table(rows, columns, headers=None, width=110):
    """Print data in tabular format."""
    if not rows:
        print("(none)")
        return
    
    if headers is None:
        headers = columns
    
    col_widths = [max(len(str(h)), max(len(str(r.get(c, ""))) for r in rows)) for c, h in zip(columns, headers)]
    fmt = " | ".join(f"{{:{w}}}" for w in col_widths)
    
    print_rule("-", width)
    print(fmt.format(*headers))
    print_rule("-", width)
    for r in rows:
        print(fmt.format(*[str(r.get(c, "")) for c in columns]))
    print_rule("-", width)


def get_trend_indicator(value):
    """Get trend indicator emoji based on value."""
    if value > 0:
        return "↗️"
    elif value < 0:
        return "↘️"
    else:
        return "➡️"


def print_simple_summary(h_agg, d_m2m, n_m2m, avail_cash, utilised, holdings_rows):
    """Print simple portfolio summary."""
    print_rule("=")
    print(f"Zerodha Portfolio Status @ {ts()} IST")
    print_rule("=")
    print()
    
    # Portfolio overview
    portfolio_trend = get_trend_indicator(h_agg['pnl'])
    day_trend = get_trend_indicator(d_m2m)
    net_trend = get_trend_indicator(n_m2m)
    
    print("📊 TODAY'S PERFORMANCE")
    print(f"Portfolio Value: {rupee(h_agg['value'])}")
    print(f"Total Invested: {rupee(h_agg['invested'])}")
    print(f"Holdings P&L: {rupee(h_agg['pnl'])} ({portfolio_trend} {q2(h_agg['pnl_pct'])}%)")
    print()
    
    # Trading Performance
    print("💹 TRADING PERFORMANCE")
    
    # Holdings day change
    holdings_day_trend = get_trend_indicator(h_agg['day_change'])
    holdings_day_pct = pct(h_agg['day_change'], h_agg['value']) if h_agg['value'] != 0 else Decimal("0")
    print(f"Holdings Day Change: {rupee(h_agg['day_change'])} ({holdings_day_trend} {q2(holdings_day_pct)}%)")
    
    if d_m2m != 0:
        day_pct = pct(d_m2m, h_agg['value']) if h_agg['value'] != 0 else Decimal("0")
        print(f"Positions Day Trading: {rupee(d_m2m)} ({day_trend} {q2(day_pct)}%)")
    
    if n_m2m != 0:
        net_pct = pct(n_m2m, h_agg['value']) if h_agg['value'] != 0 else Decimal("0")
        print(f"Net Positions P&L: {rupee(n_m2m)} ({net_trend} {q2(net_pct)}%)")
    
    # Total Performance
    total_pnl = h_agg['pnl'] + n_m2m
    total_trend = get_trend_indicator(total_pnl)
    total_pct = pct(total_pnl, h_agg['invested']) if h_agg['invested'] != 0 else Decimal("0")
    print(f"Total P&L: {rupee(total_pnl)} ({total_trend} {q2(total_pct)}%)")
    print()
    
    # Show top gainers and losers
    if holdings_rows:
        print()
        print("🔥 TOP MOVERS")
        
        # Sort holdings by P&L percentage
        sorted_holdings = sorted(holdings_rows, key=lambda x: float(x.get('pnl_pct', 0)), reverse=True)
        
        # Top 3 gainers
        gainers = [h for h in sorted_holdings if float(h.get('pnl_pct', 0)) > 0][:3]
        if gainers:
            print("📈 Top Gainers:")
            for h in gainers:
                pnl_pct = float(h.get('pnl_pct', 0))
                pnl = float(h.get('pnl', 0))
                trend = get_trend_indicator(pnl)
                print(f"  {h['tradingsymbol']}: {rupee(pnl)} ({trend} {pnl_pct:.2f}%)")
        
        # Top 3 losers
        losers = [h for h in sorted_holdings if float(h.get('pnl_pct', 0)) < 0][-3:]
        losers.reverse()  # Show worst first
        if losers:
            print("📉 Top Losers:")
            for h in losers:
                pnl_pct = float(h.get('pnl_pct', 0))
                pnl = float(h.get('pnl', 0))
                trend = get_trend_indicator(pnl)
                print(f"  {h['tradingsymbol']}: {rupee(pnl)} ({trend} {pnl_pct:.2f}%)")
    
    print()
    print("💰 FUNDS")
    print(f"Available Cash: {rupee(avail_cash)}")
    print(f"Utilised: {rupee(utilised)}")
    
    print_rule("=")


def print_detailed_view(kite, mode="all", debug=False, sort_by=DEFAULT_SORT_BY, sort_order=DEFAULT_SORT_ORDER):
    """Print detailed view based on mode."""
    print_rule("=")
    print(f"Zerodha Portfolio Status @ {ts()} IST")
    print_rule("=")

    # Fetch data
    margins = fetch_margins(kite, debug)
    avail_cash = d(safe_get(margins, "available", {}).get("cash", 0)) if isinstance(margins.get("available", {}), dict) else d(0)
    utilised = d(safe_get(margins, "utilised", {}).get("debits", 0)) if isinstance(margins.get("utilised", {}), dict) else d(0)
    
    holdings = fetch_holdings(kite, debug)
    h_rows, h_agg = summarize_holdings(holdings)
    
    day_pos, net_pos = fetch_positions(kite, debug)
    d_rows, d_m2m = summarize_positions(day_pos)
    n_rows, n_m2m = summarize_positions(net_pos)

    # Sort holdings if requested
    if h_rows and sort_by:
        # Map sort field names to appropriate sorting keys
        sort_key_map = {
            "symbol": lambda x: x.get("tradingsymbol", ""),
            "quantity": lambda x: float(x.get("quantity", 0)),
            "ltp": lambda x: float(x.get("last_price", 0)),
            "invested": lambda x: float(x.get("invested", 0)),
            "value": lambda x: float(x.get("value", 0)),
            "pnl": lambda x: float(x.get("pnl", 0)),
            "pnl_pct": lambda x: float(x.get("pnl_pct", 0)),
            "day_change": lambda x: float(x.get("day_change", 0))
        }
        
        if sort_by in sort_key_map:
            h_rows.sort(key=sort_key_map[sort_by], reverse=(sort_order == "desc"))

    # Display based on mode
    if mode in ["all", "funds"]:
        print("Funds (Equity):")
        print(f"  Available cash: {rupee(avail_cash)}")
        print(f"  Utilised (debits): {rupee(utilised)}")
        print_rule()

    if mode in ["all", "holdings"]:
        sort_desc = f" (sorted by {sort_by}, {sort_order})" if sort_by != "symbol" or sort_order != "asc" else ""
        print(f"Holdings{sort_desc}:")
        print_table(
            h_rows,
            columns=["tradingsymbol", "exchange", "quantity", "avg_price", "last_price", "invested", "value", "pnl", "pnl_pct", "day_change"],
            headers=["Symbol", "Exch", "Qty", "Avg", "LTP", "Invested", "Value", "PnL", "PnL %", "Day Change"]
        )
        print(f"Total Invested: {rupee(h_agg['invested'])}")
        print(f"Current Value:  {rupee(h_agg['value'])}")
        print(f"Unrealized PnL: {rupee(h_agg['pnl'])} ({q2(h_agg['pnl_pct'])}%)")
        print(f"Day's Change: {rupee(h_agg['day_change'])} ({get_trend_indicator(h_agg['day_change'])} {q2(pct(h_agg['day_change'], h_agg['value']))}%)")
        print_rule()

    if mode in ["all", "positions"]:
        print("Positions (Day):")
        print_table(
            d_rows,
            columns=["product", "tradingsymbol", "exchange", "qty", "avg_price", "ltp", "m2m"],
            headers=["Prod", "Symbol", "Exch", "Qty", "Avg", "LTP", "M2M"]
        )
        print(f"Total Day M2M: {rupee(d_m2m)}")
        print_rule()

        print("Positions (Net):")
        print_table(
            n_rows,
            columns=["product", "tradingsymbol", "exchange", "qty", "avg_price", "ltp", "m2m"],
            headers=["Prod", "Symbol", "Exch", "Qty", "Avg", "LTP", "M2M"]
        )
        print(f"Total Net M2M (approx): {rupee(n_m2m)}")
        print_rule()

    return h_rows, d_rows, n_rows, h_agg, d_m2m, n_m2m


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Zerodha Portfolio Status Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python zerodha.py                    # Simple mode (default)
  python zerodha.py --detailed         # Detailed mode with all data
  python zerodha.py --holdings         # Holdings only
  python zerodha.py --positions        # Positions only
  python zerodha.py --funds            # Funds only
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="Show detailed view with all tables"
    )
    group.add_argument(
        "--holdings",
        action="store_true",
        help="Show only holdings information"
    )
    group.add_argument(
        "--positions", "-p",
        action="store_true",
        help="Show only positions information"
    )
    group.add_argument(
        "--funds", "-f",
        action="store_true",
        help="Show only funds information"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show raw API response data for debugging"
    )
    
    parser.add_argument(
        "--sort", "-s",
        choices=["symbol", "quantity", "ltp", "invested", "value", "pnl", "pnl_pct", "day_change"],
        default=DEFAULT_SORT_BY,
        help=f"Sort holdings by specified field (default: {DEFAULT_SORT_BY})"
    )
    
    parser.add_argument(
        "--order", "-o",
        choices=["asc", "desc"],
        default=DEFAULT_SORT_ORDER,
        help=f"Sort order: asc (ascending) or desc (descending) (default: {DEFAULT_SORT_ORDER})"
    )
    
    parser.add_argument(
        "--export", "-e",
        action="store_true",
        default=DEFAULT_EXPORT_CSV,
        help=f"Export CSV files (default: {'enabled' if DEFAULT_EXPORT_CSV else 'disabled'})"
    )
    
    # Override debug default if not specified
    parser.set_defaults(debug=DEFAULT_DEBUG)
    
    return parser.parse_args()


# Main Function
def main():
    """Main execution flow."""
    args = parse_arguments()
    kite = get_kite()

    # Determine display mode based on defaults and arguments
    if args.detailed or (DEFAULT_MODE == "detailed" and not any([args.holdings, args.positions, args.funds])):
        h_rows, d_rows, n_rows, h_agg, d_m2m, n_m2m = print_detailed_view(kite, "all", args.debug, args.sort, args.order)
    elif args.holdings or (DEFAULT_MODE == "holdings" and not any([args.detailed, args.positions, args.funds])):
        h_rows, d_rows, n_rows, h_agg, d_m2m, n_m2m = print_detailed_view(kite, "holdings", args.debug, args.sort, args.order)
    elif args.positions or (DEFAULT_MODE == "positions" and not any([args.detailed, args.holdings, args.funds])):
        h_rows, d_rows, n_rows, h_agg, d_m2m, n_m2m = print_detailed_view(kite, "positions", args.debug, args.sort, args.order)
    elif args.funds or (DEFAULT_MODE == "funds" and not any([args.detailed, args.holdings, args.positions])):
        h_rows, d_rows, n_rows, h_agg, d_m2m, n_m2m = print_detailed_view(kite, "funds", args.debug, args.sort, args.order)
    else:
        # Simple mode (default)
        margins = fetch_margins(kite, args.debug)
        avail_cash = d(safe_get(margins, "available", {}).get("cash", 0)) if isinstance(margins.get("available", {}), dict) else d(0)
        utilised = d(safe_get(margins, "utilised", {}).get("debits", 0)) if isinstance(margins.get("utilised", {}), dict) else d(0)
        
        holdings = fetch_holdings(kite, args.debug)
        h_rows, h_agg = summarize_holdings(holdings)
        
        day_pos, net_pos = fetch_positions(kite, args.debug)
        d_rows, d_m2m = summarize_positions(day_pos)
        n_rows, n_m2m = summarize_positions(net_pos)
        
        print_simple_summary(h_agg, d_m2m, n_m2m, avail_cash, utilised, h_rows)

    # Save CSV snapshots (only when export is enabled)
    if args.export:
        snap_dir = os.path.join(os.getcwd(), "kite_snapshots")
        os.makedirs(snap_dir, exist_ok=True)
        stamp = ts()

        if h_rows:
            write_csv(
                os.path.join(snap_dir, f"holdings_{stamp}.csv"),
                h_rows,
                header=["tradingsymbol", "exchange", "quantity", "avg_price", "last_price", "invested", "value", "pnl", "pnl_pct", "day_change"]
            )
        
        if d_rows:
            write_csv(
                os.path.join(snap_dir, f"positions_day_{stamp}.csv"),
                d_rows,
                header=["product", "tradingsymbol", "exchange", "qty", "avg_price", "ltp", "m2m"]
            )
        
        if n_rows:
            write_csv(
                os.path.join(snap_dir, f"positions_net_{stamp}.csv"),
                n_rows,
                header=["product", "tradingsymbol", "exchange", "qty", "avg_price", "ltp", "m2m"]
            )

        print(f"\nCSV snapshots saved under: {snap_dir}")


if __name__ == "__main__":
    # Retry mechanism for transient network issues
    for attempt in range(1, 3):
        try:
            main()
            break
        except Exception as ex:
            if attempt >= 2:
                print(f"FATAL: {ex}", file=sys.stderr)
                sys.exit(2)
            time.sleep(1.0)
