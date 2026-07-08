"""Exact Dhan derivative-instrument resolution with a daily local cache."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import httpx

IST = ZoneInfo("Asia/Kolkata")
MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE = PROJECT_ROOT / "data" / "cache" / "api-scrip-master-detailed.csv"


class InstrumentNotFoundError(LookupError):
    """Raised when the exact contract is absent from the instrument master."""


class AmbiguousInstrumentError(LookupError):
    """Raised when an supposedly exact contract maps to multiple IDs."""


def _value(row: dict[str, Any], *names: str) -> str:
    for name in names:
        if name in row and row[name] is not None:
            return str(row[name]).strip()
    return ""


def refresh_instrument_master(
    *,
    cache_path: Path = DEFAULT_CACHE,
    client: httpx.Client | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Refresh the detailed master at most once per IST calendar day."""
    now = datetime.now(IST)
    if cache_path.exists() and not force:
        modified = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=IST)
        if modified.date() == now.date():
            return {"data": str(cache_path), "fetched_at": modified.isoformat(), "trust_status": "live"}
    owns_client = client is None
    active_client = client or httpx.Client(timeout=30.0, follow_redirects=True)
    try:
        response = active_client.get(MASTER_URL)
        response.raise_for_status()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(response.content)
        return {"data": str(cache_path), "fetched_at": now.isoformat(), "trust_status": "live"}
    finally:
        if owns_client:
            active_client.close()


def _read_rows(cache_path: Path) -> list[dict[str, str]]:
    if not cache_path.exists():
        refresh_instrument_master(cache_path=cache_path)
    with cache_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def resolve(
    symbol: str,
    strike: int | float,
    expiry: str,
    option_type: str,
    *,
    master_rows: Iterable[dict[str, Any]] | None = None,
    cache_path: Path = DEFAULT_CACHE,
) -> int:
    """Resolve after exact symbol -> expiry -> option type -> strike filters."""
    datetime.strptime(expiry, "%Y-%m-%d")
    normalized_symbol = symbol.strip().upper()
    normalized_option = option_type.strip().upper()
    if normalized_option not in {"CE", "PE"}:
        raise ValueError("option_type must be CE or PE")
    rows = list(master_rows) if master_rows is not None else _read_rows(cache_path)

    by_symbol = [
        row for row in rows
        if _value(row, "UNDERLYING_SYMBOL", "SM_SYMBOL_NAME", "SYMBOL_NAME").upper() == normalized_symbol
    ]
    by_expiry = [
        row for row in by_symbol
        if _value(row, "SM_EXPIRY_DATE", "SEM_EXPIRY_DATE")[:10] == expiry
    ]
    by_option = [
        row for row in by_expiry
        if _value(row, "OPTION_TYPE", "SEM_OPTION_TYPE").upper() == normalized_option
    ]
    exact = [
        row for row in by_option
        if float(_value(row, "STRIKE_PRICE", "SEM_STRIKE_PRICE") or "nan") == float(strike)
    ]
    if not exact:
        raise InstrumentNotFoundError(
            f"No instrument for {normalized_symbol} {expiry} {strike:g} {normalized_option}"
        )
    if len(exact) > 1:
        raise AmbiguousInstrumentError(
            f"Multiple instruments for {normalized_symbol} {expiry} {strike:g} {normalized_option}"
        )
    security_id = _value(exact[0], "SECURITY_ID", "SEM_SMST_SECURITY_ID", "SEM_SECURITY_ID")
    if not security_id:
        raise InstrumentNotFoundError("matching instrument has no security ID")
    return int(float(security_id))

