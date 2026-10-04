"""Tests for money helpers."""

from decimal import Decimal

import pytest

from hr_payroll.money import format_money, round_cents, to_decimal


def test_to_decimal_from_int():
    assert to_decimal(10) == Decimal("10")


def test_to_decimal_from_string():
    assert to_decimal("10.50") == Decimal("10.50")


def test_to_decimal_from_float_uses_string():
    # 0.1 + 0.2 is notorious for float representation issues.
    assert to_decimal(0.1) == Decimal("0.1")


def test_to_decimal_invalid_type():
    with pytest.raises(TypeError):
        to_decimal([1, 2, 3])


def test_round_cents_basic():
    assert round_cents(Decimal("1.234")) == Decimal("1.23")
    assert round_cents(Decimal("1.236")) == Decimal("1.24")


def test_round_cents_banker_rounding():
    # Half-even: 1.225 -> 1.22, 1.235 -> 1.24
    assert round_cents(Decimal("1.225")) == Decimal("1.22")
    assert round_cents(Decimal("1.235")) == Decimal("1.24")


def test_format_money_with_currency():
    assert format_money(Decimal("1234.5"), "USD") == "1,234.50 USD"


def test_format_money_without_currency():
    assert format_money(Decimal("1234.5")) == "1,234.50"
