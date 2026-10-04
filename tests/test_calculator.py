"""Tests for the payroll calculator."""

from decimal import Decimal

import pytest

from hr_payroll.calculator import compute
from hr_payroll.config import Bracket, TaxConfig


def _basic_config():
    return TaxConfig(
        currency="USD",
        brackets=[
            Bracket(up_to=Decimal("10000"), rate=Decimal("0.0")),
            Bracket(up_to=Decimal("40000"), rate=Decimal("0.10")),
            Bracket(up_to=None, rate=Decimal("0.22")),
        ],
        social_security_rate=Decimal("0.062"),
        social_security_cap=Decimal("160000"),
        medicare_rate=Decimal("0.0145"),
        pension_rate=Decimal("0.05"),
    )


def test_zero_gross():
    result = compute(0, _basic_config())
    assert result.gross == Decimal("0.00")
    assert result.net == Decimal("0.00")


def test_below_first_bracket_no_income_tax():
    result = compute(5000, _basic_config())
    income_tax = next(d for d in result.deductions if d.label == "Income Tax")
    assert income_tax.amount == Decimal("0.00")


def test_first_bracket_boundary():
    result = compute(10000, _basic_config())
    income_tax = next(d for d in result.deductions if d.label == "Income Tax")
    assert income_tax.amount == Decimal("0.00")


def test_second_bracket_partial():
    # 10000 taxed at 0%, next 10000 taxed at 10% => 1000
    result = compute(20000, _basic_config())
    income_tax = next(d for d in result.deductions if d.label == "Income Tax")
    assert income_tax.amount == Decimal("1000.00")


def test_third_bracket():
    # 10000 * 0 + 30000 * 0.10 + 10000 * 0.22 = 3000 + 2200 = 5200
    result = compute(50000, _basic_config())
    income_tax = next(d for d in result.deductions if d.label == "Income Tax")
    assert income_tax.amount == Decimal("5200.00")


def test_net_is_gross_minus_deductions():
    result = compute(60000, _basic_config())
    expected_net = result.gross - result.total_deductions
    assert result.net == expected_net


def test_social_security_cap_applies():
    # With cap 160000 and gross 200000, SS should be 160000 * 0.062 = 9920
    result = compute(200000, _basic_config())
    ss = next(d for d in result.deductions if d.label == "Social Security")
    assert ss.amount == Decimal("9920.00")


def test_pre_tax_deductions_reduce_taxable_income():
    # 60000 - 10000 = 50000 taxable -> same tax as 50000 alone
    result_with = compute(60000, _basic_config(),
                          pre_tax_deductions=[("401k", 10000)])
    result_without = compute(50000, _basic_config())
    tax_with = next(d for d in result_with.deductions if d.label == "Income Tax")
    tax_without = next(d for d in result_without.deductions if d.label == "Income Tax")
    assert tax_with.amount == tax_without.amount


def test_pre_tax_deduction_appears_in_deductions():
    result = compute(60000, _basic_config(),
                     pre_tax_deductions=[("401k", 5000)])
    labels = [d.label for d in result.deductions]
    assert "401k" in labels
