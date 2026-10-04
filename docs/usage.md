# Usage Guide

## Tax config format

The config is a JSON file describing tax brackets and rates:

    {
      "currency": "USD",
      "income_tax_brackets": [
        {"up_to": 10000, "rate": 0.0},
        {"up_to": 40000, "rate": 0.10},
        {"up_to": null,  "rate": 0.22}
      ],
      "social_security_rate": 0.062,
      "social_security_cap": 160000,
      "medicare_rate": 0.0145,
      "pension_rate": 0.05
    }

- `up_to: null` means an unbounded top bracket.
- Rates are decimal fractions (0.10 = 10%).
- All amounts are pre-tax income for the pay period.

## Single employee

    hr-payroll --gross 60000 --config examples/taxes.json

## Named payslip

    hr-payroll --gross 60000 --config examples/taxes.json --name "Alice Johnson"

## Batch from CSV

CSV must have `name` and `gross` columns:

    name,gross
    Alice Johnson,60000
    Bob Smith,45000

Then run:

    hr-payroll --csv examples/employees.csv --config examples/taxes.json

## JSON output

Add `--json` to either mode:

    hr-payroll --gross 60000 --config examples/taxes.json --json

## Money correctness

This tool uses Python `Decimal` and banker's rounding (ROUND_HALF_EVEN)
to match accounting conventions. You will never see `0.30000000000000004`
style artifacts.
