"""Correlation ID generation for a single AXIS cycle."""

from __future__ import annotations

from uuid import uuid4


def new_correlation_id() -> str:
    return str(uuid4())
