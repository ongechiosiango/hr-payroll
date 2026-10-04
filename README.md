# HR Payroll

[![CI](https://github.com/ongechiosiango/hr-payroll/actions/workflows/ci.yml/badge.svg)](https://github.com/ongechiosiango/hr-payroll/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

A tiny payroll calculator: gross to net with configurable tax brackets.

## Features

- Progressive income tax with configurable brackets.
- Social security (with optional cap), medicare, and pension.
- Pre-tax deductions (e.g. 401k, health insurance).
- Batch processing from CSV for payroll registers.
- Uses Decimal + banker's rounding for correct money math.
- Pretty terminal output or JSON for scripts.

## Installation

From source:

    git clone git@github.com:ongechiosiango/hr-payroll.git
    cd hr-payroll
    python3 -m venv venv
    source venv/bin/activate
    pip install -e ".[dev]"

## Usage

Single employee:

    hr-payroll --gross 60000 --config examples/taxes.json

Batch:

    hr-payroll --csv examples/employees.csv --config examples/taxes.json

JSON output:

    hr-payroll --gross 60000 --config examples/taxes.json --json

See docs/usage.md for the config format and full details.

## Development

    pip install -e ".[dev]"
    pytest -v

## Contributing

See CONTRIBUTING.md.

## License

MIT - see LICENSE.
