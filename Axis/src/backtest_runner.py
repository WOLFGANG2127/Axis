"""Historical Backtest Runner."""

from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from src.data.event_calendar import get_monthly_expiries
from src.scheduling.calendar_gate import is_market_open
from src.graph.graph import build_graph

IST = ZoneInfo("Asia/Kolkata")

def _generate_cycle_timestamps(start_date: date, end_date: date) -> list[datetime]:
    timestamps = []
    current_date = start_date
    while current_date <= end_date:
        # Generate 5-minute intervals from 09:15 to 15:30
        current_time = datetime.combine(current_date, time(9, 15), tzinfo=IST)
        end_time = datetime.combine(current_date, time(15, 30), tzinfo=IST)
        
        while current_time <= end_time:
            if is_market_open(current_time):
                timestamps.append(current_time)
            current_time += timedelta(minutes=5)
            
        current_date += timedelta(days=1)
    return timestamps

async def run_backtest(symbol: str, start_date: date, end_date: date) -> None:
    timestamps = _generate_cycle_timestamps(start_date, end_date)
    print(f"Starting backtest for {symbol} from {start_date} to {end_date} ({len(timestamps)} cycles)")
    
    graph = build_graph()
    
    for current in timestamps:
        state = {
            "symbol": symbol,
            "is_backtest": True,
            "cycle_timestamp": current,
            "market_context": {
                "now": current.isoformat(),
                "calendar_open": True,
                "lock_acquired": True,
                "direction_score": 3,
                "structure_confirmed": False,
                "risk_approved": False,
            }
        }
        try:
            result = await graph.ainvoke(state)
            print(f"[{current.isoformat()}] Completed: {result.get('dedup_status')} - {result.get('active_strategy')}")
        except Exception as e:
            print(f"[{current.isoformat()}] Error: {e}")

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run historical backtest.")
    parser.add_argument("--symbol", required=True, choices=["NIFTY", "BANKNIFTY"])
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    return parser

if __name__ == "__main__":
    args = _parser().parse_args()
    asyncio.run(run_backtest(args.symbol, date.fromisoformat(args.start), date.fromisoformat(args.end)))
