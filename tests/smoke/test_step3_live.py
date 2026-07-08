"""Manual read-only Step 3 smoke test; never imported by the live pipeline."""

from __future__ import annotations

from src.data.dhan_client import get_candles
from src.data.instrument_resolver import refresh_instrument_master, resolve
from src.data.nse_fetcher import fetch_option_chain


def main() -> None:
    symbol = "NIFTY"
    nse = fetch_option_chain(symbol)
    payload = nse["data"]
    if "records" in payload:
        expiry = payload["records"]["expiryDates"][0]
        underlying = float(payload["records"]["underlyingValue"])
        expiry_rows = [
            row for row in payload["records"]["data"]
            if row.get("expiryDate") == expiry
        ]
        strike = float(min(expiry_rows, key=lambda row: abs(float(row["strikePrice"]) - underlying))["strikePrice"])
        strike_count = len(expiry_rows)
    else:
        expiry = payload["expiry"]
        underlying = float(payload["last_price"])
        strikes = [float(item) for item in payload["oc"]]
        strike = min(strikes, key=lambda item: abs(item - underlying))
        strike_count = len(strikes)

    candles = get_candles(symbol, 5)
    refresh_instrument_master()
    token = resolve(symbol, strike, expiry, "CE")

    assert candles["trust_status"] == "live" and candles["data"]
    assert nse["trust_status"] == "live"
    assert token > 0
    print(f"PASS candle: {symbol} close={candles['data'][-1]['close']}")
    print(f"PASS option chain: expiry={expiry}, strikes={strike_count}")
    print(f"PASS resolver: {symbol} {expiry} {strike:g} CE -> {token}")


if __name__ == "__main__":
    main()
