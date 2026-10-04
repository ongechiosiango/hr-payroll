"""Read employees from CSV and compute payroll for each."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .calculator import PayrollResult, compute
from .config import TaxConfig
from .money import to_decimal


class RegisterError(Exception):
    """Raised when the employee CSV cannot be loaded or is invalid."""


@dataclass
class EmployeeRow:
    """One row from the employees CSV."""

    name: str
    gross: str           # kept as string, parsed by calculator
    result: PayrollResult


def load_employees(path: str) -> List[dict]:
    """Read the employee CSV. Required column: name, gross."""
    p = Path(path)
    if not p.exists():
        raise RegisterError(f"Employees file not found: {path}")
    if not p.is_file():
        raise RegisterError(f"Not a file: {path}")

    try:
        with p.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise RegisterError("CSV has no header row.")
            missing = {"name", "gross"} - set(reader.fieldnames)
            if missing:
                raise RegisterError(
                    f"CSV is missing required column(s): {sorted(missing)}"
                )
            rows = [dict(r) for r in reader]
    except OSError as exc:
        raise RegisterError(f"Could not read {path}: {exc}") from exc

    return rows


def process_register(path: str, config: TaxConfig) -> List[EmployeeRow]:
    """Load employees and compute payroll for each."""
    rows = load_employees(path)
    results: List[EmployeeRow] = []

    for i, row in enumerate(rows, start=1):
        name = (row.get("name") or "").strip()
        gross_raw = (row.get("gross") or "").strip()
        if not name:
            raise RegisterError(f"Row {i}: missing 'name'.")
        if not gross_raw:
            raise RegisterError(f"Row {i}: missing 'gross'.")

        try:
            gross = to_decimal(gross_raw)
        except Exception as exc:  # noqa: BLE001
            raise RegisterError(f"Row {i}: invalid gross {gross_raw!r}: {exc}") from exc

        result = compute(gross, config)
        results.append(EmployeeRow(name=name, gross=gross_raw, result=result))

    return results
