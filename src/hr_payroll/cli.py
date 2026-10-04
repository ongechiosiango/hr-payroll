"""Command-line interface for HR Payroll."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from . import __version__
from .calculator import compute
from .config import ConfigError, load_config
from .money import to_decimal
from .register import RegisterError, process_register
from .reporter import (
    print_payslip,
    print_register,
    register_to_json,
    to_json,
)

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hr-payroll",
        description="Compute net pay from gross, using a JSON tax config.",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--gross", "-g", help="Gross pay for a single employee.")
    src.add_argument("--csv", help="Path to an employees CSV (columns: name, gross).")

    parser.add_argument("--config", "-c", required=True,
                        help="Path to the tax config JSON.")
    parser.add_argument("--name", "-n", default="Employee",
                        help="Name for single-employee payslip (default: Employee).")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Output as JSON instead of a pretty table.")
    parser.add_argument("--version", action="version",
                        version=f"hr-payroll {__version__}")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        console.print(f"[bold red]Config error:[/bold red] {exc}")
        return 1

    if args.gross is not None:
        try:
            gross = to_decimal(args.gross)
        except Exception as exc:  # noqa: BLE001
            console.print(f"[bold red]Invalid gross:[/bold red] {exc}")
            return 1

        result = compute(gross, config)

        if args.as_json:
            print(to_json(result, currency=config.currency, name=args.name))
        else:
            print_payslip(result, currency=config.currency, name=args.name)
        return 0

    # --csv path
    try:
        rows = process_register(args.csv, config)
    except RegisterError as exc:
        console.print(f"[bold red]Register error:[/bold red] {exc}")
        return 1

    if args.as_json:
        print(register_to_json(rows, currency=config.currency))
    else:
        print_register(rows, currency=config.currency)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
