"""Read-only Dhan v2 market-data client.

This module deliberately exposes no order-placement operation.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Literal
from zoneinfo import ZoneInfo

import httpx

from src.config.settings import settings

IST = ZoneInfo("Asia/Kolkata")
DHAN_API = "https://api.dhan.co/v2"
DHAN_AUTH_API = "https://auth.dhan.co/app/generateAccessToken"
UNDERLYINGS = {
    "NIFTY": {"security_id": 13, "segment": "IDX_I"},
    "BANKNIFTY": {"security_id": 25, "segment": "IDX_I"},
}
VALID_INTERVALS = {"1", "5", "15", "25", "60"}
TrustStatus = Literal["live", "stale", "demo-fallback"]


def _now() -> datetime:
    return datetime.now(IST)


def _envelope(data: Any, trust_status: TrustStatus = "live") -> dict[str, Any]:
    return {
        "data": data,
        "fetched_at": _now().isoformat(),
        "trust_status": trust_status,
    }


def _headers(*, include_client_id: bool = True) -> dict[str, str]:
    from src.database.supabase import get_supabase_client
    client = get_supabase_client()
    res = client.table("broker_tokens").select("access_token").eq("id", 1).execute()
    if not res.data:
        raise RuntimeError("broker_tokens table missing row id=1")
    active_token = res.data[0]["access_token"]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "access-token": active_token,
    }
    if include_client_id:
        headers["client-id"] = settings.DHAN_CLIENT_ID
    return headers


def _underlying(symbol: str) -> dict[str, Any]:
    normalized = symbol.strip().upper()
    try:
        return UNDERLYINGS[normalized]
    except KeyError as exc:
        raise ValueError("symbol must be NIFTY or BANKNIFTY") from exc


def _raise_for_api_error(response: httpx.Response) -> None:
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict) and payload.get("errorCode"):
        raise RuntimeError(
            f"Dhan API {payload['errorCode']}: {payload.get('errorMessage', 'unknown error')}"
        )


def _candles_from_columnar(payload: dict[str, Any]) -> list[dict[str, Any]]:
    timestamps = payload.get("timestamp", [])
    columns = ("open", "high", "low", "close", "volume", "oi")
    candles: list[dict[str, Any]] = []
    for index, stamp in enumerate(timestamps):
        candle: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(float(stamp), tz=IST).isoformat()
        }
        for column in columns:
            values = payload.get(column, [])
            candle[column] = values[index] if index < len(values) else None
        candles.append(candle)
    return candles


def get_candles(
    symbol: str,
    interval: str | int,
    *,
    client: httpx.Client | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Fetch today's read-only index candles in the standard data envelope."""
    interval_text = str(interval)
    if interval_text not in VALID_INTERVALS:
        raise ValueError(f"interval must be one of {sorted(VALID_INTERVALS)}")
    instrument = _underlying(symbol)
    current = (now or _now()).astimezone(IST)
    start = current.replace(hour=9, minute=15, second=0, microsecond=0)
    body = {
        "securityId": str(instrument["security_id"]),
        "exchangeSegment": instrument["segment"],
        "instrument": "INDEX",
        "interval": interval_text,
        "oi": False,
        "fromDate": start.strftime("%Y-%m-%d %H:%M:%S"),
        "toDate": current.strftime("%Y-%m-%d %H:%M:%S"),
    }
    owns_client = client is None
    active_client = client or httpx.Client(timeout=20.0)
    try:
        response = active_client.post(
            f"{DHAN_API}/charts/intraday", headers=_headers(), json=body
        )
        _raise_for_api_error(response)
        return _envelope(_candles_from_columnar(response.json()))
    finally:
        if owns_client:
            active_client.close()


def get_option_chain(
    symbol: str,
    expiry: str,
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Fetch a Dhan option-chain snapshot without placing any order."""
    instrument = _underlying(symbol)
    datetime.strptime(expiry, "%Y-%m-%d")
    body = {
        "UnderlyingScrip": instrument["security_id"],
        "UnderlyingSeg": instrument["segment"],
        "Expiry": expiry,
    }
    owns_client = client is None
    active_client = client or httpx.Client(timeout=20.0)
    try:
        response = active_client.post(
            f"{DHAN_API}/optionchain", headers=_headers(), json=body
        )
        _raise_for_api_error(response)
        payload = response.json()
        return _envelope(payload.get("data", payload))
    finally:
        if owns_client:
            active_client.close()


def get_expiry_list(
    symbol: str,
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Fetch active option expiries for an index underlying."""
    instrument = _underlying(symbol)
    body = {
        "UnderlyingScrip": instrument["security_id"],
        "UnderlyingSeg": instrument["segment"],
    }
    owns_client = client is None
    active_client = client or httpx.Client(timeout=20.0)
    try:
        response = active_client.post(
            f"{DHAN_API}/optionchain/expirylist", headers=_headers(), json=body
        )
        _raise_for_api_error(response)
        payload = response.json()
        return _envelope(payload.get("data", payload))
    finally:
        if owns_client:
            active_client.close()


def renew_token(*, client: httpx.Client | None = None) -> dict[str, Any]:
    """Renew a still-active Dhan Web token for another 24 hours."""
    from src.database.supabase import get_supabase_client
    db_client = get_supabase_client()
    res = db_client.table("broker_tokens").select("access_token").eq("id", 1).execute()
    if not res.data:
        raise RuntimeError("broker_tokens table missing row id=1")
    active_token = res.data[0]["access_token"]

    owns_client = client is None
    active_client = client or httpx.Client(timeout=20.0)
    headers = {
        "Accept": "application/json",
        "access-token": active_token,
        "dhanClientId": settings.DHAN_CLIENT_ID,
    }
    try:
        response = active_client.get(f"{DHAN_API}/RenewToken", headers=headers)
        _raise_for_api_error(response)
        return _envelope(response.json())
    finally:
        if owns_client:
            active_client.close()


def generate_access_token(
    pin: str,
    totp: str,
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Generate a token using a PIN and a pyotp-produced live TOTP code."""
    if not pin.strip() or not totp.strip():
        raise ValueError("pin and totp are required")
    owns_client = client is None
    active_client = client or httpx.Client(timeout=20.0)
    try:
        response = active_client.post(
            DHAN_AUTH_API,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json={
                "dhanClientId": settings.DHAN_CLIENT_ID,
                "pin": pin,
                "totp": totp,
            },
        )
        _raise_for_api_error(response)
        return _envelope(response.json())
    finally:
        if owns_client:
            active_client.close()


def generate_totp(secret: str) -> str:
    """Produce the live code expected by :func:`generate_access_token`."""
    try:
        import pyotp
    except ImportError as exc:  # pragma: no cover - deployment dependency guard
        raise RuntimeError("pyotp is required to generate a Dhan TOTP") from exc
    return pyotp.TOTP(secret).now()
