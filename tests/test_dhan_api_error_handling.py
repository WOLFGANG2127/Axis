"""Tests for _raise_for_api_error in src/data/dhan_client.py.

Covers the critical post-patch behaviour:
  - HTTP 4xx → RuntimeError (unchanged)
  - HTTP 200 + {"errorCode": ...} → RuntimeError (existing path, unchanged)
  - HTTP 200 + {"status": "error", rate-limit message} → DhanRateLimitError (NEW)
  - HTTP 200 + {"status": "error", other message} → RuntimeError (NEW)
  - HTTP 200 + clean JSON → returns normally (no regression)
  - HTTP 200 + non-JSON body → returns normally (no crash on HTML pages)
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock

import pytest

from src.data.dhan_client import DhanRateLimitError, _raise_for_api_error


def _mock_response(status_code: int, body: object | str) -> MagicMock:
    """Build a minimal httpx.Response mock."""
    mock = MagicMock()
    mock.status_code = status_code

    if isinstance(body, str):
        mock.text = body
        mock.json.side_effect = ValueError("not JSON")
    else:
        mock.text = json.dumps(body)
        mock.json.return_value = body

    # raise_for_status should raise only for 4xx/5xx
    if status_code >= 400:
        mock.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    else:
        mock.raise_for_status.return_value = None

    return mock


class TestRaiseForApiError(unittest.TestCase):

    # -----------------------------------------------------------------------
    # HTTP-level errors (pre-existing behaviour, must not regress)
    # -----------------------------------------------------------------------

    def test_http_401_raises_runtime_error(self):
        mock = _mock_response(401, {"errorCode": "UNAUTHORIZED", "errorMessage": "bad token"})
        with self.assertRaises(RuntimeError) as ctx:
            _raise_for_api_error(mock)
        self.assertIn("401", str(ctx.exception))

    def test_http_400_raises_runtime_error(self):
        mock = _mock_response(400, {"message": "Bad request"})
        with self.assertRaises(RuntimeError) as ctx:
            _raise_for_api_error(mock)
        self.assertIn("400", str(ctx.exception))

    def test_http_200_with_error_code_raises_runtime_error(self):
        """Pre-existing errorCode check on 200 must still work."""
        mock = _mock_response(200, {"errorCode": "DH-902", "errorMessage": "Invalid token"})
        with self.assertRaises(RuntimeError) as ctx:
            _raise_for_api_error(mock)
        self.assertIn("DH-902", str(ctx.exception))

    # -----------------------------------------------------------------------
    # NEW: JSON-body status=error on HTTP 200
    # -----------------------------------------------------------------------

    def test_http_200_rate_limit_raises_dhan_rate_limit_error(self):
        """The exact Dhan rate-limit payload must raise DhanRateLimitError, not RuntimeError."""
        payload = {
            "status": "error",
            "message": "Token can be generated once every 2 minutes.",
        }
        mock = _mock_response(200, payload)
        with self.assertRaises(DhanRateLimitError) as ctx:
            _raise_for_api_error(mock)
        self.assertIn("rate limit", str(ctx.exception).lower())

    def test_dhan_rate_limit_error_is_subclass_of_runtime_error(self):
        """DhanRateLimitError must be catchable as a RuntimeError for backwards compat."""
        self.assertTrue(issubclass(DhanRateLimitError, RuntimeError))

    def test_http_200_other_status_error_raises_runtime_error(self):
        """status=error with a non-rate-limit message → plain RuntimeError, not DhanRateLimitError."""
        payload = {"status": "error", "message": "Service unavailable"}
        mock = _mock_response(200, payload)
        with self.assertRaises(RuntimeError) as ctx:
            _raise_for_api_error(mock)
        # Must NOT be the retryable subclass
        self.assertNotIsInstance(ctx.exception, DhanRateLimitError)
        self.assertIn("status=error", str(ctx.exception))

    # -----------------------------------------------------------------------
    # Clean pass-through cases — must NOT regress
    # -----------------------------------------------------------------------

    def test_http_200_clean_json_returns_normally(self):
        """A normal success response must not raise anything."""
        payload = {"dhanClientId": "123", "accessToken": "eyJ..."}
        mock = _mock_response(200, payload)
        # Should complete without exception
        _raise_for_api_error(mock)

    def test_http_200_non_json_body_returns_normally(self):
        """Non-JSON 200 (e.g. raw HTML health-check) must not crash."""
        mock = _mock_response(200, "<html>OK</html>")
        # Should complete without exception
        _raise_for_api_error(mock)

    def test_http_200_non_dict_json_returns_normally(self):
        """A JSON array body on 200 must not raise (some list endpoints)."""
        mock = _mock_response(200, [{"candle": 1}])
        _raise_for_api_error(mock)


if __name__ == "__main__":
    unittest.main()
