"""Load a tax configuration from JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from .money import to_decimal


class ConfigError(Exception):
    """Raised when a tax config is missing, unreadable, or invalid."""


@dataclass
class Bracket:
    """One income tax bracket."""

    up_to: Optional[Decimal]   # None means "no upper bound"
    rate: Decimal              # e.g. Decimal("0.10")

    def __post_init__(self):
        """Coerce rate/up_to to Decimal so callers can pass int or float safely."""
        self.rate = to_decimal(self.rate)
        if self.up_to is not None:
            self.up_to = to_decimal(self.up_to)


@dataclass
class TaxConfig:
    """Parsed tax configuration."""

    currency: str = "USD"
    brackets: List[Bracket] = field(default_factory=list)
    social_security_rate: Decimal = Decimal("0")
    social_security_cap: Optional[Decimal] = None
    medicare_rate: Decimal = Decimal("0")
    pension_rate: Decimal = Decimal("0")


def _parse_bracket(raw: dict) -> Bracket:
    if "rate" not in raw:
        raise ConfigError("Each income_tax_brackets entry needs a 'rate'.")
    rate = to_decimal(raw["rate"])
    if rate < 0 or rate > 1:
        raise ConfigError(f"Bracket rate must be between 0 and 1, got {rate}")

    up_to_raw = raw.get("up_to")
    up_to = None if up_to_raw is None else to_decimal(up_to_raw)
    if up_to is not None and up_to < 0:
        raise ConfigError(f"Bracket up_to must be >= 0, got {up_to}")

    return Bracket(up_to=up_to, rate=rate)


def load_config(path: str) -> TaxConfig:
    """Load a tax config from a JSON file."""
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: {path}")
    if not p.is_file():
        raise ConfigError(f"Not a file: {path}")

    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Could not read {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("Config root must be a JSON object.")

    brackets_raw = raw.get("income_tax_brackets", [])
    if not isinstance(brackets_raw, list):
        raise ConfigError("'income_tax_brackets' must be a list.")

    brackets = [_parse_bracket(b) for b in brackets_raw]

    cap_raw = raw.get("social_security_cap")
    cap = None if cap_raw is None else to_decimal(cap_raw)

    return TaxConfig(
        currency=str(raw.get("currency", "USD")),
        brackets=brackets,
        social_security_rate=to_decimal(raw.get("social_security_rate", 0)),
        social_security_cap=cap,
        medicare_rate=to_decimal(raw.get("medicare_rate", 0)),
        pension_rate=to_decimal(raw.get("pension_rate", 0)),
    )
