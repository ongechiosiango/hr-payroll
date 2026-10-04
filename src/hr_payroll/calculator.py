"""Core payroll calculator: gross -> net with configurable deductions."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Tuple

from .config import TaxConfig
from .money import ZERO, round_cents, to_decimal


@dataclass
class Deduction:
    """One line item on a payslip."""

    label: str
    amount: Decimal


@dataclass
class PayrollResult:
    """Full breakdown for one employee."""

    gross: Decimal
    deductions: List[Deduction] = field(default_factory=list)
    net: Decimal = ZERO

    @property
    def total_deductions(self) -> Decimal:
        return sum((d.amount for d in self.deductions), start=ZERO)


def _income_tax(gross: Decimal, brackets: List[Tuple[Decimal, Decimal]]) -> Decimal:
    """Progressive tax: brackets is a sorted list of (upper_bound_or_None, rate)."""
    if not brackets:
        return ZERO

    tax = ZERO
    lower = ZERO

    for upper, rate in brackets:
        rate = to_decimal(rate)
        if upper is None:
            taxable = max(gross - lower, ZERO)
            tax += taxable * rate
            break
        if gross <= lower:
            break
        taxable = min(gross, upper) - lower
        if taxable > 0:
            tax += taxable * rate
        lower = upper

    return tax


def compute(
    gross,
    config: TaxConfig,
    pre_tax_deductions=None,
) -> PayrollResult:
    """Compute net pay.

    Args:
        gross: gross pay for the period.
        config: tax configuration.
        pre_tax_deductions: optional list of (label, amount) deducted BEFORE tax.
    """
    gross = round_cents(to_decimal(gross))
    pre_tax_deductions = pre_tax_deductions or []
    pre_tax_total = sum((to_decimal(v) for _, v in pre_tax_deductions), start=ZERO)
    pre_tax_total = round_cents(pre_tax_total)

    taxable_income = max(gross - pre_tax_total, ZERO)

    brackets_sorted: List[Tuple[Decimal, Decimal]] = [
        (b.up_to, b.rate) for b in config.brackets
    ]
    # Sort with None last (unbounded bracket)
    brackets_sorted.sort(key=lambda x: (x[0] is None, x[0] if x[0] is not None else ZERO))

    income_tax = round_cents(_income_tax(taxable_income, brackets_sorted))

    # Social security, capped at the configured threshold.
    ss_base = taxable_income
    if config.social_security_cap is not None:
        ss_base = min(ss_base, config.social_security_cap)
    social_security = round_cents(ss_base * config.social_security_rate)
    medicare = round_cents(taxable_income * config.medicare_rate)
    pension = round_cents(taxable_income * config.pension_rate)

    deductions: List[Deduction] = []
    for label, amount in pre_tax_deductions:
        deductions.append(Deduction(label=label, amount=round_cents(to_decimal(amount))))
    deductions.append(Deduction("Income Tax", income_tax))
    deductions.append(Deduction("Social Security", social_security))
    deductions.append(Deduction("Medicare", medicare))
    deductions.append(Deduction("Pension", pension))

    total_deductions = sum((d.amount for d in deductions), start=ZERO)
    net = round_cents(gross - total_deductions)

    return PayrollResult(gross=gross, deductions=deductions, net=net)
