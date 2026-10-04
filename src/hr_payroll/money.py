"""Money helpers using Decimal with banker's rounding to cents.

Never use float for currency. Decimal avoids the classic 0.1 + 0.2 bug
and ROUND_HALF_EVEN matches the accounting standard used by most tax
authorities.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def to_decimal(value) -> Decimal:
    """Coerce int/str/Decimal to Decimal. Floats are accepted but discouraged."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        return Decimal(value)
    if isinstance(value, float):
        # Convert via string to avoid float binary artifacts.
        return Decimal(str(value))
    raise TypeError(f"Cannot convert {type(value).__name__} to Decimal")


def round_cents(value: Decimal) -> Decimal:
    """Round to two decimal places using banker's rounding."""
    return to_decimal(value).quantize(CENT, rounding=ROUND_HALF_EVEN)


def format_money(value: Decimal, currency: str = "") -> str:
    """Format a Decimal as a currency string, e.g. '1,234.56 USD'."""
    value = round_cents(value)
    formatted = f"{value:,.2f}"
    return f"{formatted} {currency}".strip()
