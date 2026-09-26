#!/usr/bin/env python3
"""Compute net pay given gross, tax rate, deductions."""
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Employee:
    name: str
    gross: Decimal
    tax_rate: Decimal = Decimal("0.16")
    deductions: Decimal = Decimal("0")

    @property
    def net(self) -> Decimal:
        return self.gross * (Decimal("1") - self.tax_rate) - self.deductions


if __name__ == "__main__":
    employees = [
        Employee("Alice", Decimal("5000")),
        Employee("Bob", Decimal("4200"), deductions=Decimal("200")),
    ]
    for e in employees:
        print(f"{e.name}: gross={e.gross}, net={e.net:.2f}")
